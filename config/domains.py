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

from apps.utils.function import ignored
from config.env import load_domains

API_ROOTS = [
    # 蓝鲸平台模块域名
    "BK_PAAS_APIGATEWAY_ROOT",
    "BK_PAAS_V3_APIGATEWAY_ROOT",
    "CC_APIGATEWAY_ROOT_V2",
    "GSE_APIGATEWAY_ROOT_V2",
    "GSE_APIGATEWAY_ROOT_V3",
    "MONITOR_APIGATEWAY_ROOT",
    "BCS_CC_APIGATEWAY_ROOT",
    "USER_MANAGE_APIGATEWAY_ROOT",
    # 数据平台模块域名
    "ACCESS_APIGATEWAY_ROOT",
    "AUTH_APIGATEWAY_ROOT",
    "DATAQUERY_APIGATEWAY_ROOT",
    "DATABUS_APIGATEWAY_ROOT",
    "STOREKIT_APIGATEWAY_ROOT",
    "META_APIGATEWAY_ROOT",
    "RESOURCE_CENTER_APIGATEWAY_ROOT",
    # 节点管理
    "BK_NODE_APIGATEWAY_ROOT",
    # LOG_SEARCH
    "LOG_SEARCH_APIGATEWAY_ROOT",
    # IAM
    "IAM_APIGATEWAY_ROOT_V2",
    # ITSM
    "ITSM_APIGATEWAY_ROOT_V2",
    # CMSI
    "CMSI_APIGATEWAY_ROOT_V2",
    # JOB
    "JOB_APIGATEWAY_ROOT_V2",
    # JOBV3
    "JOB_APIGATEWAY_ROOT_V3",
    "BK_SSM_ROOT",
    # BCS
    "BCS_APIGATEWAY_ROOT",
    # AIOPS
    "AIOPS_APIGATEWAY_ROOT",
    # DATAFLOW
    "DATAFLOW_APIGATEWAY_ROOT",
    # AIOPS modules
    "AIOPS_MODEL_APIGATEWAY_ROOT",
    # Wework api
    "WEWORK_APIGATEWAY_ROOT",
]

env_domains = load_domains(settings)
for _root in API_ROOTS:
    with ignored(Exception):
        locals()[_root] = env_domains.get(_root, "")

__all__ = API_ROOTS
