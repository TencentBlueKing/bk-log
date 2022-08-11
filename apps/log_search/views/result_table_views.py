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
from rest_framework.response import Response
from apps.generic import APIViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import insert_permission_field
from apps.log_search.handlers.result_table import ResultTableHandler
from apps.log_search.serializers import (
    ResultTableAdaptSerializer,
    ResultTableDetailSerializer,
    ResultTableListSerializer,
    ResultTableTraceMatchSerializer,
)
from apps.log_search.models import Scenario
from apps.log_search.exceptions import (
    IndexDuplicateException,
    FieldsDateNotSameException,
    FieldsDateTypeNotSameException,
)

from apps.utils.drf import list_route


class ResultTablesViewSet(APIViewSet):
    """
    结果数据表
    """

    lookup_field = "result_table_id"
    lookup_value_regex = "[^/]+"

    def get_permissions(self):
        # TODO 鉴权逻辑需要细化
        return []
        # if self.action in ["adapt"]:
        #     return []
        # return [ViewBusinessPermission()]

    @insert_permission_field(
        id_field=lambda d: d.get("collector_config_id"),
        actions=[ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /result_table/?scenario_id=$scenario_id&storage_cluster_id=$storage_cluster_id&bk_biz_id=$bk_biz_id
        数据源-索引列表
        @apiDescription 获取集群索引列表（在新增索引集根据用户选择的场景&集群拉取）
        @apiName list_result_tables
        @apiGroup 06_ResultTables
        @apiParam {String} scenario_id 接入场景
        @apiParam {Int} bk_biz_id 业务ID，数据平台&采集接入场景提供
        @apiParam {Int} storage_cluster_id 集群ID，外部ES场景提供
        @apiParam {String} result_table_id 索引
        @apiSuccess {String} result_table_id 索引
        @apiSuccess {String} result_table_name_alias 索引别名
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "result_table_id": "591_a",
                    "result_table_name_alias": "中文名称",
                },
                {
                    "result_table_id": "log_login_11",
                    "result_table_name_alias": null,
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(ResultTableListSerializer)
        return Response(
            ResultTableHandler(data["scenario_id"], data.get("storage_cluster_id")).list(
                data.get("bk_biz_id"), data.get("result_table_id")
            )
        )

    def retrieve(self, request, *args, **kwargs):
        """
        @api {get} /result_table/$result_table_id/?scenario_id=$scenario_id&storage_cluster_id=$storage_cluster_id
        数据源-索引详情
        @apiDescription 获取结果数据表详细信息
        @apiGroup 06_ResultTables
        @apiName list_result_table_fields
        @apiParam {String} result_table_id 结果数据表ID
        @apiParam {String} scenario_id 接入场景
        @apiParam {Int} [bk_biz_id] 业务ID，数据平台场景
        @apiParam {Int} [storage_cluster_id] 集群ID，外部ES场景
        @apiSuccess {Object} fields 字段信息
        @apiSuccess {String} fields.field_type 字段类型
        @apiSuccess {String} fields.field_name 字段名称
        @apiSuccess {String} fields.field_alias 字段别名，如果此字段不为空，则在字段名称后面加上：（字段别名）
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "fields": [
                    {
                        "field_type": "string",
                        "field_name": "log",
                        "field_alias": "",
                    },
                    {
                        "field_type": "timestamp",
                        "field_name": "date",
                        "field_alias": "",
                    },
                    {
                        "field_type": "long",
                        "field_name": "server_id",
                        "field_alias": "",
                    }
                ],
                "date_candidate":[
                    {
                        "field_name": "timestamp",
                        "field_type": "date"
                    }
                ]
                "storage_cluster_id": "default",
                "storage_cluster_name": "default_name",
                "bk_biz_id": 2
            },
            "result": true
        }
        """
        data = self.params_valid(ResultTableDetailSerializer)
        result_table_id = kwargs.get("result_table_id")
        return Response(
            ResultTableHandler(data["scenario_id"], data.get("storage_cluster_id")).retrieve(result_table_id)
        )

    @list_route(methods=["POST"], url_path="adapt")
    def adapt(self, request, *args, **kwargs):
        """
        @api {post} /result_table/adapt/ 数据源-索引适配
        @apiDescription 检测两个索引是否可以加到同一个索引集，仅用于新建索引集-新增索引时匹配
        @apiGroup 06_ResultTables
        @apiName adapt_result_table
        @apiParam {String} scenario_id 接入场景
        @apiParam {Int} [storage_cluster_id] 数据源ID，外部ES场景
        @apiParam {Json} basic_index 源索引
        @apiParam {Json} append_index 待追加的索引ID
        @apiParamExample {Json} 请求参数
        {
            "scenario_id": "es",
            "storage_cluster_id": 1,
            "basic_index": {
                "index": "591_abc",
                "time_field": "dtEventTime",
                "time_field_type": "date"
            },
            "append_index": {
                "index": "591_xxx",
                "time_field": "dtEventTime",
                "time_field_type": "date"
            },
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        data = self.params_valid(ResultTableAdaptSerializer)
        basic_indices = data.get("basic_indices", [])
        basic_indices_index = [basic_index["index"] for basic_index in basic_indices]
        append_index = data["append_index"]

        # 数据平台不需要检查第一个索引
        if not basic_indices and data["scenario_id"] == Scenario.BKDATA:
            return Response()

        if append_index["index"] in basic_indices_index:
            raise IndexDuplicateException()

        # 第三方ES校验需要校验时间字段和类型是否一致
        if basic_indices and data["scenario_id"] == Scenario.ES:
            for basic_index in basic_indices:
                if basic_index["time_field"] != append_index["time_field"]:
                    raise FieldsDateNotSameException()
                if basic_index["time_field_type"] != append_index["time_field_type"]:
                    raise FieldsDateTypeNotSameException()

        return Response(
            ResultTableHandler(data["scenario_id"], data.get("storage_cluster_id")).adapt(
                basic_indices_index, append_index["index"]
            )
        )

    @list_route(methods=["POST"], url_path="trace_fields_match")
    def trace_fields_match(self, request, *args, **kwargs):
        """
        @api {post} /result_table/trace_fields_match/ 匹配索引集rt与trace字段
        @apiName trace_fields_match
        @apiGroup 06_ResultTables
        @apiParam {List[String]} indices 接入场景
        @apiParam {String} scenario_id 接入场景
        @apiParam {Int} [storage_cluster_id] 集群ID，外部ES场景
        @apiParamExample {json} 请求样例:
            {
                "indices": ["10082_bklog_asdf", "12321_bklog_asdf"],
                "scenario_id": "bkdata",
                "storage_cluster_id": 1
            }
        @apiSuccess {List[Dict]} item
        @apiSuccess {String} item.field_name 字段名称
        @apiSuccess {String} item.field_type 字段类型 MUST,SUGGEST,USER_DEFINE
        @apiSuccess {String} item.field_type_display 字段类型展示
        @apiSuccess {String} item.ch_name 中文名称
        @apiSuccess {String} item.data_type 数据类型
        @apiSuccess {String} item.match_result 匹配结果
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data":[
                {
                "field_name": "traceID",
                "field_type": "MUST",
                "field_type_display": "必须",
                "ch_name": "traceId",
                "data_type": "keyword",
                "match_result": "FIELD_MISS",
                "match_result_display": "字段缺失"
                }
            ]
        }
        """
        data = self.params_valid(ResultTableTraceMatchSerializer)
        result = ResultTableHandler(data.get("scenario_id"), data.get("storage_cluster_id")).trace_fields_match(
            data.get("indices")
        )
        return Response(result)
