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
"""
import functools
import re
import socket
from collections import defaultdict
from typing import Union, List
import arrow

from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Sum
from elasticsearch import Elasticsearch

from apps.log_databus.utils.es_config import get_es_config
from apps.utils.log import logger
from apps.utils.thread import MultiExecuteFunc
from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.iam import Permission, ResourceEnum
from apps.log_esquery.utils.es_route import EsRoute
from apps.log_search.models import Scenario, ProjectInfo
from apps.utils.cache import cache_five_minute
from apps.utils.local import get_local_param, get_request_username
from apps.api import TransferApi, BkLogApi
from apps.log_databus.models import StorageCapacity, StorageUsed, DataLinkConfig
from apps.log_databus.constants import (
    STORAGE_CLUSTER_TYPE,
    REGISTERED_SYSTEM_DEFAULT,
    DEFAULT_ES_SCHEMA,
    NODE_ATTR_PREFIX_BLACKLIST,
    BKLOG_RESULT_TABLE_PATTERN,
    EsSourceType,
)
from apps.log_databus.exceptions import (
    StorageNotExistException,
    StorageNotPermissionException,
    StorageConnectInfoException,
    StorageUnKnowEsVersionException,
    StorageHaveResource,
)
from apps.decorators import user_operation_record
from apps.utils.time_handler import format_user_time_zone

CACHE_EXPIRE_TIME = 300


class StorageHandler(object):
    def __init__(self, cluster_id=None):
        self.cluster_id = cluster_id
        super().__init__()

    def get_cluster_groups(self, bk_biz_id, is_default=True):
        """
        获取集群列表
        :param bk_biz_id:
        :param is_default:
        :return:
        """
        cluster_groups = self.filter_cluster_groups(
            TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE}), bk_biz_id, is_default=is_default
        )
        return [
            {
                "storage_cluster_id": i["cluster_config"].get("cluster_id"),
                "storage_cluster_name": i["cluster_config"].get("cluster_name"),
                "storage_version": i["cluster_config"].get("version"),
                "storage_type": STORAGE_CLUSTER_TYPE,
                "priority": i["priority"],
                "registered_system": i["cluster_config"].get("registered_system"),
                "bk_biz_id": i["bk_biz_id"],
                "enable_hot_warm": i["cluster_config"]["custom_option"]
                .get("hot_warm_config", {})
                .get("is_enabled", False),
            }
            for i in cluster_groups
            if i
        ]

    def get_cluster_groups_filter(self, bk_biz_id, is_default=True, data_link_id=0):
        """
        获取集群列表并过滤
        :param bk_biz_id:
        :param is_default:
        :param data_link_id: 链路ID
        :return:
        """
        cluster_groups = self.get_cluster_groups(bk_biz_id, is_default=is_default)

        if data_link_id:
            # 如果传了链路ID，则根据链路ID过滤
            link_object = DataLinkConfig.objects.filter(data_link_id=data_link_id).first()
            if link_object:
                es_list = link_object.es_cluster_ids
            else:
                es_list = []

            # 如果集群不是公共集群，则不过滤
            cluster_groups = [
                c
                for c in cluster_groups
                if c["storage_cluster_id"] in es_list or c.get("registered_system") != REGISTERED_SYSTEM_DEFAULT
            ]

        # 排序：第三方集群 > 默认集群
        cluster_groups.sort(key=lambda c: c["priority"])

        # 获取公共集群使用情况
        public_clusters = [
            cluster["storage_cluster_id"]
            for cluster in cluster_groups
            if cluster.get("registered_system") == REGISTERED_SYSTEM_DEFAULT
        ]
        if not public_clusters:
            return cluster_groups

        es_config = get_es_config(bk_biz_id)
        # 获取公共集群容易配额
        storage_capacity = self.get_storage_capacity(bk_biz_id, public_clusters)
        for cluster in cluster_groups:
            if cluster.get("registered_system") == REGISTERED_SYSTEM_DEFAULT:
                cluster["storage_capacity"] = storage_capacity["storage_capacity"]
                cluster["storage_used"] = storage_capacity["storage_used"]
                cluster["max_retention"] = es_config["ES_PUBLIC_STORAGE_DURATION"]
            else:
                cluster["storage_capacity"] = 0
                cluster["storage_used"] = 0
                cluster["max_retention"] = es_config["ES_PRIVATE_STORAGE_DURATION"]
        return cluster_groups

    @classmethod
    def filter_cluster_groups(cls, cluster_groups, bk_biz_id, is_default=True):
        """
        筛选集群，并判断集群是否可编辑
        :param cluster_groups:
        :param bk_biz_id:
        :param is_default:
        :return:
        """
        cluster_data = list()
        projects = ProjectInfo.get_cmdb_projects()
        # 筛选集群 & 判断是否可编辑
        for cluster_obj in cluster_groups:
            cluster_obj["cluster_config"]["create_time"] = StorageHandler.convert_standard_time(
                cluster_obj["cluster_config"]["create_time"]
            )
            cluster_obj["cluster_config"]["last_modify_time"] = StorageHandler.convert_standard_time(
                cluster_obj["cluster_config"]["last_modify_time"]
            )
            cluster_obj["cluster_config"]["schema"] = cluster_obj["cluster_config"].get("schema") or DEFAULT_ES_SCHEMA
            enable_hot_warm = (
                cluster_obj["cluster_config"]["custom_option"].get("hot_warm_config", {}).get("is_enabled", False)
            )
            cluster_obj["cluster_config"]["enable_hot_warm"] = enable_hot_warm

            es_config = get_es_config(bk_biz_id)
            # 公共集群：凭据信息和域名置空处理，并添加不允许编辑标签
            if cluster_obj["cluster_config"].get("registered_system") == REGISTERED_SYSTEM_DEFAULT:
                if not is_default:
                    continue
                cluster_obj.update({"auth_info": {"username": "", "password": ""}, "is_editable": False})
                cluster_obj["cluster_config"]["domain_name"] = ""
                cluster_obj["cluster_config"]["max_retention"] = es_config["ES_PUBLIC_STORAGE_DURATION"]
                # 默认集群权重：推荐集群 > 其他
                cluster_obj["priority"] = 1 if cluster_obj["cluster_config"].get("is_default_cluster") else 2
                cluster_obj["bk_biz_id"] = 0
                cluster_data.append(cluster_obj)
                continue

            # 非公共集群， 筛选bk_biz_id，密码置空处理，并添加可编辑标签
            custom_option = cluster_obj["cluster_config"]["custom_option"]
            custom_biz_id = custom_option.get("bk_biz_id")
            custom_visible_bk_biz = custom_option.get("visible_bk_biz", [])

            cluster_obj["cluster_config"]["max_retention"] = es_config["ES_PRIVATE_STORAGE_DURATION"]
            if not cls.storage_visible(bk_biz_id, custom_biz_id, custom_visible_bk_biz):
                continue
            cluster_obj["is_editable"] = True
            cluster_obj["auth_info"]["password"] = ""
            # 第三方es权重最高
            cluster_obj["priority"] = 0
            cluster_obj["bk_biz_id"] = custom_biz_id
            from apps.log_search.handlers.index_set import IndexSetHandler

            index_sets = IndexSetHandler.get_index_set_for_storage(cluster_obj["cluster_config"]["cluster_id"])
            cluster_obj["visible_bk_biz"] = [
                {
                    "bk_biz_id": bk_biz_id,
                    "is_use": index_sets.filter(project_id=projects.get(bk_biz_id), is_active=True).exists(),
                }
                for bk_biz_id in custom_visible_bk_biz
            ]
            # 处理来源
            cluster_obj["source_type"] = custom_option.get("source_type", EsSourceType.PRIVATE.value)
            cluster_obj["source_name"] = (
                custom_option.get("source_name")
                if cluster_obj["source_type"] == EsSourceType.OTHER.value
                else EsSourceType.get_choice_label(cluster_obj["source_type"])
            )
            cluster_data.append(cluster_obj)
        return cluster_data

    @staticmethod
    def storage_visible(bk_biz_id, custom_bk_biz_id, visible_bk_biz: List[int]) -> bool:
        bk_biz_id = int(bk_biz_id)
        if bk_biz_id in visible_bk_biz:
            return True
        if not custom_bk_biz_id:
            return False
        custom_bk_biz_id = int(custom_bk_biz_id)
        return custom_bk_biz_id == bk_biz_id

    @staticmethod
    def convert_standard_time(time_stamp):
        try:
            time_zone = get_local_param("time_zone")
            return arrow.get(int(time_stamp)).to(time_zone).strftime("%Y-%m-%d %H:%M:%S%z")
        except Exception:  # pylint: disable=broad-except
            return time_stamp

    def list(self, bk_biz_id, cluster_id=None, is_default=True):
        """
        存储集群列表
        :return:
        """
        params = {"cluster_type": STORAGE_CLUSTER_TYPE}
        if cluster_id:
            params["cluster_id"] = cluster_id
        cluster_info = TransferApi.get_cluster_info(params)
        if cluster_id:
            cluster_info = self._get_cluster_nodes(cluster_info)
            cluster_info = self._get_cluster_detail_info(cluster_info)
        return self.filter_cluster_groups(cluster_info, bk_biz_id, is_default)

    def _get_cluster_nodes(self, cluster_info: List[dict]):
        for cluster in cluster_info:
            cluster_id = cluster.get("cluster_config").get("cluster_id")
            nodes_stats = EsRoute(
                scenario_id=Scenario.ES, storage_cluster_id=cluster_id, raise_exception=False
            ).cluster_nodes_stats()
            if not nodes_stats:
                cluster["nodes"] = []
                continue
            cluster["nodes"] = [
                {
                    "tag": node.get("attributes", {}).get("tag", ""),
                    "attributes": node.get("attributes"),
                    "name": node["name"],
                    "ip": node["ip"],
                    "host": node["host"],
                    "roles": node["roles"],
                    "mem_total": node["os"]["mem"]["total_in_bytes"],
                    "store_total": node["fs"]["total"]["total_in_bytes"],
                }
                for node in nodes_stats["nodes"].values()
            ]
        return cluster_info

    def _get_cluster_detail_info(self, cluster_info: List[dict]):
        multi_execute_func = MultiExecuteFunc()

        def get_cluster_stats(cluster_id: int):
            return EsRoute(
                scenario_id=Scenario.ES, storage_cluster_id=cluster_id, raise_exception=False
            ).cluster_stats()

        for cluster in cluster_info:
            cluster_id = cluster.get("cluster_config").get("cluster_id")
            multi_execute_func.append(cluster_id, get_cluster_stats, cluster_id)
        result = multi_execute_func.run()
        for cluster in cluster_info:
            cluster_id = cluster.get("cluster_config").get("cluster_id")
            cluster_stats = result.get(cluster_id)
            cluster["cluster_stats"] = cluster_stats
        return cluster_info

    def create(self, params):
        """
        创建集群
        :param params:
        :return:
        """

        bk_biz_id = int(params["custom_option"]["bk_biz_id"])
        es_source_id = TransferApi.create_cluster_info(params)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": bk_biz_id,
            "record_type": UserOperationTypeEnum.STORAGE,
            "record_object_id": int(es_source_id),
            "action": UserOperationActionEnum.CREATE,
            "params": params,
        }
        user_operation_record.delay(operation_record)

        Permission().grant_creator_action(
            resource=ResourceEnum.ES_SOURCE.create_simple_instance(
                es_source_id, attribute={"name": params["cluster_name"]}
            )
        )

        return es_source_id

    def update(self, params):
        """
        更新集群
        :param params:
        :return:
        """
        # 判断是否可编辑
        bk_biz_id = int(params["custom_option"]["bk_biz_id"])
        get_cluster_info_params = {"cluster_type": STORAGE_CLUSTER_TYPE, "cluster_id": int(self.cluster_id)}
        cluster_objs = TransferApi.get_cluster_info(get_cluster_info_params)
        if not cluster_objs:
            raise StorageNotExistException()
        # 判断该集群是否可编辑
        if cluster_objs[0]["cluster_config"].get("registered_system") == REGISTERED_SYSTEM_DEFAULT:
            raise StorageNotPermissionException()
        # 判断该集群是否属于该业务
        if cluster_objs[0]["cluster_config"]["custom_option"].get("bk_biz_id") != bk_biz_id:
            raise StorageNotPermissionException()

        # 当前端传入的账号或密码为空时，取原账号密码
        if not params["auth_info"]["username"] or not params["auth_info"]["password"]:
            params["auth_info"]["username"] = cluster_objs[0]["auth_info"]["username"]
            params["auth_info"]["password"] = cluster_objs[0]["auth_info"]["password"]

        BkLogApi.connectivity_detect(
            params={
                "bk_biz_id": bk_biz_id,
                "domain_name": params["domain_name"],
                "port": params["port"],
                "schema": params["schema"],
                "cluster_id": self.cluster_id,
                "es_auth_info": {
                    "username": params["auth_info"]["username"],
                    "password": params["auth_info"]["password"],
                },
            },
        )

        cluster_obj = TransferApi.modify_cluster_info(params)
        cluster_obj["auth_info"]["password"] = ""

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": bk_biz_id,
            "record_type": UserOperationTypeEnum.STORAGE,
            "record_object_id": self.cluster_id,
            "action": UserOperationActionEnum.UPDATE,
            "params": params,
        }
        user_operation_record.delay(operation_record)

        return cluster_obj

    def destroy(self):

        from apps.log_search.handlers.index_set import IndexSetHandler

        # check index_set
        index_sets = IndexSetHandler.get_index_set_for_storage(self.cluster_id)
        if index_sets.filter(is_active=True).exists():
            raise StorageHaveResource

        # TODO 检查计算平台关联的集群

        TransferApi.delete_cluster_info({"cluster_id": self.cluster_id})

    def connectivity_detect(
        self,
        bk_biz_id,
        domain_name=None,
        port=None,
        username=None,
        password=None,
        version_info=False,
        default_auth=False,
        schema=DEFAULT_ES_SCHEMA,
        **kwargs,
    ):

        # 有传用户但是没有密码，通过接口查询该cluster密码信息
        # version_info 为True，会返回连接状态和版本信息的元组，False只返回连接状态bool
        if self.cluster_id:
            params = {"cluster_type": STORAGE_CLUSTER_TYPE, "cluster_id": int(self.cluster_id)}
            clusters = TransferApi.get_cluster_info(params)

            # 判断集群信息是否存在，及是否有读取改集群信息权限
            if not clusters:
                raise StorageNotExistException()

            cluster_obj = clusters[0]
            # 比较集群bk_biz_id是否匹配
            cluster_config = cluster_obj["cluster_config"]
            custom_option = cluster_config.get("custom_option", {})
            custom_biz_id = custom_option.get("bk_biz_id")
            if custom_biz_id:
                if custom_biz_id != bk_biz_id:
                    raise StorageNotPermissionException()

            # 集群不可以修改域名、端口
            domain_name = cluster_config["domain_name"]
            port = cluster_config["port"]

            # 现有集群用户不修改密码则使用集群现有密码
            if username and not password:
                password = cluster_obj["auth_info"]["password"]

            # 兼容批量连通性测试，使用存储凭据信息
            if default_auth:
                username = cluster_obj["auth_info"].get("username")
                password = cluster_obj["auth_info"].get("password")
                # 新增批量获取状态时schema
                schema = cluster_config.get("schema") or DEFAULT_ES_SCHEMA

        connect_result = self._send_detective(domain_name, port, username, password, version_info, schema)
        return connect_result

    def list_node_attrs(
        self,
        bk_biz_id,
        domain_name=None,
        port=None,
        username=None,
        password=None,
        default_auth=False,
        schema=DEFAULT_ES_SCHEMA,
        **kwargs,
    ):
        """
        获取集群各节点的属性
        """
        # 有传用户但是没有密码，通过接口查询该cluster密码信息
        if self.cluster_id:
            params = {"cluster_type": STORAGE_CLUSTER_TYPE, "cluster_id": int(self.cluster_id)}
            cluster_obj = TransferApi.get_cluster_info(params)[0]

            # 判断集群信息是否存在，及是否有读取改集群信息权限
            if not cluster_obj:
                raise StorageNotExistException()

            # 比较集群bk_biz_id是否匹配
            cluster_config = cluster_obj["cluster_config"]
            custom_option = cluster_config.get("custom_option", {})
            custom_biz_id = custom_option.get("bk_biz_id")
            if custom_biz_id:
                if int(custom_biz_id) != int(bk_biz_id):
                    raise StorageNotPermissionException()

            # 集群不可以修改域名、端口
            domain_name = cluster_config["domain_name"]
            port = cluster_config["port"]

            # 现有集群用户不修改密码则使用集群现有密码
            if username and not password:
                password = cluster_obj["auth_info"]["password"]

            # 兼容批量连通性测试，使用存储凭据信息
            if default_auth:
                username = cluster_obj["auth_info"].get("username")
                password = cluster_obj["auth_info"].get("password")

        http_auth = (username, password) if username and password else None
        es_client = Elasticsearch(
            [domain_name], http_auth=http_auth, scheme=schema, port=port, sniffer_timeout=600, verify_certs=True
        )

        nodes = es_client.cat.nodeattrs(format="json", h="name,host,attr,value,id,ip")

        # 对节点属性进行过滤，有些是内置的，需要忽略
        filtered_nodes = []
        for node in nodes:
            for prefix in NODE_ATTR_PREFIX_BLACKLIST:
                if node["attr"].startswith(prefix):
                    break
            else:
                filtered_nodes.append(node)

        return filtered_nodes

    @classmethod
    def batch_connectivity_detect(cls, cluster_list, bk_biz_id):
        """
        :param cluster_list:
        :return:
        """
        multi_execute_func = MultiExecuteFunc()
        for _cluster_id in cluster_list:
            multi_execute_func.append(
                _cluster_id, cls._get_cluster_status_and_stats, {"cluster_id": _cluster_id, "bk_biz_id": bk_biz_id}
            )
        return multi_execute_func.run()

    @staticmethod
    def _get_cluster_status_and_stats(params):
        @cache_five_minute("connect_info_{cluster_id}")
        def _cache_status_and_stats(*, cluster_id, bk_biz_id):
            cluster_stats_info = None
            try:
                _status = BkLogApi.connectivity_detect(
                    params={"bk_biz_id": bk_biz_id, "cluster_id": cluster_id, "default_auth": True},
                )
                cluster_stats = EsRoute(
                    scenario_id=Scenario.ES, storage_cluster_id=cluster_id, raise_exception=False
                ).cluster_stats()
                if cluster_stats:
                    cluster_stats_info = StorageHandler._build_cluster_stats(cluster_stats)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"[storage] get cluster status failed => [{e}]")
                _status = False
            return {"status": _status, "cluster_stats": cluster_stats_info}

        cluster_id = params.get("cluster_id")
        bk_biz_id = params.get("bk_biz_id")
        return _cache_status_and_stats(cluster_id=cluster_id, bk_biz_id=bk_biz_id)

    @staticmethod
    def _build_cluster_stats(cluster_stats):
        return {
            "node_count": cluster_stats["nodes"]["count"]["total"],
            "shards_total": cluster_stats["indices"]["shards"]["total"],
            "shards_pri": cluster_stats["indices"]["shards"]["primaries"],
            "data_node_count": cluster_stats["nodes"]["count"]["data"],
            "indices_count": cluster_stats["indices"]["count"],
            "indices_docs_count": cluster_stats["indices"]["docs"]["count"],
            "indices_store": cluster_stats["indices"]["store"]["size_in_bytes"],
            "total_store": cluster_stats["nodes"]["fs"]["total_in_bytes"],
            "status": cluster_stats["status"],
        }

    def _send_detective(
        self, domain_name: str, port: int, username="", password="", version_info=False, schema=DEFAULT_ES_SCHEMA
    ) -> Union[bool, tuple]:
        # 对host和port的连通性进行验证
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        es_address = (str(domain_name), int(port))
        cs.settimeout(2)
        try:
            status = cs.connect_ex(es_address)
            # this status is returnback from tcpserver
            if status != 0:
                raise StorageConnectInfoException(
                    StorageConnectInfoException.MESSAGE.format(info=_("IP or PORT can not be reached"))
                )
        except Exception as e:  # pylint: disable=broad-except
            raise StorageConnectInfoException(
                StorageConnectInfoException.MESSAGE.format(info=_("IP or PORT can not be reached, %s" % e))
            )
        cs.close()
        http_auth = (username, password) if username and password else None
        es_client = Elasticsearch(
            [domain_name], http_auth=http_auth, scheme=schema, port=port, sniffer_timeout=600, verify_certs=True
        )
        if not es_client.ping():
            connect_result = False
        else:
            connect_result = True

        if not version_info:
            return connect_result
        else:
            if connect_result:
                info_dict = es_client.info()
                version_number: str = self.dump_version_info(info_dict, domain_name, port)
                return connect_result, version_number
            else:
                raise StorageUnKnowEsVersionException(
                    StorageUnKnowEsVersionException.MESSAGE.format(ip=domain_name, port=port)
                )

    def dump_version_info(self, info_dict: dict, domain_name: str, port: int) -> str:
        if info_dict:
            version = info_dict.get("version")
            if version:
                number = version.get("number")
            else:
                raise StorageUnKnowEsVersionException(
                    StorageUnKnowEsVersionException.MESSAGE.format(ip=domain_name, port=port)
                )
        else:
            raise StorageUnKnowEsVersionException(
                StorageUnKnowEsVersionException.MESSAGE.format(ip=domain_name, port=port)
            )

        return number

    def get_cluster_info_by_id(self):
        """
        根据集群ID查询集群信息，密码返回
        :return:
        """
        cluster_info = TransferApi.get_cluster_info({"cluster_id": self.cluster_id})
        if not cluster_info:
            raise StorageNotExistException()
        return cluster_info[0]

    def get_cluster_info_by_table(self, table_id):
        """
        根据result_table_id查询集群信息
        :return:
        """
        cluster_info = TransferApi.get_result_table_storage(
            {"result_table_list": table_id, "storage_type": STORAGE_CLUSTER_TYPE}
        )
        if not cluster_info.get(table_id):
            raise StorageNotExistException()
        return cluster_info[table_id]

    @classmethod
    def get_storage_capacity(cls, bk_biz_id, storage_clusters):
        storage = {"storage_capacity": 0, "storage_used": 0}
        if int(settings.ES_STORAGE_CAPACITY) <= 0:
            return storage
        biz_storage = StorageCapacity.objects.filter(bk_biz_id=bk_biz_id).first()
        storage["storage_capacity"] = int(settings.ES_STORAGE_CAPACITY)
        if biz_storage:
            storage["storage_capacity"] = biz_storage.storage_capacity

        storage_used = (
            StorageUsed.objects.filter(bk_biz_id=bk_biz_id, storage_cluster_id__in=storage_clusters)
            .all()
            .aggregate(total=Sum("storage_used"))
        )
        if storage_used:
            storage["storage_used"] = round(storage_used.get("total", 0) or 0, 2)
        return storage

    def cluster_nodes(self):
        result = EsRoute(scenario_id=Scenario.ES, storage_cluster_id=self.cluster_id).cluster_nodes_stats()
        return [
            {
                "name": node["name"],
                "ip": node["host"],
                "cpu_use": node["os"]["cpu"]["percent"],
                "disk_use": node["fs"]["total"]["available_in_bytes"] / node["fs"]["total"]["total_in_bytes"],
                "jvm_mem_use": node["jvm"]["mem"]["heap_used_percent"],
                "tag": node["attributes"].get("tag", ""),
            }
            for node in result.get("nodes").values()
        ]

    def indices(self):
        indices_info = EsRoute(scenario_id=Scenario.ES, storage_cluster_id=self.cluster_id).cat_indices()
        indices_info = self.sort_indices(indices_info)
        ret = defaultdict(dict)
        other_indices = {"index_pattern": "other", "indices": []}
        for indices in indices_info:
            is_bklog_rt, rt = self._match_bklog_indices(indices["index"])
            if is_bklog_rt and not indices["index"].startswith("write"):
                ret[rt]["index_pattern"] = rt
                ret[rt].setdefault("indices", []).append(indices)
                continue
            other_indices["indices"].append(indices)
        result = []
        for index in ret.values():
            result.append(index)
        result.append(other_indices)
        return result

    def _match_bklog_indices(self, index: str) -> (bool, str):
        pattern = re.compile(BKLOG_RESULT_TABLE_PATTERN)
        match = pattern.findall(index)
        if match:
            return True, match[0]
        return False, ""

    @staticmethod
    def sort_indices(indices: list):
        def compare_indices_by_date(index_a, index_b):
            index_a = index_a.get("index")
            index_b = index_b.get("index")

            def convert_to_normal_date_tuple(index_name) -> tuple:
                # example 1: 2_bklog_xxxx_20200321_1 -> (20200321, 1)
                # example 2: 2_xxxx_2020032101 -> (20200321, 1)
                result = re.findall(r"(\d{8})_(\d{1,7})$", index_name) or re.findall(r"(\d{8})(\d{2})$", index_name)
                if result:
                    return result[0][0], int(result[0][1])
                # not match
                return index_name, 0

            converted_index_a = convert_to_normal_date_tuple(index_a)
            converted_index_b = convert_to_normal_date_tuple(index_b)

            return (converted_index_a > converted_index_b) - (converted_index_a < converted_index_b)

        return sorted(indices, key=functools.cmp_to_key(compare_indices_by_date), reverse=True)

    def repository(self, bk_biz_id=None, cluster_id=None):
        cluster_info = self.list(bk_biz_id=bk_biz_id, cluster_id=cluster_id, is_default=False)
        cluster_info_by_id = {cluster["cluster_config"]["cluster_id"]: cluster for cluster in cluster_info}
        repository_info = TransferApi.list_es_snapshot_repository({"cluster_ids": list(cluster_info_by_id.keys())})
        for repository in repository_info:
            repository.update(
                {
                    "cluster_name": cluster_info_by_id[repository["cluster_id"]]["cluster_config"]["cluster_name"],
                    "cluster_source_name": cluster_info_by_id[repository["cluster_id"]].get("source_name"),
                    "cluster_source_type": cluster_info_by_id[repository["cluster_id"]].get("source_type"),
                    "create_time": format_user_time_zone(repository["create_time"], get_local_param("time_zone")),
                }
            )
            repository.pop("settings")
        return repository_info
