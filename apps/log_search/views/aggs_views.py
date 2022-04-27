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

from rest_framework import serializers
from rest_framework.response import Response

from apps.utils.drf import detail_route
from apps.generic import APIViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import InstanceActionPermission
from apps.log_search.handlers.search.aggs_handlers import AggsViewAdapter
from apps.log_trace.serializers import AggsTermsSerializer, DateHistogramSerializer


class AggsViewSet(APIViewSet):
    serializer_class = serializers.Serializer
    lookup_field = "index_set_id"

    def get_permissions(self):
        return [InstanceActionPermission([ActionEnum.SEARCH_LOG], ResourceEnum.INDICES)]

    @detail_route(methods=["POST"], url_path="aggs/terms")
    def terms(self, request, index_set_id=None):
        """
        @api {post} /search/index_set/$index_set_id/aggs/terms/ 02_Trace-terms聚合doc_count
        @apiName agg_all_trace_log
        @apiDescription 生成选项卡
        @apiGroup 17_Trace
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParam {Int} time_dimension 时间维度（默认最近1天，-1代表全量）
        @apiParam {Int} size 聚集大小 默认100
        @apiParam {String} time_range 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]
        @apiParam {String} keyword 搜索关键字
        @apiParam {Dict} order 排序 {"_count": "aes"} {"_count": "desc" }
        @apiParam {List} fields 需要聚合字段,需要请求的聚合字段doc_count,["tag.scenario", "tag.service", "operationname"]
        @apiParamExample {Json} 请求参数
        {
            "start_time": "2020-03-25 09:14:38",
            "end_time": "2020-03-26 09:14:38",
            "keyword": "*",
            "fields": ["tag.scenario", "tag.service"]
        }

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "aggs": {
                    "tag.scenario": [
                        ["a", 1],
                        ["b", 2],
                        ["d", 4]
                    ],
                    "tag.service": [
                        ["a", 1],
                        ["b", 2],
                        ["c", 4]
                    ]
                }
                "aggs_items": {
                    "tag.scenario" : ["a", "b", "d"],
                    "tag.service": ["a", "b", "c"]
                }
            },
            "result": true
        }
        """
        data = self.params_valid(AggsTermsSerializer)
        return Response(AggsViewAdapter().terms(index_set_id, data))

    @detail_route(methods=["POST"], url_path="aggs/date_histogram")
    def date_histogram(self, request, index_set_id=None):
        """
        @api {post} /search/index_set/$index_set_id/aggs/date_histogram/ 03_Trace-按照时间聚合
        @apiName date_agg_trace_log
        @apiDescription 生成时间线曲线图
        @apiGroup 17_Trace
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParam {String} time_range 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]
        @apiParam {List} fields  需要聚合字段 需要请求的聚合字段doc_count [{"term_filed": "tags.result_code"},
                        {"term_filed": "tags.local_service", "metric_type": "avg", "metric_field": "duration"}]
        @apiParam {String} interval 聚合周期，默认为"auto"，后台会具体调整
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} addition 搜索条件
        @apiParamExample {Json} 请求参数
        {
            "start_time": "2019-06-12 00:00:00",
            "end_time": "2019-06-12 11:11:11",
            "time_range": "customized"
            "fields": ["tag.result_code"],
            "keyword": "*",
            "addition": [
                {
                  "key": "tags.local_service",
                  "method": "is",
                  "value": "login_service",
                  "condition": "and", (默认不传是and，只支持and, or)
                  "type": "field" (默认field目前支持field，其他无效)
                },
                {
                  "key": "tag.scene",
                  "method": "is",
                  "value": "login",
                  "condition": "and", (默认不传是and，只支持and, or)
                  "type": "field" (默认field目前支持field，其他无效)
                },
                {
                  "key": "operationName",
                  "method": "is",
                  "value": "login",
                  "condition": "and", (默认不传是and，只支持and, or)
                  "type": "field" (默认field目前支持field，其他无效)
                },
            ],
        }

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "aggs": {
                    "tag.result_code": {
                        "labels": ["00:00", "00:01", "00:02"],
                        "datasets": [{
                            "label": 891,
                            "data": [{
                                    "label": "00:00",
                                    "value": 15,
                                    "count": 15
                                },
                                {
                                    "label": "00:01",
                                    "value": 9,
                                    "count": 9
                                },
                                {
                                    "label": "00:02",
                                    "value": 1,
                                    "count": 1
                                }
                            ]
                        }]
                    }
                }
            },
            "result": true
        }
        """
        data = self.params_valid(DateHistogramSerializer)
        return Response(AggsViewAdapter().date_histogram(index_set_id, data))
