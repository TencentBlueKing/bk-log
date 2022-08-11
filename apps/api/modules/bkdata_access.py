# -*- coding=utf-8 -*-
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

"""
Access 部署 + 采集模块
"""

from django.utils.translation import ugettext_lazy as _  # noqa

from apps.api.base import DataAPI  # noqa
from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user  # noqa
from config.domains import ACCESS_APIGATEWAY_ROOT  # noqa


class _BkDataAccessApi:
    MODULE = _("数据平台接入模块")

    def __init__(self):
        self.list_raw_data = DataAPI(
            method="GET",
            url=ACCESS_APIGATEWAY_ROOT + "rawdata/",
            module=self.MODULE,
            description="源数据列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.get_deploy_summary = DataAPI(
            method="GET",
            url=ACCESS_APIGATEWAY_ROOT + "deploy_plan/{raw_data_id}/",
            module=self.MODULE,
            description="查询部署计划",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            url_keys=["raw_data_id"],
            cache_time=60,
        )
        self.stop_collectorhub = DataAPI(
            method="POST",
            url=ACCESS_APIGATEWAY_ROOT + "collectorhub/{raw_data_id}/stop/",
            module=self.MODULE,
            description="停止单个采集器",
            before_request=add_esb_info_before_request_for_bkdata_user,
            url_keys=["raw_data_id"],
            after_request=None,
        )
        self.deploy_plan_post = DataAPI(
            method="POST",
            url=ACCESS_APIGATEWAY_ROOT + "deploy_plan/",
            module=self.MODULE,
            description="创建部署计划",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.deploy_plan_put = DataAPI(
            method="PUT",
            url=ACCESS_APIGATEWAY_ROOT + "deploy_plan/{raw_data_id}/",
            module=self.MODULE,
            description="更新部署计划",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            url_keys=["raw_data_id"],
        )


BkDataAccessApi = _BkDataAccessApi()
