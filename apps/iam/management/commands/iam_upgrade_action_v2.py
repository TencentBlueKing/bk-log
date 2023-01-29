# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
import sys
import time
from multiprocessing.pool import ThreadPool
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.api import TransferApi
from apps.iam import Permission, ActionEnum, ResourceEnum
from apps.iam.handlers.actions import ActionMeta, get_action_by_id
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_databus.models import CollectorConfig
from apps.log_search.models import LogIndexSet, Space, GlobalConfig
from iam.api.http import http_post
from iam.auth.models import ApiBatchAuthRequest as OldApiBatchAuthRequest, Subject, Action, ApiBatchAuthResourceWithPath
from iam.contrib.iam_migration.migrator import IAMMigrator
from iam.exceptions import AuthAPIError

ACTIONS_TO_UPGRADE = [
    ActionEnum.VIEW_BUSINESS,
    ActionEnum.SEARCH_LOG,
    ActionEnum.VIEW_COLLECTION,
    ActionEnum.CREATE_COLLECTION,
    ActionEnum.MANAGE_COLLECTION,
    ActionEnum.CREATE_ES_SOURCE,
    ActionEnum.MANAGE_ES_SOURCE,
    ActionEnum.CREATE_INDICES,
    ActionEnum.MANAGE_INDICES,
    ActionEnum.VIEW_DASHBOARD,
    ActionEnum.MANAGE_DASHBOARD,
    ActionEnum.MANAGE_EXTRACT_CONFIG,
]


class ApiBatchAuthRequest(OldApiBatchAuthRequest):
    def __init__(self, *args, expired_at=None, **kwargs):
        super(ApiBatchAuthRequest, self).__init__(*args, **kwargs)
        self.expired_at = expired_at

    def to_dict(self):
        request_dict = super(ApiBatchAuthRequest, self).to_dict()
        if self.expired_at is not None:
            request_dict["expired_at"] = self.expired_at
        return request_dict


