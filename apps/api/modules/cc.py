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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.api.base import DataAPI
from apps.api.modules.utils import (
    add_esb_info_before_request,
    adapt_non_bkcc,
)
from config.domains import CC_APIGATEWAY_ROOT_V2


def get_supplier_account_before(params):
    params = add_esb_info_before_request(params)
    params = adapt_non_bkcc(params)
    if settings.BK_SUPPLIER_ACCOUNT != "":
        params["bk_supplier_account"] = settings.BK_SUPPLIER_ACCOUNT
    return params


def filter_bk_field_prefix_before(params):
    """
    剔除bk前缀之外的参数，有些CMDB接口会受到无关参数的干扰
    """
    params = get_supplier_account_before(params)
    filtered_params = {}
    for key, value in params.items():
        if key.startswith("bk_"):
            filtered_params[key] = value
    return filtered_params


class _CCApi:

    MODULE = _("配置平台")

    def __init__(self):
        self.get_app_list = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_business/",
            module=self.MODULE,
            description="查询业务列表",
            before_request=get_supplier_account_before,
            cache_time=60,
        )
        self.search_inst_by_object = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_inst_by_object/",
            module=self.MODULE,
            description="查询CC对象列表",
            before_request=get_supplier_account_before,
        )
        self.search_biz_inst_topo = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_biz_inst_topo/",
            module=self.MODULE,
            description="查询业务TOPO，显示各个层级",
            before_request=get_supplier_account_before,
        )
        self.search_module = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_module",
            module=self.MODULE,
            description="查询模块",
            before_request=get_supplier_account_before,
        )
        self.get_host_info = DataAPI(
            method="GET",
            url=CC_APIGATEWAY_ROOT_V2 + "search_module",
            module=self.MODULE,
            description="查询模块",
            before_request=get_supplier_account_before,
        )
        self.get_biz_internal_module = DataAPI(
            method="GET",
            url=CC_APIGATEWAY_ROOT_V2 + "get_biz_internal_module",
            module=self.MODULE,
            description="查询内部业务模块",
            before_request=get_supplier_account_before,
        )
        self.search_object_attribute = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_object_attribute",
            module=self.MODULE,
            description="查询对象属性",
            before_request=filter_bk_field_prefix_before,
        )
        self.list_biz_hosts = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_biz_hosts",
            module=self.MODULE,
            description="查询业务下的主机",
            before_request=get_supplier_account_before,
        )
        self.list_biz_hosts_topo = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_biz_hosts_topo",
            module=self.MODULE,
            description="查询业务下的主机和拓扑信息",
            before_request=get_supplier_account_before,
        )
        self.search_cloud_area = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_cloud_area",
            module=self.MODULE,
            description="查询云区域",
            before_request=get_supplier_account_before,
        )
        self.find_host_topo_relation = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_host_topo_relation",
            module=self.MODULE,
            description="获取主机与拓扑的关系",
            before_request=get_supplier_account_before,
        )
        self.search_set = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_set",
            module=self.MODULE,
            description="查询集群",
            before_request=get_supplier_account_before,
        )
        self.list_service_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_service_template",
            module=self.MODULE,
            description="获取服务模板列表",
            before_request=get_supplier_account_before,
        )
        self.list_set_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_set_template",
            module=self.MODULE,
            description="获取集群模板列表",
            before_request=get_supplier_account_before,
        )
        self.find_host_by_set_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_host_by_set_template",
            module=self.MODULE,
            description="查询集群模板下的主机",
            before_request=get_supplier_account_before,
        )
        self.find_host_by_service_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_host_by_service_template",
            module=self.MODULE,
            description="查询服务模板下的主机",
            before_request=get_supplier_account_before,
        )
        self.find_module_with_relation = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_module_with_relation",
            module=self.MODULE,
            description="根据条件查询业务下的模块",
            before_request=get_supplier_account_before,
        )
        self.search_dynamic_group = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_dynamic_group",
            module=self.MODULE,
            description="查询动态分组列表",
            before_request=get_supplier_account_before,
        )
        self.execute_dynamic_group = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "execute_dynamic_group",
            module=self.MODULE,
            description="根据指定动态分组规则查询获取数据",
            before_request=get_supplier_account_before,
        )
        self.find_host_by_topo = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_host_by_topo",
            module=self.MODULE,
            description="查询拓扑节点下的主机",
            before_request=get_supplier_account_before,
        )
        self.list_host_total_mainline_topo = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_host_total_mainline_topo",
            module=self.MODULE,
            description="查询主机及其对应拓扑",
            before_request=get_supplier_account_before,
        )
        self.find_topo_node_paths = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_topo_node_paths",
            module=self.MODULE,
            description="查询业务拓扑节点的拓扑路径",
            before_request=get_supplier_account_before,
        )
        self.list_service_category = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_service_category",
            module=self.MODULE,
            description="list_service_category",
            before_request=get_supplier_account_before,
        )

    def get_biz_location(self, *args, **kwargs):
        return []


CCApi = _CCApi()
