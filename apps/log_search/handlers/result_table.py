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
from typing import List

from apps.log_search.constants import TraceMatchResult, TraceMatchFieldType
from apps.log_search.exceptions import (
    IndexCrossBusinessException,
    IndexCrossClusterException,
    FieldsTypeConsistencyException,
    MappingEmptyException,
)
from apps.log_search.models import Scenario
from apps.log_trace.handlers.trace_field_handlers import (
    TRACE_SUGGEST_FIELD,
    LOG_FIELD_ADAPTER_META,
    TRACE_DESC_MAPPING,
)
from apps.utils import APIModel
from apps.api import BkLogApi, BkDataAuthApi
from apps.log_search.handlers.search.mapping_handlers import MappingHandlers
from apps.utils.db import array_group
from apps.utils.local import get_request_username


class ResultTableHandler(APIModel):
    def __init__(self, scenario_id, storage_cluster_id=None, bk_username=None):
        super().__init__()
        self.scenario_id = scenario_id
        self.storage_cluster_id = storage_cluster_id
        self.username = bk_username if bk_username else get_request_username()

    def list(self, bk_biz_id=None, result_table_id=None):
        """
        查询索引列表
        :param bk_biz_id:
        :param result_table_id:
        :return:
        """
        result = BkLogApi.indices(
            {
                "bk_biz_id": bk_biz_id,
                "indices": result_table_id,
                "scenario_id": self.scenario_id,
                "storage_cluster_id": self.storage_cluster_id,
                "with_storage": True,
            }
        )

        # 如果是数据平台则只显示用户有管理权限的RT列表
        if self.scenario_id == Scenario.BKDATA:
            scopes = BkDataAuthApi.get_user_perm_scope(
                {"user_id": self.username, "action_id": "result_table.manage_auth", "show_admin_scopes": True}
            )
            authorized_tables = [scope["result_table_id"] for scope in scopes if scope.get("result_table_id")]
            result = [index for index in result if index["result_table_id"] in authorized_tables]
        return result

    def retrieve(self, result_table_id):
        """
        查询结果表详情
        """
        kwargs = {
            "scenario_id": self.scenario_id,
            "storage_cluster_id": self.storage_cluster_id,
            "indices": result_table_id,
            "bk_username": self.username,
            "bkdata_authentication_method": "user",
        }
        mapping_list = BkLogApi.mapping(kwargs)
        if not mapping_list:
            raise MappingEmptyException(MappingEmptyException.MESSAGE.format(result_table_id=result_table_id))

        date_candidate = MappingHandlers.get_date_candidate(mapping_list)
        property_dict: dict = MappingHandlers(
            result_table_id, -1, self.scenario_id, self.storage_cluster_id
        ).find_merged_property(mapping_list)
        field_list: list = MappingHandlers.get_all_index_fields_by_mapping(property_dict)
        index_retrieve = {
            "date_candidate": date_candidate,
            "fields": [
                {
                    "field_type": field["field_type"],
                    "field_name": field["field_name"],
                    "field_alias": field.get("field_alias"),
                }
                for field in field_list
            ],
        }

        # 获取集群信息
        cluster_info = BkLogApi.cluster(kwargs)
        index_retrieve.update(
            {
                "storage_cluster_id": cluster_info.get("storage_cluster_id"),
                "storage_cluster_name": cluster_info.get("storage_cluster_name"),
                "bk_biz_id": cluster_info.get("bk_biz_id"),
            }
        )
        return index_retrieve

    def adapt(self, basic_indices: List[str], append_index):
        """
        1、检查两索引字段类型是否一致；
        2、检查两索引时间字段和类型是否一致；
        :param basic_index:
        :param append_index:
        :param raise_exception: 是否抛出异常
        :return:
        """
        basic_detail = self.retrieve(",".join(basic_indices)) if basic_indices else {}
        append_detail = self.retrieve(append_index)

        basic_fields = basic_detail.get("fields", [])
        append_fields = append_detail.get("fields", [])

        # 如果是第一个索引，则只判断新增的索引是否冲突
        if not basic_indices and append_fields:
            return append_fields

        # 采集接入：检查跨集群&检查跨业务
        if self.scenario_id == Scenario.LOG:
            basic_storage_id = basic_detail.get("storage_cluster_id")
            append_storage_id = append_detail.get("storage_cluster_id")
            if not basic_storage_id or not append_storage_id or basic_storage_id != append_storage_id:
                raise IndexCrossClusterException()

            if (
                not basic_detail["bk_biz_id"]
                or not append_detail["bk_biz_id"]
                or basic_detail["bk_biz_id"] != append_detail["bk_biz_id"]
            ):
                raise IndexCrossBusinessException()

        return self.check_fields_consistency(basic_fields, append_fields, raise_exception=True)

    @staticmethod
    def check_fields_consistency(fields_one, fields_two, raise_exception=False):
        """
        校验索引字段类型的一致性
        :param fields_one: 字段列表一
        :param fields_two: 字段列表二
        :param raise_exception: 是否抛出异常
        :return: Boolean
        """
        basic_fields = {}
        for _field in fields_one:
            basic_fields[_field["field_name"]] = _field["field_type"]

        not_consistency_fields = []
        for _field in fields_two:
            field_name = _field["field_name"]
            basic_type = basic_fields.get(field_name)
            if basic_type and basic_type != _field["field_type"]:
                not_consistency_fields.append(field_name)
        if not_consistency_fields:
            if raise_exception:
                raise FieldsTypeConsistencyException(
                    FieldsTypeConsistencyException.MESSAGE.format(field_type=",".join(not_consistency_fields))
                )
            else:
                return False
        return True

    def trace_fields_match(self, indices):
        index_list: list = indices
        rt_handler = ResultTableHandler(self.scenario_id, self.storage_cluster_id)
        rt_info = rt_handler.retrieve(",".join(index_list))
        fields = rt_info.get("fields")
        fields_map = array_group(fields, "field_name", True)
        result = []
        # 处理必须字段
        result.extend(self._build_match_result_set(TraceMatchFieldType.MUST.value, fields_map, LOG_FIELD_ADAPTER_META))
        # 建议字段
        result.extend(self._build_match_result_set(TraceMatchFieldType.SUGGEST.value, fields_map, TRACE_SUGGEST_FIELD))
        for field, field_info in fields_map.items():
            result.append(
                self._build_match_result(
                    field,
                    TraceMatchFieldType.USER_DEFINE.value,
                    field_info["field_alias"],
                    field_info["field_type"],
                    TraceMatchResult.OTHER.value,
                )
            )
        return result

    def _build_match_result_set(self, field_type, index_set_fields, trace_fields):
        result = []
        for field, field_types in trace_fields.items():
            ch_name = TRACE_DESC_MAPPING[field]
            if field in index_set_fields:
                match_result = TraceMatchResult.SUCCESS
                ch_name = index_set_fields[field]["field_alias"]
                field_actual_type = index_set_fields[field]["field_type"]
                if index_set_fields[field]["field_type"] not in field_types:
                    match_result = TraceMatchResult.TYPE_NOT_MATCH
                    field_actual_type = f"{'/'.join(field_types)}({field_actual_type})"
                result.append(
                    self._build_match_result(field, field_type, ch_name, field_actual_type, match_result.value)
                )
                index_set_fields.pop(field)
                continue
            result.append(
                self._build_match_result(
                    field, field_type, ch_name, "/".join(field_types), TraceMatchResult.FIELD_MISS.value
                )
            )
        return result

    def _build_match_result(self, field_name, field_type, ch_name, data_type, match_result):
        return {
            "field_name": field_name,
            "field_type": field_type,
            "field_type_display": TraceMatchFieldType.get_choice_label(field_type),
            "ch_name": ch_name,
            "data_type": data_type,
            "match_result": match_result,
            "match_result_display": TraceMatchResult.get_choice_label(match_result),
        }
