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

from django.utils.functional import cached_property

from apps.log_clustering.constants import (
    AGGS_FIELD_PREFIX,
    PERCENTAGE_RATE,
    MIN_COUNT,
    HOUR_MINUTES,
    NEW_CLASS_QUERY_TIME_RANGE,
    NEW_CLASS_QUERY_FIELDS,
    NEW_CLASS_SENSITIVITY_FIELD,
    DOUBLE_PERCENTAGE,
    NEW_CLASS_FIELD_PREFIX,
)
from apps.log_clustering.exceptions import ClusteringConfigNotExistException
from apps.log_clustering.models import AiopsSignatureAndPattern, ClusteringConfig
from apps.log_search.handlers.search.aggs_handlers import AggsHandlers
from apps.utils.bkdata import BkData
from apps.utils.db import array_hash
from apps.utils.local import get_local_param
from apps.utils.thread import MultiExecuteFunc
from apps.utils.time_handler import generate_time_range_shift, generate_time_range


class PatternHandler:
    def __init__(self, index_set_id, query):
        self._index_set_id = index_set_id
        self._pattern_level = query["pattern_level"]
        self._show_new_pattern = query["show_new_pattern"]
        self._year_on_year_hour = query["year_on_year_hour"]
        self._group_by = query["group_by"]
        self._clustering_config = ClusteringConfig.objects.filter(
            index_set_id=index_set_id, signature_enable=True
        ).first()
        self._query = query
        if not self._clustering_config:
            raise ClusteringConfigNotExistException

    def pattern_search(self):
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

        result = self._multi_query()
        pattern_aggs = result.get("pattern_aggs", [])
        year_on_year_result = result.get("year_on_year_result", {})
        new_class = result.get("new_class", set())

        pattern_map = AiopsSignatureAndPattern.objects.filter(model_id=self._clustering_config.model_id).values(
            "signature", "pattern"
        )
        signature_map_pattern = array_hash(pattern_map, "signature", "pattern")

        sum_count = sum([pattern.get("doc_count", MIN_COUNT) for pattern in pattern_aggs])
        result = []
        for pattern in pattern_aggs:
            count = pattern["doc_count"]
            signature = pattern["key"]
            group_key = f"{signature}|{pattern.get('group', '')}"
            year_on_year_compare = year_on_year_result.get(group_key, MIN_COUNT)
            result.append(
                {
                    "pattern": signature_map_pattern.get(signature, ""),
                    "count": count,
                    "signature": signature,
                    "percentage": self.percentage(count, sum_count),
                    "is_new_class": signature in new_class,
                    "year_on_year_count": count - year_on_year_compare,
                    "year_on_year_percentage": self._year_on_year_calculate_percentage(count, year_on_year_compare),
                    "group": pattern.get("group", ""),
                }
            )
        return result

    def _multi_query(self):
        multi_execute_func = MultiExecuteFunc()
        multi_execute_func.append(
            "pattern_aggs",
            lambda p: self._get_pattern_aggs_result(p["index_set_id"], p["query"]),
            {"index_set_id": self._index_set_id, "query": self._query},
        )
        multi_execute_func.append("year_on_year_result", lambda: self._get_year_on_year_aggs_result())
        multi_execute_func.append("new_class", lambda: self._get_new_class())
        return multi_execute_func.run()

    def _get_pattern_aggs_result(self, index_set_id, query):
        query["fields"] = [{"field_name": self.pattern_aggs_field, "sub_fields": self._build_aggs_group}]
        aggs_result = AggsHandlers.terms(index_set_id, query)
        return self._parse_pattern_aggs_result(self.pattern_aggs_field, aggs_result)

    @property
    def _build_aggs_group(self):
        aggs_group = {}
        aggs_group_reuslt = aggs_group
        for group_key in self._group_by:
            aggs_group["field_name"] = group_key
            aggs_group["sub_fields"] = {}
            aggs_group = aggs_group["sub_fields"]
        return aggs_group_reuslt

    def _get_year_on_year_aggs_result(self) -> dict:
        if self._year_on_year_hour == MIN_COUNT:
            return {}
        new_query = copy.deepcopy(self._query)
        start_time, end_time = generate_time_range_shift(
            self._query["start_time"], self._query["end_time"], self._year_on_year_hour * HOUR_MINUTES
        )
        new_query["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        new_query["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        new_query["time_range"] = "customized"
        buckets = self._get_pattern_aggs_result(self._index_set_id, new_query)
        for bucket in buckets:
            bucket["key"] = f"{bucket['key']}|{bucket.get('group', '')}"
        return array_hash(buckets, "key", "doc_count")

    @staticmethod
    def _year_on_year_calculate_percentage(target, compare):
        if compare == MIN_COUNT:
            return DOUBLE_PERCENTAGE
        return ((target - compare) / compare) * PERCENTAGE_RATE

    @staticmethod
    def percentage(count, sum_count) -> int:
        # avoid division by zero
        if sum_count == 0:
            return MIN_COUNT
        return (count / sum_count) * PERCENTAGE_RATE

    @cached_property
    def pattern_aggs_field(self) -> str:
        return f"{AGGS_FIELD_PREFIX}_{self._pattern_level}"

    @cached_property
    def new_class_field(self) -> str:
        return f"{NEW_CLASS_FIELD_PREFIX}_{self._pattern_level}"

    def _parse_pattern_aggs_result(self, pattern_field: str, aggs_result: dict) -> List[dict]:
        aggs = aggs_result.get("aggs")
        pattern_field_aggs = aggs.get(pattern_field)
        if not pattern_field_aggs:
            return []
        return self._get_group_by_value(pattern_field_aggs.get("buckets", []))

    def _get_group_by_value(self, bucket):
        for group_key in self._group_by:
            result_buckets = []
            for iter_bucket in bucket:
                doc_key = iter_bucket.get("key")
                group_buckets = iter_bucket.get(group_key, {}).get("buckets", [])
                for group_bucket in group_buckets:
                    result_buckets.append(
                        {
                            **group_bucket,
                            "key": doc_key,
                            "doc_count": group_bucket.get("doc_count", 0),
                            "group": (
                                f"{iter_bucket.get('group', '')}|{group_bucket['key']}"
                                if iter_bucket.get("group", "")
                                else group_bucket["key"]
                            ),
                        }
                    )
            bucket = result_buckets
        return bucket

    def _get_new_class(self):
        if not self._show_new_pattern:
            return set()
        start_time, end_time = generate_time_range(NEW_CLASS_QUERY_TIME_RANGE, "", "", get_local_param("time_zone"))
        new_classes = (
            BkData(self._clustering_config.new_cls_pattern_rt)
            .select(*NEW_CLASS_QUERY_FIELDS)
            .where(NEW_CLASS_SENSITIVITY_FIELD, "=", self.new_class_field)
            .time_range(start_time.timestamp, end_time.timestamp)
            .query()
        )
        return {new_class["signature"] for new_class in new_classes}
