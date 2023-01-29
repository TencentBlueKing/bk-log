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
import copy
from collections import defaultdict, namedtuple
from inspect import signature
from typing import List

from pypinyin import lazy_pinyin

from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from apps.api import CCApi, GseApi
from apps.constants import DEFAULT_MAX_WORKERS
from apps.log_search.constants import (
    AgentStatusEnum,
    AgentStatusTranslationEnum,
    InstanceTypeEnum,
    BK_SUPPLIER_ACCOUNT,
    CMDB_HOST_SEARCH_FIELDS,
    CMDB_SET_INFO_FIELDS,
    TemplateType,
    MAX_LIST_BIZ_HOSTS_PARAMS_COUNT,
    CCInstanceType,
    FIND_MODULE_WITH_RELATION_FIELDS,
    BK_PROPERTY_GROUP_ROLE,
    BIZ_PROPERTY_TYPE_ENUM,
)
from apps.utils import APIModel
from apps.utils.cache import cache_five_minute, cache_one_hour, cache_half_hour
from apps.log_search.models import BizProperty, Space
from apps.utils.db import array_hash, array_chunk
from apps.utils.function import ignored
from apps.utils.thread import MultiExecuteFunc


class BizHandler(APIModel):
    Node = namedtuple("Node", ["bk_biz_id", "bk_obj_id", "bk_inst_id", "bk_inst_name"])

    def __init__(self, bk_biz_id=None):
        super().__init__()

        if bk_biz_id and int(bk_biz_id) < 0:
            # 业务ID为负数的情况，直接转为0
            raise ValueError(_("当前空间类型不支持查询业务资源"))

        self.bk_biz_id = bk_biz_id

    @classmethod
    def list(cls, fields=None):
        params = {
            "fields": [
                "bk_biz_id",
                "bk_biz_name",
                "time_zone",
                "bk_biz_maintainer",
                "bk_biz_developer",
                "bk_biz_productor",
            ]
        }
        biz_list = CCApi.get_app_list.bulk_request(params)
        if not fields or not biz_list:
            return biz_list
        business = []
        for biz in biz_list:
            item = {}
            for field in fields:
                item[field] = biz.get(field, None)
            business.append(item)
        return business

    @classmethod
    def list_clouds(cls):
        """
        获取云区域ID
        """

        clouds = CCApi.search_cloud_area.bulk_request()

        return {"count": len(clouds), "info": clouds}

    def list_dynamic_group(self):
        """
        获取动态分组列表
        """
        dynamic_groups = CCApi.search_dynamic_group.bulk_request(params={"bk_biz_id": self.bk_biz_id})
        return {"count": len(dynamic_groups), "list": dynamic_groups or []}

    def get_dynamic_group(self, dynamic_group_id_list):
        """
        根据指定动态分组规则查询获取数据
        """
        dynamic_group_id_list = dynamic_group_id_list or []

        ret = {}
        for dynamic_group_id in dynamic_group_id_list:
            data = CCApi.execute_dynamic_group.bulk_request(
                params={
                    "bk_biz_id": self.bk_biz_id,
                    "id": dynamic_group_id,
                    "fields": ["bk_cloud_id", "bk_host_innerip", "bk_supplier_account", "bk_set_id", "bk_set_name"],
                }
            )
            ret[dynamic_group_id] = []
            for each_instance in data or []:
                if each_instance.get("bk_host_innerip"):
                    ret[dynamic_group_id].append(
                        {
                            "ip": each_instance["bk_host_innerip"],
                            "bk_cloud_id": each_instance["bk_cloud_id"],
                            "bk_supplier_id": each_instance["bk_supplier_account"],
                        }
                    )
                else:
                    ret[dynamic_group_id].append(
                        {
                            "bk_inst_id": each_instance["bk_set_id"],
                            "bk_obj_id": "set",
                            "bk_set_name": each_instance["bk_set_name"],
                        }
                    )

        return ret

    def get_instance_topo(self, params=None, is_inner=False):
        """
        获取CC各个层级构成TOPO，不仅仅支持 set、moudlehas_auth
        """
        # 缓存
        if not params:
            params = {}
        biz_inst_topo = self.get_biz_inst_topo(bk_biz_id=self.bk_biz_id, params=params)
        extra_params = {"bk_biz_id": self.bk_biz_id, "index": 0}
        self.foreach_topo_tree(biz_inst_topo, self._compatible, extra_params=extra_params)
        self._format_set_with_ch_name(biz_inst_topo)
        self._remove_child(biz_inst_topo)
        return biz_inst_topo

    @cache_five_minute("biz_inst_topo_{bk_biz_id}_{params}", need_md5=True)
    def get_biz_inst_topo(self, *, bk_biz_id, params):
        biz_inst_topo = CCApi.search_biz_inst_topo({"bk_biz_id": bk_biz_id, "level": -1})
        if biz_inst_topo:
            with ignored(Exception):
                internal_topo = self.get_biz_internal_module()
                if internal_topo:
                    biz_inst_topo[0]["child"].insert(0, internal_topo)

        # 静态拓扑，补充hosts信息
        if params.get("instance_type") == InstanceTypeEnum.HOST.value:
            module_dict = {}
            self.get_module_dict(biz_inst_topo, module_dict)
            host_list = self.get_hosts()
            for host in host_list:
                for module in host.get("module"):
                    module_dict[module["bk_inst_id"]].append(self.host_dict_with_os_type(host["host"]))
            if params.get("remove_empty_nodes"):
                self.foreach_topo_tree(biz_inst_topo, self._remove_empty_nodes, order="desc")
        biz_inst_topo = self.sort_topo_tree_by_pinyin(biz_inst_topo)
        return biz_inst_topo

    @classmethod
    def sort_topo_tree_by_pinyin(cls, topo_trees: list):
        """
        深度优先遍历, 将拓扑结构按拼音排序
        """
        if not topo_trees:
            return topo_trees
        topo_trees.sort(key=lambda topo: lazy_pinyin(topo.get("bk_inst_name", "")))
        for topo_tree in topo_trees:
            cls.sort_topo_tree_by_pinyin(topo_tree.get("child", []))

        return topo_trees

    def _remove_child(self, topo):
        for child in topo:
            child_topo = child.get("child", [])
            self._remove_child(child_topo)
            if "child" in child:
                child.pop("child")

    def _format_set_with_ch_name(self, biz_inst_topo):
        if not biz_inst_topo:
            return
        child_set = biz_inst_topo[0]["child"]
        params = {"bk_biz_id": self.bk_biz_id, "fields": CMDB_SET_INFO_FIELDS}
        try:
            bk_set_info = CCApi.search_set.bulk_request(params)
        except Exception:  # pylint: disable=broad-except
            return

        bk_set_info = array_hash(bk_set_info, "bk_set_id", "bk_chn_name")
        self._deal_set_ch_name(child_set, bk_set_info)

    @classmethod
    def _deal_set_ch_name(cls, set_objs, bk_set_info):
        for set in set_objs:
            set_ch_name = bk_set_info.get(set["bk_inst_id"])
            if set_ch_name:
                set["bk_inst_name"] = f"{set['bk_inst_name']} ({set_ch_name})"
                set["name"] = f"{set['name']} ({set_ch_name})"

    def get_biz_internal_module(self):
        internal_module = CCApi.get_biz_internal_module(
            {"bk_biz_id": self.bk_biz_id, "bk_supplier_account": BK_SUPPLIER_ACCOUNT}
        )
        internal_topo = {
            "host_count": 0,
            "default": 0,
            "bk_obj_name": _("集群"),
            "bk_obj_id": "set",
            "child": [
                {
                    "host_count": 0,
                    "default": _module.get("default", 0),
                    "bk_obj_name": _("模块"),
                    "bk_obj_id": "module",
                    "child": [],
                    "bk_inst_id": _module["bk_module_id"],
                    "bk_inst_name": _module["bk_module_name"],
                }
                for _module in internal_module.get("module", [])
            ],
            "bk_inst_id": internal_module["bk_set_id"],
            "bk_inst_name": internal_module["bk_set_name"],
        }
        return internal_topo

    def get_host_instance_by_ip_list(self, ip_list):
        """
        根据ip获取主机实例
        :param ip_list: [ip, bk_cloud_id]
        :return:
        """

        host_info_list = self.get_host_list_by_ip_list(ip_list)

        # 若有bk_cloud_id,过滤掉host_list中不满足的主机
        filtered_host_list = []
        for ip in ip_list:
            if "bk_cloud_id" in ip.keys():
                # todo if语句要改
                filtered_host_list.extend(
                    [
                        item
                        for item in host_info_list
                        if item["bk_cloud_id"] == ip["bk_cloud_id"] and item["bk_host_innerip"] == ip["ip"]
                    ]
                )
            else:
                filtered_host_list.extend([item for item in host_info_list if item["bk_host_innerip"] == ip["ip"]])
        biz_to_host = defaultdict(list)
        for host in filtered_host_list:
            biz_to_host[self.bk_biz_id].append(host)
        biz_agent_status_list = [self.get_agent_status(host_list) for biz, host_list in biz_to_host.items()]

        # 组合不同业务主机的agent状态
        agent_status_dict = {}
        for agent_status in biz_agent_status_list:
            agent_status_dict.update(agent_status)

        # 云区域名称
        cloud_name_dict = {}
        clouds = self.list_clouds()
        for cloud in clouds["info"]:
            cloud_name_dict[cloud["bk_cloud_id"]] = cloud["bk_cloud_name"]

        result = []
        for host in filtered_host_list:
            bk_host_innerip = host["bk_host_innerip"]
            bk_cloud_id = host["bk_cloud_id"]
            host_id = f"{bk_host_innerip}|{bk_cloud_id}"
            agent_status = agent_status_dict.get(host_id)
            result.append(
                {
                    "ip": bk_host_innerip,
                    "bk_cloud_id": bk_cloud_id,
                    "bk_cloud_name": cloud_name_dict.get(host["bk_cloud_id"], host["bk_cloud_id"]),
                    "agent_status": AgentStatusTranslationEnum.get_choice_label(agent_status),
                    "agent_status_name": AgentStatusEnum.get_choice_label(agent_status),
                    "bk_os_type": host["bk_os_name"],
                    "bk_supplier_id": host.get("bk_supplier_account"),
                    "is_innerip": True,
                }
            )
        return result

    def get_host_list_by_ip_list(self, ip_list):
        """
        根据ip列表获取主机列表
        :param ip_list:
        :return:
        """
        return CCApi.list_biz_hosts.bulk_request(
            {
                "bk_biz_id": self.bk_biz_id,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [
                        {"field": "bk_host_innerip", "operator": "in", "value": [host["ip"] for host in ip_list]}
                    ],
                },
                "fields": CMDB_HOST_SEARCH_FIELDS,
            }
        )

    def search_host(self, conditions):
        """
        由于CC查询主机接口暂不支持"或"语句查询，因此暂时分多次进行查询
        :param: conditions 条件 [{"bk_obj_id": "set", "bk_inst_id": 1,}]
        :return: [
            {
                "bk_host_innerip": "127.0.0.1",
                "bk_cloud_id": 0,
            }
        ]
        """
        hosts = []

        node_mapping = defaultdict(set)

        # 根据节点类型进行分组，加速查询
        for condition in conditions:
            node_mapping[condition["bk_obj_id"]].add(condition["bk_inst_id"])

        for obj_id, inst_ids in node_mapping.items():
            hosts.extend(self._get_hosts(obj_id=obj_id, inst_ids=inst_ids))
        return hosts

    def _get_hosts(self, obj_id, inst_ids):
        """
        按照obj_id获取对应_search_host接口返回并组合
        obj_id {str} 实例类型
        inst_ids {set} 实例id列表
        """
        hosts = []
        if obj_id in (CCInstanceType.SET.value, CCInstanceType.MODULE.value, CCInstanceType.BUSINESS.value):
            inst_ids_array = array_chunk(sorted(inst_ids), MAX_LIST_BIZ_HOSTS_PARAMS_COUNT)
            for inst_id in inst_ids_array:
                hosts.extend(self._search_host(bk_obj_id=obj_id, bk_inst_id=inst_id))
            return hosts

        if obj_id in (TemplateType.SERIVCE_TEMPLATE.value, TemplateType.SET_TEMPLATE.value):
            template_dict = self._get_template_dict(inst_ids=list(inst_ids), obj_id=obj_id)
            hosts = self._get_template_hosts(template_dict=template_dict, obj_id=obj_id)
            return self._generate_template_hosts(hosts=hosts, obj_id=obj_id, template_dict=template_dict)

        hosts.extend(self._search_host(bk_obj_id=obj_id, bk_inst_id=sorted(inst_ids)))
        return hosts

    def _get_template_dict(self, inst_ids: List, obj_id: str):
        """
        获取template_dict
        @param inst_ids {List} 实例id列表
        @param obj_id {str} 实例类型
        @return {Dict}
        {
            1: "2"
        }
        """
        modules = self._list_module(inst_ids, obj_id)
        if obj_id == TemplateType.SERIVCE_TEMPLATE.value:
            module_dict = {module["bk_module_id"]: module["service_template_id"] for module in modules}
            return module_dict
        return {module["set_id"]: module["set_template_id"] for module in modules}

    def _get_template_hosts(self, template_dict: dict, obj_id: str):
        """
        服务模板集群模板获取host
        @param template_dict {Dict} set_id或者module_id与对应模板iddict
        @param obj_id {Str} 实例类型
        """
        hosts = []
        inst_ids_array = array_chunk(sorted(template_dict.keys()), MAX_LIST_BIZ_HOSTS_PARAMS_COUNT)
        child_obj_id = CCInstanceType.MODULE.value
        if obj_id == TemplateType.SET_TEMPLATE.value:
            child_obj_id = CCInstanceType.SET.value

        for inst_id in inst_ids_array:
            hosts.extend(self._search_host(bk_obj_id=child_obj_id, bk_inst_id=inst_id))
        return hosts

    def _generate_template_hosts(self, hosts: List, obj_id: str, template_dict: dict):
        """
        处理模板返回hosts返回obj_id及对应parent_obj_id字段，及将对应bk_obj_id，parent_inst_id替换为对应模板类型以及模板实例id
        @param hosts {List} _search_host 返回host列表
        @param obj_id {str} 实例类型
        @param template_dict {dict} _get_module_dict 返回module_dict
        """
        generate_hosts = []
        for host in hosts:
            tmp_host = copy.deepcopy(host)
            tmp_host["bk_obj_id"] = obj_id
            tmp_host["parent_inst_id"] = []
            for inst_id in host["parent_inst_id"]:
                if not template_dict.get(inst_id):
                    continue
                tmp_host["parent_inst_id"].append(template_dict.get(inst_id))
            generate_hosts.append(tmp_host)
        return generate_hosts

    @cache_five_minute("bk_inst_host_{bk_obj_id}_{bk_inst_id}", need_md5=True)
    def _search_host(self, *, bk_obj_id, bk_inst_id):
        """
        调用CC接口根据条件查询主机
        :return: [
            {
                "bk_host_innerip": "127.0.0.1",
                "bk_cloud_id": 0,
            }
        ]
        """
        hosts = self._get_hosts_by_inst_id(bk_obj_id, bk_inst_id, with_parent_obj_id=True)
        return [
            {
                "bk_host_innerip": host["bk_host_innerip"],
                "bk_cloud_id": host["bk_cloud_id"],
                "parent_inst_id": host["parent_inst_id"],
                "bk_obj_id": bk_obj_id,
            }
            for host in hosts
        ]

    @cache_one_hour("get_host_instance_by_node_{node_list}", need_md5=True)
    def get_host_instance_by_node(self, *, node_list):
        """
        根据节点获取拓扑情况获取主机实例
        :return:
        """
        host_dict = self.get_node_path(node_list)
        host_result = self.get_service_category(host_dict, is_dynamic=True)

        return host_result

    def get_biz_topo_tree(self):
        """
        获取业务拓扑树
        :return:
        """
        inst_topo = CCApi.search_biz_inst_topo({"bk_biz_id": self.bk_biz_id, "level": -1})

        free_set = CCApi.get_biz_internal_module({"bk_biz_id": self.bk_biz_id, "bk_supplier_account": 0})

        if free_set:
            free_set = dict(
                bk_obj_id="set",
                bk_obj_name="集群",
                bk_inst_id=free_set["bk_set_id"],
                bk_inst_name=free_set["bk_set_name"],
                child=[
                    dict(
                        bk_obj_id="module",
                        bk_obj_name="模块",
                        bk_inst_id=m["bk_module_id"],
                        bk_inst_name=m["bk_module_name"],
                        child=[],
                    )
                    for m in free_set["module"]
                ],
            )

        if inst_topo:
            inst_topo, *_ = inst_topo
            if free_set:
                inst_topo["child"] = [free_set] + inst_topo["child"]
            return inst_topo
        return []

    def host_dict_with_os_type(self, host):
        data = {"ip": host["bk_host_innerip"]}
        if "bk_cloud_id" in host:
            data["plat_id"] = host["bk_cloud_id"]
            data["bk_cloud_id"] = host["bk_cloud_id"]
        data["os_type"] = host.get("bk_os_type") or ""
        data["bk_supplier_id"] = host.get("bk_supplier_account", "")
        return data

    def get_hosts(self, fields=None):
        fields = fields or CMDB_HOST_SEARCH_FIELDS
        host_list = CCApi.list_biz_hosts_topo.bulk_request({"bk_biz_id": self.bk_biz_id, "fields": fields})
        self._get_host_topo_inst(host_list)
        for host in host_list:
            host["bk_biz_id"] = self.bk_biz_id
            host["app_module"] = host["module"]
        return host_list

    @cache_half_hour("cmdb:get_cache_hosts_{bk_biz_id}", compress=True)
    def get_cache_hosts(self, bk_biz_id):
        host_info = self.get_hosts()
        result = defaultdict(dict)
        for host in host_info:
            result[host["host"]["bk_host_innerip"]][str(host["host"]["bk_cloud_id"])] = host
        return result

    @staticmethod
    def _remove_empty_nodes(node):
        """
        删除空节点
        :param node:
        :return:
        """
        if not node.get("bk_obj_id") or node.get("bk_obj_id") == "module":
            return True
        # 对其他节点，看它的子节点的child为空
        childs = node.get("child", [])
        node["child"] = [child for child in childs if child.get("child")]

    @staticmethod
    def _compatible(node, node_link, extra_params):
        """
        兼容拓扑选择器，添加 children, name, id 字段
        :param node:
        :param extra_params:
        {
            'bk_biz_id': 2,
            'index': 0
        }
        :return:
        """
        node["children"] = node.get("child", [])
        node["bk_biz_id"] = extra_params["bk_biz_id"]
        extra_params["index"] += 1
        node["id"] = str(extra_params["index"])
        if node.get("ip"):
            node["name"] = node["ip"]
            return
        if node.get("bk_inst_name"):
            node["name"] = node["bk_inst_name"]
            return
        node["name"] = _("无法识别节点")

    def get_module_dict(self, topo, module_dict=None):
        """
        获取模块dict信息
        :param topo: topo信息 dict or list
        :param module_dict: 要写入的模块dict
        """
        # 因为可能传过来的是一个空dict所以不需要重新赋值
        if module_dict is None:
            module_dict = {}
        if isinstance(topo, dict):
            child = topo.get("child")
            if isinstance(child, list) and len(child) == 0:
                module_dict[topo["bk_inst_id"]] = child
            else:
                self.get_module_dict(child, module_dict)

        if isinstance(topo, list):
            for item in topo:
                self.get_module_dict(item, module_dict)

    @cache_one_hour(key="get_service_instance_{node_list}", need_md5=True)
    def get_service_instance(self, node_list):
        """
        获取某个业务下的服务实例
        :param node_list: list[{bk_inst_id, bk_inst_name, bk_obj_id, bk_obj_name, bk_biz_id}]
        :return:
        """
        instance_topo = self.get_instance_topo()
        module_id_dict = {}

        for node in node_list:
            module_id_dict[
                self.Node(self.bk_biz_id, node["bk_obj_id"], node["bk_inst_id"], node["bk_inst_name"])
            ] = self.get_module(node["bk_obj_id"], node["bk_inst_id"], instance_topo)
        node_service_instance = self._get_service_instance(module_id_dict)

        # 需要查询服务分类的集群
        node_and_bk_set_id_list = set()
        for node, set_module_list in module_id_dict.items():
            for set_module in set_module_list:
                node_and_bk_set_id_list.add((node, set_module["bk_set_id"]))

        node_service_category_id = self.get_service_category_id(node_and_bk_set_id_list)
        return self.get_service_category(node_service_instance, node_service_category_id)

    def batch_get_hosts_by_inst_id(self, params):
        return self.get_hosts_by_inst_id(*params)

    def batch_get_agent_status(self, params):
        host_list, node, node_mapping = params
        map_key = "{}|{}".format(str(node[1]), str(node[2]))
        node_path = "/".join(
            [
                node_mapping.get(node, {}).get("bk_inst_name")
                for node in node_mapping.get(map_key, {}).get("node_link", [])
            ]
        )
        agent_error_count = 0
        if host_list:
            agent_status_dict = self.get_agent_status(host_list)
            agent_error_count = len(
                [status for status in list(agent_status_dict.values()) if status != AgentStatusEnum.ON.value]
            )
        return {
            "bk_obj_id": node.bk_obj_id,
            "bk_inst_id": node.bk_inst_id,
            "bk_inst_name": node.bk_inst_name,
            "count": len(host_list),
            "agent_error_count": agent_error_count,
            "bk_biz_id": node.bk_biz_id,
            "node_path": node_path,
        }

    def get_host_info(self, node_list):
        """
        获取主机信息
        :param node_list:
        :return:
        """

        # 获取业务拓扑信息
        biz_topo = CCApi.search_biz_inst_topo({"bk_biz_id": self.bk_biz_id, "level": -1})
        # 获取业务模块信息
        if biz_topo:
            internal_topo = self.get_biz_internal_module()
            biz_topo[0]["child"].insert(0, internal_topo)
        # 节点Mapping
        node_mapping = self.get_node_mapping(biz_topo)
        # 构造结果
        result_dict = {
            self.Node(node["bk_biz_id"], node["bk_obj_id"], node["bk_inst_id"], node["bk_inst_name"]): []
            for node in node_list
        }

        # 获取节点主机信息
        host_multi_execute = MultiExecuteFunc(DEFAULT_MAX_WORKERS)
        for bk_biz_id, bk_obj_id, bk_inst_id, bk_inst_name in result_dict.keys():
            host_multi_execute.append(
                result_key=(bk_biz_id, bk_obj_id, bk_inst_id, bk_inst_name),
                func=self.batch_get_hosts_by_inst_id,
                params=(bk_obj_id, bk_inst_id),
            )
        host_result_dict = host_multi_execute.run()
        for key, host_result in host_result_dict.items():
            result_dict[key].extend(host_result)

        # 获取节点Agent状态
        agent_multi_execute = MultiExecuteFunc(DEFAULT_MAX_WORKERS)
        for node, host_list in result_dict.items():
            agent_multi_execute.append(
                result_key=(node.bk_biz_id, node.bk_obj_id, node.bk_inst_id),
                func=self.batch_get_agent_status,
                params=(host_list, node, node_mapping),
            )
        results = agent_multi_execute.run()

        return results

    def get_node_path(self, node_list):
        """
        获取node_path
        :param node_list: [List] 节点列表 demo 如下
            [{"bk_biz_id": 215, "bk_inst_id": 2000000991, "bk_inst_name": "linux", "bk_obj_id": "module"}]
            bk_biz_id为业务id， bk_inst_id为选择节点id, bk_inst_name为选择节点名称， bk_obj_id为选择节点类型
        :returns: [Dict] 返回(bk_biz_id, bk_obj_id, bk_inst_id)为key 对应dict demo如下:
             {
                (215, "module", 2000000991): {
                    "bk_obj_id": "module",
                    "bk_inst_id": 2000000991,
                    "bk_inst_name": "linux",
                    "bk_biz_id": 215,
                    "node_path": "功夫西游/linux01/linux",
                }
            }
        """
        result_dict = set()
        biz_topo = CCApi.search_biz_inst_topo({"bk_biz_id": self.bk_biz_id, "level": -1})
        if biz_topo:
            internal_topo = self.get_biz_internal_module()
            biz_topo[0]["child"].insert(0, internal_topo)
        node_mapping = self.get_node_mapping(biz_topo)
        for node in node_list:
            result_dict.add(self.Node(node["bk_biz_id"], node["bk_obj_id"], node["bk_inst_id"], node["bk_inst_name"]))

        result = {}
        for node in result_dict:
            map_key = "{}|{}".format(str(node.bk_obj_id), str(node.bk_inst_id))
            node_path = "/".join(
                [
                    node_mapping.get(node).get("bk_inst_name")
                    for node in node_mapping.get(map_key, {}).get("node_link", [])
                ]
            )

            result[(node.bk_biz_id, node.bk_obj_id, node.bk_inst_id)] = {
                "bk_obj_id": node.bk_obj_id,
                "bk_inst_id": node.bk_inst_id,
                "bk_inst_name": node.bk_inst_name,
                "bk_biz_id": node.bk_biz_id,
                "node_path": node_path,
            }
        return result

    def get_hosts_by_inst_id(self, bk_obj_id, bk_inst_id):
        """
        根据主机实例获取主机信息
        :param bk_obj_id: int 对象id
        :param bk_inst_id: int 实例id
        :return:
        """
        hosts = self._get_hosts_by_inst_id(bk_obj_id, bk_inst_id, with_parent_obj_id=False)
        if isinstance(hosts, (str, str)):
            hosts = [hosts]
        return hosts

    def get_module(self, bk_obj_id, bk_inst_id, topo_tree):
        """
        获取模块信息
        :param bk_obj_id: int 对象id
        :param bk_inst_id: int 实例id
        :param topo_tree: dict 拓扑信息
        :return: list[]
        """
        results = []

        def _find_module(node, node_link, module_id_list):
            if node["bk_obj_id"] != "set":
                return False
            inst_key = f"{bk_obj_id}|{bk_inst_id}"
            children = node.get("child")
            if children:
                for item in children:
                    if inst_key in node_link or (bk_obj_id == "module" and bk_inst_id == item["bk_inst_id"]):
                        module_id_list.append({"bk_set_id": node["bk_inst_id"], "bk_module_id": item["bk_inst_id"]})

        self.foreach_topo_tree(topo_tree, _find_module, module_id_list=results)
        return results

    def foreach_topo_tree(self, topo_tree, func=None, topo_link=None, order="asc", *args, **kwargs):
        """
        遍历处理拓扑树方法
        :param topo_tree: 传入需要处理的topo树
        :param func: 具体处理方法，方法接收参数：node（当前节点），node_link（节点的路径），*args，**kwargs
        :param topo_link: 不需传此参数
        :param order: 处理节点的顺序，asc: 从根节点开始处理，desc：从叶子节点开始处理
        :param args:
        :param kwargs:
        """
        params_len = len(signature(func).parameters)
        # 从上到下遍历topo树
        if isinstance(topo_tree, dict):
            # 记录层级
            bk_obj_id = topo_tree.get("bk_obj_id")
            bk_inst_id = topo_tree.get("bk_inst_id")
            inst_key = (
                f'{topo_tree["bk_obj_id"]}|{bk_inst_id}'
                if bk_obj_id and bk_inst_id
                else f'{topo_tree.get("ip")}|{topo_tree.get("bk_cloud_id")}'
            )

            if not topo_link or not isinstance(topo_link, list):
                c_topo_link = [inst_key]
            else:
                c_topo_link = copy.deepcopy(topo_link)
                c_topo_link.append(inst_key)
            # 执行操作
            if func and order == "asc":
                if params_len == 1:
                    func(topo_tree, *args, **kwargs)
                else:
                    func(topo_tree, c_topo_link, *args, **kwargs)
            child = topo_tree.get("child")
            if child:
                if params_len == 1:
                    self.foreach_topo_tree(child, func, order, *args, **kwargs)
                else:
                    self.foreach_topo_tree(child, func, c_topo_link, order, *args, **kwargs)

            if func and order == "desc":
                if params_len == 1:
                    func(topo_tree, *args, **kwargs)
                else:
                    func(topo_tree, c_topo_link, *args, **kwargs)

        if isinstance(topo_tree, list):
            for item in topo_tree:
                c_topo_link = copy.deepcopy(topo_link)
                if params_len == 1:
                    self.foreach_topo_tree(item, func, order, *args, **kwargs)
                else:
                    self.foreach_topo_tree(item, func, c_topo_link, order, *args, **kwargs)

    def get_node_mapping(self, topo_tree):
        """
        节点映射关系
        :param  [list] topo_tree: 拓扑树
        :return: [dict]
        """
        node_mapping = {}

        def mapping(node, node_link, node_mapping):
            node.update(node_link=node_link)
            node_mapping[node_link[-1]] = node

        BizHandler().foreach_topo_tree(topo_tree, mapping, node_mapping=node_mapping)
        return node_mapping

    def _get_service_instance(self, module_id_dict):
        """
        获取服务实例
        :param module_id_dict: dict 模块id字典 {}
        :return:
        """
        return {
            node: CCApi.search_service_instance({"metadata": {"label": {"bk_biz_id": node[0]}}})["info"]
            for node, module_id_list in module_id_dict.items()
        }

    def get_service_category_id(self, node_and_bk_set_id_list, is_dynamic=False):
        """
        :param node_and_bk_set_id_list: list 节点与集群id列表
        :param is_dynamic: bool 是否是动态
        :return: dict{}
        """
        node_service_category_dict = defaultdict(set)
        for node_and_bk_set_id in node_and_bk_set_id_list:
            node = node_and_bk_set_id[0]
            bk_set_id = node_and_bk_set_id[1]
            bk_biz_id = node[2] if is_dynamic else node.bk_biz_id
            module_in_set = self.search_module(bk_biz_id, bk_set_id)
            for module in module_in_set:
                node_service_category_dict[node].add(module["service_category_id"])
        return node_service_category_dict

    def get_service_category(self, node_service_instance, node_service_category_id=None, is_dynamic=False):
        """
        获取服务分类
        :param node_service_instance: dict{node, service_instance}  节点服务实例
        :param node_service_category_id: str 节点分类id
        :param is_dynamic: bool 是否是动态
        :return: list{}
        """
        results = []
        for node, service_instance_list in node_service_instance.items():

            # service_category_id_list = node_service_category_id.get(node, [])
            labels = [
                # ServiceCategorySearcher().search(node[0], service_category_id)
                # for service_category_id in service_category_id_list
            ]
            if is_dynamic:
                results.append(
                    {
                        "bk_obj_id": service_instance_list["bk_obj_id"],
                        "bk_inst_id": service_instance_list["bk_inst_id"],
                        "bk_inst_name": service_instance_list["bk_inst_name"],
                        "count": service_instance_list.get("count", 0),
                        "node_path": service_instance_list["node_path"],
                        "agent_error_count": service_instance_list.get("agent_error_count", 0),  # 保留字段，暂不提供真实异常数据
                        "labels": labels,
                    }
                )
            else:
                results.append(
                    {
                        "bk_obj_id": node[1],
                        "bk_inst_id": node[2],
                        "bk_inst_name": node[3],
                        "count": service_instance_list["count"],
                        "node_path": service_instance_list["node_path"],
                        "instance_error_count": 0,  # 保留字段，暂不提供真实异常数据
                        "labels": labels,
                    }
                )
        results = sorted(results, key=lambda e: lazy_pinyin(e["bk_inst_name"]))
        return results

    def search_module(self, bk_biz_id, bk_set_id):
        """
        查询模块
        :param bk_biz_id: 业务id
        :param bk_set_id: 集群id
        :return: list(json) 主机信息
        """
        return CCApi.search_module({"bk_biz_id": bk_biz_id, "bk_set_id": bk_set_id}).get("info")

    def _get_hosts_by_inst_id(self, bk_obj_id, bk_inst_id, with_parent_obj_id=True):
        query_params = {"bk_biz_id": self.bk_biz_id, "fields": CMDB_HOST_SEARCH_FIELDS}
        query_params.update(self._generate_query_params(bk_obj_id=bk_obj_id, bk_inst_id=bk_inst_id))

        # 由于 CMDB 不支持按集群模块过滤时返回集群模块信息，因此先查出符合条件的主机，再获取拓扑
        host_details = CCApi.list_biz_hosts.bulk_request(query_params)

        if not host_details:
            return []

        if not with_parent_obj_id:
            return host_details

        hosts = CCApi.list_biz_hosts_topo.bulk_request(
            {
                "bk_biz_id": self.bk_biz_id,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [
                        {
                            "field": "bk_host_id",
                            "operator": "in",
                            "value": [host["bk_host_id"] for host in host_details],
                        }
                    ],
                },
                "fields": CMDB_HOST_SEARCH_FIELDS,
            }
        )
        hosts = self._get_host_parent_obj_id(bk_obj_id=bk_obj_id, hosts_info=hosts)
        return hosts

    def _get_host_parent_obj_id(self, bk_obj_id: str, hosts_info: List):
        """
        获取主机对应父节点id信息
        @param bk_obj_id {str} 父节点实例类型
        """
        host_list = []
        for host in hosts_info:
            tmp_host = {"bk_host_innerip": host["host"]["bk_host_innerip"], "bk_cloud_id": host["host"]["bk_cloud_id"]}
            if bk_obj_id in (CCInstanceType.BUSINESS.value):
                tmp_host["parent_inst_id"] = [self.bk_biz_id]
            if bk_obj_id in (CCInstanceType.MODULE.value, TemplateType.SERIVCE_TEMPLATE.value,):
                tmp_host["parent_inst_id"] = [
                    module["bk_module_id"] for topo in host["topo"] for module in topo["module"]
                ]
            if bk_obj_id in (CCInstanceType.SET.value, TemplateType.SET_TEMPLATE.value):
                tmp_host["parent_inst_id"] = [topo["bk_set_id"] for topo in host["topo"]]
            host_list.append(tmp_host)
        return host_list

    def _generate_query_params(self, bk_obj_id, bk_inst_id):
        """
        获取标准query_params
        @param bk_obj_id {str} 实例类型
        @param bk_inst_id {Int} 实例id
        """
        query_params = {}
        if bk_obj_id == CCInstanceType.MODULE.value:
            query_params["bk_module_ids"] = bk_inst_id if isinstance(bk_inst_id, list) else [bk_inst_id]
            return query_params
        if bk_obj_id == "set":
            query_params["bk_set_ids"] = bk_inst_id if isinstance(bk_inst_id, list) else [bk_inst_id]
            return query_params
        if bk_obj_id == TemplateType.SET_TEMPLATE.value:
            query_params["bk_set_ids"] = self._get_template_instance_id(
                bk_inst_ids=[int(inst_id) for inst_id in bk_inst_id]
                if isinstance(bk_inst_id, list)
                else [int(bk_inst_id)],
                bk_obj_id=bk_obj_id,
            )
            return query_params
        if bk_obj_id == TemplateType.SERIVCE_TEMPLATE.value:
            query_params["bk_module_ids"] = self._get_template_instance_id(
                bk_inst_ids=[int(inst_id) for inst_id in bk_inst_id]
                if isinstance(bk_inst_id, list)
                else [int(bk_inst_id)],
                bk_obj_id=bk_obj_id,
            )
            return query_params
        if bk_obj_id == "biz":
            return query_params

        # 自定义层级，需要转化为 set_id 的列表
        set_ids = set()
        _, topo_link_dict = self._get_topo_link()
        target_key = f"{bk_obj_id}|{bk_inst_id}"
        for key, value in topo_link_dict.items():
            obj_id, inst_id = key.split("|")
            if obj_id != "set":
                continue
            if target_key in value:
                set_ids.add(int(inst_id))
        query_params["bk_set_ids"] = list(set_ids)
        return query_params

    def _get_template_instance_id(self, bk_inst_ids: List, bk_obj_id: str):
        """
        获取服务模板，集群模板对应实例id
        @params bk_inst_ids [List] 服务模板或集群模板id列表
        @param bk_obj_id [Str] 模板类型
        """
        modules = self._list_module(bk_inst_ids=bk_inst_ids, template_type=bk_obj_id)
        if bk_obj_id == TemplateType.SET_TEMPLATE.value:
            return [module["set_id"] for module in modules]
        return [module["bk_module_id"] for module in modules]

    def _get_topo_link(self):
        """
        生成拓扑链
        """
        topo_tree_dict = self.get_instance_topo(is_inner=True)
        if not topo_tree_dict:
            return {}, {}

        queue = copy.deepcopy(topo_tree_dict)
        inst_obj_dict = {}
        topo_link_dict = {}

        while queue:
            node = queue.pop()
            inst_obj_dict[f'{node["bk_obj_id"]}|{node["bk_inst_id"]}'] = node
            if not node.get("topo_link"):
                node["topo_link"] = [f'{node["bk_obj_id"]}|{node["bk_inst_id"]}']
                node["topo_link_display"] = [node["bk_inst_name"]]
            topo_link_dict[f'{node["bk_obj_id"]}|{node["bk_inst_id"]}'] = node["topo_link"]
            for child in node["children"]:
                child["topo_link"] = node["topo_link"] + [f'{child["bk_obj_id"]}|{child["bk_inst_id"]}']
                child["topo_link_display"] = node["topo_link_display"] + [child["bk_inst_name"]]

            queue = queue + node["children"]
        return inst_obj_dict, topo_link_dict

    # 获取主机所有拓扑信息
    def _get_host_topo_inst(self, host_list):
        """
        :param host_list: list {} 主机列表
        """
        inst_obj_dict, topo_link_dict = self._get_topo_link()

        for host in host_list:
            module_list = ["module|%s" % x["bk_module_id"] for topo in host["topo"] for x in topo["module"]]
            topo_dict = {"module": [], "set": []}
            for module_key in module_list:
                for inst_key in topo_link_dict.get(module_key, []):
                    bk_obj_id, _ = inst_key.split("|")
                    if bk_obj_id not in topo_dict:
                        topo_dict[bk_obj_id] = []
                    if inst_key not in [f'{x["bk_obj_id"]}|{x["bk_inst_id"]}' for x in topo_dict[bk_obj_id]]:
                        topo_dict[bk_obj_id].append(inst_obj_dict[inst_key])
            for bk_obj_id in topo_dict:
                host[bk_obj_id] = topo_dict[bk_obj_id]

    def get_agent_status(self, host_list):
        """
        获取agent状态信息
        agent状态详细分成4个状态：正常，离线，未安装。已安装，无数据。
        """
        result = defaultdict(int)
        ip_info_list = [{"ip": host["bk_host_innerip"], "plat_id": host["bk_cloud_id"]} for host in host_list]
        if not ip_info_list:
            return {}
        status_list = GseApi.get_agent_status({"app_id": self.bk_biz_id, "is_real_time": 1, "ip_infos": ip_info_list})
        for info in status_list:
            host_id = self.get_host_id(info["ip"], info["plat_id"])
            result[host_id] = AgentStatusEnum.ON.value if info["status"] else AgentStatusEnum.NOT_EXIST.value
        return result

    def get_host_id(self, bk_host_inner_ip, bk_cloud_id):
        """
        获取主机id信息
        :param bk_host_inner_ip: str 蓝鲸主机内网ip
        :param bk_cloud_id: 蓝鲸云id
        :return:
        """
        return f"{bk_host_inner_ip}|{bk_cloud_id}"

    @staticmethod
    def _get_backup_biz_list():
        """
        从备份中获取业务列表
        """
        backup_biz_list = cache.get("cc_biz_list_backup")
        if backup_biz_list is not None:
            return backup_biz_list
        else:
            return []

    def list_module(self):
        params = {
            "bk_obj_id": "module",
            "condition": {"bk_biz_id": self.bk_biz_id},
        }
        return CCApi.search_inst_by_object(params)["info"]

    def list_set(self):
        params = {
            "bk_obj_id": "set",
            "condition": {"bk_biz_id": self.bk_biz_id},
        }
        return CCApi.search_inst_by_object(params)["info"]

    def get_biz_template_topo(self, template_type: str):
        params = {"bk_biz_id": self.bk_biz_id}
        response_data = []
        if template_type == TemplateType.SERIVCE_TEMPLATE.value:
            response_data = CCApi.list_service_template.bulk_request(params)
        if template_type == TemplateType.SET_TEMPLATE.value:
            response_data = CCApi.list_set_template.bulk_request(params)
        space = Space.objects.get(bk_biz_id=self.bk_biz_id)
        response_data = sorted(response_data, key=lambda e: lazy_pinyin(e.get("name", "")))
        result = {
            "bk_biz_id": self.bk_biz_id,
            "bk_biz_name": space.space_name,
            "children": [
                {
                    "bk_biz_id": self.bk_biz_id,
                    "bk_inst_name": query.get("name"),
                    "bk_obj_id": template_type,
                    "bk_inst_id": query.get("id"),
                }
                for query in response_data
            ],
        }

        return result

    def _list_module(self, bk_inst_ids, template_type):
        params = dict(bk_biz_id=self.bk_biz_id, fields=FIND_MODULE_WITH_RELATION_FIELDS)
        if template_type == TemplateType.SERIVCE_TEMPLATE.value:
            modules = []
            params["bk_service_template_ids"] = bk_inst_ids
            modules.extend(CCApi.find_module_with_relation.bulk_request(params, limit=200))
            return modules

        if template_type == TemplateType.SET_TEMPLATE.value:
            return self._get_set_items(bk_inst_ids)

    def get_nodes_by_template(self, bk_inst_ids: list, template_type: str):
        bk_inst_ids = [int(bk_inst_id) for bk_inst_id in bk_inst_ids]
        modules = self._list_module(bk_inst_ids, template_type)
        if template_type == TemplateType.SERIVCE_TEMPLATE.value:
            nodes = [
                dict(
                    bk_biz_id=self.bk_biz_id,
                    bk_inst_id=module["bk_module_id"],
                    bk_inst_name=module["bk_module_name"],
                    bk_obj_id="module",
                )
                for module in modules
            ]
        if template_type == TemplateType.SET_TEMPLATE.value:
            nodes = [
                dict(
                    bk_biz_id=self.bk_biz_id,
                    bk_inst_id=module["set_id"],
                    bk_inst_name=module["bk_set_name"],
                    bk_obj_id="set",
                )
                for module in modules
            ]

        host_dict = self.get_node_path(nodes)
        host_result = self.get_service_category(host_dict, is_dynamic=True)
        return host_result

    def list_agent_status(self, bk_inst_objs: List):
        """
        批量获取agent状态
        @param bk_inst_objs 节点列表
        """
        if not bk_inst_objs:
            return []
        host_dict = self.get_host_info(bk_inst_objs)
        host_result = self.get_service_category(host_dict, is_dynamic=True)
        return host_result

    def _get_set_items(self, set_template_ids: List[int]):
        params = dict(bk_biz_id=self.bk_biz_id, fields=["bk_set_id", "set_template_id", "bk_set_name"])
        result = CCApi.search_set.bulk_request(params)
        return [
            {
                "set_id": set_item["bk_set_id"],
                "bk_set_name": set_item["bk_set_name"],
                "set_template_id": set_item["set_template_id"],
            }
            for set_item in result
            if set_item.get("set_template_id") in set_template_ids
        ]

    def get_modules_info(self, module_ids: List[int]):
        params = {"bk_biz_id": self.bk_biz_id, "fields": ["bk_module_name", "bk_module_id"]}
        result = CCApi.search_module.bulk_request(params)
        modules_info = [
            dict(
                bk_biz_id=self.bk_biz_id,
                bk_inst_id=module["bk_module_id"],
                bk_inst_name=module["bk_module_name"],
                bk_obj_id="module",
            )
            for module in result
            if module.get("bk_module_id") in module_ids
        ]
        host_dict = self.get_node_path(modules_info)
        host_result = self.get_service_category(host_dict, is_dynamic=True)
        return host_result

    def get_sets_info(self, set_ids: List[int]):
        params = {"bk_biz_id": self.bk_biz_id, "fields": ["bk_set_name", "bk_set_id"]}
        result = CCApi.search_set.bulk_request(params)
        sets_info = [
            dict(
                bk_biz_id=self.bk_biz_id,
                bk_inst_id=module["bk_set_id"],
                bk_inst_name=module["bk_set_name"],
                bk_obj_id="set",
            )
            for module in result
            if module.get("bk_set_id") in set_ids
        ]
        host_dict = self.get_node_path(sets_info)
        host_result = self.get_service_category(host_dict, is_dynamic=True)
        return host_result

    @staticmethod
    def get_biz_properties() -> dict:
        """
        获取CMDB业务属性值信息
        """
        biz_properties_dict = {}
        biz_properties_enum_dict = defaultdict(dict)
        biz_properties = CCApi.search_object_attribute({"bk_obj_id": "biz"})
        for bi in biz_properties:
            if bi["bk_property_group"] == BK_PROPERTY_GROUP_ROLE:
                continue
            biz_properties_dict[bi["bk_property_id"]] = bi["bk_property_name"]
            if bi["bk_property_type"] == BIZ_PROPERTY_TYPE_ENUM:
                for oi in bi["option"]:
                    biz_properties_enum_dict[bi["bk_property_id"]][oi["id"]] = oi["name"]

        params = {"fields": [pi for pi in biz_properties_dict]}
        params["fields"].append("bk_biz_id")
        biz_list = CCApi.get_app_list.bulk_request(params)
        result = {}
        for biz in biz_list:
            bk_biz_id = int(biz["bk_biz_id"])
            result[bk_biz_id] = {}
            for bk_property_id in biz_properties_dict:
                biz_property_value = biz.get(bk_property_id)
                if not biz_property_value:
                    continue
                biz_property_value = biz_properties_enum_dict.get(bk_property_id, {}).get(
                    biz_property_value, biz_property_value
                )
                result[bk_biz_id][bk_property_id] = {
                    "biz_property_name": biz_properties_dict[bk_property_id],
                    "biz_property_value": biz_property_value,
                }

        return result

    def list_biz_property(self):
        return BizProperty.list_biz_property()


class ServiceCategorySearcher(object):
    """
    搜索服务分类
    """

    def __init__(self):
        # 用于存储服务分类数据，避免多次调用cmdb接口
        self._service_category_data = {}

    def get_biz_service_category_data(self, bk_biz_id):
        if not self._service_category_data.get(bk_biz_id):
            # 获取业务下的服务分类
            res_service_category = CCApi.search_service_category({"metadata": {"label": {"bk_biz_id": str(bk_biz_id)}}})
            for cate in res_service_category["info"]:
                category_id = cate["id"]
                biz_service_category_mapping = self._service_category_data.setdefault(bk_biz_id, {})
                biz_service_category_mapping[category_id] = cate

        return self._service_category_data[bk_biz_id]

    def search(self, bk_biz_id, category_id):
        category_mapping = self.get_biz_service_category_data(bk_biz_id)
        category_info = category_mapping[category_id]
        label = {"second": ""}
        if category_info.get("bk_parent_id"):
            parent_info = category_mapping.get(category_info["bk_parent_id"], {})
            label["first"] = parent_info.get("name", "")
            label["second"] = category_info.get("name", "")
        else:
            label["first"] = category_info.get("name", "")

        return label
