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

from apps.api import BkLogApi
from apps.log_search.handlers.search.mapping_handlers import MappingHandlers
from apps.log_trace.handlers.trace_field_handlers import TraceMappingAdapter
from apps.utils.cache import cache_one_day


class PreSearchHandlers(object):
    def __init__(self):
        pass

    @classmethod
    def pre_check_fields(cls, indices: str, scenario_id: str, storage_cluster_id: int) -> dict:
        trace_type = None
        result_table_id_list: list = indices.split(",")
        if not result_table_id_list:
            return {"default_sort_tag": False, "trace_type": trace_type}
        result_table_id, *_ = result_table_id_list
        # get fields from cache
        fields = cls._get_fields(
            result_table_id=result_table_id, scenario_id=scenario_id, storage_cluster_id=storage_cluster_id
        )
        # Trace type
        trace_type = TraceMappingAdapter.adapter(fields)

        fields_list: list = [x["field"] for x in fields]
        if ("gseindex" in fields_list and "_iteration_idx" in fields_list) or (
            "gseIndex" in fields_list and "iterationIndex" in fields_list
        ):
            return {"default_sort_tag": True, "trace_type": trace_type, "fields_from_es": fields}
        return {"default_sort_tag": False, "trace_type": trace_type, "fields_from_es": fields}

    @staticmethod
    @cache_one_day("fields_{result_table_id}")
    def _get_fields(*, result_table_id, scenario_id, storage_cluster_id):
        mapping_from_es = BkLogApi.mapping(
            {"indices": result_table_id, "scenario_id": scenario_id, "storage_cluster_id": storage_cluster_id}
        )
        property_dict: dict = MappingHandlers.find_property_dict(mapping_from_es)
        fields_result: list = MappingHandlers.get_all_index_fields_by_mapping(property_dict)
        return [
            {
                "field_type": field["field_type"],
                "field_name": field["field_name"],
                "field": field["field_name"],
                "field_alias": field.get("field_alias"),
                "is_display": False,
                "is_editable": True,
                "tag": field.get("tag", "metric"),
                "es_doc_values": field.get("es_doc_values", False),
            }
            for field in fields_result
        ]
