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
import json

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from apps.log_trace.handlers.trace_handlers import TraceHandler
from apps.utils.drf import list_route, detail_route
from apps.utils.log import logger
from apps.generic import APIViewSet
from apps.log_search.permission import Permission as JwtPermission
from apps.grafana.authentication import NoCsrfSessionAuthentication
from apps.grafana.handlers.home_dashboard import patch_home_panels
from apps.grafana.handlers.query import GrafanaQueryHandler
from apps.grafana.serializers import (
    GetVariableValueSerializer,
    GetVariableFieldSerializer,
    GetMetricListSerializer,
    TargetTreeSerializer,
    QuerySerializer,
    QueryLogSerializer,
    DimensionSerializer,
    TracesSerializer,
)

from apps.iam import ActionEnum, Permission, ResourceEnum
from apps.iam.handlers.drf import BusinessActionPermission, InstanceActionPermission
from apps.log_search.handlers.biz import BizHandler
from bk_dataview.grafana.views import ProxyView


class GrafanaProxyView(ProxyView):
    def get_request_headers(self, request):
        headers = super(GrafanaProxyView, self).get_request_headers(request)

        is_dashboard_api = request.path.rstrip("/").endswith("/api/dashboards/db")
        is_folder_api = request.path.rstrip("/").endswith("/api/folders")

        if request.method == "POST" and (is_dashboard_api or is_folder_api):
            # 先判断是否有权限编辑
            has_manage_permission = Permission().is_allowed(
                action=ActionEnum.MANAGE_DASHBOARD,
                resources=[ResourceEnum.BUSINESS.create_instance(request.org_name)],
            )
            if has_manage_permission or request.user.is_superuser:
                headers["X-WEBAUTH-USER"] = "admin"

        return headers

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        response = super(GrafanaProxyView, self).dispatch(request, *args, **kwargs)

        # 这里对 Home 仪表盘进行 patch，替换为指定的面板
        if request.method == "GET" and request.path.rstrip("/").endswith("/grafana/api/dashboards/home"):
            try:
                origin_content = json.loads(response.content)
                patched_content = json.dumps(patch_home_panels(origin_content))
                return HttpResponse(patched_content, status=response.status_code)
            except Exception as e:  # pylint: disable=broad-except
                logger.exception("patch home panels error: {}".format(e))
                # 异常则不替换了
                return response
        return response


class GrafanaTraceViewSet(APIViewSet):
    lookup_field = "index_set_id"

    def get_permissions(self):
        return [InstanceActionPermission([ActionEnum.SEARCH_LOG], ResourceEnum.INDICES)]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "traces": TracesSerializer,
        }
        return action_serializer_map.get(self.action, serializers.Serializer)

    def get_validated_data(self, many=False):
        """
        使用serializer校验参数，并返回校验后参数
        :return: dict
        """
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data

        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        return copy.deepcopy(serializer.validated_data)

    @detail_route(methods=["GET", "POST"], url_path="api/services/(?P<service_name>[^./]+)/operations")
    def operations(self, request, index_set_id, service_name, *args, **kwargs):
        return Response(TraceHandler(index_set_id).operations(service_name))

    @detail_route(methods=["GET", "POST"], url_path="api/traces/(?P<trace_id>[^./]+)")
    def traces_detail(self, request, index_set_id, trace_id, *args, **kwargs):
        return Response(TraceHandler(index_set_id).trace_detail(trace_id))

    @detail_route(methods=["GET", "POST"], url_path="api/services")
    def services(self, request, index_set_id, *args, **kwargs):
        return Response(TraceHandler(index_set_id).services())

    @detail_route(methods=["GET", "POST"], url_path="api/traces")
    def traces(self, request, index_set_id, *args, **kwargs):
        params = self.get_validated_data()
        return Response(TraceHandler(index_set_id).traces(params))


