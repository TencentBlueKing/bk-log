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
from collections import defaultdict
from typing import List

import arrow

from django.utils.translation import ugettext_lazy as _
from apps.log_trace.constants import TraceProto
from apps.log_trace.exceptions import TraceIDNotExistsException
from apps.log_trace.handlers.proto.proto import Proto
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery
from apps.utils.local import get_local_param
from apps.utils.time_handler import generate_time_range

SCATTER_TEMPLATE = [
    {"label": _("成功"), "pointBackgroundColor": "#45E35F", "borderColor": "#45E35F", "pointRadius": 5, "data": []},
    {"label": _("失败"), "pointBackgroundColor": "#FB9C9C", "borderColor": "#FB9C9C", "pointRadius": 5, "data": []},
]


class LogTrace(Proto):
    TAGS_FIELD = "tags"
    SERVICE_NAME_FIELD = "tags.local_service"
    OPERATION_NAME_FIELD = "operationName"
    TRACE_ID_FIELD = "traceID"
    TRACES_ADDITIONS = {
        "operation": {"field": "operationName", "method": "is"},
        "service": {"field": "tags.local_service", "method": "is"},
        "maxDuration": {"method": "gte", "field": "duration"},
        "minDuration": {"method": "lte", "field": "duration"},
    }

    TYPE = TraceProto.LOG.value
    TRACE_PLAN = {
        "trace_type": "log",
        "additions": [
            {
                "fields_alias": _("场景"),
                "field_name": "tags.scene",
                "show_type": "select",
                "display": True,
                "tips": _("请选择"),
            },
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
            {
                "fields_alias": _("返回码"),
                "field_name": "tags.result_code",
                "show_type": "text",
                "display": True,
                "tips": "0",
            },
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

    DISPLAY_FIELDS = [
        "traceID",
        "tags.local_service",
        "operationName",
        "dtEventTimeStamp",
        "duration",
        "tags.result_code",
        "tags.error",
    ]

    MUST_MATCH_FIELDS = {
        "parentSpanID": ["keyword"],
        "spanID": ["keyword"],
        "traceID": ["keyword"],
        "operationName": ["keyword"],
        "duration": ["long", "int", "float"],
        "startTime": ["date", "long"],
    }

    def trace_id(self, index_set_id: int, data: dict) -> dict:
        start_time = arrow.get(data.get("startTime")[0:10]).shift(days=-1)
        query_data = {
            "addition": [
                {"key": "traceID", "method": "is", "value": data["traceID"], "condition": "and", "type": "field"}
            ],
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": start_time.shift(days=2).strftime("%Y-%m-%d %H:%M:%S"),
            "search_type": "trace_detail",
            "size": self.TRACE_SIZE,
        }

        search_handler = SearchHandlerEsquery(index_set_id, query_data, can_highlight=False)
        result: dict = search_handler.search(search_type=None)
        if not result["total"]:
            raise TraceIDNotExistsException()
        result["list"] = sorted(result["list"], key=lambda x: x["startTime"])
        result["tree"] = self.result_to_tree(result)
        return result

    @classmethod
    def result_to_tree(cls, result) -> dict:
        result_list: list = result.get("list", [])
        return cls.build_tree(result_list)

    @classmethod
    def build_tree(cls, nodes):
        if not nodes:
            return nodes
        first_root, *_ = nodes
        cls.update_node(first_root)
        nodes.remove(first_root)
        return cls._build_tree(nodes, first_root)

    @classmethod
    def _insert_children(cls, childrens: List[dict], nodes):
        for children in childrens:
            if "children" not in children:
                cls.update_node(children)

            child_nodes = [
                node for node in nodes if node.get("parentSpanID", "parentSpanID") == children.get("spanID", "spanID")
            ]
            for c_node in child_nodes:
                cls.update_node(c_node)
                children["children"].append(c_node)
                nodes.remove(c_node)
            cls._insert_children(children["children"], nodes)

    @classmethod
    def _build_tree(cls, nodes: List[dict], cur_node: dict):
        """
        从当前节点cur_node开始，找出父子关系，然后返回整颗树的根节点
        """
        # 找到子节点
        cls._insert_children([cur_node], nodes)

        # 找到父节点
        parent_nodes = [
            node for node in nodes if cur_node.get("parentSpanID", "parentSpanID") == node.get("spanID", "spanID")
        ]
        for p_node in parent_nodes:
            cls.update_node(p_node)
            p_node["children"].append(cur_node)
            nodes.remove(p_node)

        # 父节点继续往上查找父父节点，直到root根节点 (这里父节点只会有一个，所以递归遍历第0个即可)
        return cls._build_tree(nodes, parent_nodes[0]) if parent_nodes else cur_node

    @classmethod
    def update_node(cls, child: dict) -> dict:
        child.update(
            {
                "group": child.get("spanID", ""),
                "from": child.get("startTime", 0),
                "to": child.get("startTime", 0) + child.get("duration", 0),
                "unit": "ms",
                "parentSpanID": child.get("parentSpanID", ""),
                "children": [],
            }
        )
        return child

    def search(self, index_set_id: int, data: dict) -> dict:
        data.update({"collapse": {"field": "traceID"}})
        search_handler = SearchHandlerEsquery(index_set_id, data, can_highlight=False)
        return search_handler.search(search_type="trace")

    def scatter(self, index_set_id: int, data: dict):
        data.update({"search_type": "trace_scatter"})
        search_handler = SearchHandlerEsquery(index_set_id, data)
        result: dict = search_handler.search(search_type=None)
        scatter_list: list = self.result_to_scatter(result)
        return {"scatter": scatter_list}

    @classmethod
    def result_to_scatter(cls, result) -> list:
        scatter_label_true_list: list = SCATTER_TEMPLATE[0]["data"]
        scatter_label_false_list: list = SCATTER_TEMPLATE[1]["data"]
        result_list: list = result.get("list", [])
        for item in result_list:
            tmp_dict: dict = {}
            tag = item.get("tag", None)
            if tag:
                tmp_dict.update(
                    {
                        "x": cls.mills_to_timestamp(item.get("startTime", 0)),
                        "y": item.get("duration", 0),
                        "traceID": item.get("traceID", ""),
                        "spanID": item.get("spanID", ""),
                        "startTime": item.get("startTime", ""),
                        "duration": item.get("duration", 0),
                        "error": tag.get("error", False),
                        "result_code": item.get("result_code", 0),
                    }
                )

                if tag.get("error", None) is True:
                    scatter_label_true_list.append(tmp_dict)
                    continue
                if tag.get("error", None) is False:
                    scatter_label_false_list.append(tmp_dict)
        return SCATTER_TEMPLATE

    @classmethod
    def mills_to_timestamp(cls, mills: int) -> str:
        seconds = int(mills / 1000)
        d1 = arrow.get(seconds)
        time_format_str = d1.to(get_local_param("time_zone")).format("YYYY-MM-DD HH:mm:ss")
        return time_format_str

    def traces(self, index_set_id, params):
        result = super(LogTrace, self).traces(index_set_id, params)
        trace_ids = [trace[self.TRACE_ID_FIELD] for trace in result.get("list", [])]
        if not trace_ids:
            return []
        search_dict = {
            "start_time": params["start"] / 1000000,
            "end_time": params["end"] / 1000000,
            "addition": [
                {
                    "key": self.TRACE_ID_FIELD,
                    "method": "is one of",
                    "value": ",".join(trace_ids),
                    "condition": "and",
                    "type": "field",
                }
            ],
            "begin": 0,
            "size": 9999,
            "keyword": "*",
            "time_range": "customized",
        }
        result = SearchHandlerEsquery(index_set_id, search_dict).search()
        return self._transform_to_jaeger(result.get("list", []))

    def trace_detail(self, index_set_id, trace_id):
        start_time, end_time = generate_time_range("36m", "", "", get_local_param("time_zone"))
        search_dict = {
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "addition": [{"key": self.TRACE_ID_FIELD, "method": "is", "value": trace_id, "condition": "and"}],
            "begin": 0,
            "size": self.TRACE_SIZE,
            "keyword": "*",
            "time_range": "customized",
        }

        result = SearchHandlerEsquery(index_set_id, search_dict).search()
        return self._transform_to_jaeger(result.get("list", []))

    def _transform_to_jaeger(self, spans):
        jaeger_traces = defaultdict(lambda: {"spans": [], "traceID": ""})
        for span in spans:
            trace_id = span[self.TRACE_ID_FIELD]
            jaeger_traces[trace_id]["traceID"] = trace_id
            jaeger_traces[trace_id]["spans"].append(
                {
                    "traceID": trace_id,
                    "spanID": span["spanID"],
                    "duration": span["duration"],
                    "references": self._transform_to_refs(span),
                    "flags": 0,
                    "logs": [],
                    "operationName": span["operationName"],
                    "startTime": span["startTime"] * 1000,
                    "tags": self._transform_to_tags(span.get("tags", {})),
                    "processID": "",
                },
            )
        return [
            {**trace, "processes": {"": {"serviceName": "", "tags": []}}} for trace_id, trace in jaeger_traces.items()
        ]

    def _transform_to_tags(self, attributes):
        return [{"key": key, "value": value, "type": "string"} for key, value in attributes.items()]

    def _transform_to_refs(self, span):
        refs = []
        if span.get("parentSpanID"):
            refs.append({"refType": "CHILD_OF", "spanID": span["parentSpanID"], "traceID": span[self.TRACE_ID_FIELD]})
        return refs
