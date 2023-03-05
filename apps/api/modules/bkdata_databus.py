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
from config.domains import DATABUS_APIGATEWAY_ROOT


class _BkDataDatabusApi:
    MODULE = _("计算平台总线模块")

    def __init__(self):
        self.get_config_db_list = DataAPI(
            method="GET",
            url=DATABUS_APIGATEWAY_ROOT + "data_storages/",
            module=self.MODULE,
            description="获取数据入库列表",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            cache_time=60,
        )
        self.databus_data_storages_post = DataAPI(
            method="POST",
            url=DATABUS_APIGATEWAY_ROOT + "data_storages/",
            module=self.MODULE,
            description="创建入库",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            cache_time=60,
        )
        self.databus_data_storages_put = DataAPI(
            method="PUT",
            url=DATABUS_APIGATEWAY_ROOT + "data_storages/{result_table_id}/",
            module=self.MODULE,
            description="更新入库",
            url_keys=["result_table_id"],
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            cache_time=60,
        )

        self.get_cleans = DataAPI(
            method="GET",
            url=DATABUS_APIGATEWAY_ROOT + "cleans/",
            module=self.MODULE,
            description="获取清洗配置列表",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )
        self.databus_cleans_post = DataAPI(
            method="POST",
            url=DATABUS_APIGATEWAY_ROOT + "cleans/",
            module=self.MODULE,
            description="创建清洗配置",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )
        self.databus_cleans_put = DataAPI(
            method="PUT",
            url=DATABUS_APIGATEWAY_ROOT + "cleans/{processing_id}/",
            module=self.MODULE,
            url_keys=["processing_id"],
            description="更新清洗配置",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )
        self.post_tasks = DataAPI(
            method="POST",
            url=DATABUS_APIGATEWAY_ROOT + "tasks/",
            module=self.MODULE,
            description="创建清洗分发任务",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )
        self.delete_tasks = DataAPI(
            method="DELETE",
            url=DATABUS_APIGATEWAY_ROOT + "tasks/{result_table_id}/",
            module=self.MODULE,
            url_keys=["result_table_id"],
            description="停止清洗，分发任务",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
        )


BkDataDatabusApi = _BkDataDatabusApi()
