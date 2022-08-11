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
from config.domains import BK_PAAS_APIGATEWAY_ROOT, BK_PAAS_V3_APIGATEWAY_ROOT


class _BKPAASApi:

    MODULE = _(u"PaaS平台")

    def __init__(self):
        self.get_app_info = DataAPI(
            method="GET",
            url=BK_PAAS_APIGATEWAY_ROOT + "get_app_info/",
            module=self.MODULE,
            description=u"获取app信息",
            before_request=add_esb_info_before_request,
        )

        # ####### 下面是apigw上的 PAAS V3 接口 ###########
        self.get_minimal_app_list = DataAPI(
            method="GET",
            url=BK_PAAS_V3_APIGATEWAY_ROOT + "bkapps/applications/lists/minimal/",
            module=self.MODULE,
            description=u"获取app信息",
            before_request=add_esb_info_before_request,
        )

        self.uni_apps_query_by_id = DataAPI(
            method="GET",
            url=BK_PAAS_V3_APIGATEWAY_ROOT + "system/uni_applications/query/by_id/",
            module=self.MODULE,
            description=u"通过app_id查看app信息",
            before_request=add_esb_info_before_request,
        )


BKPAASApi = _BKPAASApi()
