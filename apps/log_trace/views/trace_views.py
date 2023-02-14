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
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.response import Response
from apps.utils.drf import detail_route
from apps.generic import APIViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import InstanceActionPermission, ViewBusinessPermission, insert_permission_field
from apps.log_trace.constants import FIELDS_SCOPE_VALUE
from apps.exceptions import ValidationError
from apps.log_trace.serializers import (
    TraceIndexSetScopeSerializer,
    TraceSearchAttrSerializer,
    TraceSearchTraceIdAttrSerializer,
)
from apps.log_trace.handlers.trace_handlers import TraceHandler
from apps.log_trace.handlers.trace_config_handlers import TraceConfigHandlers


class TraceViewSet(APIViewSet):
    serializer_class = serializers.Serializer
    # 根据用户输入的result_table_id确定用户是否有访问查询接口权限
    lookup_field = "index_set_id"

    def get_permissions(self):
        if self.action == "list":
            return [ViewBusinessPermission()]

        return [InstanceActionPermission([ActionEnum.SEARCH_LOG], ResourceEnum.INDICES)]

    @insert_permission_field(
        actions=[ActionEnum.SEARCH_LOG],
        resource_meta=ResourceEnum.INDICES,
        id_field=lambda d: d["index_set_id"],
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /trace/index_set/?bk_biz_id=bk_biz_id 01_Trace-索引集列表
        @apiDescription 用户有权限的索引集列表
        @apiName trace_index_set
        @apiGroup 17_Trace
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Int} index_set_id 索引集ID
        @apiSuccess {String} index_set_name 索引集名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "index_set_id": 1,
                    "index_set_name": "索引集名称",
                    "scenario_id": "接入场景",
                    "scenario_name": "接入场景名称",
                    "storage_cluster_id": "存储集群ID",
                    "indices": [
                        {
                            "result_table_id": "结果表id",
                            "result_table_name": "结果表名称"
                        }
                    ]
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(TraceIndexSetScopeSerializer)
        return Response(TraceConfigHandlers.get_user_trace_index_set(data["space_uid"], request))

    @detail_route(methods=["POST"], url_path="search/scatter")
    def scatter(self, request, index_set_id=None):
        """
        @api {post} /trace/index_set/$index_set_id/search/scatter/ 04_Trace-散点图表搜索
        @apiName graph_search_trace_log
        @apiDescription 生成散点图
        @apiGroup 17_Trace
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParam {String} time_range 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} addition 搜索条件
        @apiParam {Int} size 条数
        @apiParamExample {Json} 请求参数
        {
          "start_time": "2019-06-11 00:00:00",
          "end_time": "2019-06-12 11:11:11",
          "time_range": "customized",
          "keyword": "error",
          "addition": [
            {
              "key": "tag.service",
              "method": "is",
              "value": "login_service",
              "condition": "and", (默认不传是and，只支持and, or)
              "type": "field" (默认field目前支持field，其他无效)
            },
            {
              "key": "tag.scenario",
              "method": "is",
              "value": "login",
              "condition": "and", (默认不传是and，只支持and, or)
              "type": "field" (默认field目前支持field，其他无效)
            },
            {
              "key": "operationname",
              "method": "is",
              "value": "login",
              "condition": "and", (默认不传是and，只支持and, or)
              "type": "field" (默认field目前支持field，其他无效)
            },
          ],
          "size": 9999
        }

        @apiSuccessExample {json} 成功返回:
        {
          "message": "",
          "code": 0,
          "data": {
            "total": 100,
            "took": 0.29,
            scatter: [
                {
                    "label": "成功",
                    "pointBackgroundColor": "#45E35F",
                    "borderColor": "#45E35F",
                    "pointRadius": 5,
                    "data": [
                        {
                            "x": "2020-04-10 16:02:04",
                            "y": 6600,
                            "traceID": "4mk4X2gLRfuWQpb9g997fkdP3VC5E0h6",
                            "spanID": "xUz20f4m5Fu8AUV7gGjKA5hee6kJX8ZX",
                            "startTime": 1586505724179,
                            "duration": 6600,
                            "error": true,
                            "result_code": 0
                        },
                        {
                            "x": "2020-04-10 16:02:04",
                            "y": 22800,
                            "traceID": "WXe1Ns8W0OUFijqiBNL59YAFGJzLt9nE",
                            "spanID": "NrK9EsGZu8BM748xkUFDA2kQTnivfmuH",
                            "startTime": 1586505724297,
                            "duration": 22800,
                            "error": true,
                            "result_code": 0
                        }
                    ]
                },
                {
                    "label": "失败",
                    "pointBackgroundColor": "#FB9C9C",
                    "borderColor": "#FB9C9C",
                    "pointRadius": 5,
                    "data": [
                        {
                            "x": "2020-04-10 16:02:04",
                            "y": 10200,
                            "traceID": "4mk4X2gLRfuWQpb9g997fkdP3VC5E0h6",
                            "spanID": "ClPztofjKbDF0QOqB3QnBGb0Zg5GndJN",
                            "startTime": 1586505724178,
                            "duration": 10200,
                            "error": false,
                            "result_code": 0
                        },
                        {
                            "x": "2020-04-10 16:02:04",
                            "y": 13800,
                            "traceID": "4mk4X2gLRfuWQpb9g997fkdP3VC5E0h6",
                            "spanID": "WAV5UPSlyhKb294tuLtMBlcJ2Tz9AhvB",
                            "startTime": 1586505724178,
                            "duration": 13800,
                            "error": false,
                            "result_code": 0
                        }
                    ]
                }
            ]
          },
          "result": true
        }
        """
        data = self.params_valid(TraceSearchAttrSerializer)
        return Response(TraceHandler(index_set_id).scatter(data))

    @detail_route(methods=["POST"], url_path="search")
    def search(self, request, index_set_id=None):
        """
        @api {post} /trace/index_set/$index_set_id/search/ 05_Trace-通用搜索
        @apiName key_search_trace_log
        @apiDescription 查询
        @apiGroup 17_Trace
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParam {String} time_range 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} addition 搜索条件
        @apiParam {Int} begin 起始位置
        @apiParam {Int} size 条数
        @apiParamExample {Json} 请求参数
        {
          "start_time": "2019-06-11 00:00:00",
          "end_time": "2019-06-12 11:11:11",
          "time_range": "customized",
          "keyword": "error",
          "addition": [
            {
              "key": "tag.service",
              "method": "is",
              "value": "login_service",
              "condition": "and", (默认不传是and，只支持andor)
              "type": "field" (默认field目前支持field，其他无效)
            },
            {
              "key": "tag.scenario",
              "method": "is",
              "value": "login",
              "condition": "and", (默认不传是and，只支持andor)
              "type": "field" (默认field目前支持field，其他无效)
            },
            {
              "key": "operationname",
              "method": "is",
              "value": "login",
              "condition": "and", (默认不传是and，只支持andor)
              "type": "field"(默认field目前支持field，其他无效)
            },
          ],
          "begin": 0,
          "size": 500
        }

        @apiSuccessExample {json} 成功返回:
        {
          "message": "",
          "code": 0,
          "data": {
            "total": 100,
            "took": 0.29,
            "list": [
              {
                "traceID": "18efccf037d85f2b",
                "spanID": "3011b0f5facad739",
                "flags": 1,
                "operationName": "HTTP GET /route",
                "references": [
                  {
                    "refType": "CHILD_OF",
                    "traceID": "18efccf037d85f2b",
                    "spanID": "5697b54e9795f849"
                  }
                ],
                "startTime": 1583829446893921,
                "startTimeMillis": 1583829446893,
                "duration": 52230,
                "tags": [

                ],
                "tag": {
                  "service": "a",
                  "scenario": "b""component": "net/http",
                  "http@method": "GET",
                  "http@status_code": 200,
                  "http@url": "/route?dropoff=728%2C326\u0026pickup=139%2C24",
                  "internal@span@format": "proto",
                  "span@kind": "server"
                },
                "logs": [
                  {
                    "timestamp": 1583829446893960,
                    "fields": [
                      {
                        "key": "event",
                        "type": "string",
                        "value": "HTTP request received"
                      },
                      {
                        "key": "level",
                        "type": "string",
                        "value": "info"
                      },
                      {
                        "key": "method",
                        "type": "string",
                        "value": "GET"
                      },
                      {
                        "key": "url",
                        "type": "string",
                        "value": "/route?dropoff=728%2C326\u0026pickup=139%2C24"
                      }
                    ]
                  },
                ],
              },
            ],
            "fields": {
              "agent": {
                "max_length": 101
              },
              "bytes": {
                "max_length": 4
              },

            },
            "origin_log_list": [

            ],
            "aggs": {
              "tag.service": [["login_service", 10]],
              "tag.scenario": [["login", 11]],
              "duration": [[10, 100]]
            }
          },
          "result": true
        }
        """
        data = self.params_valid(TraceSearchAttrSerializer)
        return Response(TraceHandler(index_set_id).search(data))

    @detail_route(methods=["POST"], url_path="search/trace_id")
    def trace_id(self, request, index_set_id=None):
        """
        @api {post} /trace/index_set/$index_set_id/search/trace_id/ 06_Trace-TraceID搜索
        @apiName trace_id_search_trace_log
        @apiDescription TraceId查询，生成时间线甘特图,生成树形图
        @apiGroup 17_Trace
        @apiParam {String} startTime 当前日志的startTime字段信息
        @apiParam {String} traceID 搜索条件traceID
        @apiParamExample {Json} 请求参数
        {
          "startTime": "1583829446893921",
          "traceID": "18efccf037d85f2b"
        }

        @apiSuccessExample {json} 成功返回:
        {
          "message": "",
          "code": 0,
          "data": {
            "total": 100,
            "took": 0.29,
            "list": []
            "tree": {
                "group": "3011b0f5facad739",
                "from": 1583829446893921,
                "to": 1583829446946151，
                "unit": "ms",
                "parentId": None,
                "traceID": "18efccf037d85f2b",
                "spanID": "5697b54e9795f849",
                ……
                "children": [
                    {
                        "group": "3011b0f5facad739",
                        "from": 1583829446893921,
                        "to": 1583829446946151，"unit": "ms",
                        "parentId": 5697b54e9795f849, (关注)
                        "traceID": "18efccf037d85f2b", (关注)
                        "spanID": "3011b0f5facad739",
                        ……
                        "children": []
                    },
                    {
                        "group": "3011b0f5facad739",
                        "from": 1583829446893921,
                        "to": 1583829446946151，"unit": "ms",
                        "parentId": 5697b54e9795f849, (关注)
                        "traceID": "18efccf037d85f2b", (关注)
                        "spanID": "3011b0f5facad741",
                        ……
                        "children": []
                    }

                ]
            }

          },
          "result": true
        }
        """
        data = self.params_valid(TraceSearchTraceIdAttrSerializer)
        return Response(TraceHandler(index_set_id).trace_id(data))

    @detail_route(methods=["GET"], url_path="fields")
    def fields(self, request, *args, **kwargs):
        """
        @api {get} /trace/index_set/$index_set_id/fields/?scope=list 07_Trace-获取索引集配置
        @apiDescription 获取用户在某个索引集的配置
        @apiName list_trace_index_set_user_config
        @apiGroup 17_Trace
        @apiParam {String} scope 范围（trace、trace_detail）
        @apiSuccess {String} display_fields 列表页显示的字段
        @apiSuccess {String} fields.field_name 字段名
        @apiSuccess {String} fields.field_alias 字段中文称 (为空时会直接取description)
        @apiSuccess {String} fields.description 字段说明
        @apiSuccess {String} fields.field_type 字段类型
        @apiSuccess {Bool} fields.is_display 是否显示给用户
        @apiSuccess {Bool} fields.is_editable 是否可以编辑（是否显示）
        @apiSuccess {Bool} fields.es_doc_values 是否聚合字段
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "ip_topo_switch": true,
                "context_search_usable": false,
                "realtime_search_usable": false,
                "display_fields": ["dtEventTimeStamp", "log"],
                "fields": [
                    {
                        "field_name": "log",
                        "field_alias": "日志",
                        "field_type": "text",
                        "is_display": true,
                        "is_editable": true,
                        "description": "日志",
                        "es_doc_values": false
                    },
                    {
                        "field_name": "dtEventTimeStamp",
                        "field_alias": "时间",
                        "field_type": "date",
                        "is_display": true,
                        "is_editable": true,
                        "description": "描述",
                        "es_doc_values": true
                    }
                ],
                "sort_list": [
                    ["aaa", "desc"],
                    ["bbb", "asc"]
                ],
                "trace": {
                    "trace_type": "jaeger/zipkin/log",
                    "additions": [
                        {
                            "fields_alias": "场景",
                            "field_name": "tag.scene",
                            "show_type": "select",
                            "display": true,
                            "tips": "请选择"
                        },
                        {
                            "fields_alias": "服务",
                            "field_name": "tags.local_service",
                            "show_type": "select",
                            "display": true,
                            "tips": "请选择"
                        },
                        {
                            "fields_alias": "操作名",
                            "field_name": "operationName",
                            "show_type": "select",
                            "display": true,
                            "tips": "请选择"
                        }

                    ],
                    "advance_additions": [
                        {
                            "fields_alias": "耗时min_max",
                            "field_name": "duration",
                            "show_type": "duration",
                            "display": true,
                            "tips": "0"
                        },
                        {
                            "fields_alias": "返回码",
                            "field_name": "tag.result_code",
                            "show_type": "text",
                            "display": true,
                            "tips": "0"
                        }

                    ],
                    "charts": [
                        {
                            "chart_alias": "line"
                            "chart_name": "曲线图",
                            "field_name": "tag.result_code",
                            "show_type": null,
                            "display": true,
                            "tips": "曲线图"
                        },
                        {
                            "chart_alias": "scatter"
                            "chart_name": "散点图",
                            "field_name": ["x", "y"],
                            "show_type": null,
                            "display": true,
                            "tips": "曲线图"
                        },

                    ],
                    "chart_tree": {
                        "chart_name": _("调用关系图"),
                        "display_field": "operationName",
                        "error_field": "tag.error",
                        "span_width": 120
                        "show_type": None,
                        "display": True,
                        "tips": _("operationName调用关系")
                    },
                    "log_detail": [
                    ]
                }
            },
            "result": true
        }
        """
        index_set_id = kwargs.get("index_set_id", "")
        scope = request.GET.get("scope")
        if scope not in FIELDS_SCOPE_VALUE:
            raise ValidationError(_("scope取值范围：trace、trace_detail、trace_detail_log"))
        return Response(TraceHandler(index_set_id).fields(scope=scope))