class GrafanaViewSet(APIViewSet):
    def get_permissions(self):
        if settings.BKAPP_IS_BKLOG_API:
            # 只在后台部署时做白名单校验
            auth_info = JwtPermission.get_auth_info(self.request, raise_exception=False)
            # ESQUERY白名单不需要鉴权
            if auth_info and auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
                return []
        return [BusinessActionPermission([ActionEnum.VIEW_DASHBOARD])]

    def get_authenticators(self):
        authenticators = super(GrafanaViewSet, self).get_authenticators()
        authenticators = [
            authenticator for authenticator in authenticators if not isinstance(authenticator, SessionAuthentication)
        ]
        authenticators.append(NoCsrfSessionAuthentication())
        return authenticators

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "get_variable_value": GetVariableValueSerializer,
            "get_variable_field": GetVariableFieldSerializer,
            "metric": GetMetricListSerializer,
            "target_tree": TargetTreeSerializer,
            "query": QuerySerializer,
            "query_log": QueryLogSerializer,
            "dimension": DimensionSerializer,
        }
        return action_serializer_map.get(self.action, serializers.Serializer)

    def get_validated_data(self, many=False):
        """
        使用serializer校验参数，并返回校验后参数
        :return: dict
        """
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data

        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        return copy.deepcopy(serializer.validated_data)

    @list_route(methods=["post"])
    def query(self, request):
        """
        @api {post} /grafana/query/ 01_Grafana指标数据查询
        @apiName grafana_query
        @apiDescription Grafana 指标数据查询
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} metric_field 监控指标
        @apiParam {String} result_table_id 结果表ID
        @apiParam {List} where 过滤条件
        @apiParam {List} group_by 聚合字段
        @apiParam {String} query_string 查询字符串
        @apiParam {String} method 聚合方法
        @apiParam {Int} interval 时间间隔
        @apiParam {List} target 监控目标
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParamExample {Json} 请求参数
        {
        }

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {

            },
            "result": true
        }
        """
        params = self.get_validated_data()
        data = GrafanaQueryHandler(params["bk_biz_id"]).query(params)
        return Response(data)

    @list_route(methods=["post"])
    def query_log(self, request):
        """
        @api {post} /grafana/query_log/ 02_Grafana日志数据查询
        @apiName grafana_query_log
        @apiDescription Grafana 日志数据查询
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} result_table_id 结果表ID
        @apiParam {List} where 过滤条件
        @apiParam {String} query_string 查询字符串
        @apiParam {List} target 监控目标
        @apiParam {Int} [size] 返回条数
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParamExample {Json} 请求参数
        {
        }

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {

            },
            "result": true
        }
        """
        params = self.get_validated_data()
        data = GrafanaQueryHandler(params["bk_biz_id"]).query_log(params)
        return Response(data)

    @list_route(methods=["get"])
    def options(self, request):
        """
        @api {get} /grafana/options/ 03_获取配置
        @apiName grafana_options
        @apiDescription 获取配置
        @apiGroup 30_Grafana
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": "hosts",
                    "name": "主机",
                    "children": [
                        {
                            "id": "os",
                            "name": "操作系统",
                            "children": [

                            ]
                        }
                    ]
                }
            ],
            "result": true
        }
        """
        return Response(
            {
                "agg_method_choices": GrafanaQueryHandler.AGG_METHOD_CHOICES,
                "condition_choices": GrafanaQueryHandler.CONDITION_CHOICES,
            }
        )

    @list_route(methods=["get", "post"])
    def metric(self, request):
        """
        @api {post} /grafana/metric/ 04_获取指标列表
        @apiName grafana_metric
        @apiDescription 获取指标列表
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} [result_table_label] 分类ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                  "id": "os",
                  "name": "操作系统",
                  "children": [
                    {
                      "id": 1,
                      "name": "[采集项]测试采集1",
                      "children": [
                        {
                          "id": "usage",
                          "name": "使用率",
                          "metric_field": "usage",
                          "metric_field_name": "使用率",
                          "default_dimensions": [],
                          "default_condition": [],
                          "dimensions": [
                            {
                              "id": "level",
                              "name": "日志级别"
                            }
                          ],
                          "result_table_id": 1,
                          "result_table_name": "[采集项]测试采集1",
                          "result_table_label": "os",
                          "result_table_label_name": "操作系统",
                          "scenario_id": "log"
                        }
                      ]
                    }
                  ]
                }
            ],
            "result": true
        }
        """
        params = self.get_validated_data()
        data = GrafanaQueryHandler(params["bk_biz_id"]).get_metric_list(params["result_table_label"])
        return Response(data)

    @list_route(methods=["get"])
    def dimension(self, request):
        """
        @api {get} /grafana/metric/ 05_获取维度取值列表
        @apiName grafana_dimension
        @apiDescription 获取维度取值列表
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} result_table_id 结果表ID
        @apiParam {String} field 查询字段
        @apiParam {Int} start_time 开始时间
        @apiParam {Int} end_time 结束时间
        @apiParam {String} query_string 查询字符串

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": "123",
                    "name": "123"
                }
            ],
            "result": true
        }
        """
        params = self.get_validated_data()
        dimensions = GrafanaQueryHandler(params["bk_biz_id"]).get_dimension_values(
            index_set_id=int(params["result_table_id"]),
            field=params["field"],
            start_time=params["start_time"],
            end_time=params["end_time"],
            query_string=params["query_string"],
        )
        result = [{"id": dim, "name": dim} for dim in dimensions]
        return Response(result)

    @list_route(methods=["get"])
    def target_tree(self, request):
        """
        @api {get} /grafana/target_tree/ 06_获取拓扑树
        @apiName grafana_target_tree
        @apiDescription 获取拓扑树
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} [instance_type] 实例类型，可选 service, host
        @apiParam {Boolean} [remove_empty_nodes] 是否删除空节点

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [

            ],
            "result": true
        }
        """
        params = self.get_validated_data()
        bk_biz_id = params["bk_biz_id"]
        data = BizHandler(bk_biz_id).get_instance_topo(params)
        return Response(data)

    @list_route(methods=["get"])
    def get_variable_field(self, request):
        """
        @api {get} /grafana/get_variable_field/ 07_获取变量名列表
        @apiName grafana_get_variable_field
        @apiDescription 获取变量名列表
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} type 查询类型，可选 host, module, set

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "bk_property_id": "xxx",
                    "bk_property_name": "yyy"
                }
            ],
            "result": true
        }
        """
        params = self.get_validated_data()
        data = GrafanaQueryHandler(params["bk_biz_id"]).get_variable_field(params["type"])
        return Response(data)

    @list_route(methods=["get", "post"])
    def get_variable_value(self, request):
        """
        @api {post} /grafana/get_variable_value/ 08_获取变量取值列表
        @apiName grafana_get_variable_value
        @apiDescription 获取变量取值列表
        @apiGroup 30_Grafana
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} type 查询类型，可选 host, module, set, dimension
        @apiParam {Object} params 查询参数

        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "label": "xxx",
                    "value": "yyy"
                }
            ],
            "result": true
        }
        """
        params = self.get_validated_data()
        data = GrafanaQueryHandler(params["bk_biz_id"]).get_variable_value(params["type"], params["params"])
        return Response(data)
