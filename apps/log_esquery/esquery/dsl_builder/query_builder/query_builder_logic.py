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
from abc import ABC
from collections import defaultdict
from typing import List, Dict, Any
import copy

from elasticsearch_dsl import Search, Q
from luqum.auto_head_tail import auto_head_tail
from luqum.elasticsearch import SchemaAnalyzer, ElasticsearchQueryBuilder
from luqum.exceptions import ParseError
from luqum.parser import parser, lexer
from luqum.tree import Word
from luqum.visitor import TreeTransformer

from apps.log_esquery.exceptions import BaseSearchDslException
from apps.log_search.constants import FieldDataTypeEnum
from apps.log_search.handlers.search.mapping_handlers import MappingHandlers

type_match_phrase = Dict[str, Dict[str, Any]]  # pylint: disable=invalid-name
type_match_phrase_query = Dict[str, Dict[str, Dict[str, Any]]]  # pylint: disable=invalid-name
type_should_list = List[type_match_phrase]  # pylint: disable=invalid-name
type_should = Dict[str, type_should_list]  # pylint: disable=invalid-name
type_bool = Dict[str, type_should]  # pylint: disable=invalid-name
type_query_string = Dict[str, Dict[str, Any]]  # pylint: disable=invalid-name

filter_dict = Dict[str, Any]  # pylint: disable=invalid-name

type_query_bool_dict = Dict[str, Dict[str, Dict[str, List]]]  # pylint: disable=invalid-name
type_bool_must_dict = Dict[str, Dict[str, List]]  # pylint: disable=invalid-name
type_bool_should_dict = Dict[str, Dict[str, List]]  # pylint: disable=invalid-name
type_range = Dict[str, Dict[str, Dict[str, Any]]]  # pylint: disable=invalid-name

query_final_dict_template: type_query_bool_dict = {
    "query": {"bool": {"must": [{"bool": {"should": []}}], "filter": [], "should": [], "must_not": []}}
}

bool_must_dict_template: type_bool_must_dict = {"bool": {"must": [], "must_not": []}}

bool_should_dict_template: type_bool_should_dict = {"bool": {"should": []}}


class NestedFieldQueryTransformer(TreeTransformer):
    def __init__(self, nested_fields, *args, **kwargs):
        super(NestedFieldQueryTransformer, self).__init__(*args, **kwargs)
        self.nested_fields = nested_fields

    def visit_search_field(self, node, context):
        for field in self.nested_fields:
            if node.name.startswith(f"{field}."):
                setattr(self, "has_nested_field", True)
                break

        yield from self.generic_visit(node, context)


