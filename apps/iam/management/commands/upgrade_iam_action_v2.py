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
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.api import TransferApi
from apps.iam import Permission, ActionEnum, ResourceEnum
from apps.iam.handlers.actions import ActionMeta
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_databus.models import CollectorConfig
from apps.log_search.models import LogIndexSet, Space
from iam.auth.models import ApiBatchAuthRequest, Subject, Action, ApiBatchAuthResourceWithPath
from iam.contrib.iam_migration.migrator import IAMMigrator

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


class Command(BaseCommand):
    OPERATOR = "admin"

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

        IAMMigrator("initial.json").migrate()
        IAMMigrator("space.json").migrate()

        print("[upgrade_iam_model] [END]")

    def upgrade_policy(self):
        print("[upgrade_policy] [START]")

        for action in ACTIONS_TO_UPGRADE:
            old_action_id = action.id.replace("_v2", "")
            policies = self.query_polices(old_action_id)
            print("[grant_resource] [START] action[%s], policy count: %d" % (action.id, len(policies)))

            total = len(policies)
            progress = 0

            for policy in policies:
                resource = self.policy_to_resource(action, policy)
                self.grant_resource(resource)

                progress += 1
                print(
                    "[grant_resource] grant permission for action: %s, progress: %d%% (%d/%d)"
                    % (action.id, progress / total * 100, progress, total)
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
            if result[2] - result[1] < 0:
                # 新策略数量少于旧策略是不正常的
                no_ok_actions.append(result[0])
            print(
                "[check_upgrade_polices] action[%s] old count: %d, new count: %d, diff: %d"
                % (result[0], result[1], result[2], result[2] - result[1])
            )

        print("##### CHECK RESULT #####")
        if not no_ok_actions:
            print("Everything is OK. IAM upgrade successfully!!!")
        else:
            print("Sorry, following actions not OK: %s" % ", ".join(no_ok_actions))

    def handle(self, **options):
        print("[upgrade_iam_action_v2] ##### START #####")

        self.upgrade_iam_model()
        self.upgrade_policy()

        print("[upgrade_iam_action_v2] ##### END #####")

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
        if not paths:
            # path 为空，则为无限制授权
            results.append(self.grant_resource_chunked(resource, []))
        else:
            chunked_paths = [paths[pos : pos + size] for pos in range(0, len(paths), size)]
            for chunk in chunked_paths:
                results.append(self.grant_resource_chunked(resource, chunk))
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
        result = self.iam_client.batch_grant_or_revoke_path_permission(request, bk_username=self.OPERATOR)
        return result

    def delete_action(self, action_id):
        """
        删除IAM操作
        注意！！！此为高危操作，请慎用！！！
        """
        result = self.iam_client._client.delete_action_policy(system_id=self.system_id, action_id=action_id)
        print("delete iam action policy [{}], result: {}".format(action_id, result))
        result = self.iam_client._client.batch_delete_actions(system_id=self.system_id, data=[{"id": action_id}])
        print("delete iam action [{}], result: {}".format(action_id, result))
