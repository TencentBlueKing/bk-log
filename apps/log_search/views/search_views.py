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
import json

from urllib import parse

from six import StringIO
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.response import Response
from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.generic import APIViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import (
    ViewBusinessPermission,
    InstanceActionPermission,
    insert_permission_field,
)
from apps.log_search.exceptions import BaseSearchIndexSetException
from apps.log_search.handlers.search.async_export_handlers import AsyncExportHandlers
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import LogIndexSet
from apps.log_search.permission import Permission
from apps.utils.drf import detail_route, list_route
from apps.log_search.serializers import (
    SearchAttrSerializer,
    SearchUserIndexSetConfigSerializer,
    SearchExportSerializer,
    SearchIndexSetScopeSerializer,
    BcsWebConsoleSerializer,
    SearchAsyncExportSerializer,
)
from apps.decorators import user_operation_record
from apps.log_search.constants import (
    SEARCH_SCOPE_VALUE,
    FEATURE_ASYNC_EXPORT_COMMON,
    FEATURE_ASYNC_EXPORT_NOTIFY_TYPE,
)
from apps.constants import NotifyType
from apps.exceptions import ValidationError
from apps.log_search.decorators import search_history_record
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.utils.local import get_request_username


class SearchViewSet(APIViewSet):
    """
    检索
    """

    queryset = LogIndexSet.objects.all()
    serializer_class = serializers.Serializer
    lookup_field = "index_set_id"

    def get_permissions(self):
        if settings.BKAPP_IS_BKLOG_API:
            # 只在后台部署时做白名单校验
            auth_info = Permission.get_auth_info(self.request, raise_exception=False)
            # ESQUERY白名单不需要鉴权
            if auth_info and auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
                return []

        if self.action in ["operators", "user_search_history"]:
            return []
        if self.action in ["bizs", "search", "context", "tailf", "export", "fields", "config", "history"]:
            return [InstanceActionPermission([ActionEnum.SEARCH_LOG], ResourceEnum.INDICES)]
        return [ViewBusinessPermission()]

    @insert_permission_field(
        actions=[ActionEnum.SEARCH_LOG],
        resource_meta=ResourceEnum.INDICES,
        id_field=lambda d: d["index_set_id"],
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /search/index_set/?project_id=$project_id 01_搜索-索引集列表
        @apiDescription 用户有权限的索引集列表
        @apiName search_index_set
        @apiGroup 11_Search
        @apiParam {Int} project_id 项目id
        @apiSuccess {Int} index_set_id 索引集ID
        @apiSuccess {String} index_set_name 索引集名称
        @apiSuccess {Boolean} is_favorite 索引集为收藏索引集
        @apiSuccess {List} tags 索引集标签
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
                    ],
                    "time_field": "dtEventTimeStamp",
                    "time_field_type": "date",
                    "time_field_unit": "microsecond",
                    "tags": [{"name": "test", "color": "xxx"}],
                    "is_favorite": true
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(SearchIndexSetScopeSerializer)
        return Response(IndexSetHandler().get_user_index_set(data.get("project_id")))

    @detail_route(methods=["GET"], url_path="bizs")
    def bizs(self, request, *args, **kwargs):
        """
        @api {get} /search/index_set/$index_set_id/bizs/ 05_索引集-业务列表
        @apiName get_index_set_bizs
        @apiGroup 11_Search
        @apiParam {Int} index_set_id 索引集ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "bk_biz_id": 1,
                    "bk_biz_name": "业务名称"
                }
            ],
            "result": true
        }
        """
        return Response(IndexSetHandler(index_set_id=kwargs["index_set_id"]).bizs())

    @detail_route(methods=["POST"], url_path="search")
    @search_history_record
    def search(self, request, index_set_id=None):
        """
        @api {post} /search/index_set/$index_set_id/search/ 11_搜索-日志内容
        @apiName search_log
        @apiGroup 11_Search
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParam {String} time_range 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} ip IP列表
        @apiParam {Json} addition 搜索条件
        @apiParam {Int} begin 起始位置
        @apiParam {Int} size 条数
        @apiParamExample {Json} 请求参数
        {
            "start_time": "2019-06-11 00:00:00",
            "end_time": "2019-06-12 11:11:11",
            "time_range": "customized"
            "keyword": "error",
            "host_scopes": {
                "modules": [
                    {
                        "bk_obj_id": "module",
                        "bk_inst_id": 4
                    },
                    {
                        "bk_obj_id": "set",
                        "bk_inst_id": 4
                    }
                ],
                "ips": "127.0.0.1, 127.0.0.2"
            },
            "addition": [
                {
                    "key": "ip",
                    "method": "is",
                    "value": "127.0.0.1",
                    "condition": "and",  (默认不传是and，只支持and or)
                    "type": "field" (默认field 目前支持field，其他无效)
                }
            ],
            "begin": 0,
            "size": 15
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
                        "srcDataId": "2087",
                        "dtEventTimeStamp": 1534825132000,
                        "moduleName": "公共组件->consul",
                        "log": "is_cluster</em>-COMMON: ok",
                        "sequence": 1,
                        "dtEventTime": "2018-08-21 04:18:52",
                        "timestamp": 1534825132,
                        "serverIp": "127.0.0.1",
                        "errorCode": "0",
                        "gseIndex": 152358,
                        "dstDataId": "2087",
                        "worldId": "-1",
                        "logTime": "2018-08-21 12:18:52",
                        "path": "/tmp/health_check.log",
                        "platId": 0,
                        "localTime": "2018-08-21 04:18:00"
                    }
                ],
                "fields": {
                    "agent": {
                        "max_length": 101
                    },
                    "bytes": {
                        "max_length": 4
                    },
                }
            },
            "result": true
        }
        """
        data = self.params_valid(SearchAttrSerializer)
        search_handler = SearchHandlerEsquery(index_set_id, data)
        return Response(search_handler.search())

    @detail_route(methods=["POST"], url_path="context")
    def context(self, request, index_set_id=None):
        """
        @api {post} /search/index_set/$index_set_id/context/ 13_搜索-上下文 [TODO]
        @apiName search_log_context
        @apiGroup 11_Search
        @apiParam {String} index_id 索引ID
        @apiParam {String} ip IP
        @apiParam {String} path 日志路径
        @apiParam {Int} gse_index 日志所在GSE位置
        @apiParam {Int} size 上下文条数
        @apiParam {Int} container_id docker used
        @apiParam {String} logfile docker used
        @apiParam {Int} begin 日志游标
        @apiParamExample {Json} 请求参数
        {
            "gseindex": 59810429,
            "ip": "127.0.0.1",
            "path": "/data/home/user00/log/accountsvrd/accountsvrd_127.0.0.1.error",
            "size": 500,
            "begin": 0
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
                        "srcDataId": "2087",
                        "dtEventTimeStamp": 1534825132000,
                        "moduleName": "公共组件->consul",
                        "log": "is_cluster</em>-COMMON: ok",
                        "sequence": 1,
                        "dtEventTime": "2018-08-21 04:18:52",
                        "timestamp": 1534825132,
                        "serverIp": "127.0.0.1",
                        "errorCode": "0",
                        "gseIndex": 152358,
                        "dstDataId": "2087",
                        "worldId": "-1",
                        "logTime": "2018-08-21 12:18:52",
                        "path": "/tmp/health_check.log",
                        "platId": 0,
                        "localTime": "2018-08-21 04:18:00"
                    }
                ]
            },
            "result": true
        }
        """
        data = request.data
        # data.update({
        #     "size": 30
        # })
        data.update({"search_type_tag": "context"})
        # search_handler = SearchHandler(index_set_id, data)
        search_handler = SearchHandlerEsquery(index_set_id, data)
        return Response(search_handler.search_context())

    @detail_route(methods=["POST"], url_path="tail_f")
    def tailf(self, request, index_set_id=None):
        """
        @api {post} /search/index_set/$index_set_id/tail_f/ 12_搜索-实时日志 [TODO]
        @apiName search_log_tailf
        @apiGroup 11_Search
        @apiParam {String} index_id 索引ID
        @apiParam {String} ip IP
        @apiParam {String} path 日志路径
        @apiParam {Int} gse_index 日志所在GSE位置(not necessary, timestamp would be better)
        @apiParamExample {Json} 请求参数
        {
            "ip": "127.0.0.1",
            "path": "/data/home/user00/log/accountsvrd/accountsvrd_127.0.0.1.error",
            "size": 500,
            "gseindex": 59810429,
            "order": "-"
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
                        "srcDataId": "2087",
                        "dtEventTimeStamp": 1534825132000,
                        "moduleName": "公共组件->consul",
                        "log": "is_cluster</em>-COMMON: ok",
                        "sequence": 1,
                        "dtEventTime": "2018-08-21 04:18:52",
                        "timestamp": 1534825132,
                        "serverIp": "127.0.0.1",
                        "errorCode": "0",
                        "gseIndex": 152358,
                        "dstDataId": "2087",
                        "worldId": "-1",
                        "logTime": "2018-08-21 12:18:52",
                        "path": "/tmp/health_check.log",
                        "platId": 0,
                        "localTime": "2018-08-21 04:18:00"
                    }
                ]
            },
            "result": true
        }
        """
        data = request.data
        data.update({"search_type_tag": "tail"})
        # search_handler = SearchHandler(index_set_id, data)
        search_handler = SearchHandlerEsquery(index_set_id, data)
        return Response(search_handler.search_tail_f())

    @detail_route(methods=["GET"], url_path="export")
    def export(self, request, index_set_id=None):
        """
        @api {get} /search/index_set/$index_set_id/export/ 14_搜索-导出日志
        @apiName search_log_export
        @apiGroup 11_Search
        @apiParam {Dict} export_dict 序列化后的查询字典
        @apiParam {String} start_time 开始时间
        @apiParam {String} end_time 结束时间
        @apiParam {String} time_range 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} ip IP列表
        @apiParam {Json} addition 搜索条件
        @apiParam {Int} start 起始位置
        @apiDescription 直接下载结果
        @apiParamExample {Json} 请求参数
        /api/v1/search/index_set/3/export/
        ?export_dict={"start_time":"2019-06-26 00:00:00","end_time":"2019-06-27 11:11:11","time_range":"customized",
        "keyword":"error",
        "host_scopes":{"modules":[{"bk_obj_id":"module","bk_inst_id":4},
        {"bk_obj_id":"set","bk_inst_id":4}],"ips":"127.0.0.1, 127.0.0.2"},
        "addition":[{"field":"ip","operator":"eq","value":[]}],"begin":0,"size":10000}

        @apiSuccessExample text/plain 成功返回:
        {"a": "good", "b": {"c": ["d", "e"]}}
        {"a": "good", "b": {"c": ["d", "e"]}}
        {"a": "good", "b": {"c": ["d", "e"]}}
        """

        params = self.params_valid(SearchExportSerializer).get("export_dict")
        data = json.loads(params)
        index_set_id = int(index_set_id)

        tmp_index_obj = LogIndexSet.objects.filter(index_set_id=index_set_id).first()
        if tmp_index_obj:
            index_set_data_obj_list = tmp_index_obj.get_indexes(has_applied=True)
            if len(index_set_data_obj_list) > 0:
                index_list = [x.get("result_table_id", "unknow") for x in index_set_data_obj_list]
                index = "_".join(index_list).replace(".", "_")
            else:
                raise BaseSearchIndexSetException(BaseSearchIndexSetException.MESSAGE.format(index_set_id=index_set_id))
        else:
            raise BaseSearchIndexSetException(BaseSearchIndexSetException.MESSAGE.format(index_set_id=index_set_id))

        output = StringIO()
        search_handler = SearchHandlerEsquery(index_set_id, data)
        result = search_handler.search()
        result_list = result.get("origin_log_list")
        for item in result_list:
            output.write(f"{json.dumps(item)}\n")
        response = HttpResponse(output.getvalue())
        response["Content-Type"] = "application/x-msdownload"
        file_name = f"bk_log_search_{index}.txt"
        file_name = parse.quote(file_name, encoding="utf8")
        file_name = parse.unquote(file_name, encoding="ISO8859_1")
        response["Content-Disposition"] = 'attachment;filename="{}"'.format(file_name)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": 0,
            "project_id": tmp_index_obj.project_id,
            "record_type": UserOperationTypeEnum.EXPORT,
            "record_object_id": index_set_id,
            "action": UserOperationActionEnum.START,
            "params": data,
        }
        user_operation_record.delay(operation_record)

        return response

    @detail_route(methods=["POST"], url_path="async_export")
    def async_export(self, request, index_set_id=None):
        """
        @api /search/index_set/$index_set_id/async_export/ 15-搜索-异步导出日志
        @apiDescription 异步下载检索日志
        @apiName async_export
        @apiGroup 11_Search
        @apiParam bk_biz_id [Int] 业务id
        @apiParam keyword [String] 搜索关键字
        @apiParam time_range [String] 时间范围
        @apiParam start_time [String] 起始时间
        @apiParam end_time [String] 结束时间
        @apiParam host_scopes [Dict] 检索模块ip等信息
        @apiParam begin [Int] 检索开始 offset
        @apiParam size [Int]  检索结果大小
        @apiParam interval [String] 匹配规则
        @apiParamExample {Json} 请求参数
        {
            "bk_biz_id":"215",
            "keyword":"*",
            "time_range":"5m",
            "start_time":"2021-06-08 11:02:21",
            "end_time":"2021-06-08 11:07:21",
            "host_scopes":{
                "modules":[

                ],
                "ips":""
            },
            "addition":[

            ],
            "begin":0,
            "size":188,
            "interval":"auto",
            "isTrusted":true
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "task_id": 1,
                "prompt": "任务提交成功，系统处理后将通过邮件通知，请留意！"
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(SearchAsyncExportSerializer)
        index_set_id = int(index_set_id)
        notify_type_name = NotifyType.get_choice_label(
            FeatureToggleObject.toggle(FEATURE_ASYNC_EXPORT_COMMON).feature_config.get(FEATURE_ASYNC_EXPORT_NOTIFY_TYPE)
        )
        return Response(
            {
                "task_id": AsyncExportHandlers(index_set_id=index_set_id, search_dict=data).async_export(),
                "prompt": _("任务提交成功，系统处理后将通过{notify_type_name}通知，请留意！").format(notify_type_name=notify_type_name),
            }
        )

    @detail_route(methods=["GET"], url_path="fields")
    def fields(self, request, *args, **kwargs):
        """
        @api {get} /search/index_set/$index_set_id/fields/?scope=search_context 02_搜索-获取索引集配置
        @apiDescription 获取用户在某个索引集的配置 @TODO 前端需要调整
        @apiName list_search_index_set_user_config
        @apiGroup 11_Search
        @apiParam {String} [start_time] 开始时间(非必填)
        @apiParam {String} [end_time] 结束时间（非必填)
        @apiSuccess {String} display_fields 列表页显示的字段
        @apiSuccess {String} fields.field_name 字段名
        @apiSuccess {String} fields.field_alias 字段中文称 (为空时会直接取description)
        @apiSuccess {String} fields.description 字段说明
        @apiSuccess {String} fields.field_type 字段类型
        @apiSuccess {Bool} fields.is_display 是否显示给用户
        @apiSuccess {Bool} fields.is_editable 是否可以编辑（是否显示）
        @apiSuccess {Bool} fields.es_doc_values 是否聚合字段
        @apiSuccess {Bool} fields.is_analyzed 是否分词字段
        @apiSuccess {String} time_field 时间字段
        @apiSuccess {String} time_field_type 时间字段类型
        @apiSuccess {String} time_field_unit 时间字段单位
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "config": [
                    {
                        "name": "bcs_web_console"
                        "is_active": True,
                    },
                    {
                        name: "bkmonitor",
                        "is_active": True,
                    },
                    {
                        "name": "ip_topo_switch",
                        "is_active": True,
                    },
                    {
                        "name": "async_export",
                        "is_active": True, # async_export_usable
                        "extra": {
                            "fields": ["dtEventTimeStamp", "serverIp", "gseIndex", "iterationIndex"],
                            "usable_reason": ""
                        }
                    },
                    {
                        "name": "context_and_realtime", # context_search_usable realtime_search_usable
                        "is_active": True,
                        "extra": {
                            "reason": ""  #usable_reason
                        }
                    },
                    {
                        "name": "trace",
                        "is_active": True,
                        "extra": {
                            field: "trace_id"
                            index_set_name: "test_stag_oltp"
                        }
                    },
                ],
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
                ]
            },
            "result": true
        }
        """
        index_set_id = kwargs.get("index_set_id", "")
        scope = request.GET.get("scope", "default")
        is_realtime = bool(request.GET.get("is_realtime", False))
        if scope is not None and scope not in SEARCH_SCOPE_VALUE:
            raise ValidationError(_("scope取值范围：default、search_context"))

        start_time = request.GET.get("start_time", "")
        end_time = request.GET.get("end_time", "")

        if scope == "default" and not is_realtime and not start_time and not end_time:
            # 使用缓存
            fields = self.get_object().get_fields(use_snapshot=True)
        else:
            search_handler_esquery = SearchHandlerEsquery(
                index_set_id, {"start_time": start_time, "end_time": end_time}
            )
            fields = search_handler_esquery.fields(scope)
        return Response(fields)

    @detail_route(methods=["GET"], url_path="bcs_web_console")
    def bcs_web_console(self, request, *args, **kwargs):
        """
        @api {get} /search/index_set/$index_set_id/bcs_web_console/ 获取bcs容器管理页面url
        @apiDescription 获取bcs容器管理页面url
        @apiName bcs_web_console
        @apiGroup 11_Search
        @apiParam {String} cluster_id 集群id
        @apiParam {String} container_id 容器id
        @apiSuccess {String} data bcs容器管理页面url
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "http://...",
            "result": true
        }
        """
        data = self.params_valid(BcsWebConsoleSerializer)

        return Response(SearchHandlerEsquery.get_bcs_manage_url(data["cluster_id"], data["container_id"]))

    @detail_route(methods=["POST"], url_path="config")
    def config(self, request, *args, **kwargs):
        """
        @api {post} /search/index_set/$index_set_id/config/?scope=search_context 03_搜索-索引集配置
        @apiDescription 创建或更新用户在某个索引集的配置
        @apiName search_index_set_user_config
        @apiGroup 11_Search
        @apiParamExample {Json} 请求参数
        {
            "display_fields": ["aaa", "bbb"]
            "sort_list": [
                ["aaa", "desc"],
                ["bbb", "asc"]
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": null,
            "result": true
        }
        """
        index_set_id = kwargs.get("index_set_id", "")
        scope = request.GET.get("scope", "default")
        if scope is not None and scope not in SEARCH_SCOPE_VALUE:
            raise ValidationError(_("scope取值范围：default、search_context"))
        # display_fields = request.data.get("display_fields", list())
        data = self.params_valid(SearchUserIndexSetConfigSerializer)
        SearchHandlerEsquery(index_set_id, {}).verify_sort_list_item(data["sort_list"])
        result = IndexSetHandler.add_field_config_record(
            index_set_id, data["display_fields"], data["sort_list"], scope=scope
        )
        return Response(result)

    @list_route(methods=["get"], url_path="operators")
    def operators(self, request, *args, **kwargs):
        """
        @api {get} /search/index_set/operators/ 04_搜索-检索条件operator
        @apiName search_index_set_operators
        @apiGroup 11_Search
        @apiSuccess {Int} index_set_id 索引集ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "operator": "is",
                    "label": "is",
                    "placeholder": _("请输入，注意空格符号")
                },
                {
                    "operator": "is one of",
                    "label": "is one of "，
                    "placeholder": _("逗号分隔")
                },
            ],
            "result": true
        }
        """
        data = [
            {"operator": "is", "label": _("is"), "placeholder": _("请输入，注意空格符号")},
            {"operator": "is one of", "label": _("is one of"), "placeholder": _("逗号分隔")},
            {"operator": "is not", "label": _("is not"), "placeholder": _("请输入，注意空格符号")},
            {"operator": "is not one of", "label": _("is not one of"), "placeholder": _("逗号分隔")},
            {"operator": "gt", "label": _("大于"), "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
            {"operator": "gte", "label": _("大于等于"), "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
            {"operator": "lt", "label": _("小于"), "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
            {"operator": "lte", "label": _("小于等于"), "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
            {"operator": "exists", "label": _("exists"), "placeholder": _("确认字段已存在")},
            {"operator": "does not exists", "label": _("does not exists"), "placeholder": _("确认字段不存在")},
        ]
        return Response(data)

    @detail_route(methods=["GET"], url_path="history")
    def history(self, request, *args, **kwargs):
        """
        @api {get} /search/index_set/$index_set_id/history/ 06_搜索-检索历史
        @apiDescription 检索历史记录
        @apiName search_index_set_user_history
        @apiGroup 11_Search
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": 13,
                    "params": {
                        "keyword": "*",
                        "host_scopes": {
                            "modules": [
                                {
                                    "bk_inst_id": 25,
                                    "bk_obj_id": "module"
                                }
                            ],
                            "ips": "127.0.0.1,127.0.0.2"
                        },
                        "addition": [
                            {
                                "field": "cloudId",
                                "operator": "is",
                                "value": "0"
                            }
                        ]
                    },
                    "query_string": "keyword:* ADN modules:25 AND ips:127.0.0.1,127.0.0.2"
                }],
            "result": true
        }
        """
        index_set_id = kwargs.get("index_set_id")
        return Response(SearchHandlerEsquery.search_history(index_set_id))
