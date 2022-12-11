# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Union, Any
from collections import defaultdict

from pypinyin import lazy_pinyin

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.handlers.base import BaseHandler

logger = logging.getLogger("bkm_ipchooser")


class Template:
    def __init__(self, scope_list: types.ScopeList, template_type: str):
        self.scope_list = scope_list
        self.template_type = template_type
        # 暂时不支持多业务同时查询
        self.bk_biz_id = [scope["bk_biz_id"] for scope in self.scope_list][0]
        self.meta = BaseHandler.get_meta_data(self.bk_biz_id)

    def format_templates(self, templates: List[Dict]) -> List[types.Template]:
        """格式化CC API接口获取到的模板列表"""
        templates = sorted(templates, key=lambda x: lazy_pinyin(x.get("name", "")))
        return [
            {
                "id": template.get("id"),
                "name": template.get("name"),
                "template_type": self.template_type,
                "meta": self.meta,
            }
            for template in templates
        ]

    def list_templates(self) -> List[types.Template]:
        """获取模板列表"""
        templates = self.query_cc_templates()
        return self.format_templates(templates)

    def list_template_nodes(self, template_ids: List[int] = None) -> List[types.TemplateNode]:
        """获取节点列表"""
        raise NotImplementedError

    def list_template_node_agent_status(self, node_ids: List[int]) -> List[Dict]:
        """查询节点Agent状态"""
        raise NotImplementedError

    def query_cc_templates(self) -> List[Dict]:
        """子类实现查询CC API接口获取模板列表"""
        raise NotImplementedError

    def format_template_node(self, node: Dict) -> types.TemplateNode:
        """子类实现模板节点格式化"""
        raise NotImplementedError

    def query_cc_sets(self) -> List[Dict]:
        """查询CC API接口获取集群列表"""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_SET_FIELDS.value,
        }
        return BkApi.search_set(params)

    def query_cc_modules(self) -> List[Dict]:
        """查询CC API接口获取模块列表"""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_MODULE_FIELDS.value,
        }
        return BkApi.search_module(params)

    def list_hosts_with_topo(self, node_ids: List[int] = None) -> Dict:
        """查询节点主机列表"""
        if not node_ids:
            return {}
        result = {node_id: [] for node_id in node_ids}
        hosts = self._list_biz_hosts_topo(node_ids)
        if not hosts:
            return result
        for host in hosts:
            host_with_topo = self._get_host_with_topo(host, node_ids)
            result[host_with_topo["node_id"]].append(host_with_topo)
        return result

    def _list_biz_hosts_topo(self, node_ids: List[int] = None) -> List:
        """子类重写获取主机列表"""
        raise NotImplementedError

    def _get_host_with_topo(self, host: Dict, node_ids: List[int] = None) -> Union[Dict[str, Any], Any]:
        """子类重写获取主机以及拓扑信息"""
        raise NotImplementedError

    def list_agent_status(self, hosts_with_topo: List[Dict]) -> Dict:
        """
        hosts: list_hosts_with_topo: List[Dict]返回的主机列表
        """
        result = dict(count=len(hosts_with_topo), agent_error_count=0)
        if not hosts_with_topo:
            return result
        params = {
            "hosts": [
                {
                    "ip": host.get("bk_host_innerip"),
                    "bk_cloud_id": host.get("bk_cloud_id"),
                }
                for host in hosts_with_topo
            ]
        }
        agent_status_result = BkApi.get_agent_status(params)
        for host_status in agent_status_result.values():
            if host_status.get("bk_agent_alive") != constants.AgentStatusType.ALIVE.value:
                result["agent_error_count"] += 1
        return result


class SetTemplate(Template):
    """集群模板"""

    def __init__(self, scope_list: types.ScopeList):
        super().__init__(scope_list=scope_list, template_type=constants.TemplateType.SET_TEMPLATE.value)

    def query_cc_templates(self):
        """调用CC接口获取集群模板"""
        return BkApi.list_set_template({"bk_biz_id": self.bk_biz_id})

    def list_template_nodes(self, template_ids: List[int] = None) -> List[types.TemplateNode]:
        """获取集群模板下的节点列表"""
        nodes = self.query_cc_sets()
        if not template_ids:
            return [self.format_template_node(node) for node in nodes if node.get("set_template_id")]
        return [self.format_template_node(node) for node in nodes if node.get("set_template_id") in template_ids]

    def format_template_node(self, node: Dict) -> types.TemplateNode:
        """格式化节点"""
        return dict(
            instance_id=node.get("bk_set_id"),
            instance_name=node.get("bk_set_name"),
            template_id=node.get("set_template_id"),
            object_id=constants.ObjectType.SET.value,
            object_name=constants.ObjectType.get_member_value__alias_map().get(constants.ObjectType.SET.value),
            meta=self.meta,
        )

    def _list_biz_hosts_topo(self, node_ids: List[int] = None) -> List[Dict]:
        """获取主机列表"""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "set_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_set_id", "operator": "in", "value": node_ids}],
            },
            "fields": constants.CommonEnum.DEFAULT_HOST_FIELDS.value,
        }
        return BkApi.list_biz_hosts_topo(params)

    def _get_host_with_topo(self, host: Dict, node_ids: List[int] = None) -> Union[Dict[str, Any], Any]:
        """获取主机拓扑"""
        result = dict(
            bk_cloud_id=host["host"]["bk_cloud_id"],
            bk_host_innerip=host["host"]["bk_host_innerip"],
            bk_host_id=host["host"]["bk_host_id"],
        )
        for _set in host["topo"]:
            if _set["bk_set_id"] in node_ids:
                result["node_id"] = _set["bk_set_id"]
                result["node_name"] = _set["bk_set_name"]
                return result
        return None


