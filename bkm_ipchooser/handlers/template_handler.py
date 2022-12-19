# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Union
from collections import defaultdict

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.query import resource
from bkm_ipchooser.handlers.base import BaseHandler
from bkm_ipchooser.handlers.topo_handler import TopoHandler

logger = logging.getLogger("bkm_ipchooser")


class Template:

    TEMPLATE_ID_KEY_MAP = {
        constants.TemplateType.SET_TEMPLATE.value: "set_template_id",
        constants.TemplateType.SERVICE_TEMPLATE.value: "service_template_id",
    }

    NODE_ID_KEY_MAP = {
        constants.TemplateType.SET_TEMPLATE.value: "bk_set_id",
        constants.TemplateType.SERVICE_TEMPLATE.value: "bk_module_id",
    }

    def __init__(self, scope_list: types.ScopeList, template_type: str, template_id: int = None):
        self.scope_list = scope_list
        self.template_type = template_type
        self.template_id = template_id
        # 暂时不支持多业务同时查询
        self.bk_biz_id = [scope["bk_biz_id"] for scope in self.scope_list][0]
        self.meta = BaseHandler.get_meta_data(self.bk_biz_id)

    def format_templates(self, templates: List[Dict]) -> List[types.Template]:
        """格式化CC API接口获取到的模板列表"""
        BaseHandler.add_latest_label_and_sort(templates)
        self.add_node_count(templates)
        return [
            {
                "id": template.get("id"),
                "name": template.get("name"),
                "template_type": self.template_type,
                "is_latest": template.get("is_latest"),
                "count": template.get("count", 0),
                "meta": self.meta,
            }
            for template in templates
        ]

    def query_template_nodes(self):
        raise NotImplementedError

    def add_node_count(self, templates: List[types.Template]):
        template_node_map = defaultdict(int)
        nodes = self.query_template_nodes()
        for node in nodes:
            template_id = node.get(self.TEMPLATE_ID_KEY_MAP[self.template_type])
            template_node_map[template_id] += 1
        for template in templates:
            template["count"] = template_node_map.get(template["id"], 0)

    def list_template_nodes(self) -> List[types.TemplateNode]:
        """获取节点列表"""
        bk_biz_name = resource.ResourceQueryHelper.fetch_biz_list([self.bk_biz_id])[0]["bk_biz_name"]
        template_name = ""
        for template in self.query_cc_templates():
            if template["id"] == self.template_id:
                template_name = template["name"]
                break
        nodes = self.query_template_nodes()
        nodes = [
            self.format_template_node(node, bk_biz_name, template_name)
            for node in nodes
            if self.template_id == node.get(self.TEMPLATE_ID_KEY_MAP[self.template_type])
        ]
        node_agent_status = self.node_agent_status()
        for node in nodes:
            node_id = node["instance_id"]
            hosts = node_agent_status.get(node_id, [])
            node["agent_count"] = len(hosts)
            node["agent_error_count"] = len(
                [host for host in hosts if host["status"] != constants.AgentStatusType.ALIVE.value]
            )
        return {
            "count": len(nodes),
            "nodes": nodes,
        }

    def node_agent_status(self, return_all: bool = False) -> List[Dict]:
        result = defaultdict(list)
        nodes = self.query_cc_sets()
        nodes = [node for node in nodes if self.template_id == node.get(self.TEMPLATE_ID_KEY_MAP[self.template_type])]
        node_info = {node[self.NODE_ID_KEY_MAP[self.template_type]]: node for node in nodes}
        node_ids = list(node_info.keys())
        hosts = self._list_biz_hosts_topo(node_ids)
        for host in hosts:
            host = self._get_host_with_topo(host, node_ids)
            result[host["node_id"]].append(host)
        for hosts in result.values():
            TopoHandler.fill_agent_status(hosts)

        if not return_all:
            return result

        hosts = []
        for hosts in result.values():
            hosts.extend(hosts)
        return hosts

    def list_template_hosts(self) -> List[types.TemplateNode]:
        """获取主机列表"""
        nodes = self.query_template_nodes()
        nodes = [node for node in nodes if self.template_id == node.get(self.TEMPLATE_ID_KEY_MAP[self.template_type])]
        hosts = self.node_agent_status(return_all=True)
        return {
            "count": len(hosts),
            "hosts": hosts,
        }

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

    def _list_biz_hosts_topo(self, node_ids: List[int] = None) -> List:
        """子类重写获取主机列表"""
        raise NotImplementedError

    def _get_host_with_topo(self, host: Dict, node_ids: List[int] = None):
        """子类重写添加主机拓扑信息"""
        raise NotImplementedError


