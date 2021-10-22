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
from django.utils.translation import ugettext_lazy as _  # noqa
from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user  # noqa
from config.domains import DATAFLOW_APIGATEWAY_ROOT  # noqa
from apps.api.base import DataAPI  # noqa


class _BkDataDataFlowApi:
    MODULE = _("数据平台dataflow模块")

    def __init__(self):
        self.export_flow = DataAPI(
            method="GET",
            url=DATAFLOW_APIGATEWAY_ROOT + "/{flow_id}/export/",
            url_keys=["flow_id"],
            module=self.MODULE,
            description=u"导出flow",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.create_flow = DataAPI(
            method="POST",
            url=DATAFLOW_APIGATEWAY_ROOT + "/create/",
            module=self.MODULE,
            description=u"创建flow",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.start_flow = DataAPI(
            method="POST",
            url=DATAFLOW_APIGATEWAY_ROOT + "/{flow_id}/start/",
            module=self.MODULE,
            url_keys=["flow_id"],
            description=u"启动flow",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.stop_flow = DataAPI(
            method="POST",
            url=DATAFLOW_APIGATEWAY_ROOT + "/{flow_id}/stop/",
            module=self.MODULE,
            url_keys=["flow_id"],
            description=u"停止flow",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )


BkDataDataFlowApi = _BkDataDataFlowApi()
