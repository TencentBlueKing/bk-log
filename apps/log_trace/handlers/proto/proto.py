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
from abc import ABC
from typing import List
import json

from django.utils.module_loading import import_string

from apps.log_search.handlers.search.aggs_handlers import AggsHandlers
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery
from apps.log_trace.constants import TraceProto
from apps.log_trace.exceptions import ProtoNotSupport


class Proto(ABC):
    TYPE = None
    TRACE_MAPPING = None
    TRACE_PLAN = None
    DISPLAY_FIELDS = None
    TRACE_SIZE = 1000
    SERVICE_NAME_FIELD = None
    OPERATION_NAME_FIELD = None
    TRACE_ID_FIELD = None
    TAGS_FIELD = None
    TRACES_ADDITIONS = {
        "operation": {"method": "is", "field": ""},
        "service": {"method": "is", "field": ""},
        "minDuration": {"method": "gte", "field": ""},
        "maxDuration": {"method": "lte", "field": ""},
    }

    LOG_DISPLAY_FIELDS = [
        {
            "field_type": "keyword",
            "field_name": "operationName",
            "field_alias": "Span",
            "is_display": True,
            "is_editable": False,
            "tag": "dimension",
            "es_doc_values": True,
            "is_analyzed": False,
            "description": "Span",
        },
        {
            "field_type": "keyword",
            "field_name": "parentSpanID",
            "field_alias": "parentSpanID",
            "is_display": False,
            "is_editable": True,
            "tag": "dimension",
            "es_doc_values": True,
            "is_analyzed": False,
            "description": "parentSpanID",
        },
        {
            "field_type": "keyword",
            "field_name": "spanID",
            "field_alias": "spanID",
            "is_display": False,
            "is_editable": False,
            "tag": "dimension",
            "es_doc_values": True,
            "is_analyzed": False,
            "description": "spanID",
        },
        {
            "field_type": "keyword",
            "field_name": "traceID",
            "field_alias": "traceID",
            "is_display": True,
            "is_editable": True,
            "tag": "dimension",
            "es_doc_values": True,
            "is_analyzed": False,
            "description": "traceID",
        },
    ]

    MUST_MATCH_FIELDS = None

    PROTO_MAP = {TraceProto.LOG.value: "LogTrace", TraceProto.OTLP.value: "OtlpTrace"}

    @classmethod
    def judge_trace_type(cls, field_list):
        for proto_type in cls.PROTO_MAP.keys():
            if cls.get_proto(proto_type).match_field(field_list):
                return proto_type
        return None

    @classmethod
    def get_proto(cls, proto_type) -> "Proto":
        try:
            proto = import_string("apps.log_trace.handlers.proto.{}.{}".format(proto_type, cls.PROTO_MAP[proto_type]))
            return proto()
        except KeyError:
            raise ProtoNotSupport

    @staticmethod
    def _deal_plan(trace_plan: dict, field_result: list):
        ret_plan = copy.deepcopy(trace_plan)
        fields = list(map(lambda v: v["field_name"], field_result))
        for show_type in ["additions", "advance_additions", "charts"]:
            show_list: List[dict] = ret_plan.get(show_type, [])
            remove_item = []
            for _show in show_list:
                if _show.get("field_name") not in fields:
                    remove_item.append(_show)
            list(map(lambda item: show_list.remove(item), remove_item))
        return ret_plan

    def trace_id(self, index_set_id: int, data: dict) -> dict:
        pass

    def search(self, index_set_id: int, data: dict) -> dict:
        pass

    def fields(self, index_set_id: int, scope: str) -> dict:
        data = {"search_type": scope}
        search_handler = SearchHandlerEsquery(index_set_id, data)
        result_dict = search_handler.fields(scope)
        result_dict["trace"] = self._deal_plan(self.TRACE_PLAN, result_dict["fields"])
        result_dict["fields"].extend(self.LOG_DISPLAY_FIELDS)
        if self.DISPLAY_FIELDS:
            result_dict["display_fields"] = self.DISPLAY_FIELDS
        return result_dict

    def match_field(self, field_list) -> bool:
        if not self.MUST_MATCH_FIELDS:
            return False
        must_fields_len = len(self.MUST_MATCH_FIELDS.keys())
        record = []
        for field in field_list:
            field_name = field.get("field_name", "")
            field_type = field.get("field_type", "")
            if field_type in self.MUST_MATCH_FIELDS.get(field_name, []):
                record.append(field_name)
        if len(record) == must_fields_len:
            return True
        return False

    def scatter(self, index_set_id: int, data: dict):
        pass

    def _deal_term_result(self, term_result, field_name: str):
        aggs = term_result.get("aggs", {})
        return [bucket.get("key", "") for bucket in aggs.get(field_name, {}).get("buckets", [])]

    def services(self, index_set_id: int) -> list:
        query_data = {
            "fields": [self.SERVICE_NAME_FIELD],
        }
        term_result = AggsHandlers.terms(index_set_id, query_data)
        return self._deal_term_result(term_result, self.SERVICE_NAME_FIELD)

    def operations(self, index_set_id, service_name):
        query_data = {
            "fields": [self.OPERATION_NAME_FIELD],
            "addition": [{"method": "is", "key": self.SERVICE_NAME_FIELD, "value": service_name}],
        }
        term_result = AggsHandlers.terms(index_set_id, query_data)
        return self._deal_term_result(term_result, self.OPERATION_NAME_FIELD)

    def traces(self, index_set_id, params):
        search_dict = {
            "start_time": params["start"] / 1000000,
            "end_time": params["end"] / 1000000,
            "addition": self.get_traces_additions(params),
            "begin": 0,
            "size": params.get("limit"),
            "keyword": "*",
            "time_range": "customized",
            "collapse": {"field": self.TRACE_ID_FIELD},
        }
        search_handler = SearchHandlerEsquery(index_set_id, search_dict)
        return search_handler.search()

    def get_traces_additions(self, params):
        addition = []
        for filter_key in self.TRACES_ADDITIONS.keys():
            if params.get(filter_key):
                addition.append(
                    {
                        "method": self.TRACES_ADDITIONS.get(filter_key).get("method", "is"),
                        "key": self.TRACES_ADDITIONS.get(filter_key).get("field", ""),
                        "value": params.get(filter_key),
                        "condition": "and",
                        "type": "field",
                    }
                )
        if params.get("tags"):

            tags_key_value = json.loads(params.get("tags"))
            for tag_key, tag_value in tags_key_value.items():
                if tag_value:
                    addition.append(
                        {
                            "method": "is",
                            "key": f"{self.TAGS_FIELD}.{tag_key}",
                            "value": tag_value,
                            "condition": "and",
                            "type": "field",
                        }
                    )
        return addition

    def trace_detail(self, index_set_id, trace_id):
        pass
