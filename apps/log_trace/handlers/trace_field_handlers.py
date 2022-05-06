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
import copy
from typing import List

from django.utils.translation import ugettext_lazy as _


TRACE_TYPE_AVAILABLE = ["log", "jaeger"]
TRACE_PRODUCE_FIELDS = [
    "traceID",
    "tags.local_service",
    "operationName",
    "dtEventTimeStamp",
    "duration",
    "tags.result_code",
    "tags.error",
]
TRACE_DETAIL_PRODUCE_FIELDS = ["tags.local_service", "spanID", "operationName", "tags.result_code"]
TRACE_DETAIL_LOG_FIELDS = ["tags.local_service", "operationName", "dtEventTimeStamp", "log"]
TRACE_NOT_EDITABLE_FIELDS = ["tags.local_service", "spanID", "operationName", "tags.result_code"]
TRACE_DESC_MAPPING = {
    "traceID": "traceID",
    "spanID": "spanID",
    "parentSpanID": "parentSpanID",
    "operationName": "Span",
    "startTime": _("开始时间"),
    "duration": _("耗时"),
    "tags.scene": _("场景"),
    "tags.local_service": _("服务"),
    "tags.result_code": _("返回码"),
    "tags.error": _("状态"),
    "log": _("日志"),
    "dtEventTimeStamp": _("开始时间"),
}
TRACE_SUGGEST_FIELD = {
    "tags.scene": ["keyword"],
    "tags.local_service": ["keyword"],
    "tags.result_code": ["long", "integer", "short"],
    "tags.error": ["boolean"],
}
LOG_FIELD_ADAPTER_META = {
    "traceID": ["keyword"],
    "spanID": ["keyword"],
    "operationName": ["keyword"],
    "parentSpanID": ["keyword"],
    "startTime": ["date", "long"],
    "duration": ["long", "float"],
}
JAEGER_FIELD_ADAPTER_META = {
    "duration": ["long"],
    "flags": ["integer"],
    "logs": ["nested"],
    "operationName": ["keyword"],
    "parentSpanID": ["keyword"],
    # {"process": [""]},
    "references": ["nested"],
    "spanID": ["keyword"],
    "startTime": ["long"],
    # jaeger 版本差异 startTimeMillis
    # "startTimeMillis": ["date"],
    # "tag",
    "tags": ["nested"],
    "traceID": ["keyword"],
}

TRACE_SHOW = ["additions", "advance_additions", "charts"]

LOG_TRACE_PLAN = {
    "trace_type": "log",
    "additions": [
        {"fields_alias": _("场景"), "field_name": "tags.scene", "show_type": "select", "display": True, "tips": _("请选择")},
        {
            "fields_alias": _("服务"),
            "field_name": "tags.local_service",
            "show_type": "select",
            "display": True,
            "tips": _("请选择"),
        },
        {
            "fields_alias": _("操作名"),
            "field_name": "operationName",
            "show_type": "select",
            "display": True,
            "tips": _("请选择"),
        },
    ],
    "advance_additions": [
        {
            "fields_alias": _("耗时min_max"),
            "field_name": "duration",
            "show_type": "duration",
            "display": True,
            "tips": "0",
        },
        {"fields_alias": _("返回码"), "field_name": "tags.result_code", "show_type": "text", "display": True, "tips": "0"},
    ],
    "charts": [
        {
            "chart_alias": "line",
            "chart_name": _("曲线图"),
            "field_name": "tags.result_code",
            "show_type": None,
            "display": True,
            "tips": _("返回码"),
        },
        {
            "chart_alias": "consuming",
            "chart_name": _("耗时图"),
            "field_name": "tags.scene",
            "show_type": None,
            "display": True,
            "tips": _("场景"),
        },
        {
            "chart_alias": "consuming",
            "chart_name": _("耗时图"),
            "field_name": "tags.local_service",
            "show_type": None,
            "display": True,
            "tips": _("服务"),
        },
    ],
    "chart_tree": {
        "chart_name": _("调用关系图"),
        "display_field": "operationName",
        "error_field": "tags.error",
        "span_width": 120,
        "show_type": None,
        "display": True,
        "tips": _("operationName调用关系"),
    },
}

JAEGER_TRACE_PLAN = {
    "trace_type": "jaeger",
    "additions": [
        {
            "fields_alias": _("服务"),
            "field_name": "process.serviceName",
            "show_type": "select",
            "display": True,
            "tips": _("请选择"),
        },
        {
            "fields_alias": _("操作名"),
            "field_name": "operationName",
            "show_type": "select",
            "display": True,
            "tips": _("请选择"),
        },
    ],
    "advance_additions": [
        {
            "fields_alias": _("耗时min_max"),
            "field_name": "duration",
            "show_type": "duration",
            "display": True,
            "tips": "0",
        },
        {"fields_alias": _("状态"), "field_name": "tag.error", "show_type": "text", "display": True, "tips": _("状态")},
    ],
    "charts": [
        {
            "chart_alias": "line",
            "chart_name": _("曲线图"),
            "field_name": "process.serviceName",
            "show_type": None,
            "display": True,
            "tips": _("服务"),
        },
    ],
    "chart_tree": {
        "chart_name": _("调用关系图"),
        "display_field": "operationName",
        "error_field": "tag.error",
        "span_width": 120,
        "show_type": None,
        "display": True,
        "tips": _("operationName调用关系"),
    },
}


