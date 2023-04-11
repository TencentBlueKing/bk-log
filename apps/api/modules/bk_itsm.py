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

from django.utils.translation import ugettext_lazy as _

from apps.api.base import DataAPI
from apps.api.modules.utils import add_esb_info_before_request
from config.domains import ITSM_APIGATEWAY_ROOT_V2


class _BkItsm(object):
    MODULE = _("ITSM服务流程管理")

    def __init__(self):
        self.create_ticket = DataAPI(
            method="POST",
            url=ITSM_APIGATEWAY_ROOT_V2 + "create_ticket/",
            module=self.MODULE,
            description="创建单据接口",
            before_request=add_esb_info_before_request,
        )
        self.callback_failed_ticket = DataAPI(
            method="POST",
            url=ITSM_APIGATEWAY_ROOT_V2 + "callback_failed_ticket/",
            module=self.MODULE,
            description="回调失败的单号",
            before_request=add_esb_info_before_request,
        )
        self.get_ticket_status = DataAPI(
            method="POST",
            url=ITSM_APIGATEWAY_ROOT_V2 + "get_ticket_status/",
            module=self.MODULE,
            description="单据状态查询，支持根据单号查询单据的状态（携带基本信息）",
            before_request=add_esb_info_before_request,
        )
        self.token_verify = DataAPI(
            method="POST",
            url=ITSM_APIGATEWAY_ROOT_V2 + "token/verify/",
            module=self.MODULE,
            description="token校验接口",
            before_request=add_esb_info_before_request,
        )
        self.ticket_approval_result = DataAPI(
            method="POST",
            url=ITSM_APIGATEWAY_ROOT_V2 + "ticket_approval_result/",
            module=self.MODULE,
            description="单据详情查询，支持根据单号查询单据的详情（携带基本信息和提单信息）",
            before_request=add_esb_info_before_request,
        )
        self.get_ticket_info = DataAPI(
            method="POST",
            url=ITSM_APIGATEWAY_ROOT_V2 + "get_ticket_info/",
            module=self.MODULE,
            description="单据详情查询，支持根据单号查询单据的详情（携带基本信息和提单信息）",
            before_request=add_esb_info_before_request,
        )
        self.get_services = DataAPI(
            method="GET",
            url=ITSM_APIGATEWAY_ROOT_V2 + "get_services/",
            module=self.MODULE,
            description="服务列表查询，支持根据指定的目录查询服务列表",
            before_request=add_esb_info_before_request,
        )


BkItsm = _BkItsm()
