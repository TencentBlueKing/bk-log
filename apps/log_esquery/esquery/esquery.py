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
import json

from typing import List, Dict, Any, Tuple
from dateutil import tz

from apps.log_esquery.type_constants import (
    type_search_dict,
    type_index_set_string,
    type_time_range_dict,
    type_addition,
)
from apps.log_esquery.esquery.builder.query_time_builder import QueryTimeBuilder
from apps.log_esquery.esquery.builder.query_string_builder import QueryStringBuilder
from apps.log_esquery.esquery.builder.query_filter_builder import QueryFilterBuilder
from apps.log_esquery.esquery.builder.query_index_optimizer import QueryIndexOptimizer
from apps.log_esquery.esquery.builder.query_sort_builder import QuerySortBuilder
from apps.log_esquery.esquery.dsl_builder.dsl_builder import DslBuilder
from apps.log_search.models import Scenario
from apps.log_esquery.esquery.client.QueryClient import QueryClient
from apps.utils.log import logger
from apps.log_search.exceptions import ScenarioQueryIndexFailException, ScenarioNotSupportedException
from apps.utils.time_handler import generate_time_range


class EsQuery(object):
    def __init__(self, search_dict: type_search_dict):

        self.search_dict: Dict[str, Any] = search_dict

    def _init_common_args(self):
        # 初始刷查询场景类型 bkdata log 或者 es, 以及连接信息ID
        scenario_id: str = self.search_dict.get("scenario_id", Scenario.LOG)
        indices: type_index_set_string = self.search_dict.get("indices")
        storage_cluster_id: int = self.search_dict.get("storage_cluster_id", -1)
        return scenario_id, indices, storage_cluster_id

    def _init_time_field_args(self):
        time_field: str = self.search_dict.get("time_field", "")
        time_field_type: str = self.search_dict.get("time_field_type", "date")
        time_field_unit: str = self.search_dict.get("time_field_unit", "second")
        return time_field, time_field_type, time_field_unit

    def _init_include_time_args(self):
        include_start_time: bool = self.search_dict.get("include_start_time", True)
        include_end_time: bool = self.search_dict.get("include_end_time", True)
        return include_start_time, include_end_time

    def _init_time_args(self):
        start_time: str = self.search_dict.get("start_time")
        end_time: str = self.search_dict.get("end_time")
        time_range: str = self.search_dict.get("time_range", None)
        time_zone: str = self.search_dict.get("time_zone", None)
        use_time_range: bool = self.search_dict.get("use_time_range", True)
        return start_time, end_time, time_range, time_zone, use_time_range

    def _init_bkdata_args(self):
        bkdata_authentication_method: str = self.search_dict.get("bkdata_authentication_method", "")
        bkdata_data_token: str = self.search_dict.get("bkdata_data_token", "")
        return bkdata_authentication_method, bkdata_data_token

    def _init_search_after_args(self):
        search_after = self.search_dict.get("search_after", [])
        track_total_hits = self.search_dict.get("track_total_hits", False)
        return search_after, track_total_hits

    def _optimizer(self, indices, scenario_id, start_time, end_time, time_zone, use_time_range):

        # 优化query_string
        query_string: str = self.search_dict.get("query_string")
        query_string = QueryStringBuilder(query_string).query_string

        # 优化filter
        addition: type_addition = self.search_dict.get("filter", [])
        filter_dict_list: type_addition = QueryFilterBuilder(addition).filter_dict_list

        # 优化查询索引
        index: str = QueryIndexOptimizer(
            indices,
            scenario_id,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            use_time_range=use_time_range,
        ).index

        # 优化排序,需要预查询介入，需要client
        sort_list: List[List[str, str]] = self.search_dict.get("sort_list", [])
        sort_tuple: Tuple = tuple(QuerySortBuilder(sort_list).sort_list)
        return query_string, filter_dict_list, index, sort_tuple

    def _init_other_args(self):
        # 查询条目
        size: int = self.search_dict.get("size")

        # 查询开始位置
        start: int = self.search_dict.get("start")

        # 透传aggs聚合
        aggs: Dict = self.search_dict.get("aggs")

        # 透传高亮
        highlight: Dict = self.search_dict.get("highlight")

        # scroll
        scroll = self.search_dict.get("scroll", None)

        # collapse
        collapse = self.search_dict.get("collapse")
        return size, start, aggs, highlight, scroll, collapse

    def compatibility_result(self, result):
        # 兼容ES不同版本的Total
        if "hits" in result and "total" in result["hits"] and isinstance(result["hits"]["total"], dict):
            result["hits"]["total"] = result["hits"]["total"]["value"]
        return result

    def search(self):
        scenario_id, indices, storage_cluster_id = self._init_common_args()
        time_field, time_field_type, time_field_unit = self._init_time_field_args()
        include_start_time, include_end_time = self._init_include_time_args()
        start_time, end_time, time_range, time_zone, use_time_range = self._init_time_args()
        # 统一开始结束时间
        start_time, end_time = self.time_start_end_builder(time_range, start_time, end_time, time_zone)
        bkdata_authentication_method, bkdata_data_token = self._init_bkdata_args()
        search_after, track_total_hits = self._init_search_after_args()

        time_range_dict: type_time_range_dict = QueryTimeBuilder(
            time_field,
            start_time,
            end_time,
            time_field_type=time_field_type,
            time_field_unit=time_field_unit,
            include_start_time=include_start_time,
            include_end_time=include_end_time,
        ).time_range_dict

        query_string, filter_dict_list, index, sort_tuple = self._optimizer(
            indices, scenario_id, start_time, end_time, time_zone, use_time_range
        )
        size, start, aggs, highlight, scroll, collapse = self._init_other_args()
        mappings = self.mapping()

        # 调用DSL生成器
        body = DslBuilder(
            search_string=query_string,
            filter_dict_list=filter_dict_list,
            time_range_dict=time_range_dict,
            sort_tuple=sort_tuple,
            size=size,
            begin=start,
            aggs=aggs,
            highlight=highlight,
            collapse=collapse,
            search_after=search_after,
            use_time_range=use_time_range,
            mappings=mappings,
        ).body

        logger.info(f"scenario_id => [{scenario_id}], indices => [{index}], body => [{body}]")

        if self.search_dict.get("debug"):
            return {"scenario": scenario_id, "indices": index, "body": body}

        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
            bkdata_authentication_method=bkdata_authentication_method,
            bkdata_data_token=bkdata_data_token,
        ).get_instance()

        logger.info(f"[Esquery] scenario_id => [{scenario_id}], indices => [{index}], body => [{body}]")

        result: Dict[str:Any] = client.query(index, body, scroll=scroll, track_total_hits=track_total_hits)

        return self.compatibility_result(result)

    def scroll(self):
        # 调用客户端执行scroll
        scenario_id, indices, storage_cluster_id = self._init_common_args()

        # TODO 暂不支持bkdata场景
        if scenario_id == Scenario.BKDATA:
            raise ScenarioNotSupportedException(
                ScenarioNotSupportedException.MESSAGE.format(scenario_id=Scenario.BKDATA)
            )

        # scroll_id
        scroll_id: str = self.search_dict.get("scroll_id")

        # scroll
        scroll: str = self.search_dict.get("scroll")

        client = QueryClient(scenario_id, storage_cluster_id=storage_cluster_id).get_instance()

        result = client.scroll(indices, scroll_id, scroll)

        return result

    # 调用客户端执行dsl
    def dsl(self):
        dsl: dict = self.search_dict.get("body", {})
        scenario_id, index_set_string, storage_cluster_id = self._init_common_args()
        bkdata_authentication_method, bkdata_data_token = self._init_bkdata_args()
        # 获取client
        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
            bkdata_authentication_method=bkdata_authentication_method,
            bkdata_data_token=bkdata_data_token,
        ).get_instance()

        index = index_set_string

        logger.info(f"[esquery_dsl] index => [{index}], dsl => [{dsl}]")

        result: Dict = client.query(index, dsl)
        result = self.compatibility_result(result)
        result.update({"dsl": json.dumps(dsl)})
        return result

    def _optimizer_mapping_time_range(self, index, scenario_id, start_time, end_time, time_zone):
        if start_time and end_time:
            # 如果提供了时间范围，则按时间范围查
            time_start_end: Tuple = self.time_start_end_builder("customized", start_time, end_time, time_zone)
            start_time, end_time = time_start_end
            index: str = QueryIndexOptimizer(
                index, scenario_id, start_time=start_time, end_time=end_time, time_zone=time_zone
            ).index
        return index

    def mapping(self):
        # 调用客户端执行mapping
        scenario_id, index_set_string, storage_cluster_id = self._init_common_args()
        bkdata_authentication_method, bkdata_data_token = self._init_bkdata_args()
        start_time, end_time, _, time_zone, __ = self._init_time_args()
        index_set_string = self._optimizer_mapping_time_range(
            index_set_string, scenario_id, start_time, end_time, time_zone
        )
        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
            bkdata_authentication_method=bkdata_authentication_method,
            bkdata_data_token=bkdata_data_token,
        ).get_instance()

        result: Dict = client.mapping(index_set_string)

        result_key_list: list = list(result)
        sorted_result_key_list: list = sorted(result_key_list, key=lambda x: x, reverse=True)
        final_result_list: list = []
        for key in sorted_result_key_list:
            final_result_list.append({key: result.get(key)})
        return final_result_list

    def indices(self):
        # 索引集列表查询

        scenario_id, indices, storage_cluster_id = self._init_common_args()
        bk_biz_id: int = self.search_dict.get("bk_biz_id")
        with_storage: bool = self.search_dict.get("with_storage", False)
        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
        ).get_instance()

        if scenario_id == Scenario.BKDATA and not bk_biz_id:
            raise ScenarioQueryIndexFailException(
                ScenarioQueryIndexFailException.MESSAGE.format(es_fail_reason="get index list with bk_biz_id None")
            )

        return client.indices(bk_biz_id=bk_biz_id, result_table_id=indices, with_storage=with_storage)

    def cluster_stats(self):
        scenario_id, indices, storage_cluster_id = self._init_common_args()
        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
        ).get_instance()
        return client.cluster_stats(indices)

    def cluster_nodes_stats(self):
        client = self._get_client()
        indices = self.search_dict.get("indices")
        return client.cluster_nodes_stats(indices)

    def get_cluster_info(self):
        # 获取集群信息
        scenario_id, indices, storage_cluster_id = self._init_common_args()

        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
        ).get_instance()
        return client.get_cluster_info(result_table_id=indices)

    def cat_indices(self):
        scenario_id, indices, storage_cluster_id = self._init_common_args()
        bytes = self.search_dict.get("bytes")
        client = QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
        ).get_instance()
        return client.cat_indices(index=indices, bytes=bytes)

    def es_route(self):
        client = self._get_client()
        url = self.search_dict.get("url", "/")
        indices: str = self.search_dict.get("indices")
        return client.es_route(url, indices)

    def _get_client(self):
        scenario_id: str = self.search_dict.get("scenario_id")
        storage_cluster_id: int = self.search_dict.get("storage_cluster_id", -1)

        return QueryClient(
            scenario_id,
            storage_cluster_id=storage_cluster_id,
        ).get_instance()

    @staticmethod
    def time_start_end_builder(time_range: str, start_time: str, end_time: str, time_zone=None) -> Tuple:
        time_zone = time_zone
        local_time_zone = tz.gettz(time_zone) if time_zone else tz.tzlocal()

        start_time, end_time = generate_time_range(time_range, start_time, end_time, local_time_zone)
        logger.info(
            f"[time_start_end_builder] start_time=>{start_time}, end_time=>{end_time}, "
            f"time_zone=>{time_zone}, local_time_zone=>{local_time_zone}, "
            f"output: {start_time.timestamp} {end_time.timestamp}"
        )
        return start_time, end_time
