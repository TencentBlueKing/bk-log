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
from rest_framework import serializers

from django.db.models import Q

from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import insert_permission_field, ViewBusinessPermission
from apps.generic import ModelViewSet
from apps.log_databus.handlers.clean import CleanTemplateHandler, CleanHandler
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.models import BKDataClean, CleanTemplate
from apps.log_databus.constants import VisibleEnum
from apps.log_databus.serializers import (
    CleanTemplateSerializer,
    CleanTemplateListSerializer,
    CollectorEtlSerializer,
    CleanRefreshSerializer,
    CleanSerializer,
    CleanSyncSerializer,
    CleanTemplateDestroySerializer,
    CleanTemplateListFilterSerializer,
)
from apps.log_databus.utils.clean import CleanFilterUtils
from apps.utils.drf import detail_route, list_route


class CleanViewSet(ModelViewSet):
    """
    清洗列表
    """

    lookup_field = "collector_config_id"
    model = BKDataClean

    def get_permissions(self):
        return [ViewBusinessPermission()]

    @insert_permission_field(
        id_field=lambda d: d["collector_config_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    @insert_permission_field(
        id_field=lambda d: d["index_set_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.SEARCH_LOG],
        resource_meta=ResourceEnum.INDICES,
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/clean/?page=$page&pagesize=$pagesize&bk_biz_id=$bk_biz_id 1_清洗-列表
        @apiName list_clean
        @apiGroup 22_clean
        @apiDescription 清洗列表，获取入库列表及基础清洗合集
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Int} page 页数
        @apiParam {Int} pagesize 每页数量
        @apiSuccess {Int} count 总数
        @apiSuccess {Int} total_page 总页数
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                "count": 10,
                "total_page": 1,
                "results": [
                {
                    "collector_config_id":1,
                    "collector_config_name":"test",
                    "bk_data_id": 10,
                    "result_table_id":"test",
                    "updated_by":"test",
                    "updated_at":"2021-07-24 17:42:32+0800"
                }
            ]
            },
            "result": true
        }
        """
        data = self.params_valid(CleanSerializer)
        return Response(
            CleanFilterUtils(bk_biz_id=data["bk_biz_id"]).filter(
                keyword=data.get("keyword", ""),
                etl_config=data.get("etl_config", ""),
                page=data["page"],
                pagesize=data["pagesize"],
            )
        )

    @detail_route(methods=["DELETE"], url_path="destroy_clean")
    def destroy_clean(self, request, collector_config_id=None):
        """
        @api {destroy} /databus/clean/$collector_config_id/destroy_clean 1_清洗-删除清洗
        @apiName destroy_clean
        @apiGroup 22_clean
        @apiDescription 删除清洗配置
        @apiParam {Int} $collector_config_id 采集项ID
        @apiSuccess {Bool} 删除结果
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                true
            },
            "result": true
        }
        """
        return Response(CleanFilterUtils().delete(collector_config_id))

    @detail_route(methods=["GET"])
    def refresh(self, request, *args, collector_config_id=None, **kwargs):
        """
        @api {get} /databus/clean/$collector_config_id/refresh/?bk_biz_id=$bk_biz_id&bk_data_id=$bk_data_id 2_高级清洗-刷新
        @apiName refresh_clean
        @apiGroup 22_clean
        @apiDescription 刷新高级清洗
        @apiParam {Int} bk_biz_id 业务id
        @apiParam {Int} bk_data_id 数据源id
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": [
                "test"
            ],
            "result": true
        }
        @apiSuccessExample {json} 成功返回(未找到对应记录)
        {
            "message": "",
            "code": 0,
            "data": {
                "result": False,
                "log_set_index_id": null,
            },
            "result": true
        }
        """
        data = self.params_valid(CleanRefreshSerializer)
        return Response(
            CleanHandler(collector_config_id=collector_config_id).refresh(
                raw_data_id=data["bk_data_id"], bk_biz_id=data["bk_biz_id"]
            )
        )

    @list_route(methods=["GET"])
    def sync(self, request, *args, **kwargs):
        """
        @api {get} /databus/clean/sync/?bk_biz_id=$bk_biz_id 3_高级清洗-同步
        @apiName sync_clean
        @apiGroup 22_clean
        @apiDescription 同步高级清洗
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccessExample {json} 任务已完成
        {
            "message": "",
            "code": 0,
            "data": {
                "status": "DONE"
            },
            "result": true
        }
        @apiSuccessExample {json} 任务正在进行中
        {
            "message": "",
            "code": 0,
            "data": {
                "status": "RUNNING"
            },
            "result": true
        }
        """
        data = self.params_valid(CleanSyncSerializer)
        return Response({"status": CleanHandler.sync(bk_biz_id=data["bk_biz_id"], polling=data["polling"])})


class CleanTemplateViewSet(ModelViewSet):
    """
    清洗模板
    """

    lookup_field = "clean_template_id"
    model = CleanTemplate
    filter_fields_exclude = ["etl_params", "etl_fields"]
    search_fields = ("name",)

    def get_permissions(self):
        return [ViewBusinessPermission()]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "list": CleanTemplateListSerializer,
        }
        return action_serializer_map.get(self.action, serializers.Serializer)

    def get_queryset(self):
        qs = self.model.objects
        if self.request.query_params.get("bk_biz_id"):
            bk_biz_id = int(self.request.query_params.get("bk_biz_id"))
            qs = qs.filter(
                Q(bk_biz_id=bk_biz_id)
                | Q(visible_type=VisibleEnum.ALL_BIZ.value)
                | Q(
                    visible_type=VisibleEnum.MULTI_BIZ.value,
                    visible_bk_biz_id__contains=f",{bk_biz_id},",
                )
            )
        return qs.all()

    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/clean_template/?page=$page&pagesize=$pagesize&bk_biz_id=$bk_biz_id 1_清洗模板-列表
        @apiName list_clean_template
        @apiGroup 23_clean_template
        @apiDescription 获取清洗模板列表
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccessExample {json} 成功返回
        {
            "message":"",
            "code":0,
            "data":{
                "count":10,
                "total_page":1,
                "results":[
                    {
                        "clean_template_id":1,
                        "name": "test",
                        "clean_type":"bk_log_text",
                        "etl_params":{
                            "retain_original_text":true,
                            "separator":" "
                        },
                        "etl_fields":[
                            {
                                "field_name":"user",
                                "alias_name":"",
                                "field_type":"long",
                                "description":"字段描述",
                                "is_analyzed":true,
                                "is_dimension":false,
                                "is_time":false,
                                "is_delete":false
                            },
                            {
                                "field_name":"report_time",
                                "alias_name":"",
                                "field_type":"string",
                                "description":"字段描述",
                                "tag":"metric",
                                "is_analyzed":false,
                                "is_dimension":false,
                                "is_time":true,
                                "is_delete":false,
                                "option":{
                                    "time_zone":8,
                                    "time_format":"yyyy-MM-dd HH:mm:ss"
                                }
                            }
                        ],
                        "bk_biz_id": 0,
                        "visible_bk_biz_id": "",
                        "visible_type": "current_biz"
                    }
                ]
            },
            "result":true
        }
        """
        queryset = self.get_queryset()

        data = self.params_valid(CleanTemplateListFilterSerializer)
        name_filter = data.get("keyword")
        if name_filter:
            queryset = queryset.filter(name__contains=name_filter)

        clean_type = data.get("clean_type")
        if clean_type:
            queryset = queryset.filter(clean_type=clean_type)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, clean_template_id=None, **kwargs):
        """
        @api {get} /databus/clean_template/$clean_template_id/?bk_biz_id=$bk_biz_id 2_清洗模板-详情
        @apiName retrieve_clean_template
        @apiGroup 23_clean_template
        @apiDescription 清洗模板详情
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccessExample {json} 成功返回
        {
            "message":"",
            "code":0,
            "data":{
                "name": "xxx",
                "clean_template_id":1,
                "clean_type":"bk_log_text",
                "etl_params":{
                    "retain_original_text":true,
                    "separator":" "
                },
                "etl_fields":[
                    {
                        "field_name":"user",
                        "alias_name":"",
                        "field_type":"long",
                        "description":"字段描述",
                        "is_analyzed":true,
                        "is_dimension":false,
                        "is_time":false,
                        "is_delete":false
                    },
                    {
                        "field_name":"report_time",
                        "alias_name":"",
                        "field_type":"string",
                        "description":"字段描述",
                        "tag":"metric",
                        "is_analyzed":false,
                        "is_dimension":false,
                        "is_time":true,
                        "is_delete":false,
                        "option":{
                            "time_zone":8,
                            "time_format":"yyyy-MM-dd HH:mm:ss"
                        }
                    }
                ],
                "bk_biz_id": 0,
                "visible_bk_biz_id": [],
                "visible_type": "current_biz"
            },
            "result":true
        }
        """
        return Response(CleanTemplateHandler(clean_template_id=clean_template_id).retrieve())

    def update(self, request, *args, clean_template_id=None, **kwargs):
        """
        @api {put} /databus/clean_template/$clean_template_id/ 4_清洗模板-更新
        @apiName update_clean_template
        @apiGroup 23_clean_template
        @apiDescription 更新清洗模板
        @apiParam {String} visible_type 可见类型, 支持 current_biz, multi_biz, all_biz
        @apiParam {list} visible_bk_biz_id 可见业务id范围
        @apiParamExample {json} 成功请求
        {
            "name": "xxx",
            "clean_type":"bk_log_text",
            "etl_params":{
                "retain_original_text":true,
                "separator":" "
            },
            "etl_fields":[
                {
                    "field_name":"user",
                    "alias_name":"",
                    "field_type":"long",
                    "description":"字段描述",
                    "is_analyzed":true,
                    "is_dimension":false,
                    "is_time":false,
                    "is_delete":false
                },
                {
                    "field_name":"report_time",
                    "alias_name":"",
                    "field_type":"string",
                    "description":"字段描述",
                    "tag":"metric",
                    "is_analyzed":false,
                    "is_dimension":false,
                    "is_time":true,
                    "is_delete":false,
                    "option":{
                        "time_zone":8,
                        "time_format":"yyyy-MM-dd HH:mm:ss"
                    }
                }
            ],
            "bk_biz_id": 0,
            "visible_bk_biz_id": [1, 2, 3],
            "visible_type": "multi_biz"
        }
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                "clean_template_id": 1
            },
            "result": true
        }
        """
        data = self.params_valid(CleanTemplateSerializer)
        return Response(CleanTemplateHandler(clean_template_id=clean_template_id).create_or_update(params=data))

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/clean_template/ 3_清洗模板-新建
        @apiName create_clean_template
        @apiGroup 23_clean_template
        @apiParam {String} visible_type 可见类型, 支持 current_biz, multi_biz, all_biz
        @apiParam {list} visible_bk_biz_id 可见业务id范围
        @apiDescription 新建清洗模板
        @apiParamExample {json} 成功请求
        {
            "name": "test",
            "clean_type":"bk_log_text",
            "etl_params":{
                "retain_original_text":true,
                "separator":" "
            },
            "etl_fields":[
                {
                    "field_name":"user",
                    "alias_name":"",
                    "field_type":"long",
                    "description":"字段描述",
                    "is_analyzed":true,
                    "is_dimension":false,
                    "is_time":false,
                    "is_delete":false
                },
                {
                    "field_name":"report_time",
                    "alias_name":"",
                    "field_type":"string",
                    "description":"字段描述",
                    "tag":"metric",
                    "is_analyzed":false,
                    "is_dimension":false,
                    "is_time":true,
                    "is_delete":false,
                    "option":{
                        "time_zone":8,
                        "time_format":"yyyy-MM-dd HH:mm:ss"
                    }
                }
            ],
            "bk_biz_id": 0,
            "visible_bk_biz_id": [1, 2, 3],
            "visible_type": "multi_biz"
        }
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                "clean_template_id": 1
            },
            "result": true
        }
        """
        data = self.params_valid(CleanTemplateSerializer)
        return Response(CleanTemplateHandler().create_or_update(params=data))

    def destroy(self, request, *args, clean_template_id=None, **kwargs):
        """
        @api {delete} /databus/clean_template/$clean_template_id/ 5_清洗模板-删除
        @apiName destry_clean_template
        @apiGroup 23_clean_template
        @apiDescription 删除清洗模板
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": 1,
            "result": true
        }
        """
        data = self.params_valid(CleanTemplateDestroySerializer)
        return Response(CleanTemplateHandler(clean_template_id=clean_template_id).destroy(data["bk_biz_id"]))

    @list_route(methods=["POST"])
    def etl_preview(self, request, collector_config_id=None):
        """
        @api {post} /databus/clean_template/etl_preview/ 6_清洗模板-预览提取结果
        @apiName clean_template_etl_preview
        @apiDescription 清洗模板-预览提取结果
        @apiGroup 23_clean_template
        @apiParam {String} etl_config 清洗类型（格式化方式）
        @apiParam {Object} etl_params 清洗配置，不同的清洗类型的参数有所不同
        @apiParam {String} etl_params.separator 分隔符，当etl_config=="bk_log_delimiter"时需要传递
        @apiParam {String} etl_params.separator_regexp 正则表达式，当etl_config=="bk_log_regexp"时需要传递
        @apiParam {String} data 日志内容

        @apiSuccess {list} fields 字段列表
        @apiSuccess {Int} fields.field_index 字段顺序
        @apiSuccess {String} fields.field_name 字段名称 (分隔符默认为空)
        @apiSuccess {String} fields.value 值
        @apiParamExample {json} 请求样例:
        {
            "etl_config": "bk_log_text | bk_log_json | bk_log_regexp | bk_log_delimiter",
            "etl_params": {
                "separator": "|"
            },
            "data": "a|b|c"
        }
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
                "fields": [
                    {
                        "field_index": 1,
                        "field_name": "",
                        "value": "a"
                    },
                    {
                        "field_index": 2,
                        "field_name": "",
                        "value": "b"
                    },
                    {
                        "field_index": 3,
                        "field_name": "",
                        "value": "c"
                    }
                ]
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorEtlSerializer)
        return Response(EtlHandler.etl_preview(**data))
