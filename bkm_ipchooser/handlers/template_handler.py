# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Union

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.tools import batch_request, topo_tool
from bkm_ipchooser.handlers.base import BaseHandler
from bkm_ipchooser.handlers.topo_handler import TopoHandler

logger = logging.getLogger("bkm_ipchooser")


class Template:
    def __init__(self, scope_list: types.ScopeList, template_type: str, template_id: int = None):
        self.scope_list = scope_list
        self.template_type = template_type
        self.template_id = template_id
        # 暂时不支持多业务同时查询
        self.bk_biz_id = [scope["bk_biz_id"] for scope in self.scope_list][0]
        self.meta = BaseHandler.get_meta_data(self.bk_biz_id)

    def list_templates(self, template_id_list: List[int] = None) -> List[types.Template]:
        templates = self.query_cc_templates(template_id_list)
        return self.format_templates(templates)

    def format_templates(self, templates: List[Dict]) -> List[types.Template]:
        """格式化CC API接口获取到的模板列表"""
        raise NotImplementedError

    def query_template_nodes(self, start: int, page_size: int):
        """分页查询模板下的节点列表"""
        raise NotImplementedError

    def query_template_hosts(self, start: int, page_size: int):
        raise NotImplementedError

    def fill_host_count(self, templates: List[types.Template]):
        """填充模板下主机数量"""
        params_list = [
            {
                "template_id": template["id"],
                "fields": constants.CommonEnum.FETCH_HOST_COUNT_FIELDS.value,
            }
            for template in templates
        ]
        template_host_result = batch_request.request_multi_thread(
            func=self.fetch_template_host_total, params_list=params_list, get_data=lambda x: x
        )
        template_host_map = {i["id"]: len(i["data"]) for i in template_host_result}
        for template in templates:
            template["count"] = template_host_map.get(template["id"], 0)

    def list_template_nodes(self, start: int, page_size: int) -> List[types.TemplateNode]:
        """获取节点列表"""
        result = {"start": start, "page_size": page_size, "total": 0, "data": []}
        nodes = self.query_template_nodes(start=start, page_size=page_size)
        if not nodes or not nodes["info"]:
            return result
        nodes = nodes["info"]
        nodes = [self.format_template_node(node) for node in nodes]
        self.fill_node_path(nodes)
        result["data"] = nodes
        return result

    def agent_statistics(self, template_id_list: List[int]) -> List[Dict]:
        """统计模板下主机的agent状态"""
        templates = self.list_templates(template_id_list=template_id_list)
        params_list = [{"template": template} for template in templates]
        template_agent_result = batch_request.request_multi_thread(
            self.template_agent_statistics, params_list=params_list, get_data=lambda x: x
        )
        return template_agent_result

    def template_agent_statistics(self, template: Dict) -> List[Dict]:
        """统计模板下主机的agent状态"""
        raise NotImplementedError

    def list_template_hosts(self, start: int, page_size: int) -> List[types.TemplateNode]:
        """获取主机列表, 带分页"""
        result = {"start": start, "page_size": page_size, "count": 0, "data": []}
        hosts = self.query_template_hosts(start=start, page_size=page_size)
        if not hosts or not hosts["info"]:
            return result
        result["count"] = hosts["count"]
        hosts = hosts["info"]
        result["data"] = BaseHandler.format_hosts(hosts, self.bk_biz_id)

        return result

    def query_cc_templates(self, template_id_list: List[int] = None) -> List[Dict]:
        """子类实现查询CC API接口获取模板列表"""
        raise NotImplementedError

    def fetch_template_node_total(self, template_id: int) -> Dict:
        """
        子类实现获取模板下所有节点
        param: template_id: 模板ID
        param: fields: 需要返回的字段, 默认返回所有字段, 当只为了统计总数的时候, 可以只返回bk_set_id
        """
        raise NotImplementedError

    def fetch_template_host_total(
        self, template_id: int, fields: List[str] = constants.CommonEnum.SIMPLE_HOST_FIELDS.value
    ) -> Dict:
        """
        子类实现获取模板下所有主机
        param: template_id: 模板ID
        param: fields: 需要返回的字段, 默认返回所有字段, 当只为了统计总数的时候, 可以只返回bk_host_id
        """
        raise NotImplementedError

    def format_template_node(self, node: Dict) -> types.TemplateNode:
        """子类实现模板节点格式化"""
        raise NotImplementedError

    def fill_node_path(self, node_list: List[Dict]):
        """获取节点路径"""
        result = []
        if not node_list:
            return result

        def _build_node_key(object_id, instance_id) -> str:
            return f"{object_id}-{instance_id}"

        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_nodes": [
                {
                    "bk_obj_id": node["object_id"],
                    "bk_inst_id": node["instance_id"],
                }
                for node in node_list
            ],
        }
        topo_node_paths = BkApi.find_topo_node_paths(params)
        if not topo_node_paths:
            return result

        node_path_map = {}
        for topo_node_path in topo_node_paths:
            node_key = _build_node_key(topo_node_path["bk_obj_id"], topo_node_path["bk_inst_id"])
            node_path = [topo_tool.TopoTool.format_topo_node(bk_path) for bk_path in topo_node_path["bk_paths"][0]]
            node_path.append(topo_tool.TopoTool.format_topo_node(topo_node_path))
            node_path_map[node_key] = node_path

        for node in node_list:
            node_key = _build_node_key(node["object_id"], node["instance_id"])
            node["node_path"] = node_path_map[node_key]

        return result


