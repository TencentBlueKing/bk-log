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

import sys
import arrow
import humanize
import datetime as dt
from django.utils.translation import ugettext_lazy as _
from apps.log_trace.constants import TraceProto
from apps.log_trace.exceptions import TraceIDNotExistsException
from apps.log_trace.handlers.proto.proto import Proto

from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery
from apps.utils.local import get_local_param
from apps.utils.thread import MultiExecuteFunc

OTLP_JAEGER_SPAN_KIND = {2: "server", 3: "client", 4: "producer", 5: "consumer", 1: "internal", 0: "unset"}

OTLP_ERROR_STATUS_CODE = 2


class OtlpTrace(Proto):
    TYPE = TraceProto.OTLP.value
    SERVICE_NAME_FIELD = "resource.service.name"
    OPERATION_NAME_FIELD = "span_name"
    TRACE_ID_FIELD = "trace_id"
    TAGS_FIELD = "attributes"
    TRACES_ADDITIONS = {"operation": "span_name", "service": "resource.service.name"}
    TRACES_ADDITIONS = {
        "operation": {"method": "is", "field": "span_name"},
        "service": {"method": "is", "field": "resource.service.name"},
        "minDuration": {"method": "gte", "field": "elapsed_time"},
        "maxDuration": {"method": "lte", "field": "elapsed_time"},
    }

    TRACE_PLAN = {
        "trace_type": "otlp",
        "additions": [
            {
                "fields_alias": _("服务"),
                "field_name": "resource.service.name",
                "show_type": "select",
                "display": True,
                "tips": _("请选择"),
            },
            {
                "fields_alias": _("名称"),
                "field_name": "span_name",
                "show_type": "select",
                "display": True,
                "tips": _("请选择"),
            },
            {
                "fields_alias": _("类型"),
                "field_name": "kind",
                "show_type": "select",
                "display": True,
                "tips": _("请选择"),
            },
            {
                "fields_alias": _("trace状态"),
                "field_name": "trace_state",
                "show_type": "select",
                "display": True,
                "tips": _("请选择"),
            },
        ],
        "advance_additions": [],
        "charts": [],
        "chart_tree": {
            "chart_name": _("调用关系图"),
            "display_field": "span_name",
            "error_field": "attributes.error",
            "span_width": 120,
            "show_type": None,
            "display": True,
            "tips": _("operationName调用关系"),
        },
    }

    DISPLAY_FIELDS = ["traceID", "operationName", "start_time", "duration"]

    FIELD_LOG_MAP = {
        "trace_id": "traceID",
        "span_id": "spanID",
        "span_name": "operationName",
        "parent_span_id": "parentSpanID",
        "start_time": "startTime",
    }

    MUST_MATCH_FIELDS = {
        "parent_span_id": ["keyword"],
        "span_name": ["keyword"],
        "trace_id": ["keyword"],
        "span_id": ["keyword"],
        "start_time": ["long", "float"],
        "end_time": ["long", "float"],
    }

    def trace_id(self, index_set_id: int, data: dict) -> dict:
        start_time = arrow.get(data.get("startTime")[0:10]).shift(days=-1)
        query_data = {
            "addition": [
                {"key": "trace_id", "method": "is", "value": data["traceID"], "condition": "and", "type": "field"}
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
        result["list"] = self.map_fields_to_log(result.get("list", []), True)
        result["list"] = sorted(result["list"], key=lambda x: x["start_time"])
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
                node
                for node in nodes
                if node.get("parent_span_id", "parent_span_id") == children.get("span_id", "span_id")
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
            node for node in nodes if cur_node.get("parent_span_id", "parent_span_id") == node.get("span_id", "span_id")
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
                "start_time": cls.format_time(child.get("start_time")),
                "end_time": cls.format_time(child.get("end_time")),
                "group": child.get("span_id", ""),
                "from": child.get("start_time", 0),
                "to": child.get("end_time", 0),
                "unit": "ms",
                "parentSpanID": child.get("parent_span_id", "parent_span_id"),
                "children": [],
            }
        )
        return child

    def search(self, index_set_id: int, data: dict) -> dict:
        data.update({"collapse": {"field": "trace_id"}})
        search_handler = SearchHandlerEsquery(index_set_id, data, can_highlight=False)
        result = search_handler.search(search_type="trace")
        trace_ids = [trace["trace_id"] for trace in result.get("list", [])]
        if not trace_ids:
            return result

        result = self.multi_search_trace(trace_ids, index_set_id)
        trace_result = {"list": []}

        for search_result in result.values():
            trace_result["list"].extend(search_result.get("origin_log_list", []))

        trace_data = self._transform_to_jaeger(trace_result.get("list", []))
        trace_result["list"] = self.map_fields_to_log(trace_data)
        return trace_result

    def multi_search_trace(self, trace_ids: List[str], index_set_id):
        multi_execute = MultiExecuteFunc()
        for trace_id in trace_ids:

            def get_trace_search(param):
                return SearchHandlerEsquery(param["index_set_id"], param["search_body"]).search()

            search_dict = {
                "use_time_range": False,
                "addition": [
                    {
                        "key": "trace_id",
                        "method": "is",
                        "value": trace_id,
                        "condition": "and",
                        "type": "field",
                    }
                ],
                "begin": 0,
                "size": 10000,
                "keyword": "*",
                "time_range": "customized",
            }
            multi_execute.append(trace_id, get_trace_search, {"index_set_id": index_set_id, "search_body": search_dict})
        return multi_execute.run()

    def map_fields_to_log(self, field_list, is_detail=False):
        return [self.transfer_trace_data(item) for item in field_list]

    def transfer_trace_data(self, trace_data):
        trace_start_time = sys.maxsize
        trace_end_time = 0
        for span in trace_data["spans"]:
            start_time = span["startTime"]
            if start_time < trace_start_time:
                trace_start_time = start_time
            if start_time + span["duration"] > trace_end_time:
                trace_end_time = start_time + span["duration"]

        duration = humanize.precisedelta(dt.timedelta(microseconds=trace_end_time - trace_start_time))
        return {
            "traceID": trace_data.get("traceID"),
            "operationName": self.trace_name(trace_data["spans"], trace_data["processes"]),
            "start_time": self.format_time(trace_start_time),
            "duration": duration,
        }

    def trace_name(self, spans, process):
        candidate_span = None
        all_span_id = {span.get("spanID") for span in spans}
        for span in spans:
            has_interval_ref = any(
                [ref["traceID"] == span["traceID"] and ref["spanID"] in all_span_id for ref in span["references"]]
            )
            if has_interval_ref:
                continue
            if not candidate_span:
                candidate_span = span
                continue
            cur_ref_len = len(span["references"])
            candidate_span_ref_len = len(candidate_span["references"])
            if cur_ref_len < candidate_span_ref_len or (
                cur_ref_len == candidate_span_ref_len and span["startTime"] < candidate_span["startTime"]
            ):
                candidate_span = span
        if candidate_span:
            service_name = process[candidate_span["processID"]]["serviceName"]
            return f"{service_name} {candidate_span['operationName']}"
        return ""

    @classmethod
    def format_time(cls, timestamp):
        return arrow.get(str(timestamp)[0:10]).to(get_local_param("time_zone")).strftime("%Y-%m-%d %H:%M:%S")

    def to_microseconds(self, timestamp):
        return int(str(timestamp)[0:13])

    def scatter(self, index_set_id: int, data: dict):
        pass

    def traces(self, index_set_id, params):
        result = super(OtlpTrace, self).traces(index_set_id, params)
        trace_ids = [trace["trace_id"] for trace in result.get("list", [])]
        if not trace_ids:
            return []
        result = self.multi_search_trace(trace_ids, index_set_id)
        trace_result = {"list": []}

        for search_result in result.values():
            trace_result["list"].extend(search_result.get("origin_log_list", []))
        return self._transform_to_jaeger(trace_result.get("list", []))

    def _transform_to_jaeger(self, spans):
        jaeger_traces = defaultdict(lambda: {"spans": [], "traceID": ""})
        resources = defaultdict(list)
        processes = defaultdict(dict)
        for span in spans:
            trace_id = span["trace_id"]
            process_id = ""
            for index, resource in enumerate(resources[trace_id], 1):
                if span["resource"] == resource:
                    process_id = f"p{index}"
                    break
            if process_id == "":
                resources[trace_id].append(span["resource"])
                index = len(resources[trace_id])
                processes[trace_id][f"p{index}"] = {
                    "serviceName": span["resource"].get("service.name", "unknown service"),
                    "tags": self._transform_to_tags(span["resource"]),
                }
                process_id = f"p{index}"

            jaeger_traces[span["trace_id"]]["traceID"] = span["trace_id"]
            jaeger_traces[span["trace_id"]]["spans"].append(
                {
                    "traceID": span["trace_id"],
                    "spanID": span["span_id"],
                    "duration": span["elapsed_time"],
                    "references": self._transform_to_refs(span),
                    "flags": 0,
                    "logs": self._transform_to_logs(span["events"]),
                    "operationName": span["span_name"],
                    "startTime": span["start_time"],
                    "tags": self._transform_to_tags(span["attributes"])
                    + [
                        {"key": "span.kind", "type": "string", "value": OTLP_JAEGER_SPAN_KIND[span["kind"]]},
                        {"key": "span_context.trace_state", "type": "string", "value": span["trace_state"]},
                    ]
                    + self._transform_to_status(span.get("status", {})),
                    "processID": process_id,
                },
            )
        return [{**trace, "processes": processes[trace_id]} for trace_id, trace in jaeger_traces.items()]

    def _transform_to_refs(self, span) -> list:
        refs = []
        if span["parent_span_id"]:
            refs.append({"refType": "CHILD_OF", "spanID": span["parent_span_id"], "traceID": span["trace_id"]})
        for link in span.get("links", []):
            refs.append({"refType": "FOLLOWS_FROM", "traceID": link["trace_id"], "spanID": link["span_id"]})
        return refs

    def _transform_to_status(self, status):
        if status.get("code") == OTLP_ERROR_STATUS_CODE:
            return [{"key": "error", "type": "string", "value": True}]
        return []

    def _transform_to_tags(self, attributes):
        return [{"key": key, "value": value, "type": "string"} for key, value in attributes.items()]

    def _transform_to_logs(self, events):
        return [
            {
                "timestamp": event["timestamp"] / 1000,
                "fields": self._transform_to_tags({**event["attributes"], "message": event["name"]}),
            }
            for event in events
        ]

    def trace_detail(self, index_set_id, trace_id):
        search_dict = {
            "use_time_range": False,
            "addition": [{"key": "trace_id", "method": "is", "value": trace_id, "condition": "and", "type": "field"}],
            "begin": 0,
            "size": 10000,
            "keyword": "*",
            "time_range": "customized",
        }
        result = SearchHandlerEsquery(index_set_id, search_dict).search()
        return self._transform_to_jaeger(result.get("list", []))
