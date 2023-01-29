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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.response import Response
from apps.utils.drf import detail_route, list_route
from apps.generic import ModelViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import (
    BusinessActionPermission,
    InstanceActionPermission,
    ViewBusinessPermission,
    insert_permission_field,
)
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import LogIndexSet, Scenario
from apps.log_search.permission import Permission
from apps.exceptions import ValidationError
from apps.log_search.constants import TimeFieldTypeEnum, TimeFieldUnitEnum
from apps.log_search.tasks.bkdata import sync_auth_status
from apps.log_search.exceptions import BkJwtVerifyException, IndexSetNotEmptyException
from bkm_space.serializers import SpaceUIDField


class IndexSetViewSet(ModelViewSet):
    """
    索引集管理
    """

    lookup_field = "index_set_id"
    model = LogIndexSet
    search_fields = ("index_set_name",)
    lookup_value_regex = "[^/]+"

    def get_permissions(self):
        try:
            auth_info = Permission.get_auth_info(self.request)
            # ESQUERY白名单不需要鉴权
            if auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
                return []
        except Exception:  # pylint: disable=broad-except
            pass
        if self.action in ["mark_favorite", "cancel_favorite"]:
            return []
        if self.action in ["create", "replace"]:
            return [BusinessActionPermission([ActionEnum.CREATE_INDICES])]
        if self.action in ["update", "destroy"]:
            return [InstanceActionPermission([ActionEnum.MANAGE_INDICES], ResourceEnum.INDICES)]
        return [ViewBusinessPermission()]

    def get_queryset(self):
        return LogIndexSet.objects.filter(collector_config_id__isnull=True)

    def get_serializer_class(self, *args, **kwargs):
        serializer_class = super().get_serializer_class()

        class CustomSerializer(serializer_class):
            view_roles = serializers.ListField(default=[])
            bkdata_project_id = serializers.IntegerField(read_only=True)
            indexes = serializers.ListField(allow_empty=True)
            is_trace_log = serializers.BooleanField(required=False, default=False)
            time_field = serializers.CharField(required=False, default=None)
            time_field_type = serializers.ChoiceField(
                required=False, default=None, choices=TimeFieldTypeEnum.get_choices()
            )
            time_field_unit = serializers.ChoiceField(
                required=False, default=None, choices=TimeFieldUnitEnum.get_choices()
            )

            class Meta:
                model = LogIndexSet
                fields = "__all__"

            def validate_indexes(self, value):
                if value:
                    return value
                raise IndexSetNotEmptyException

        class CreateSerializer(CustomSerializer):
            index_set_name = serializers.CharField(required=True)
            result_table_id = serializers.CharField(required=False)
            storage_cluster_id = serializers.IntegerField(required=False)
            category_id = serializers.CharField(required=True)
            scenario_id = serializers.CharField(required=True)
            space_uid = SpaceUIDField(label=_("空间唯一标识"), required=True)
            bkdata_auth_url = serializers.ReadOnlyField()
            is_editable = serializers.BooleanField(required=False, default=True)

            def validate(self, attrs):
                attrs = super().validate(attrs)

                scenario_id = attrs["scenario_id"]
                if scenario_id == Scenario.ES and not attrs.get("storage_cluster_id"):
                    raise ValidationError(_("集群ID不能为空"))
                return attrs

        class UpdateSerializer(CustomSerializer):
            index_set_name = serializers.CharField(required=True)
            storage_cluster_id = serializers.IntegerField(required=False, default=None)
            scenario_id = serializers.CharField(required=True)
            category_id = serializers.CharField(required=True)
            space_uid = SpaceUIDField(label=_("空间唯一标识"), required=True)
            bkdata_auth_url = serializers.ReadOnlyField()

        class ShowMoreSerializer(CustomSerializer):
            source_name = serializers.CharField(read_only=True)

        class ReplaceSerializer(CreateSerializer):
            category_id = serializers.CharField(required=False)
            bk_app_code = serializers.CharField(required=True, write_only=True)

        if self.request.query_params.get("show_more", False):
            # 显示更多，把索引集内的索引一并查出，一般列表中无需使用到
            return ShowMoreSerializer

        action_serializer_map = {
            "update": UpdateSerializer,
            "create": CreateSerializer,
            "retrieve": ShowMoreSerializer,
            "replace": ReplaceSerializer,
        }
        return action_serializer_map.get(self.action, CustomSerializer)

    @insert_permission_field(
        actions=[ActionEnum.MANAGE_INDICES],
        resource_meta=ResourceEnum.INDICES,
        id_field=lambda d: d["index_set_id"],
        data_field=lambda d: d["list"],
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /index_set/ 索引集-列表
        @apiName list_index_set
        @apiGroup 05_AccessIndexSet
        @apiDescription 未做分页处理; view_roles需同时返回角色名称； 需同时返回索引数据
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {Int} [storage_cluster_id] 数据源ID
        @apiParam {String} [keyword] 搜索关键字
        @apiParam {Int} page 当前页数
        @apiParam {Int} pagesize 分页大小
        @apiSuccess {Int} index_set_id 索引集ID
        @apiSuccess {String} index_set_name 索引集名称
        @apiSuccess {String} space_uid 空间唯一标识
        @apiSuccess {Int} storage_cluster_id 数据源ID
        @apiSuccess {Int} source_name 数据源名称
        @apiSuccess {String} scenario_id 接入场景
        @apiSuccess {String} scenario_name 接入场景名称
        @apiSuccess {String} category_id 数据分类
        @apiSuccess {String} cluster_name 数据分类名称
        @apiSuccess {Int} storage_cluster_id 存储集群ID
        @apiSuccess {Int} storage_cluster_name 存储集群名称
        @apiSuccess {List} view_roles 可查看角色ID列表
        @apiSuccess {List} view_roles_list 可查看角色列表
        @apiSuccess {Int} view_roles_list.role_id 角色ID
        @apiSuccess {String} view_roles_list.role_name 角色名称
        @apiSuccess {Object} indexes 索引集名称
        @apiSuccess {Int} indexes.bk_biz_id 业务ID
        @apiSuccess {String} indexes.index_id 索引ID
        @apiSuccess {String} indexes.result_table_id 数据源-索引ID
        @apiSuccess {String} indexes.time_field 时间字段
        @apiSuccess {String} indexes.apply_status 审核状态
        @apiSuccess {String} indexes.apply_status_name 审核状态名称
        @apiSuccess {String} indexes.created_at 创建时间
        @apiSuccess {String} indexes.created_by 创建者
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "total": 100,
                "list": [
                    {
                        "index_set_id": 1,
                        "index_set_name": "登陆日志",
                        "space_uid": "bkcc__2",
                        "storage_cluster_id": 1,
                        "source_name": "ES集群",
                        "scenario_id": "es",
                        "scenario_name": "用户ES",
                        "category_id": "hosts",
                        "category_name": "主机",
                        "storage_cluster_id": 15,
                        "storage_cluster_name": "es_demo",
                        "orders": 1,
                        "view_roles": [1, 2, 3],
                        "view_roles_list": [
                            {
                                "role_id": 1,
                                "role_name": "运维"
                            },
                            {
                                "role_id": 2,
                                "role_name": "产品"
                            }
                        ],
                        "indexes": [
                            {
                                "index_id": 1,
                                "index_set_id": 1,
                                "bk_biz_id": 1,
                                "bk_biz_name": "业务名称",
                                "storage_cluster_id": 1,
                                "source_name": "数据源名称",
                                "result_table_id": "结果表",
                                "result_table_name_alias": "结果表显示名",
                                "time_field": "时间字段",
                                "apply_status": "pending",
                                "apply_status_name": "审核状态名称",
                                "created_at": "2019-10-10 11:11:11",
                                "created_by": "user",
                                "updated_at": "2019-10-10 11:11:11",
                                "updated_by": "user",
                            }
                        ]
                        "created_at": "2019-10-10 11:11:11",
                        "created_by": "user",
                        "updated_at": "2019-10-10 11:11:11",
                        "updated_by": "user",
                        "time_field": "dtEventTimeStamp",
                        "time_field_type": "date",
                        "time_field_unit": "microsecond"
                    }
                ]
            },
            "result": true
        }
        """
        # 强制前端必须传分页参数
        if not request.GET.get("page") or not request.GET.get("pagesize"):
            raise ValueError(_("分页参数不能为空"))
        response = super().list(request, *args, **kwargs)
        response.data["list"] = IndexSetHandler.post_list(response.data["list"])
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        @api {get} /index_set/$index_set_id/ 索引集-详情
        @apiName retrieve_index_set
        @apiGroup 05_AccessIndexSet
        @apiParam {Int} index_set_id 索引集ID
        @apiSuccess {Int} index_set_id 索引集ID
        @apiSuccess {String} index_set_name 索引集名称
        @apiSuccess {String} space_uid 空间唯一标识
        @apiSuccess {Int} storage_cluster_id 数据源ID
        @apiSuccess {Int} source_name 数据源名称
        @apiSuccess {String} scenario_id 接入场景
        @apiSuccess {String} scenario_name 接入场景名称
        @apiSuccess {List} view_roles 可查看角色ID列表
        @apiSuccess {List} view_roles_list 可查看角色列表
        @apiSuccess {Int} view_roles_list.role_id 角色ID
        @apiSuccess {String} view_roles_list.role_name 角色名称
        @apiSuccess {Object} indexes 索引集名称
        @apiSuccess {Int} [indexes.bk_biz_id] 业务ID
        @apiSuccess {String} indexes.index_id 索引ID
        @apiSuccess {String} indexes.result_table_id 数据源-索引ID
        @apiSuccess {String} indexes.time_field 时间字段
        @apiSuccess {String} indexes.apply_status 审核状态
        @apiSuccess {String} indexes.apply_status_name 审核状态名称
        @apiSuccess {String} indexes.created_at 创建时间
        @apiSuccess {String} indexes.created_by 创建者
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "index_set_id": 1,
                "index_set_name": "登陆日志",
                "space_uid": "bkcc__2",
                "storage_cluster_id": 1,
                "source_name": "ES集群",
                "scenario_id": "es",
                "scenario_name": "用户ES",
                "orders": 1,
                "view_roles": [1, 2, 3],
                "view_roles_list": [
                    {
                        "role_id": 1,
                        "role_name": "运维"
                    },
                    {
                        "role_id": 2,
                        "role_name": "产品"
                    }
                ],
                "indexes": [
                    {
                        "index_id": 1,
                        "index_set_id": 1,
                        "bk_biz_id": 1,
                        "bk_biz_name": "业务名称",
                        "storage_cluster_id": 1,
                        "source_name": "数据源名称",
                        "result_table_id": "结果表",
                        "result_table_name_alias": "结果表显示名",
                        "time_field": "时间字段",
                        "apply_status": "pending",
                        "apply_status_name": "审核状态名称",
                        "created_at": "2019-10-10 11:11:11",
                        "created_by": "user",
                        "updated_at": "2019-10-10 11:11:11",
                        "updated_by": "user",
                    }
                ]
                "created_at": "2019-10-10 11:11:11",
                "created_by": "user",
                "updated_at": "2019-10-10 11:11:11",
                "updated_by": "user",
            },
            "result": true
        }
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        @api {post} /index_set/ 索引集-创建
        @apiName create_index_set
        @apiDescription storage_cluster_id&view_roles校验、索引列表处理
        @apiGroup 05_AccessIndexSet
        @apiParam {String} index_set_name 索引集名称
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {String} [is_editable] 此索引集是否可以编辑
        @apiParam {Int} storage_cluster_id 数据源ID
        @apiParam {String} result_table_id 数据源ID
        @apiParam {String} category_id 数据分类
        @apiParam {String} scenario_id 接入场景ID
        @apiParam {List} view_roles 可查看角色ID列表，可填角色ID，如 "1", "2", 也可以填角色名称，
                                    如 "bk_biz_maintainer", "bk_biz_developer", "bk_biz_productor"
        @apiParam {Object} indexes 索引集列表
        @apiParam {String} indexes.result_table_id 索引ID
        @apiParam {String} indexes.time_field 时间字段(逻辑暂时保留)
        @apiParam {String} is_trace_log 是否是trace类日志
        @apiParam {String} time_field 时间字段
        @apiParam {String} time_field_type 时间字段类型（当选择第三方es时候需要传入，默认值是date,可传入如long）
        @apiParam {String} time_field_unit 时间字段类型单位（当选择非date的时候传入，秒/毫秒/微秒）
        @apiParamExample {Json} 请求参数
        {
            "index_set_name": "登陆日志",
            "space_uid": "bkcc__2",
            "storage_cluster_id": 1,
            "scenario_id": "es",
            "view_roles": [1, 2, 3],
            "indexes": [
                {
                    "bk_biz_id": 1,
                    "result_table_id": "591_xx",
                    "time_field": "timestamp"
                },
                {
                    "bk_biz_id": null,
                    "result_table_id": "log_xxx",
                    "time_field": "timestamp"
                }
            ],
            "time_field": "abc",
            "time_field_type": "date"/"long",
            "time_field_unit": "second"/"millisecond"/"microsecond"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        data = self.validated_data

        if data["scenario_id"] == Scenario.BKDATA or settings.RUN_VER == "tencent":
            storage_cluster_id = None
        elif data["scenario_id"] == Scenario.ES:
            storage_cluster_id = data["storage_cluster_id"]
        else:
            storage_cluster_id = IndexSetHandler.get_storage_by_table_list(data["indexes"])
        # 获取调用方APP CODE
        data = self.validated_data
        auth_info = Permission.get_auth_info(request, raise_exception=False)
        if auth_info:
            data["bk_app_code"] = auth_info["bk_app_code"]

        index_set = IndexSetHandler.create(
            data["index_set_name"],
            data["space_uid"],
            storage_cluster_id,
            data["scenario_id"],
            data["view_roles"],
            data["indexes"],
            data["category_id"],
            is_trace_log=data["is_trace_log"],
            time_field=data["time_field"],
            time_field_type=data["time_field_type"],
            time_field_unit=data["time_field_unit"],
            bk_app_code=data.get("bk_app_code"),
            is_editable=data.get("is_editable"),
        )
        return Response(self.get_serializer_class()(instance=index_set).data)

    def update(self, request, *args, **kwargs):
        """
        @api {post} /index_set/$index_set_id/ 索引集-更新
        @apiName update_index_set
        @apiGroup 05_AccessIndexSet
        @apiParam {String} is_trace_log 是否是trace类日志
        @apiParam {Int} storage_cluster_id 数据源ID
        @apiParam {String} time_field 时间字段
        @apiParam {String} time_field_type 时间字段类型（当选择第三方es时候需要传入，默认值是date,可传入如long）
        @apiParam {String} time_field_unit 时间字段类型单位（当选择非date的时候传入，秒/毫秒/微秒）
        @apiParamExample {Json} 请求参数
        {
            "index_set_name": "登陆日志",
            "view_roles": [1, 2, 3],
            "category_id": host,
            "indexes":[
                {
                    "bk_biz_id": 1,
                    "result_table_id": "591_xx"
                    "time_field": "timestamp"
                },
                {
                    "bk_biz_id": null,
                    "result_table_id": "log_xxx",
                    "time_field": "timestamp"
                }
            ],
            "time_field": "abc",
            "time_field_type": "date"/"long",
            "time_field_unit": "second"/"millisecond"/"microsecond"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        handler = IndexSetHandler(index_set_id=kwargs["index_set_id"])

        data = self.validated_data
        if data["scenario_id"] == Scenario.BKDATA or settings.RUN_VER == "tencent":
            storage_cluster_id = None
        elif data["scenario_id"] == Scenario.ES:
            storage_cluster_id = data["storage_cluster_id"]
        else:
            storage_cluster_id = IndexSetHandler.get_storage_by_table_list(data["indexes"])

        index_set = handler.update(
            data["index_set_name"],
            data["view_roles"],
            data["indexes"],
            data["category_id"],
            is_trace_log=data["is_trace_log"],
            time_field=data["time_field"],
            time_field_type=data["time_field_type"],
            time_field_unit=data["time_field_unit"],
            storage_cluster_id=storage_cluster_id,
        )
        return Response(self.get_serializer_class()(instance=index_set).data)

    @list_route(methods=["POST"], url_path="replace")
    def replace(self, request, *args, **kwargs):
        """
        @api {post} /index_set/ 索引集-替换
        @apiName replace_index_set
        @apiDescription 索引集替换，仅用于第三方APP使用
        @apiGroup 05_AccessIndexSet
        @apiParam {String} index_set_name 索引集名称
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {Int} storage_cluster_id 数据源ID
        @apiParam {String} result_table_id 数据源ID
        @apiParam {String} category_id 数据分类
        @apiParam {String} scenario_id 接入场景ID
        @apiParam {List} view_roles 可查看角色ID列表，可填角色ID，如 "1", "2", 也可以填角色名称，
                                    如 "bk_biz_maintainer", "bk_biz_developer", "bk_biz_productor"
        @apiParam {Object} indexes 索引集列表
        @apiParam {String} indexes.result_table_id 索引ID
        @apiParam {String} indexes.time_field 时间字段(逻辑暂时保留)
        @apiParam {String} is_trace_log 是否是trace类日志
        @apiParam {String} time_field 时间字段
        @apiParam {String} time_field_type 时间字段类型（当选择第三方es时候需要传入，默认值是date,可传入如long）
        @apiParam {String} time_field_unit 时间字段类型单位（当选择非date的时候传入，秒/毫秒/微秒）
        @apiParamExample {Json} 请求参数
        {
            "index_set_name": "登陆日志",
            "space_uid": "bkcc__2",
            "storage_cluster_id": 1,
            "scenario_id": "es",
            "view_roles": [1, 2, 3],
            "indexes": [
                {
                    "bk_biz_id": 1,
                    "result_table_id": "591_xx",
                    "time_field": "timestamp"
                },
                {
                    "bk_biz_id": null,
                    "result_table_id": "log_xxx",
                    "time_field": "timestamp"
                }
            ],
            "time_field": "abc",
            "time_field_type": "date"/"long",
            "time_field_unit": "second"/"millisecond"/"microsecond"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        data = self.validated_data
        auth_info = Permission.get_auth_info(request, raise_exception=False)
        if not auth_info:
            raise BkJwtVerifyException()

        index_set = IndexSetHandler.replace(
            data["index_set_name"],
            data["scenario_id"],
            data["view_roles"],
            data["indexes"],
            auth_info["bk_app_code"],
            space_uid=data.get("space_uid"),
            storage_cluster_id=data.get("storage_cluster_id"),
            category_id=data.get("category_id"),
            collector_config_id=data.get("collector_config_id"),
        )
        return Response(self.get_serializer_class()(instance=index_set).data)

    def destroy(self, request, *args, **kwargs):
        """
        @api {delete} /index_set/$index_set_id/ 索引集-删除
        @apiName delete_index_set
        @apiGroup 05_AccessIndexSet
        @apiDescription 已删除索引未做判断
        @apiParam {Int} index_set_id 索引集ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        IndexSetHandler(index_set_id=kwargs["index_set_id"]).delete()
        return Response()

    @detail_route(methods=["GET", "POST"])
    def sync_auth_status(self, request, *args, **kwargs):
        """
        @api {post} /index_set/$index_set_id/sync_auth_status/ 更新授权状态
        @apiName sync_auth_status
        @apiGroup 05_AccessIndexSet
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "index_id": 1,
                    "index_set_id": 1,
                    "bk_biz_id": 1,
                    "bk_biz_name": "业务名称",
                    "source_name": "数据源名称",
                    "result_table_id": "结果表",
                    "result_table_name_alias": "结果表显示名",
                    "time_field": "时间字段",
                    "apply_status": "pending",
                    "apply_status_name": "审核状态名称",
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        sync_auth_status()
        return Response(self.get_object().indexes)

    @detail_route(methods=["GET"], url_path="indices")
    def indices(self, request, index_set_id, *args, **kwargs):
        """
        @api {post} /index_set/$index_set_id/indices/ 索引集物理索引信息
        @apiName indices
        @apiGroup 05_AccessIndexSet
        @apiSuccess {Int} total 索引集数量
        @apiSuccess {String} result_table_id rt_id
        @apiSuccess {Dict} item key为索引集名称
        @apiSuccess {String} health 索引健康状态 red green yellow
        @apiSuccess {String} status 索引状态
        @apiSuccess {String} pri 主分片数量
        @apiSuccess {String} rep 副本数量
        @apiSuccess {String} index 索引名称
        @apiSuccess {String} docs.count 文档数量
        @apiSuccess {String} docs.deleted 删除文档数量
        @apiSuccess {String} store.size 储存大小 Byte
        @apiSuccess {String} pri.store.size 主分片储存大小 Byte
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "total": 2,
                "list": [{
                    "result_table_id": "215_bklog.test_samuel_111111",
                    "stat": {
                        "health": "green",
                        "status": "open",
                        "pri": "3",
                        "rep": "1",
                        "docs.count": "0",
                        "docs.deleted": "0",
                        "store.size": "1698",
                        "pri.store.size": "849"
                    },
                    "details": [{
                        "health": "green",
                        "status": "open",
                        "index": "v2_215_bklog_test_samuel_111111_20210315_0",
                        "uuid": "V6ZuLKXAR06kQriSWyXXmA",
                        "pri": "3",
                        "rep": "1",
                        "docs.count": "0",
                        "docs.deleted": "0",
                        "store.size": "1698",
                        "pri.store.size": "849"
                    }]
                }]
            }
        }
        }
        """
        return Response(IndexSetHandler(index_set_id).indices())

    @detail_route(methods=["POST"])
    def mark_favorite(self, request, index_set_id, *arg, **kwargs):
        """
        @api {POST} /index_set/$index_set_id/mark_favorite/ 标记索引集为收藏索引集
        @apiName mark_favorite
        @apiGroup 05_AccessIndexSet
        """
        return Response(IndexSetHandler(index_set_id).mark_favorite())

    @detail_route(methods=["POST"])
    def cancel_favorite(self, request, index_set_id, *arg, **kwargs):
        """
        @api {POST} /index_set/$index_set_id/cancel_favorite/ 取消标记为收藏索引集
        @apiName cancel_favorite
        @apiGroup 05_AccessIndexSet
        """
        return Response(IndexSetHandler(index_set_id).cancel_favorite())