class SetTemplate(Template):
    """集群模板"""

    def __init__(self, scope_list: types.ScopeList, template_id: int = None):
        super().__init__(
            scope_list=scope_list, template_id=template_id, template_type=constants.TemplateType.SET_TEMPLATE.value
        )

    def query_cc_templates(self, template_id_list: List[int] = None):
        """调用CC接口获取集群模板"""
        params = {"bk_biz_id": self.bk_biz_id}
        if template_id_list:
            params["set_template_ids"] = template_id_list
        return BkApi.list_set_template(params)

    def format_templates(self, templates: List[Dict]) -> List[types.Template]:
        """格式化CC API接口获取到的模板列表"""
        BaseHandler.sort_by_name(templates)
        return [
            {
                "id": template.get("id"),
                "name": template.get("name"),
                "template_type": self.template_type,
                "last_time": template.get("last_time"),
                "meta": self.meta,
            }
            for template in templates
        ]

    def query_template_nodes(self, start: int, page_size: int) -> List[types.TemplateNode]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_SET_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
            "condition": {
                "set_template_id": self.template_id,
            },
        }
        return BkApi.search_set(params)

    def query_template_hosts(self, start: int, page_size: int) -> List[types.FormatHostInfo]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_set_template_ids": [self.template_id],
            "fields": constants.CommonEnum.DEFAULT_HOST_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
        }
        return BkApi.find_host_by_set_template(params)

    def fetch_template_host_total(
        self, template_id: int, fields: List[str] = constants.CommonEnum.SIMPLE_HOST_FIELDS.value
    ) -> Dict:
        result = {
            "id": template_id,
            "data": [],
        }
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_set_template_ids": [template_id],
            "fields": fields,
            # 此处添加no_request参数，避免多线程调用时, 用户信息被覆盖
            "no_request": True,
        }
        host_list = BkApi.bulk_find_host_by_set_template(params)
        if not host_list:
            return result
        result["data"] = host_list
        return result

    def template_agent_statistics(self, template: Dict) -> List[Dict]:
        """统计模板下主机的agent状态"""
        result = {"set_template": {"id": template["id"], "name": template["name"], "meta": self.meta}}

        host_list = self.fetch_template_host_total(
            template["id"], fields=constants.CommonEnum.SIMPLE_HOST_FIELDS.value
        )["data"]
        TopoHandler.fill_agent_status(host_list)
        result.update(TopoHandler.count_agent_status(host_list))
        result["host_count"] = len(host_list)
        result["node_count"] = len(self.fetch_template_node_total(template["id"])["data"])
        return result

    def fetch_template_node_total(self, template_id: int) -> Dict:
        """
        获取模板下所有节点
        param: template_id: 模板ID
        param: fields: 需要返回的字段, 默认返回所有字段, 当只为了统计总数的时候, 可以只返回bk_set_id
        """
        result = {"template_id": template_id, "data": []}
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_SET_FIELDS.value,
            "condition": {
                "set_template_id": self.template_id,
            },
            "no_request": True,
        }
        node_list = BkApi.bulk_search_set(params)
        if not node_list:
            return result

        result["data"] = node_list
        return result

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


