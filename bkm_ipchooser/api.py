# -*- coding: utf-8 -*-
import abc

from django.conf import settings
from django.utils.module_loading import import_string


class AbstractBkApi(metaclass=abc.ABCMeta):
    @staticmethod
    def search_cloud_area(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def search_business(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def search_biz_inst_topo(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def get_biz_internal_module(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def find_host_topo_relation(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def list_biz_hosts(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def list_host_total_mainline_topo(params: dict = None):
        raise NotImplementedError

    @staticmethod
    def get_agent_status(params: dict = None):
        """
        GSE1.0, 查询主机agent状态, bk_cloud_id:ip为唯一标识版本
        params:
            hosts: List[Dict[str, Any]], [{"bk_cloud_id": 0, "ip": ""]}, 云区域ID和IP
        """
        raise NotImplementedError

    @staticmethod
    def get_agent_status_v2(params: dict = None):
        """
        GSE2.0, 查询主机agent状态, bk_agent_id为唯一标识版本
        params:
            agent_id_list: List[str], ["010000000000001"] 主机agent_id列表
        """
        raise NotImplementedError

    @staticmethod
    def list_service_template(params: dict = None):
        """查询服务模板"""
        raise NotImplementedError

    @staticmethod
    def list_set_template(params: dict = None):
        """查询集群模板"""
        raise NotImplementedError

    @staticmethod
    def search_set(params: dict = None):
        """查询集群"""
        raise NotImplementedError

    @staticmethod
    def search_module(params: dict = None):
        """查询模块"""
        raise NotImplementedError

    @staticmethod
    def search_dynamic_group(params: dict = None):
        """查询动态分组"""
        raise NotImplementedError

    @staticmethod
    def execute_dynamic_group(params: dict = None):
        """执行动态分组"""
        raise NotImplementedError

    @staticmethod
    def find_host_by_service_template(params: dict = None):
        """分页查询服务模板的主机"""
        raise NotImplementedError

    @staticmethod
    def find_host_by_set_template(params: dict = None):
        """分页查询集群模板的主机"""
        raise NotImplementedError

    @staticmethod
    def find_topo_node_paths(params: dict = None):
        """查询拓扑节点所在的拓扑路径"""
        raise NotImplementedError

    @staticmethod
    def list_service_category(params: dict = None):
        """查询服务分类列表"""
        raise NotImplementedError


class BkApiProxy:
    def __init__(self):
        self._api = None

    def __getattr__(self, action):
        if self._api is None:
            self.init_api()
        func = getattr(self._api, action)
        return func

    def init_api(self):
        api_class = getattr(settings, "BKM_IPCHOOSER_BKAPI_CLASS", "bkm_ipchooser.api.AbstractBkApi")
        self._api = import_string(api_class)


BkApi: AbstractBkApi = BkApiProxy()