class TraceFieldHandlers(object):
    def __init__(self):
        pass

    @classmethod
    def trace_field_update(cls, fields_list: list, scope: str = None) -> list:
        for _field in fields_list:
            field_name = _field.get("field_name", None)
            is_editable = _field.get("is_editable", True)
            if field_name:
                if scope in ["trace", "trace_detail", "trace_detail_log"]:
                    need_desc: str = TRACE_DESC_MAPPING.get(field_name, field_name)
                    if field_name in TRACE_NOT_EDITABLE_FIELDS:
                        is_editable: bool = False
                    # 其他逻辑可能设置不能编辑，不作处理
                    # else:
                    #     is_editable: bool = True
                    _field.update({"field_alias": need_desc, "description": need_desc, "is_editable": is_editable})
        return fields_list

    @classmethod
    def trace_field_pop_up(cls, display_field_list: list, scope: str) -> list:
        if scope == "trace":
            mark_list = TRACE_PRODUCE_FIELDS
        elif scope == "trace_detail":
            mark_list = TRACE_DETAIL_PRODUCE_FIELDS
        elif scope == "trace_detail_log":
            mark_list = TRACE_DETAIL_LOG_FIELDS
        else:
            return display_field_list

        copy_display_field_list: list = copy.deepcopy(display_field_list)
        final_list: list = []
        for item in mark_list:
            for v in copy_display_field_list:
                if item == v:
                    final_list.append(v)
                    display_field_list.remove(v)
        final_list = final_list + display_field_list
        return final_list

    @classmethod
    def get_trace_fieds(cls, final_fields_list, scope):
        final_field_names = [field["field_name"] for field in final_fields_list]
        display_fields = []
        if scope == "trace":
            display_fields = TRACE_PRODUCE_FIELDS
        elif scope == "trace_detail":
            display_fields = TRACE_DETAIL_PRODUCE_FIELDS
        elif scope == "trace_detail_log":
            display_fields = TRACE_DETAIL_LOG_FIELDS
        display_fields_list = [field for field in display_fields if field in final_field_names]

        # 调整final_fields_list显示
        for final_field in final_fields_list:
            field_name = final_field["field_name"]
            if field_name in display_fields_list:
                final_field["is_display"] = True
        return display_fields_list


class TraceMappingAdapter(object):
    def __init__(self):
        pass

    @classmethod
    def adapter(cls, fields_list: list) -> str:
        # get the first layer of the filed list
        fields_list_1st_layer: list = []
        fields_list_1st_layer_type: dict = {}
        for _field in fields_list:
            field_name = _field.get("field_name", None)
            field_type = _field.get("field_type", None)
            fields_list_1st_layer.append(field_name)
            fields_list_1st_layer_type.update({field_name: field_type})

        trace_mapping_struct_type = None
        # trace kind log adapter

        score_log = 0
        for k, v in LOG_FIELD_ADAPTER_META.items():
            require_type_list = v
            if k in fields_list_1st_layer:
                _field_type = fields_list_1st_layer_type.get(k, None)
                if _field_type in require_type_list:
                    score_log += 1
                else:
                    break
            else:
                break

        if score_log == len(LOG_FIELD_ADAPTER_META):
            trace_mapping_struct_type = "log"

        # trace kind jaeger adapter
        score_jaeger = 0
        for k, v in JAEGER_FIELD_ADAPTER_META.items():
            require_type_list = v
            if k in fields_list_1st_layer:
                _field_type = fields_list_1st_layer_type.get(k, None)
                if _field_type in require_type_list:
                    score_jaeger += 1
                else:
                    break
            else:
                break

        if score_jaeger == len(JAEGER_FIELD_ADAPTER_META):
            trace_mapping_struct_type = "jaeger"

        # trace kind zipkin adapter

        return trace_mapping_struct_type

    @classmethod
    def plan(cls, trace_mapping_struce_type) -> dict:
        if trace_mapping_struce_type == "log":
            return LOG_TRACE_PLAN

        if trace_mapping_struce_type == "jaeger":
            return JAEGER_TRACE_PLAN

        return LOG_TRACE_PLAN

    @classmethod
    def get_trace_plan(cls, field_result: list, scope: str):
        trace_plan = LOG_TRACE_PLAN
        if scope in ["trace", "trace_detail", "trace_detail_log"]:
            trace_mapping_struct_type: str = TraceMappingAdapter.adapter(field_result)
            trace_plan: dict = TraceMappingAdapter.plan(trace_mapping_struct_type)
            trace_plan = cls._deal_plan(trace_plan, field_result)
        return trace_plan

    @staticmethod
    def _deal_plan(trace_plan: dict, field_result: list):
        ret_plan = copy.deepcopy(trace_plan)
        fields = list(map(lambda v: v["field_name"], field_result))
        for show_type in TRACE_SHOW:
            show_list: List[dict] = ret_plan.get(show_type, [])
            remove_item = []
            for _show in show_list:
                if _show.get("field_name") not in fields:
                    remove_item.append(_show)
            list(map(lambda item: show_list.remove(item), remove_item))
        return ret_plan
