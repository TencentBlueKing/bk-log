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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.api.base import DataAPI
from apps.api.modules.utils import add_esb_info_before_request
from config.domains import LOG_SEARCH_APIGATEWAY_ROOT


class _BkLogApi:
    MODULE = _("log_search元数据")

    def __init__(self):
        self.search = DataAPI(
            method="POST",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_search/",
            module=self.MODULE,
            description=_("查询数据"),
            before_request=add_esb_info_before_request,
            default_timeout=settings.ES_QUERY_TIMEOUT,
        )

        self.mapping = DataAPI(
            method="POST",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_mapping/",
            module=self.MODULE,
            description=_("拉取索引mapping"),
            before_request=add_esb_info_before_request,
        )

        self.dsl = DataAPI(
            method="POST",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_dsl/",
            module=self.MODULE,
            description=_("查询数据DSL模式"),
            before_request=add_esb_info_before_request,
        )

        self.scroll = DataAPI(
            method="POST",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_scroll/",
            module=self.MODULE,
            description=_("scroll滚动查询"),
            before_request=add_esb_info_before_request,
        )

        self.indices = DataAPI(
            method="GET",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_indices/",
            module=self.MODULE,
            description=_("获取索引列表"),
            before_request=add_esb_info_before_request,
        )

        self.cluster = DataAPI(
            method="GET",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_cluster/",
            module=self.MODULE,
            description=_("获取集群信息"),
            before_request=add_esb_info_before_request,
        )

        self.tail = DataAPI(
            method="GET",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "databus_collectors/{collector_config_id}/tail/",
            module=self.MODULE,
            url_keys=["collector_config_id"],
            description=_("获取kafka采样"),
            before_request=add_esb_info_before_request,
        )
        self.es_route = DataAPI(
            method="GET",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "esquery_es_route/",
            module=self.MODULE,
            description=_("es请求转发"),
            before_request=add_esb_info_before_request,
        )

        self.connectivity_detect = DataAPI(
            method="POST",
            url=LOG_SEARCH_APIGATEWAY_ROOT + "databus_storage/connectivity_detect/",
            module=self.MODULE,
            description=_("连通性测试"),
            before_request=add_esb_info_before_request,
        )


BkLog = _BkLogApi()
