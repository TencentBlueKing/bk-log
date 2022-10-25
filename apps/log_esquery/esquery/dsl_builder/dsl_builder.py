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
import re

from elasticsearch_dsl.search import Q, Search

from apps.log_esquery.constants import WILDCARD_PATTERN
from apps.log_esquery.esquery.dsl_builder.query_builder.query_builder_logic import type_query_bool_dict
from apps.log_esquery.esquery.dsl_builder.query_builder.query_builder_logic import Dsl
from apps.log_esquery.exceptions import BaseSearchQueryBuilderException


class DslBuilder(object):
    def __init__(
        self,
        search_string="*",
        fields_list: list = [],
        filter_dict_list: list = [],
        time_range_dict: dict = {},
        sort_tuple: tuple = (),
        begin=0,
        size=500,
        aggs: dict = {},
        highlight: dict = {},
        collapse={},
        search_after=[],
        use_time_range=True,
        mappings: list = [],
    ):  # pylint: disable=dangerous-default-value
        """

        :param search_string {string} "test":
        :param fields_list: {List} ['field1', 'field2']
        :param filter_dict_list:  [{'field1': [1, 2, 3]}, {'field2': [1, 2, 3]}]
        :param time_range_dict:
        {
            'timestamp': {
                {'gte': 'now-5m', 'lt': 'now'}
            }
        }
        :param sort_tuple
        'field1',
        '-field2',
        :
        :param begin {int} 0:
        :param size: {int} 30
        """

        # init params
        self._body: dict = {}
        self._query_body = None
        self._agg_body = None

        self.time_range_dict = time_range_dict
        if not use_time_range:
            self.time_range_dict = {}

        self.fields_list = fields_list
        self.filter_dict_list = filter_dict_list

        self.sort_tuple = sort_tuple
        # end init params

        # build search string
        self.search_string = search_string

        # build query body
        self.search = Search()

        query_bool_obj: type_query_bool_dict = Dsl(
            query_string=search_string,
            filter_dict_list=self.filter_dict_list,
            range_field_dict=self.time_range_dict,
            mappings=mappings,
        ).dsl_dict
        if not query_bool_obj:
            raise BaseSearchQueryBuilderException

        if self.sort_tuple:
            self.search = self.search.sort(*self.sort_tuple)

        self._query_body = self.search.to_dict()

        # 更新start和size
        self._query_body.update({"from": begin, "size": size})
        self._query_body.update({"query": query_bool_obj.get("query")})
        if collapse:
            self._query_body.update({"collapse": collapse})

        # 透传聚合
        self._agg_body = aggs

        self._body.update(self._query_body)
        if self._agg_body:
            self._body.update({"aggs": self._agg_body})

        # 透传高亮
        self.highlight_dict = highlight

        if self.highlight_dict:
            # have query filter need highlight
            if self.search_string != WILDCARD_PATTERN or filter_dict_list:
                self._body.update({"highlight": self.highlight_dict})

        # 启用search_after模式
        self.search_after = search_after
        if self.search_after:
            self._body.update({"search_after": self.search_after})
            self._body.pop("from")

    @property
    def body(self):
        return self._body

    @staticmethod
    def check_special_string(_str: str):
        """
        @summary 是否含有特殊字符
        """
        regx = re.compile(r"[+\-=&|><!(){}\[\]^\"~*?:/]|AND|OR|TO|NOT")
        return regx.search(_str)

    def build_body_using_query_string(self):
        return Q("query_string", query=self.search_string, fields=self.fields_list, analyze_wildcard=True)

    @staticmethod
    def build_filter(filter_item):
        return Q("terms", **filter_item)

    # 更多的条件需要优化bool查询
    @staticmethod
    def build_filter_match_phrase(filter_match_phrase):
        key_list = list(filter_match_phrase.keys())
        if not key_list:
            return None
        key_str, *_ = key_list

        log_str_list = filter_match_phrase[key_str]
        if not log_str_list:
            return None
        log_str, *_ = log_str_list

        return Q({"match_phrase": {key_str: {"query": log_str}}})

    def build_time_range(self):
        return Q("range", **self.time_range_dict)

    @staticmethod
    def build_agg_terms(name, field, size=0):
        return {"%s" % name: {"field": field, "size": size}}

    @staticmethod
    def build_agg_top_hit(name, size, sort_field, sort="desc"):
        return {"%s" % name: {"top_hits": {"size": size, "sort": {"%s" % sort_field: sort}}}}

    @staticmethod
    def build_agg_filter(name, field, field_value_list):
        return {"%s" % name: {"filter": {"bool": {"must": {"terms": {"%s" % field: field_value_list}}}}}}
