# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Union

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.tools import batch_request
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
        BaseHandler.sort_by_name(templates)
        self.fill_host_count(templates)
        return [
            {
                "id": template.get("id"),
                "name": template.get("name"),
                "template_type": self.template_type,
                "last_time": template.get("last_time"),
                "count": template.get("count", 0),
                "meta": self.meta,
            }
            for template in templates
        ]

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
        result["data"] = TopoHandler.agent_statistics(nodes)
        return result

    def list_template_hosts(self, start: int, page_size: int) -> List[types.TemplateNode]:
        """获取主机列表, 带分页"""
        result = {"start": start, "page_size": page_size, "total": 0, "data": []}
        hosts = self.query_template_hosts(start=start, page_size=page_size)
        if not hosts or not hosts["info"]:
            return result
        result["total"] = hosts["count"]
        hosts = hosts["info"]
        TopoHandler.fill_agent_status(hosts)
        BaseHandler.fill_meta(hosts, self.meta)
        result["data"] = hosts

        return result

    def query_cc_templates(self) -> List[Dict]:
        """子类实现查询CC API接口获取模板列表"""
        raise NotImplementedError

    def fetch_template_host_total(self, template_id: int) -> List:
        """子类实现获取模板下所有主机"""
        raise NotImplementedError

    def format_template_node(self, node: Dict) -> types.TemplateNode:
        """子类实现模板节点格式化"""
        raise NotImplementedError


class SetTemplate(Template):
    """集群模板"""

    def __init__(self, scope_list: types.ScopeList, template_id: int = None):
        super().__init__(
            scope_list=scope_list, template_id=template_id, template_type=constants.TemplateType.SET_TEMPLATE.value
        )

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

    def query_cc_templates(self):
        """调用CC接口获取集群模板"""
        return BkApi.list_set_template({"bk_biz_id": self.bk_biz_id})

    def query_template_hosts(self, start: int, page_size: int) -> List[types.FormatHostInfo]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_set_template_ids": [self.template_id],
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
        }
        return BkApi.find_host_by_set_template(params)

    def fetch_template_host_total(self, template_id: int) -> int:
        result = {
            "id": template_id,
            "data": [],
        }
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_set_template_ids": [template_id],
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
            # 此处添加no_request参数，避免多线程调用时, 用户信息被覆盖
            "no_request": True,
        }
        fetch_count_result = BkApi.bulk_find_host_by_set_template(params)
        if not fetch_count_result:
            return result
        result["data"] = fetch_count_result
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
            # TODO: node_path待研究
            node_path=node.get("bk_set_name"),
        )


class ServiceTemplate(Template):
    """服务模板"""

    def __init__(self, scope_list: types.ScopeList, template_id: int = None):
        super().__init__(
            scope_list=scope_list, template_id=template_id, template_type=constants.TemplateType.SERVICE_TEMPLATE.value
        )

    def query_cc_templates(self):
        """调用CC接口获取服务模板"""
        return BkApi.list_service_template({"bk_biz_id": self.bk_biz_id})

    def query_template_nodes(self, start: int, page_size: int) -> List[types.TemplateNode]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": constants.CommonEnum.DEFAULT_MODULE_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
            "condition": {
                "bk_service_template_ids": [self.template_id],
            },
        }
        return BkApi.find_module_with_relation(params)

    def query_template_hosts(self, start: int, page_size: int) -> List[types.FormatHostInfo]:
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_service_template_ids": [self.template_id],
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
            "page": {
                "start": start,
                "limit": page_size,
            },
        }
        return BkApi.find_host_by_service_template(params)

    def fetch_template_host_total(self, template_id: int) -> int:
        result = {
            "id": template_id,
            "data": [],
        }
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_service_template_ids": [template_id],
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
            # 此处添加no_request参数，避免多线程调用时, 用户信息被覆盖
            "no_request": True,
        }
        fetch_count_result = BkApi.bulk_find_host_by_service_template(params)
        if not fetch_count_result:
            return result
        result["data"] = fetch_count_result
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
            node_path=node.get("bk_module_name"),
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
        handler = self.get_instance()
        templates = handler.query_cc_templates()
        if template_id_list:
            templates = [template for template in templates if template["id"] in template_id_list]
        return handler.format_templates(templates)

    def list_nodes(self, start: int, page_size: int) -> List[types.TemplateNode]:
        return self.get_instance().list_template_nodes(start=start, page_size=page_size)

    def list_hosts(self, start: int, page_size: int) -> List[types.HostInfo]:
        return self.get_instance().list_template_hosts(start=start, page_size=page_size)
