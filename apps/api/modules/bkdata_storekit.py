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
from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user
from config.domains import STOREKIT_APIGATEWAY_ROOT


class _BkDataStorekitApi:
    MODULE = _("数据平台存储模块")

    def __init__(self):
        self.get_schema_and_sql = DataAPI(
            url=STOREKIT_APIGATEWAY_ROOT + "result_tables/{result_table_id}/schema_and_sql/",
            module=self.MODULE,
            method="GET",
            url_keys=["result_table_id"],
            description="查询结果表的表结构",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )
        self.get_cluster_config = DataAPI(
            url=STOREKIT_APIGATEWAY_ROOT + "storage_cluster_configs/{cluster_name}/",
            module=self.MODULE,
            method="GET",
            description="查询集群详情",
            before_request=add_esb_info_before_request_for_bkdata_user,
            url_keys=["cluster_name"],
        )
        self.storekit_es_route = DataAPI(
            url=STOREKIT_APIGATEWAY_ROOT + "es/route/",
            module=self.MODULE,
            method="GET",
            description="ES GET 请求转发",
            before_request=add_esb_info_before_request_for_bkdata_user,
        )


BkDataStorekitApi = _BkDataStorekitApi()