class ServiceTemplate(Template):
    """服务模板"""

    def __init__(self, scope_list: types.ScopeList):
        super().__init__(scope_list=scope_list, template_type=constants.TemplateType.SET_TEMPLATE.value)

    def query_cc_templates(self):
        """调用CC接口获取服务模板"""
        return BkApi.list_service_template({"bk_biz_id": self.bk_biz_id})

    def list_template_nodes(self, template_ids: List[int] = None) -> List[types.TemplateNode]:
        """获取集群模板下的节点列表"""
        nodes = self.query_cc_modules()
        if not template_ids:
            return [self.format_template_node(node) for node in nodes if node.get("service_template_id")]
        return [self.format_template_node(node) for node in nodes if node.get("service_template_id") in template_ids]

    def format_template_node(self, node: Dict) -> types.TemplateNode:
        """格式化节点"""
        return dict(
            instance_id=node.get("bk_module_id"),
            instance_name=node.get("bk_module_name"),
            template_id=node.get("service_template_id"),
            object_id=constants.ObjectType.MODULE.value,
            object_name=constants.ObjectType.get_member_value__alias_map().get(constants.ObjectType.MODULE.value),
            meta=self.meta,
        )

    def _get_host_with_topo(self, host: Dict, node_ids: List[int] = None) -> Union[Dict[str, Any], Any]:
        """获取主机拓扑"""
        result = dict(
            bk_cloud_id=host["host"]["bk_cloud_id"],
            bk_host_innerip=host["host"]["bk_host_innerip"],
            bk_host_id=host["host"]["bk_host_id"],
        )
        for _set in host["topo"]:
            for _module in _set["module"]:
                if _module["bk_module_id"] in node_ids:
                    result["node_id"] = _module["bk_module_id"]
                    result["node_name"] = _module["bk_module_name"]
                    return result
        return None

    def _list_biz_hosts_topo(self, node_ids: List[int] = None) -> List[Dict]:
        """获取主机列表"""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "module_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_module_id", "operator": "in", "value": node_ids}],
            },
            "fields": constants.CommonEnum.DEFAULT_HOST_FIELDS.value,
        }
        return BkApi.list_biz_hosts_topo(params)


class TemplateHandler:
    """模板处理类"""

    def __init__(self, scope_list: types.ScopeList, template_type: str):
        self.scope_list = scope_list
        self.template_type = template_type

    def get_instance(self) -> Union[ServiceTemplate, SetTemplate]:
        """获取模板处理实例"""
        return {
            constants.TemplateType.SET_TEMPLATE.value: SetTemplate,
            constants.TemplateType.SERVICE_TEMPLATE.value: ServiceTemplate,
        }.get(self.template_type)(scope_list=self.scope_list)

    def list_templates(self) -> List[types.Template]:
        return self.get_instance().list_templates()

    def list_nodes(self, template_ids: List[int] = None) -> List[types.TemplateNode]:
        return self.get_instance().list_template_nodes(template_ids)

    def list_agent_status(self, template_ids: List[int]) -> List[Dict]:
        """获取集群模板下的主机Agent状态"""
        handler = self.get_instance()
        templates = handler.list_templates()
        # 存放模板信息
        template_info = {template["id"]: template for template in templates if template["id"] in template_ids}
        result = [
            {
                "template_id": template_id,
                "template_name": template_info[template_id]["name"],
                "meta": handler.meta,
                "child": [],
            }
            for template_id in template_ids
            if template_info.get(template_id)
        ]
        template_nodes = handler.list_template_nodes(template_ids)
        if not template_nodes:
            return result
        # 存放模板节点信息
        template_node_info = defaultdict(lambda: defaultdict(dict))
        for node in template_nodes:
            template_node_info[node["template_id"]][node["instance_id"]] = node

        for _result in result:
            template_id = _result["template_id"]
            node_hosts_with_topo = handler.list_hosts_with_topo(list(template_node_info[template_id].keys()))
            for node_id, hosts_with_topo in node_hosts_with_topo.items():
                _child = template_node_info[template_id][node_id]
                _child.update(handler.list_agent_status(hosts_with_topo))
                _result["child"].append(_child)

        return result
