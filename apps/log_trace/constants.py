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
from apps.utils import ChoicesEnum


class TraceProto(ChoicesEnum):
    LOG = "log"
    OTLP = "otlp"

    _choices_labels = (
        (LOG, _("日志平台协议")),
        (OTLP, _("opentelemetry协议")),
    )


TIME_DIMENSION_VALUE = 1
FIELDS_SCOPE_VALUE = ["trace", "trace_detail", "trace_detail_log"]


class TraceIndexLinkOperation(ChoicesEnum):
    LINK = "link"
    UNLINK = "unlink"

    _choices_labels = ((LINK, _("关联")), (UNLINK, _("取消关联")))


TRACE_MAPPING = [
    {
        "field_name": "traceID",
        "field_type": "string",
        "tag": "dimension",
        "description": _("traceID"),
        "option": {"es_type": "keyword"},
    },
    {
        "field_name": "spanID",
        "field_type": "string",
        "tag": "dimension",
        "description": _("spanID"),
        "option": {"es_type": "keyword"},
    },
    {
        "field_name": "operationName",
        "field_type": "string",
        "tag": "dimension",
        "description": _("SPAN"),
        "option": {"es_type": "keyword"},
    },
    {
        "field_name": "startTime",
        "field_type": "string",
        "tag": "dimension",
        "description": _("开始时间"),
        "option": {"es_type": "date"},
    },
    {
        "field_name": "duration",
        "field_type": "integer",
        "tag": "metric",
        "description": _("耗时"),
        "option": {"es_type": "integer"},
    },
    {
        "field_name": "tag",
        "field_type": "string",
        "tag": "dimension",
        "description": "tags",
        "option": {
            "es_type": "object",
            "fields": [
                {"field_name": "scene", "description": _("场景")},
                {"field_name": "local_service", "description": _("服务")},
                {"field_name": "return_code", "description": _("返回码")},
                {"field_name": "error", "description": _("状态")},
            ],
        },
    },
    {
        "field_name": "log",
        "field_type": "string",
        "tag": "metric",
        "description": _("日志"),
        "option": {"es_type": "text"},
    },
    {
        "field_name": "flags",
        "field_type": "integer",
        "tag": "dimension",
        "description": "flags",
        "option": {"es_type": "integer"},
    },
    {
        "field_name": "dtEventTimeStamp",
        "field_type": "integer",
        "tag": "dimension",
        "description": _("数据时间"),
        "option": {"es_type": "date"},
    },
]


class MetricTypeEnum(ChoicesEnum):
    """
    es 指标聚合
    """

    AVG = "avg"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    CARDINALITY = "cardinality"
    STATS = "stats"

    _choices_labels = (
        (AVG, _("平均聚合")),
        (MAX, _("最大聚合")),
        (MIN, _("最小聚合")),
        (SUM, _("总和")),
        (CARDINALITY, _("基数聚合")),
        (STATS, _("统计汇总")),
    )
