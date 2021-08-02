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
        start_time, end_time = generate_time_range("1d", "", "", get_local_param("time_zone"))
        query_data = {
            "addition": [
                {"key": "traceID", "method": "is", "value": data["traceID"], "condition": "and", "type": "field"}
            ],
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
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
        root, *_ = nodes
        cls.update_node(root)
        nodes.remove(root)
        return cls._build_tree(nodes, root)

    @classmethod
    def _insert_children(cls, childrens: List[dict], nodes):
        for children in childrens:
            if "children" not in children:
                cls.update_node(children)
            [
                children["children"].append(cls.update_node(node))
                for node in nodes
                if node.get("parentSpanID", "parentSpanID") == children.get("spanID", "spanID")
            ]
            [nodes.remove(remove_item) for remove_item in children["children"]]
            cls._insert_children(children["children"], nodes)

    @classmethod
    def _build_tree(cls, nodes: List[dict], next: dict):
        cls._insert_children([next], nodes)
        _next = [node for node in nodes if next.get("parentSpanID", "parentSpanID") == node.get("spanID", "spanID")]
        [nodes.remove(remove_item) for remove_item in _next]
        return cls._build_tree(nodes, _next[0]) if _next else next

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