class ServiceTemplate(Template):
    """服务模板"""

    def __init__(self, scope_list: types.ScopeList, template_id: int = None):
        super().__init__(
            scope_list=scope_list, template_id=template_id, template_type=constants.TemplateType.SERVICE_TEMPLATE.value
        )

    def query_cc_templates(self, template_id_list: List[int] = None):
        """调用CC接口获取服务模板"""
        params = {"bk_biz_id": self.bk_biz_id}
        if template_id_list:
            params["service_template_ids"] = template_id_list
        return BkApi.list_service_template(params)

    def format_templates(self, templates: List[Dict]) -> List[types.Template]:
        """格式化CC API接口获取到的模板列表"""
        service_category_list = BkApi.list_service_category({"bk_biz_id": self.bk_biz_id})
        service_category_map = {}
        if service_category_list and service_category_list["info"]:
            for category in service_category_list["info"]:
                service_category_map[category["id"]] = category["name"]

        BaseHandler.sort_by_name(templates)
        return [
            {
                "id": template.get("id"),
                "name": template.get("name"),
                "template_type": self.template_type,
                "last_time": template.get("last_time"),
                "meta": self.meta,
                "service_category": service_category_map.get(template.get("service_category_id"), ""),
            }
            for template in templates
        ]

    def query_template_nodes(self, start: int, page_size: int) -> List[types.TemplateNode]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_MODULE_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
            "condition": {
                "service_template_id": self.template_id,
            },
        }
        return BkApi.search_module(params)

    def query_template_hosts(self, start: int, page_size: int) -> List[types.FormatHostInfo]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_service_template_ids": [self.template_id],
            "fields": constants.CommonEnum.DEFAULT_HOST_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
        }
        return BkApi.find_host_by_service_template(params)

    def template_agent_statistics(self, template: Dict) -> List[Dict]:
        """统计模板下主机的agent状态"""
        result = {"service_template": {"id": template["id"], "name": template["name"], "meta": self.meta}}

        host_list = self.fetch_template_host_total(
            template["id"], fields=constants.CommonEnum.SIMPLE_HOST_FIELDS.value
        )["data"]
        TopoHandler.fill_agent_status(host_list)
        result.update(TopoHandler.count_agent_status(host_list))
        result["host_count"] = len(host_list)
        result["node_count"] = len(self.fetch_template_node_total(template["id"])["data"])
        return result

    def fetch_template_node_total(self, template_id: int) -> Dict:
        """
        获取模板下所有节点
        param: template_id: 模板ID
        param: fields: 需要返回的字段, 默认返回所有字段, 当只为了统计总数的时候, 可以只返回bk_module_id
        """
        result = {"template_id": template_id, "data": []}
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_MODULE_FIELDS.value,
            "condition": {
                "service_template_id": self.template_id,
            },
            "no_request": True,
        }
        node_list = BkApi.bulk_search_module(params)
        if not node_list:
            return result

        result["data"] = node_list
        return result

    def fetch_template_host_total(
        self, template_id: int, fields: List[str] = constants.CommonEnum.SIMPLE_HOST_FIELDS.value
    ) -> Dict:
        result = {
            "id": template_id,
            "data": [],
        }
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_service_template_ids": [template_id],
            "fields": fields,
            # 此处添加no_request参数，避免多线程调用时, 用户信息被覆盖
            "no_request": True,
        }
        host_list = BkApi.bulk_find_host_by_service_template(params)
        if not host_list:
            return result
        result["data"] = host_list
        return result

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

    def list_templates(self, template_id_list: List[int] = None) -> List[types.Template]:
        return self.get_instance().list_templates(template_id_list=template_id_list)

    def list_nodes(self, start: int, page_size: int) -> List[types.TemplateNode]:
        return self.get_instance().list_template_nodes(start=start, page_size=page_size)

    def list_hosts(self, start: int, page_size: int) -> List[types.HostInfo]:
        return self.get_instance().list_template_hosts(start=start, page_size=page_size)

    def agent_statistics(self, template_id_list: List[int] = None) -> List[Dict]:
        return self.get_instance().agent_statistics(template_id_list=template_id_list)
