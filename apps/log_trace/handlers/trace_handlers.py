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
import copy
import arrow
import datetime

from apps.utils.local import get_local_param
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery
from apps.log_trace.handlers.trace_field_handlers import TraceMappingAdapter
from apps.log_trace.exceptions import TraceIDNotExistsException, TraceRootException

SCATTER_TEMPLATE = [
    {"label": "成功", "pointBackgroundColor": "#45E35F", "borderColor": "#45E35F", "pointRadius": 5, "data": []},
    {"label": "失败", "pointBackgroundColor": "#FB9C9C", "borderColor": "#FB9C9C", "pointRadius": 5, "data": []},
]


class TraceHandler(object):
    trace_duration_day = 1
    trace_size = 1000

    def __init__(self):
        pass

    @classmethod
    def fields(cls, index_set_id: int, scope: str) -> dict:
        data = {"search_type": scope}
        search_handler = SearchHandlerEsquery(index_set_id, data)
        result_dict = search_handler.fields(scope)
        result_dict["trace"] = TraceMappingAdapter.get_trace_plan(result_dict["fields"], scope)
        return result_dict

    @classmethod
    def search(cls, index_set_id: int, data: dict) -> dict:
        data.update({"collapse": {"field": "traceID"}})
        search_handler = SearchHandlerEsquery(index_set_id, data)
        return search_handler.search(search_type="trace")

    @classmethod
    def trace_id(cls, index_set_id: int, data: dict) -> dict:
        # 处理起止时间
        start_time = arrow.get(data["startTime"][0:10])
        begin_time = start_time - datetime.timedelta(days=cls.trace_duration_day)
        end_time = start_time + datetime.timedelta(days=cls.trace_duration_day)

        query_data = {
            "start_time": begin_time.timestamp,
            "end_time": end_time.timestamp,
            "addition": [
                {"key": "traceID", "method": "is", "value": data["traceID"], "condition": "and", "type": "field"}
            ],
            "search_type": "trace_detail",
            "size": cls.trace_size,
        }

        search_handler = SearchHandlerEsquery(index_set_id, query_data)
        result: dict = search_handler.search(search_type=None)
        if not result["total"]:
            raise TraceIDNotExistsException()
        result["tree"] = cls.result_to_tree(result)

        return result

    @classmethod
    def scatter(cls, index_set_id: int, data: dict):
        data.update({"search_type": "trace_scatter"})
        search_handler = SearchHandlerEsquery(index_set_id, data)
        result: dict = search_handler.search(search_type=None)
        scatter_list: list = cls.result_to_scatter(result)
        return {"scatter": scatter_list}

    @classmethod
    def result_to_tree(cls, result) -> dict:
        result_list: list = result.get("list", [])

        # 获取根节点
        roots = [cls.update_node(node) for node in result_list if not cls.get_parents(node)]
        if not roots:
            raise TraceRootException()
        root_data = roots[0]

        # 构建树
        tree = copy.deepcopy(root_data)
        cls.find_children(tree, result_list)
        return tree

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

    @classmethod
    def find_children(cls, tree: dict, nodes: list):
        children: list = []
        for node in nodes:
            spanID = node.get("spanID")
            if not spanID:
                continue
            reference: list = cls.get_parents(node, False)
            if not reference:
                continue
            if tree["spanID"] in reference:
                node = cls.update_node(node)
                children.append(cls.find_children(node, nodes))
        tree["children"] = children
        return tree

    @classmethod
    def get_parents(cls, node, judge_root=True):
        """
        @TODO: 后续可能根据reference支持多个parents
        获取节点的parents节点
        """
        # log reference
        reference: str = node.get("parentSpanID")

        # jaeger reference
        jaeger_reference = node.get("references", [])
        span_id = None
        for refer in jaeger_reference:
            span_id = refer.get("spanID", "")
            if span_id:
                break
            else:
                continue
        jaeger_reference_span_id: str = span_id

        if jaeger_reference_span_id:
            # jaeger father 0000
            if jaeger_reference_span_id.startswith("0000"):
                return []
            else:
                # jaeger child
                return jaeger_reference_span_id
        else:
            if reference:
                span_id = node.get("spanID", "")
                trace_id = node.get("traceID", None)
                if cls._is_parent(span_id, reference, trace_id) and judge_root:
                    return []
                else:
                    # log child
                    return [reference]
            else:
                # log root
                return []

    @staticmethod
    def _is_parent(span_id, parent_id, trace_id):
        """
        judge span is parent
        major three condition:
        1. trace_id == parent_id
        2. trace_id == span_id
        3. span_id == parent_id
        """
        return span_id == parent_id or trace_id == span_id or trace_id == parent_id

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
                elif tag.get("error", None) is False:
                    scatter_label_false_list.append(tmp_dict)
                else:
                    pass
            else:
                continue
        return SCATTER_TEMPLATE

    @classmethod
    def mills_to_timestamp(cls, mills: int) -> str:
        seconds = int(mills / 1000)
        d1 = arrow.get(seconds)
        time_format_str = d1.to(get_local_param("time_zone")).format("YYYY-MM-DD HH:mm:ss")
        return time_format_str
