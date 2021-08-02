from typing import List

from django.utils.translation import ugettext_lazy as _
from apps.log_trace.constants import TraceProto
from apps.log_trace.exceptions import TraceIDNotExistsException
from apps.log_trace.handlers.proto.proto import Proto

from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery
from apps.utils.local import get_local_param
from apps.utils.time_handler import generate_time_range


class OtlpTrace(Proto):
    TYPE = TraceProto.OTLP.value

    TRACE_PLAN = {
        "trace_type": "otlp",
        "additions": [
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
        "advance_additions": [
            {
                "fields_alias": _("返回码"),
                "field_name": "attributes.result_code",
                "show_type": "text",
                "display": True,
                "tips": "0",
            },
        ],
        "charts": [
            {
                "chart_alias": "line",
                "chart_name": _("曲线图"),
                "field_name": "attributes.result_code",
                "show_type": None,
                "display": True,
                "tips": _("返回码"),
            }
        ],
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

    DISPLAY_FIELDS = ["traceID", "operationName", "start_time", "end_time", "spanID"]

    FIELD_LOG_MAP = {
        "trace_id": "traceID",
        "span_id": "spanID",
        "span_name": "operationName",
        "parent_span_id": "parentSpanID",
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
        start_time, end_time = generate_time_range("1d", "", "", get_local_param("time_zone"))
        query_data = {
            "addition": [
                {"key": "trace_id", "method": "is", "value": data["traceID"], "condition": "and", "type": "field"}
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
        result["list"] = self.map_fields_to_log(result.get("list", []))
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
                if node.get("parent_span_id", "parent_span_id") == children.get("span_id", "span_id")
            ]
            [nodes.remove(remove_item) for remove_item in children["children"]]
            cls._insert_children(children["children"], nodes)

    @classmethod
    def _build_tree(cls, nodes: List[dict], next: dict):
        cls._insert_children([next], nodes)
        _next = [
            node for node in nodes if next.get("parent_span_id", "parent_span_id") == node.get("span_id", "span_id")
        ]
        [nodes.remove(remove_item) for remove_item in _next]
        return cls._build_tree(nodes, _next[0]) if _next else next

    @classmethod
    def update_node(cls, child: dict) -> dict:
        child.update(
            {
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
        item_list = result.get("list", [])
        result["list"] = self.map_fields_to_log(item_list)
        return result

    def map_fields_to_log(self, field_list):
        for item in field_list:
            item["start_time"] = self.format_time(item["start_time"])
            item["end_time"] = self.format_time(item["end_time"])
            for src_key, des_key in self.FIELD_LOG_MAP.items():
                item[des_key] = item[src_key]
        return field_list

    def format_time(self, timestamp):
        return int(timestamp / 1000 ** 2)

    def scatter(self, index_set_id: int, data: dict):
        pass
