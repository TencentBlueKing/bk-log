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
from apps.log_search.constants import CustomTypeEnum

CUSTOM_MAP = {}


def register(cls: "CustomMeta"):
    CUSTOM_MAP[cls.custom_type] = cls
    return cls


def get_custom(custom_type: str):
    return CUSTOM_MAP.get(custom_type, Log)


class CustomMeta:
    custom_type = None
    etl_params = None
    etl_config = None
    fields = None

    @staticmethod
    def after_hook(collector_config):
        pass

    @staticmethod
    def after_etl_hook(collector_config):
        pass


@register
class Log(CustomMeta):
    custom_type = CustomTypeEnum.LOG.value
    etl_params = {"retain_original_text": True, "separator_regexp": "", "separator": ""}
    etl_config = "bk_log_text"
    fields = []


@register
class OtlpLog(CustomMeta):
    custom_type = CustomTypeEnum.OTLP_LOG.value
    etl_params = {"retain_original_text": False}
    etl_config = "bk_log_json"
    fields = [
        {
            "field_name": "time_unix",
            "field_type": "long",
            "alias_name": "",
            "description": "",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": False,
            "is_time": True,
            "option": {"time_zone": 8, "time_format": "epoch_micros"},
        },
        {
            "field_name": "logs_name",
            "field_type": "string",
            "alias_name": "",
            "description": "logs_name",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "span_id",
            "field_type": "string",
            "alias_name": "",
            "description": "span_id",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "trace_id",
            "field_type": "string",
            "alias_name": "",
            "description": "trace_id",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "attributes",
            "field_type": "object",
            "alias_name": "",
            "description": "attributes",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "body",
            "field_type": "string",
            "alias_name": "",
            "description": "body",
            "is_delete": False,
            "is_analyzed": True,
            "is_dimension": False,
            "is_time": False,
        },
        {
            "field_name": "flags",
            "field_type": "int",
            "alias_name": "",
            "description": "flags",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "severity_number",
            "field_type": "int",
            "alias_name": "",
            "description": "severity_number",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "severity_text",
            "field_type": "string",
            "alias_name": "",
            "description": "severity_text",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "resource",
            "field_type": "object",
            "alias_name": "",
            "description": "resource",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
    ]


@register
class OtlpTrace(CustomMeta):
    custom_type = CustomTypeEnum.OTLP_TRACE.value
    etl_params = {"retain_original_text": False}
    etl_config = "bk_log_json"
    fields = [
        {
            "field_name": "attributes",
            "field_type": "object",
            "alias_name": "",
            "description": "attributes",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "elapsed_time",
            "field_type": "long",
            "alias_name": "",
            "description": "elapsed_time",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "end_time",
            "field_type": "long",
            "alias_name": "",
            "description": "end_time",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": False,
            "is_time": True,
            "option": {"time_zone": 8, "time_format": "epoch_micros"},
        },
        {
            "field_name": "events",
            "field_type": "nested",
            "alias_name": "",
            "description": "events",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "kind",
            "field_type": "int",
            "alias_name": "",
            "description": "kind",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "links",
            "field_type": "nested",
            "alias_name": "",
            "description": "links",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "parent_span_id",
            "field_type": "string",
            "alias_name": "",
            "description": "parent_span_id",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "resource",
            "field_type": "object",
            "alias_name": "",
            "description": "resource",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "span_id",
            "field_type": "string",
            "alias_name": "",
            "description": "span_id",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "span_name",
            "field_type": "string",
            "alias_name": "",
            "description": "span_name",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "start_time",
            "field_type": "long",
            "alias_name": "",
            "description": "start_time",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "status",
            "field_type": "object",
            "alias_name": "",
            "description": "status",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "trace_id",
            "field_type": "string",
            "alias_name": "",
            "description": "trace_id",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
        {
            "field_name": "trace_state",
            "field_type": "string",
            "alias_name": "",
            "description": "trace_state",
            "is_delete": False,
            "is_analyzed": False,
            "is_dimension": True,
            "is_time": False,
        },
    ]

    @staticmethod
    def after_etl_hook(collector_config):
        from apps.log_search.models import LogIndexSet

        LogIndexSet.objects.filter(index_set_id=collector_config.index_set_id).update(is_trace_log=True)