class SetTemplate(Template):
    """集群模板"""

    def __init__(self, scope_list: types.ScopeList, template_id: int = None):
        super().__init__(
            scope_list=scope_list, template_id=template_id, template_type=constants.TemplateType.SET_TEMPLATE.value
        )

    def query_template_nodes(self):
        return self.query_cc_sets()

    def query_cc_templates(self):
        """调用CC接口获取集群模板"""
        return BkApi.list_set_template({"bk_biz_id": self.bk_biz_id})

    def format_template_node(self, node: Dict, bk_biz_name: str, template_name: str) -> types.TemplateNode:
        """格式化节点"""
        return dict(
            instance_id=node.get("bk_set_id"),
            instance_name=node.get("bk_set_name"),
            template_id=node.get("set_template_id"),
            object_id=constants.ObjectType.SET.value,
            object_name=constants.ObjectType.get_member_value__alias_map().get(constants.ObjectType.SET.value),
            meta=self.meta,
            node_path="{}/{}/{}".format(bk_biz_name, node.get("bk_set_name"), template_name),
        )

    def _list_biz_hosts_topo(self, node_ids: List[int] = None) -> List[Dict]:
        """获取主机列表"""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "set_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_set_id", "operator": "in", "value": node_ids}],
            },
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
        }
        return BkApi.list_biz_hosts_topo(params)

    def _get_host_with_topo(self, host: Dict, node_ids: List[int] = None):
        """获取主机拓扑"""
        result = host["host"]
        for _set in host["topo"]:
            if _set["bk_set_id"] in node_ids:
                result["node_id"] = _set["bk_set_id"]
                result["node_name"] = _set["bk_set_name"]
        return result


class ServiceTemplate(Template):
    """服务模板"""

    def __init__(self, scope_list: types.ScopeList, template_id: int = None):
        super().__init__(
            scope_list=scope_list, template_id=template_id, template_type=constants.TemplateType.SET_TEMPLATE.value
        )

    def query_cc_templates(self):
        """调用CC接口获取服务模板"""
        return BkApi.list_service_template({"bk_biz_id": self.bk_biz_id})

    def query_template_nodes(self):
        return self.query_cc_sets()

    def format_template_node(self, node: Dict, bk_biz_name: str, template_name: str) -> types.TemplateNode:
        """格式化节点"""
        return dict(
            instance_id=node.get("bk_module_id"),
            instance_name=node.get("bk_module_name"),
            template_id=node.get("service_template_id"),
            object_id=constants.ObjectType.MODULE.value,
            object_name=constants.ObjectType.get_member_value__alias_map().get(constants.ObjectType.MODULE.value),
            meta=self.meta,
            node_path="{}/{}/{}".format(bk_biz_name, node.get("bk_module_name"), template_name),
        )

    def _get_host_with_topo(self, host: Dict, node_ids: List[int] = None):
        """获取主机拓扑"""
        result = host["host"]
        for _set in host["topo"]:
            for _module in _set["module"]:
                if _module["bk_module_id"] in node_ids:
                    host["node_id"] = _module["bk_module_id"]
                    host["node_name"] = _module["bk_module_name"]
        return result

    def _list_biz_hosts_topo(self, node_ids: List[int] = None) -> List[Dict]:
        """获取主机列表"""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "module_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_module_id", "operator": "in", "value": node_ids}],
            },
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
        }
        return BkApi.list_biz_hosts_topo(params)


class TemplateHandler:
    """模板处理类"""

    def __init__(self, scope_list: types.ScopeList, template_type: str, template_id: int = None):
        self.scope_list = scope_list
        self.template_type = template_type
        self.template_id = template_id

    def get_instance(self) -> Union[ServiceTemplate, SetTemplate]:
        """获取模板处理实例"""
        return {
            constants.TemplateType.SET_TEMPLATE.value: SetTemplate,
            constants.TemplateType.SERVICE_TEMPLATE.value: ServiceTemplate,
        }.get(self.template_type)(scope_list=self.scope_list, template_id=self.template_id)

    def list_templates(self) -> List[types.Template]:
        handler = self.get_instance()
        templates = handler.query_cc_templates()
        return handler.format_templates(templates)

    def list_nodes(self) -> List[types.TemplateNode]:
        return self.get_instance().list_template_nodes()

    def list_hosts(self) -> List[types.HostInfo]:
        return self.get_instance().list_template_hosts()
