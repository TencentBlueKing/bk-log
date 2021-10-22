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

"""
API 统一调用模块，使用方式，举例
>>> from apps.api import BkDataQueryApi
>>> BkDataQueryApi.query({})
"""
from django.apps import AppConfig  # noqa
from django.utils.functional import SimpleLazyObject  # noqa
from django.utils.module_loading import import_string  # noqa


def new_api_module(module_name, api_name, module_dir="modules"):
    mod = "apps.api.{modules}.{mod}.{api}".format(modules=module_dir, mod=module_name, api=api_name)
    return import_string(mod)()


# 对请求模块设置懒加载机制，避免项目启动出现循环引用，或者 model 提前加载

# 蓝鲸平台模块域名
BKLoginApi = SimpleLazyObject(lambda: new_api_module("bk_login", "_BKLoginApi"))
BKPAASApi = SimpleLazyObject(lambda: new_api_module("bk_paas", "_BKPAASApi"))
CCApi = SimpleLazyObject(lambda: new_api_module("cc", "_CCApi"))
GseApi = SimpleLazyObject(lambda: new_api_module("gse", "_GseApi"))
JobApi = SimpleLazyObject(lambda: new_api_module("job", "_JobApi"))

# 数据平台模块域名
BkDataMetaApi = SimpleLazyObject(lambda: new_api_module("bkdata_meta", "_BkDataMetaApi"))
BkDataQueryApi = SimpleLazyObject(lambda: new_api_module("bkdata_query", "_BkDataQueryApi"))
BkDataDatabusApi = SimpleLazyObject(lambda: new_api_module("bkdata_databus", "_BkDataDatabusApi"))
BkDataAccessApi = SimpleLazyObject(lambda: new_api_module("bkdata_access", "_BkDataAccessApi"))
BkDataAuthApi = SimpleLazyObject(lambda: new_api_module("bkdata_auth", "_BkDataAuthApi"))
BkDataStorekitApi = SimpleLazyObject(lambda: new_api_module("bkdata_storekit", "_BkDataStorekitApi"))
TransferApi = SimpleLazyObject(lambda: new_api_module("transfer", "_TransferApi"))

OldMonitorApi = SimpleLazyObject(lambda: new_api_module("old_monitor", "_OldMonitorApi"))
MonitorApi = SimpleLazyObject(lambda: new_api_module("monitor", "_MonitorApi"))

# CMSI
CmsiApi = SimpleLazyObject(lambda: new_api_module("cmsi", "_CmsiApi"))


# 节点管理
NodeApi = SimpleLazyObject(lambda: new_api_module("bk_node", "_BKNodeApi"))

# ESB
EsbApi = SimpleLazyObject(lambda: new_api_module("esb", "_ESBApi"))

# LOG SEARCH
BkLogApi = SimpleLazyObject(lambda: new_api_module("bk_log", "_BkLogApi"))

# Grafana
GrafanaApi = SimpleLazyObject(lambda: new_api_module("grafana", "_GrafanaApi"))

# IAM
IAMApi = SimpleLazyObject(lambda: new_api_module("iam", "_IAMApi"))

# ITSM
BkItsmApi = SimpleLazyObject(lambda: new_api_module("bk_itsm", "_BkItsm"))

PaasCcApi = SimpleLazyObject(lambda: new_api_module("paascc", "_PaasCcApi"))

# AIOPS
BkDataAIOPSApi = SimpleLazyObject(lambda: new_api_module("bkdata_aiops", "_BkDataAIOPSApi"))

# dataflow
BkDataDataFlowApi = SimpleLazyObject(lambda: new_api_module("bkdata_dataflow", "_BkDataDataFlowApi"))

__all__ = [
    "BKLoginApi",
    "BKPAASApi",
    "CCApi",
    "TransferApi",
    "JobApi",
    "GseApi",
    "BkDataMetaApi",
    "BkDataQueryApi",
    "BkDataAuthApi",
    "CmsiApi",
    "BkDataStorekitApi",
    "NodeApi",
    "BkLogApi",
    "BkDataDatabusApi",
    "BkDataAccessApi",
    "OldMonitorApi",
    "MonitorApi",
    "GrafanaApi",
    "IAMApi",
    "PaasCcApi",
    "BkItsmApi",
    "BkDataAIOPSApi",
    "BkDataDataFlowApi",
]


class ApiConfig(AppConfig):
    name = "apps.api"
    verbose_name = "ESB_API"

    def ready(self):
        pass


default_app_config = "apps.api.ApiConfig"
