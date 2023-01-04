# -*- coding: utf-8 -*-

from apps.api import CCApi, GseApi
from bkm_ipchooser.api import AbstractBkApi
from bkm_ipchooser.constants import CommonEnum, ObjectType
from bkm_ipchooser.tools.batch_request import request_multi_thread


class BkApi(AbstractBkApi):
    @staticmethod
    def search_cloud_area(params: dict = None):
        return CCApi.search_cloud_area(params)

    @staticmethod
    def search_business(params: dict = None):
        return CCApi.get_app_list(params)

    @staticmethod
    def search_biz_inst_topo(params: dict = None):
        return CCApi.search_biz_inst_topo(params)

    @staticmethod
    def get_biz_internal_module(params: dict = None):
        return CCApi.get_biz_internal_module(params)

    @staticmethod
    def find_host_topo_relation(params: dict = None):
        return CCApi.find_host_topo_relation(params)

    @staticmethod
    def list_biz_hosts(params: dict = None):
        return CCApi.list_biz_hosts(params)

    @staticmethod
    def bulk_list_biz_hosts(params: dict = None):
        return CCApi.list_biz_hosts.bulk_request(params)

    @staticmethod
    def list_host_total_mainline_topo(params: dict = None):
        return CCApi.list_host_total_mainline_topo(params)

    @staticmethod
    def get_agent_status(params: dict = None):
        return GseApi.get_agent_status_raw(params)

    @staticmethod
    def get_agent_status_v2(params: dict = None):
        return GseApi.get_agent_status_raw_v2(params)

    @staticmethod
    def list_service_template(params: dict = None):
        return CCApi.list_service_template.bulk_request(params)

    @staticmethod
    def list_set_template(params: dict = None):
        return CCApi.list_set_template.bulk_request(params)

    @staticmethod
    def search_set(params: dict = None):
        return CCApi.search_set(params)

    @staticmethod
    def bulk_search_set(params: dict = None):
        return CCApi.search_set.bulk_request(params)

    @staticmethod
    def search_module(params: dict = None):
        return CCApi.search_module(params)

    @staticmethod
    def bulk_search_module(params: dict = None):
        return CCApi.search_module.bulk_request(params)

    @staticmethod
    def search_dynamic_group(params: dict = None):
        return CCApi.search_dynamic_group(params)

    @staticmethod
    def bulk_search_dynamic_group(params: dict = None):
        """批量查询动态分组"""
        return CCApi.search_dynamic_group.bulk_request(params)

    @staticmethod
    def execute_dynamic_group(params: dict = None):
        return CCApi.execute_dynamic_group(params)

    @staticmethod
    def bulk_execute_dynamic_group(params: dict = None):
        return CCApi.execute_dynamic_group.bulk_request(params)

    @staticmethod
    def find_host_by_set_template(params: dict = None):
        return CCApi.find_host_by_set_template(params)

    @staticmethod
    def bulk_find_host_by_set_template(params: dict = None):
        return CCApi.find_host_by_set_template.bulk_request(params)

    @staticmethod
    def find_host_by_service_template(params: dict = None):
        return CCApi.find_host_by_service_template(params)

    @staticmethod
    def bulk_find_host_by_service_template(params: dict = None):
        return CCApi.find_host_by_service_template.bulk_request(params)

    @staticmethod
    def find_topo_node_paths(params: dict = None):
        return CCApi.find_topo_node_paths(params)

    @staticmethod
    def list_service_category(params: dict = None):
        return CCApi.list_service_category(params)


class IPChooser:
    # IP选择器转换IP列表类

    def __init__(self, bk_biz_id: int, fields: list = None):
        self.bk_biz_id = bk_biz_id
        # 默认返回的主机属性, 可以自定义传入字段列表
        self.fields = fields if fields else CommonEnum.DEFAULT_HOST_FIELDS.value

    def _get_method(self, node_type: str):
        node_type = node_type.split("_list")[0]
        method_name = "transfer_{}".format(node_type.lower())
        return getattr(self, method_name)

    def transfer2host(self, params: dict = None):
        host_list = []
        if not params:
            return host_list
        for node_type, node_value in params.items():
            _node_host_list = self._get_method(node_type)(node_value)
            if not _node_host_list:
                continue
            host_list.extend(_node_host_list)
        return host_list

    def transfer_host(self, host_list: list):
        params = {
            "bk_biz_id": self.bk_biz_id,
            "host_property_filter": {
                "condition": "AND",
                "rules": [
                    {"field": "bk_host_id", "operator": "in", "value": [i["host_id"] for i in host_list]},
                ],
            },
            "fields": self.fields,
            "no_request": True,
        }
        host_list = BkApi.bulk_list_biz_hosts(params)
        return host_list

    def transfer_node(self, node_list: list):
        params = {
            "bk_biz_id": self.bk_biz_id,
            "fields": self.fields,
            "bk_set_ids": [],
            "bk_module_ids": [],
            "no_request": True,
        }
        for node in node_list:
            if node["object_id"] == ObjectType.BIZ.value:
                params.pop("bk_set_ids")
                params.pop("bk_module_ids")
                break
            if node["object_id"] == ObjectType.SET.value:
                params["bk_set_ids"].append(node["instance_id"])
                continue
            if node["object_id"] == ObjectType.MODULE.value:
                params["bk_module_ids"].append(node["instance_id"])
                continue
        host_list = BkApi.bulk_list_biz_hosts(params)
        return host_list

    def transfer_service_template(self, service_template_list: list):
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_service_template_ids": [i["id"] for i in service_template_list],
            "fields": self.fields,
            "no_request": True,
        }
        host_list = BkApi.bulk_find_host_by_service_template(params)
        return host_list

    def transfer_set_template(self, set_template_list: list):
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_set_template_ids": [i["id"] for i in set_template_list],
            "fields": self.fields,
            "no_request": True,
        }
        host_list = BkApi.bulk_find_host_by_set_template(params)
        return host_list

    def transfer_dynamic_group(self, dynamic_group_list: list):
        params_list = [{"dynamic_group_id": i["id"]} for i in dynamic_group_list]
        host_list = request_multi_thread(
            func=self._get_dynamic_group_host, params_list=params_list, get_data=lambda x: x
        )
        return host_list

    def _get_dynamic_group_host(self, dynamic_group_id: dict):
        host_list = BkApi.bulk_execute_dynamic_group(
            {"bk_biz_id": self.bk_biz_id, "id": dynamic_group_id, "fields": self.fields, "no_request": True}
        )
        return host_list