class Command(BaseCommand):
    OPERATOR = "admin"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--concurrency", help="Concurrency of grant resource")
        parser.add_argument("-a", "--action")
        parser.add_argument("-u", "--username")

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.collector_configs = {
            str(config["collector_config_id"]): config["collector_config_name"]
            for config in CollectorConfig.objects.values("collector_config_id", "collector_config_name")
        }

        self.index_sets = {
            str(index_set["index_set_id"]): index_set["index_set_name"]
            for index_set in LogIndexSet.objects.values("index_set_id", "index_set_name")
        }

        self.spaces = {
            str(space["bk_biz_id"]): space["space_name"] for space in Space.objects.values("bk_biz_id", "space_name")
        }

        self.clusters = {
            str(cluster["cluster_config"]["cluster_id"]): cluster["cluster_config"]["cluster_name"]
            for cluster in TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True})
        }
        self.iam_client = Permission.get_iam_client()
        self.system_id = settings.BK_IAM_SYSTEM_ID
        self.username = ""

    def handle(self, action=None, concurrency=None, username=None, **options):
        start_time = time.time()
        print("[upgrade_iam_action_v2] ##### START #####")

        self.upgrade_iam_model()

        global ACTIONS_TO_UPGRADE

        if action:
            ACTIONS_TO_UPGRADE = [get_action_by_id(action)]

        print("upgrade for actions: %s" % ",".join([action.id for action in ACTIONS_TO_UPGRADE]))

        # 并发数
        concurrency = int(concurrency) if concurrency else 50
        print("upgrade with concurrency: %s" % concurrency)

        # 按用户名过滤
        self.username = username
        if username:
            print("upgrade for user: %s" % username)

        self.upgrade_policy(concurrency)

        end_time = time.time()
        print("[upgrade_iam_action_v2] ##### END #####, Cost: %d" % (end_time - start_time))

        check_result = self.check_upgrade_polices()
        if check_result:
            GlobalConfig.objects.update_or_create(config_id="IAM_V1_COMPATIBLE", defaults={"configs": False})

    def get_resource_name(self, resource_type, resource_id):
        if resource_type == ResourceEnum.BUSINESS.id:
            return self.spaces.get(resource_id, resource_id)
        if resource_type == ResourceEnum.INDICES.id:
            return self.index_sets.get(resource_id, resource_id)
        if resource_type == ResourceEnum.COLLECTION.id:
            return self.collector_configs.get(resource_id, resource_id)
        if resource_type == ResourceEnum.ES_SOURCE.id:
            return self.clusters.get(resource_id, resource_id)
        return resource_id

    @classmethod
    def upgrade_iam_model(cls):
        print("[upgrade_iam_model] [START]")

        sys.argv.append("migrate")  # enable migrator

        IAMMigrator("legacy.json").migrate()
        IAMMigrator("initial.json").migrate()

        print("[upgrade_iam_model] [END]")

    def upgrade_policy(self, concurrency):
        print("[upgrade_policy] [START]")

        global_total = 0
        global_progress = 0
        policies_by_actions = {}
        for action in ACTIONS_TO_UPGRADE:
            old_action_id = action.id.replace("_v2", "")
            policies = self.query_polices(old_action_id)
            policies_by_actions[old_action_id] = policies
            global_total += len(policies)

        for action in ACTIONS_TO_UPGRADE:
            old_action_id = action.id.replace("_v2", "")
            policies = policies_by_actions[old_action_id]
            print("[grant_resource] [START] action[%s], policy count: %d" % (action.id, len(policies)))

            total = len(policies)
            progress = 0
            resources = []

            for policy in policies:
                resource = self.policy_to_resource(action, policy)
                resources.append(resource)

            pool = ThreadPool(concurrency)
            futures = []
            results = []
            for resource in resources:
                futures.append(pool.apply_async(self.grant_resource, args=(resource,)))
            pool.close()
            pool.join()

            for future in futures:
                try:
                    results.append(future.get())
                except Exception as e:
                    print("[grant_resource] grant permission for action: {}, something wrong: {}".format(action.id, e))

            progress += len(resources)
            global_progress += len(resources)

            print(
                "[grant_resource] [%d%%(%d/%d)] grant permission for action: %s, progress: %d%% (%d/%d)"
                % (
                    global_progress / global_total * 100 if global_total > 0 else 0,
                    global_progress,
                    global_total,
                    action.id,
                    progress / total * 100 if total > 0 else 0,
                    progress,
                    total,
                )
            )

            print("[grant_resource] [END] action[%s]" % action.id)

        print("[upgrade_policy] [END]")

    def check_upgrade_polices(self):
        """
        检查升级后的策略
        """
        results = []
        for action in ACTIONS_TO_UPGRADE:
            new_policies = self.query_polices(action.id)
            old_action_id = action.id.replace("_v2", "")
            old_policies = self.query_polices(old_action_id)
            results.append((action.id, len(old_policies), len(new_policies)))

        no_ok_actions = []
        for result in results:
            if result[1] > 0 and result[2] == 0:
                # 新策略数量为0是不正常的
                no_ok_actions.append(result[0])
            print(
                "[check_upgrade_polices] action[%s] old count: %d, new count: %d, diff: %d"
                % (result[0], result[1], result[2], result[2] - result[1])
            )

        print("##### CHECK RESULT #####")
        if not no_ok_actions:
            print("Congratulations! IAM upgrade successfully!!!")
            return True

        print("Sorry, maybe something wrong with IAM upgrade. Following actions not OK: %s" % ", ".join(no_ok_actions))
        return False

    def query_polices(self, action_id):
        """
        根据操作ID查询全量权限策略
        """
        page_size = 500
        page = 1

        policies = []

        query_result = self.iam_client.query_polices_with_action_id(
            self.system_id, {"action_id": action_id, "page": page, "page_size": page_size}
        )
        policies.extend(query_result["results"])

        total = query_result["count"]

        while page * page_size < total:
            page += 1
            query_result = self.iam_client.query_polices_with_action_id(
                self.system_id, {"action_id": action_id, "page": page, "page_size": page_size}
            )
            policies.extend(query_result["results"])

        if self.username:
            policies = [policy for policy in policies if policy["subject"]["id"] == self.username]

        return policies

    def expression_to_resource_paths(self, expression, paths: List):
        """
        将权限表达式转换为资源路径
        """
        if expression["op"] == "OR":
            for sub_expr in expression["content"]:
                self.expression_to_resource_paths(sub_expr, paths)
        elif expression["op"] == "eq":
            # example: indices.id => indices
            resource_type = expression["field"].split(".")[0]
            if resource_type == "biz":
                # biz => space
                resource_type = ResourceEnum.BUSINESS.id
            resource_id = expression["value"]
            paths.append(
                [
                    {
                        "type": resource_type,
                        "id": resource_id,
                        "name": self.get_resource_name(resource_type, resource_id),
                    },
                ]
            )
        elif expression["op"] == "in":
            # example: indices.id => indices
            resource_type = expression["field"].split(".")[0]
            if resource_type == "biz":
                # biz => space
                resource_type = ResourceEnum.BUSINESS.id
            for resource_id in expression["value"]:
                paths.append(
                    [
                        {
                            "type": resource_type,
                            "id": resource_id,
                            "name": self.get_resource_name(resource_type, resource_id),
                        },
                    ]
                )
        elif expression["op"] == "starts_with":
            # example: {'field': 'indices._bk_iam_path_',
            #      'op': 'starts_with',
            #      'value': '/biz,5/'}
            resource_type = ResourceEnum.BUSINESS.id
            resource_id = expression["value"][1:-1].split(",")[1]
            paths.append(
                [
                    {
                        "type": resource_type,
                        "id": resource_id,
                        "name": self.get_resource_name(resource_type, resource_id),
                    },
                ]
            )
        elif expression["op"] == "any":
            # 拥有全部权限
            paths.append([])

    def policy_to_resource(self, action: ActionMeta, policy):
        """
        :param action: action to upgrade
        :param policy: example
        {
            'version': '1',
            'id': 392,
            'subject': {'type': 'group', 'id': '1', 'name': '运维组'},
            'expression': {'field': 'indices._bk_iam_path_',
            'op': 'starts_with',
            'value': '/biz,2/'},
            'expired_at': 4102444800
        }
        """
        paths = []
        self.expression_to_resource_paths(policy["expression"], paths)

        has_any_policy = False
        for path in paths:
            if not path:
                has_any_policy = True
                break
        if has_any_policy:
            # 拥有any全部权限，直接置空
            paths = []

        resource = {
            "asynchronous": False,
            "operate": "grant",
            "system": self.system_id,
            "actions": [{"id": action.id}],
            "subject": policy["subject"],
            "resources": [
                {
                    "system": action.related_resource_types[0].system_id,
                    "type": action.related_resource_types[0].id,
                    "paths": paths,
                }
            ],
            "expired_at": policy["expired_at"],
        }
        return resource

    def grant_resource(self, resource):
        paths = resource["resources"][0]["paths"]
        size = 1000

        results = []
        try:
            if not paths:
                # path 为空，则为无限制授权
                results.append(self.grant_resource_chunked(resource, []))
            else:
                chunked_paths = [paths[pos : pos + size] for pos in range(0, len(paths), size)]
                for chunk in chunked_paths:
                    results.append(self.grant_resource_chunked(resource, chunk))
        except Exception as e:  # pylint: disable=broad-except
            print(
                "grant permission error for action[%s], subject[%s]: %s"
                % (resource["actions"][0]["id"], resource["subject"], e)
            )
        return results

    def grant_resource_chunked(self, resource, paths):
        request = ApiBatchAuthRequest(
            system=resource["system"],
            subject=Subject(type=resource["subject"]["type"], id=resource["subject"]["id"],),
            actions=[Action(id=action["id"]) for action in resource["actions"]],
            resources=[
                ApiBatchAuthResourceWithPath(system=r["system"], type=r["type"], paths=paths)
                for r in resource["resources"]
            ],
            operate=resource["operate"],
            asynchronous=resource["asynchronous"],
            expired_at=resource["expired_at"],
        )
        result = self.batch_path_authorization(request, bk_username=self.OPERATOR)
        return result

    def batch_path_authorization(self, request, bk_token=None, bk_username=None):
        data = request.to_dict()
        path = "/api/c/compapi/v2/iam/authorization/batch_path/"
        ok, message, _data = self.iam_client._client._call_esb_api(http_post, path, data, bk_token, bk_username)
        if not ok:
            raise AuthAPIError(message)
        return _data