class EsQueryBuilder(object):
    def __init__(self):
        pass

    @classmethod
    def build_query_string(cls, search_string: str, mappings: List) -> Search:
        search = Search()

        try:
            query_tree = parser.parse(search_string, lexer=lexer)
        except ParseError:
            raise BaseSearchDslException(BaseSearchDslException.MESSAGE.format(dsl=search_string))

        nested_fields, full_mappings = cls._merge_mappings(mappings)

        if isinstance(query_tree, Word):
            # 不带字段查询
            keyword_query = Q("query_string", query=str(query_tree), analyze_wildcard=True)
            if str(query_tree) == "*":
                # 单独*通配符 作为单个query_string处理
                return search.query(keyword_query)

            # 带上nested字段检索
            nested_field_queries = []
            for f in nested_fields:
                nested_field_queries.append(Q("nested", path=f, query=keyword_query))

            return search.query("bool", should=[keyword_query] + nested_field_queries)
        else:
            transformer = NestedFieldQueryTransformer(nested_fields)
            query_tree = transformer.visit(query_tree)

            if getattr(transformer, "has_nested_field", False):
                # 存在nested字段
                schema_analyzer = SchemaAnalyzer(full_mappings)
                builder = ElasticsearchQueryBuilder(**schema_analyzer.query_builder_options())
                return search.query(builder(query_tree))

            query_tree = auto_head_tail(query_tree)
            return search.query("query_string", query=str(query_tree), analyze_wildcard=True)

    @classmethod
    def _merge_mappings(cls, mappings):
        property_dict: dict = MappingHandlers.find_property_dict(mappings)
        fields_result: list = MappingHandlers.get_all_index_fields_by_mapping(property_dict)

        conflict_fields = [i["field_name"] for i in fields_result if i["field_type"] == "conflict"]
        properties = {}
        for mapping in mappings:
            for index_name, index_config in mapping.items():
                # 只关注最上层mapping定义
                index_properties = index_config.get("mappings", {}).get("properties", {})
                properties.update({k: v for k, v in index_properties.items() if k not in conflict_fields})

        nested_fields = [k for k, v in properties.items() if v.get("type") == FieldDataTypeEnum.NESTED.value]

        for nested_field in nested_fields:
            # 保证每个嵌套类型字段都定义了一个properties，否则luqum无法正确识别nested字段
            if not properties[nested_field].get("properties"):
                properties[nested_field]["properties"] = {"_": {}}

        return nested_fields, {"mappings": {"properties": properties}}

    @classmethod
    def build_exists(cls, field: str):
        return {"exists": {"field": field}}

    @classmethod
    def build_bool(cls, should: type_should) -> type_bool:
        return {"bool": should}

    @classmethod
    def build_should(cls, should_list: type_should_list) -> type_should:
        return {"should": should_list}

    @classmethod
    def build_should_list(cls, field: str, value_list: List[Any]) -> type_should_list:
        should_list: type_should_list = []
        for item in value_list:
            match_phrase: type_match_phrase = cls.build_match_phrase(field, item)
            should_list.append(match_phrase)
        return should_list

    @classmethod
    def build_match_phrase(cls, field: str, value: Any) -> type_match_phrase:
        return {"match_phrase": {field: value}}

    @classmethod
    def build_match_phrase_query(cls, field: str, value: Any) -> type_match_phrase_query:
        return {"match_phrase": {field: {"query": value}}}

    @classmethod
    def build_range(cls, range_field_dict: Dict[str, Dict[str, Any]]) -> type_range:
        return {"range": range_field_dict}

    @classmethod
    def build_range_filter(cls, field: str, operator: str, value: Any) -> type_range:
        return {"range": {field: {operator: value}}}


class BoolQueryOperation(ABC):
    TARGET = None
    OPERATOR = None

    @staticmethod
    def get_op(op: str, bool_dict: dict):
        op_map = {
            Is.OPERATOR: Is,
            Eq.OPERATOR: Eq,
            Exists.OPERATOR: Exists,
            DoesNotExist.OPERATOR: DoesNotExist,
            IsNot.OPERATOR: IsNot,
            IsOneOf.OPERATOR: IsOneOf,
            IsNotOneOf.OPERATOR: IsNotOneOf,
            Gt.OPERATOR: Gt,
            Gte.OPERATOR: Gte,
            Lt.OPERATOR: Lt,
            Lte.OPERATOR: Lte,
        }
        op_target = op_map.get(op, BoolQueryOperation)
        return op_target(bool_dict)

    def __init__(self, bool_dict: dict):
        self._bool_dict = bool_dict

    def _has_value(self, key: str):
        return self._bool_dict.get("bool", {}).get(key)

    def _set_target_value(self, value: dict):
        if isinstance(self._bool_dict["bool"][self.TARGET], list):
            self._bool_dict["bool"][self.TARGET].append(value)

    def op(self, field):
        pass


class Is(BoolQueryOperation):
    TARGET = "must"
    OPERATOR = "is"

    def op(self, field):
        self._set_target_value(EsQueryBuilder.build_match_phrase_query(field["field"], field["value"]))


class Eq(Is):
    OPERATOR = "eq"


class Exists(BoolQueryOperation):
    OPERATOR = "exists"
    TARGET = "must"

    def op(self, field):
        self._set_target_value(EsQueryBuilder.build_exists(field["field"]))


class DoesNotExist(Exists):
    OPERATOR = "does not exists"
    TARGET = "must_not"


class IsNot(BoolQueryOperation):
    TARGET = "must_not"
    OPERATOR = "is not"

    def op(self, field):
        self._set_target_value(EsQueryBuilder.build_match_phrase_query(field["field"], field["value"]))


