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
from apps.api.modules.utils import add_esb_info_before_request
from config.domains import GSE_APIGATEWAY_ROOT_V2, GSE_APIGATEWAY_ROOT_V3


def get_agent_status_before(params):
    hosts = [{"ip": ip_info["ip"], "bk_cloud_id": ip_info["plat_id"]} for ip_info in params["ip_infos"]]

    params = {
        "hosts": hosts,
    }
    params = add_esb_info_before_request(params)

    if settings.BK_SUPPLIER_ACCOUNT != "":
        params["bk_supplier_account"] = settings.BK_SUPPLIER_ACCOUNT
    return params


def get_agent_status_after(response_result):
    hosts = response_result.get("data", {})
    response_result["data"] = [
        {"ip": host["ip"], "plat_id": host["bk_cloud_id"], "status": host["bk_agent_alive"]} for host in hosts.values()
    ]
    return response_result


class _GseApi:
    MODULE = _("GSE管控平台")

    def __init__(self):
        self.get_agent_status_raw = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "get_agent_status",
            module=self.MODULE,
            description=_("获取agent状态(原始数据)"),
            before_request=add_esb_info_before_request,
            after_request=None,
        )
        self.get_agent_status_raw_v2 = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V3 + "api/v2/cluster/list_agent_state",
            module=self.MODULE,
            description=_("V2版本获取agent状态(原始数据)"),
            before_request=add_esb_info_before_request,
            after_request=None,
        )
        self.get_agent_status = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "get_agent_status",
            module=self.MODULE,
            description=_("获取agent状态"),
            before_request=get_agent_status_before,
            after_request=get_agent_status_after,
        )
        self.query_route = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "config_query_route",
            module=self.MODULE,
            description=_("查询数据路由配置信息"),
            before_request=add_esb_info_before_request,
            after_request=None,
        )
        self.query_stream_to = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "config_query_streamto",
            module=self.MODULE,
            description=_("查询数据入库消息队列或第三方平台的配置"),
            before_request=add_esb_info_before_request,
            after_request=None,
        )


GseApi = _GseApi()
