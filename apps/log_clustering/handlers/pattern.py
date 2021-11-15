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
    HOUR_MINUTES,
    NEW_CLASS_QUERY_TIME_RANGE,
    NEW_CLASS_QUERY_FIELDS,
    NEW_CLASS_SENSITIVITY_FIELD,
)
from apps.log_clustering.exceptions import ClusteringConfigNotExistException
from apps.log_clustering.models import AiopsSignatureAndPattern, ClusteringConfig
from apps.log_search.handlers.search.aggs_handlers import AggsHandlers
from apps.utils.bkdata import BkData
from apps.utils.db import array_hash
from apps.utils.local import get_local_param
from apps.utils.time_handler import generate_time_range_shift, generate_time_range


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
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if not clustering_config:
            raise ClusteringConfigNotExistException

        pattern_aggs = self.get_pattern_aggs_result(index_set_id, query)
        year_on_year_result = self.get_year_on_year_aggs_result(index_set_id, query)
        new_class = set()
        if query["show_new_pattern"]:
            new_class = self.get_new_class(clustering_config.new_cls_pattern_rt, query["pattern_level"])

        pattern_map = AiopsSignatureAndPattern.objects.filter(model_id=clustering_config.model_id).values(
            "signature", "pattern"
        )
        signature_map_pattern = array_hash(pattern_map, "signature", "pattern")

        sum_count = sum([pattern.get("doc_count", MIN_COUNT) for pattern in pattern_aggs])
        result = []
        for pattern in pattern_aggs:
            count = pattern["doc_count"]
            signature = pattern["key"]
            year_on_year_compare = year_on_year_result.get(signature, MIN_COUNT)
            result.append(
                {
                    "pattern": signature_map_pattern.get(signature, ""),
                    "count": count,
                    "signature": signature,
                    "percentage": self.percentage(count, sum_count),
                    "is_new_class": signature in new_class,
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

    @staticmethod
    def percentage(count, sum_count) -> int:
        # avoid division by zero
        if sum_count == 0:
            return MIN_COUNT
        return (count / sum_count) * PERCENTAGE_RATE

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

    def get_new_class(self, result_table_id: str, pattern_level: str):
        start_time, end_time = generate_time_range(NEW_CLASS_QUERY_TIME_RANGE, "", "", get_local_param("time_zone"))
        new_classes = (
            BkData(result_table_id)
            .select(*NEW_CLASS_QUERY_FIELDS)
            .where(NEW_CLASS_SENSITIVITY_FIELD, "=", self._build_pattern_aggs_field(pattern_level))
            .time_range(start_time.timestamp, end_time.timestamp)
            .query()
        )
        return {new_class["signature"] for new_class in new_classes}
