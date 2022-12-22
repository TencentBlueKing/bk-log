# -*- coding: utf-8 -*-

from apps.api import CCApi, GseApi
from bkm_ipchooser.api import AbstractBkApi


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
