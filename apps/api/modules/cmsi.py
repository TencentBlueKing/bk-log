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

from config.domains import CMSI_APIGATEWAY_ROOT_V2
from apps.api.base import DataAPI
from apps.api.modules.utils import add_esb_info_before_request


def before_send_cmsi_api(params):
    receivers = params.pop("receivers", [])
    if "receiver__username" not in params:
        if isinstance(receivers, list):
            params["receiver__username"] = ",".join(receivers)
        elif isinstance(receivers, str):
            params["receiver__username"] = receivers
    return add_esb_info_before_request(params)


def before_send_cmsi_wechat(params):
    params = before_send_cmsi_api(params)
    if "content" in params:
        params["data"] = {
            "message": params.pop("content", ""),
            "heading": params.pop("title", "") or params.pop("heading", ""),
        }
    return add_esb_info_before_request(params)


def before_send_cmsi_voice_msg(params):
    params = before_send_cmsi_api(params)
    if "content" in params:
        params["auto_read_message"] = params["content"]
    return add_esb_info_before_request(params)


class _CmsiApi:
    MODULE = _("CMSI")

    def __init__(self):
        self.send_mail = DataAPI(
            method="POST",
            url=CMSI_APIGATEWAY_ROOT_V2 + "send_mail/",
            module=self.MODULE,
            description="发送邮件",
            before_request=before_send_cmsi_api,
        )
        self.send_msg = DataAPI(
            method="POST",
            url=CMSI_APIGATEWAY_ROOT_V2 + "send_msg/",
            module=self.MODULE,
            description="通用消息发送",
            before_request=before_send_cmsi_api,
        )
        self.send_sms = DataAPI(
            method="POST",
            url=CMSI_APIGATEWAY_ROOT_V2 + "send_sms/",
            module=self.MODULE,
            description="发送短信",
            before_request=before_send_cmsi_api,
        )
        self.send_voice_msg = DataAPI(
            method="POST",
            url=CMSI_APIGATEWAY_ROOT_V2 + "send_voice_msg/",
            module=self.MODULE,
            description="公共语音通知",
            before_request=before_send_cmsi_voice_msg,
        )
        self.send_weixin = DataAPI(
            method="POST",
            url=CMSI_APIGATEWAY_ROOT_V2 + "send_weixin",
            module=self.MODULE,
            description="发送微信消息",
            before_request=before_send_cmsi_wechat,
        )
        self.get_msg_type = DataAPI(
            method="GET",
            url=CMSI_APIGATEWAY_ROOT_V2 + "get_msg_type/",
            module=self.MODULE,
            description="查询消息发送类型",
            before_request=add_esb_info_before_request,
        )


CmsiApi = _CmsiApi()