class IsOneOf(BoolQueryOperation):
    OPERATOR = "is one of"
    TARGET = "must"

    def op(self, field):
        should_list: type_should_list = EsQueryBuilder.build_should_list(field["field"], field["value"])
        should: type_should = EsQueryBuilder.build_should(should_list)
        a_bool: type_bool = EsQueryBuilder.build_bool(should)
        self._set_target_value(a_bool)


class IsNotOneOf(IsOneOf):
    OPERATOR = "is not one of"
    TARGET = "must_not"


class CompareBoolQueryOperation(BoolQueryOperation):
    TARGET = "must"

    def op(self, field):
        self._set_target_value(EsQueryBuilder.build_range_filter(field["field"], field["operator"], field["value"]))


class Gt(CompareBoolQueryOperation):
    OPERATOR = "gt"


class Gte(CompareBoolQueryOperation):
    OPERATOR = "gte"


class Lt(CompareBoolQueryOperation):
    OPERATOR = "lt"


class Lte(CompareBoolQueryOperation):
    OPERATOR = "lte"


class BoolMustIns(object):
    def __init__(self, filter_dict_list: List[filter_dict] = None):
        self.bool_must_dict = copy.deepcopy(bool_must_dict_template)
        # default dict use lambda to build a dict have default value
        self.nested_map_query = defaultdict(
            lambda: {"nested": {"path": "", "query": copy.deepcopy(bool_must_dict_template)}}
        )
        for item in filter_dict_list:
            operator = item["operator"]
            field_type = item.get("type", "field")
            # nested need deal path param, then build bool query at nested query
            if field_type == FieldDataTypeEnum.NESTED.value:
                path, *_ = item["field"].split(".")
                self.nested_map_query[path]["nested"]["path"] = path
                BoolQueryOperation.get_op(operator, self.nested_map_query[path]["nested"]["query"]).op(item)
                continue
            # build bool query
            BoolQueryOperation.get_op(operator, self.bool_must_dict).op(item)

        for nested_query in self.nested_map_query.values():
            self.bool_must_dict["bool"]["must"].append(nested_query)

    @property
    def must_ins(self):
        return self.bool_must_dict


class BoolShouldIns(object):
    def __init__(self, bool_must_list: List[BoolMustIns]):
        self.bool_should_dict = copy.deepcopy(bool_should_dict_template)
        for must_ins in bool_must_list:
            self.bool_should_dict["bool"]["should"].append(must_ins)

    @property
    def should_ins(self):
        return self.bool_should_dict


class Dsl(object):
    def __init__(
        self, query_string: str, filter_dict_list: List, range_field_dict: Dict[str, Dict[str, Any]], mappings: List
    ):
        # 处理filter list
        must_ins_list: List = []
        self.filters: List = self.divid_filter_list(filter_dict_list)
        for item in self.filters:
            must_ins = BoolMustIns(filter_dict_list=item).must_ins
            must_ins_list.append(must_ins)
        self.should_ins = BoolShouldIns(must_ins_list).should_ins

        # 生成query string
        self.query_string: type_query_string = (
            EsQueryBuilder.build_query_string(query_string, mappings).to_dict().get("query", {})
        )
        self.range_dict: type_range = None
        if range_field_dict:
            # 生成range dict
            self.range_dict: type_range = EsQueryBuilder.build_range(range_field_dict)

    @property
    def dsl_dict(self):
        filter = [self.query_string, self.should_ins]
        if self.range_dict:
            filter = [self.query_string, self.range_dict, self.should_ins]
        return {"query": {"bool": {"filter": filter}}}

    def divid_filter_list(self, filter_dict_list: List):
        filters: List = []
        filter_bucket: List = []
        for index, item in enumerate(filter_dict_list):
            if index == 0 or item.get("condition", "and") == "and":
                if item.get("value") or isinstance(item.get("value"), str):
                    filter_bucket.append(item)
                continue
            if len(filter_bucket) > 0:
                filters.append(filter_bucket)
                filter_bucket = []
            if item.get("value") or isinstance(item.get("value"), str):
                filter_bucket.append(item)
        if len(filter_bucket) > 0:
            filters.append(filter_bucket)

        return filters
