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
from django.utils.translation import ugettext_lazy as _


from apps.api.base import DataAPI
from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user
from config.domains import DATABUS_APIGATEWAY_ROOT


class _BkDataDatabusApi:
    MODULE = _("计算平台总线模块")

    def __init__(self):
        self.get_config_db_list = DataAPI(
            method="GET",
            url=DATABUS_APIGATEWAY_ROOT + "data_storages/",
            module=self.MODULE,
            description=u"获取数据入库列表",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            cache_time=60,
        )

        self.get_cleans = DataAPI(
            method="GET",
            url=DATABUS_APIGATEWAY_ROOT + "cleans/",
            module=self.MODULE,
            description=u"获取清洗配置列表",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )


BkDataDatabusApi = _BkDataDatabusApi()
