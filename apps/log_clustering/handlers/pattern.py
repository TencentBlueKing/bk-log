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
from typing import List

from apps.log_clustering.constants import (
    AGGS_FIELD_PREFIX,
    PERCENTAGE_RATE,
    MIN_COUNT,
    IS_NEW_PATTERN_PREFIX,
    EX_MAX_SIZE,
    HOUR_MINUTES,
)
from apps.log_clustering.models import AiopsSignatureAndPattern
from apps.log_search.handlers.search.aggs_handlers import AggsHandlers
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler
from apps.utils.db import array_hash
from apps.utils.local import get_local_param
from apps.utils.time_handler import generate_time_range, generate_time_range_shift


class PatternHandler:
    def pattern_search(self, index_set_id, query):
        """
        aggs_result
        {
            "aggs": {
                "log_signature_01": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [
                        {
                            "key": "8d96a0935c848f8e9c876369d301d76e",
                            "doc_count": 10
                        },
                        {
                            "key": "43ba9231388c90ca3802e47f713a7a85",
                            "doc_count": 9
                        }
                    ]
                }
            }
        }
        """
        pattern_aggs = self.get_pattern_aggs_result(index_set_id, query)
        year_on_year_result = self.get_year_on_year_aggs_result(index_set_id, query)

        # todo index_set_id 与 model_id的映射关系
        model_id = None
        pattern_map = AiopsSignatureAndPattern.objects.filter(model_id=model_id).values("signature", "pattern")
        signature_map_pattern = array_hash(pattern_map, "signature", "pattern")

        new_pattern_set = self.new_pattern_search(
            query["show_new_pattern"], query["pattern_level"], index_set_id, query
        )

        sum_count = sum([pattern.get("doc_count", 0) for pattern in pattern_aggs])
        result = []
        for pattern in pattern_aggs:
            count = pattern["doc_count"]
            signature = pattern["key"]
            year_on_year_compare = year_on_year_result.get(signature, 0)
            result.append(
                {
                    "pattern": signature_map_pattern.get(signature, ""),
                    "count": count,
                    "signature": signature,
                    "percentage": self.percentage(count, sum_count),
                    "is_new_class": signature in new_pattern_set,
                    "year_on_year_count": count - year_on_year_compare,
                    "year_on_year_percentage": self._year_on_year_calculate_percentage(count, year_on_year_compare),
                }
            )
        return result

    def get_pattern_aggs_result(self, index_set_id, query):
        pattern_field = self._build_pattern_aggs_field(query["pattern_level"])
        query["fields"] = [pattern_field]
        aggs_result = AggsHandlers.terms(index_set_id, query)
        return self._parse_pattern_aggs_result(pattern_field, aggs_result)

    def get_year_on_year_aggs_result(self, index_set_id, query) -> dict:
        if query["year_on_year_hour"] == MIN_COUNT:
            return {}
        new_query = copy.deepcopy(query)
        start_time, end_time = generate_time_range_shift(
            query["start_time"], query["end_time"], query["year_on_year_hour"] * HOUR_MINUTES
        )
        new_query["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        new_query["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        return array_hash(self.get_pattern_aggs_result(index_set_id, new_query), "key", "doc_count")

    @staticmethod
    def _year_on_year_calculate_percentage(target, compare):
        if compare == MIN_COUNT:
            return MIN_COUNT
        return ((target - compare) / compare) * PERCENTAGE_RATE

    def new_pattern_search(self, show_new_pattern: bool, pattern_level: str, index_set_id, query: dict) -> set:
        if not show_new_pattern:
            return set()
        start_time, end_time = generate_time_range("1d", "", "", get_local_param("time_zone"))
        new_pattern_search_query = copy.deepcopy(query)
        new_pattern_search_query["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        new_pattern_search_query["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        new_pattern_search_query["addition"].append(
            {"key": self._build_is_new_judge_field(pattern_level), "method": "is", "value": "true"}
        )
        new_pattern_search_query["size"] = EX_MAX_SIZE
        result = SearchHandler(index_set_id, new_pattern_search_query).search(search_type=None)
        new_class_list = result.get("list", [])
        return {item.get(self._build_pattern_aggs_field(pattern_level)) for item in new_class_list}

    @staticmethod
    def percentage(count, sum_count) -> int:
        # avoid division by zero
        if sum_count == 0:
            return MIN_COUNT
        return (count / sum_count) * PERCENTAGE_RATE

    @staticmethod
    def _build_is_new_judge_field(pattern_level: str) -> str:
        return f"{IS_NEW_PATTERN_PREFIX}_{pattern_level}"

    @staticmethod
    def _build_pattern_aggs_field(pattern_level: str) -> str:
        return f"{AGGS_FIELD_PREFIX}_{pattern_level}"

    @staticmethod
    def _parse_pattern_aggs_result(pattern_field: str, aggs_result: dict) -> List[dict]:
        aggs = aggs_result.get("aggs")
        pattern_field_aggs = aggs.get(pattern_field)
        if not pattern_field_aggs:
            return []
        return pattern_field_aggs.get("buckets", [])
