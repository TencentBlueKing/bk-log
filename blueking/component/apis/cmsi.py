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
from ..base import ComponentAPI
from django.utils.translation import ugettext_lazy as _


class CollectionsCMSI(object):
    """Collections of CMSI APIS"""

    def __init__(self, client):
        self.client = client

        self.get_msg_type = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/cmsi/get_msg_type/",
            description=_("查询消息发送类型"),
        )
        self.send_mail = ComponentAPI(
            client=self.client, method="POST", path="/api/c/compapi{bk_api_ver}/cmsi/send_mail/", description=_("发送邮件")
        )
        self.send_mp_weixin = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/cmsi/send_mp_weixin/",
            description=_("发送公众号微信消息"),
        )
        self.send_msg = ComponentAPI(
            client=self.client, method="POST", path="/api/c/compapi{bk_api_ver}/cmsi/send_msg/", description=_("通用消息发送")
        )
        self.send_qy_weixin = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/cmsi/send_qy_weixin/",
            description=_("发送企业微信"),
        )
        self.send_sms = ComponentAPI(
            client=self.client, method="POST", path="/api/c/compapi{bk_api_ver}/cmsi/send_sms/", description=_("发送短信")
        )
        self.send_voice_msg = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/cmsi/send_voice_msg/",
            description=_("公共语音通知"),
        )
        self.send_weixin = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/cmsi/send_weixin/",
            description=_("发送微信消息"),
        )
