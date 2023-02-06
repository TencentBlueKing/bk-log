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
from apps.generic import ModelViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import (
    ViewBusinessPermission,
    insert_permission_field,
    InstanceActionForDataPermission,
)
from apps.log_databus.constants import ArchiveInstanceType
from apps.log_databus.handlers.archive import ArchiveHandler

from apps.log_databus.models import ArchiveConfig, CollectorPlugin
from apps.log_databus.serializers import (
    CreateArchiveSerlalizer,
    ListArchiveSerlalizer,
    UpdateArchiveSerlalizer,
    ListArhiveSwitchSerlalizer,
    PageSerializer,
)
from apps.utils.drf import list_route, detail_route
from rest_framework.response import Response


class ArchiveViewSet(ModelViewSet):
    lookup_field = "archive_config_id"
    model = ArchiveConfig
    search_fields = ("target_snapshot_repository_name", "created_by", "updated_by")
    ordering_fields = ("updated_at", "updated_by")

    def get_permissions(self):
        if self.action in ["create"]:
            instance_id = self.request.data.get("instance_id")
            instance_type = self.request.data.get("instance_type")
            # 若创建的是采集插件类型归档。需要使用任一采集项进行鉴权
            if instance_type == ArchiveInstanceType.COLLECTOR_PLUGIN.value:
                self.request.data["collector_config_id"] = CollectorPlugin.get_collector_config_id(instance_id)
            if instance_type == ArchiveInstanceType.COLLECTOR_CONFIG.value:
                self.request.data["collector_config_id"] = instance_id
            return [
                InstanceActionForDataPermission(
                    "collector_config_id", [ActionEnum.MANAGE_COLLECTION], ResourceEnum.COLLECTION
                )
            ]
        if self.action in ["destroy", "update", "restore", "retrieve"]:
            return [
                InstanceActionForDataPermission(
                    "archive_config_id",
                    [ActionEnum.MANAGE_COLLECTION],
                    ResourceEnum.COLLECTION,
                    get_instance_id=ArchiveConfig.get_collector_config_id,
                )
            ]
        return [ViewBusinessPermission()]

    @insert_permission_field(
        id_field=lambda d: d["_collector_config_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/archive/?bk_biz_id=$bk_biz_id&page=$page&pagesize=$pagesize 日志归档-归档列表
        @apiName list_archive
        @apiGroup Archive
        @apiDescription 拉取归档列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Int} page 第几页
        @apiParam {Int} pagesize 一页大小
        @apiSuccess {Int} archive_config_id 归档配置id
        @apiSuccess {Int} collector_config_id 采集项id
        @apiSuccess {String} collector_config_name 采集项名称
        @apiSuccess {Int} bk_biz_id 业务id
        @apiSuccess {Int} snapshot_days 归档存储天数 0 为永久
        @apiSuccess {String} target_snapshot_repository_name 目标快照仓库
        @apiSuccess {Dict} snapshots 归档存储的物理快照
        @apiSuccess {String} snapshots.snapshot_name 快照名称
        @apiSuccess {Dict} snapshots.indices 快照存储的物理索引
        @apiSuccess {String} snapshots.indices.index_name 物理索引名称
        @apiSuccess {String} snapshots.indices.start_time 物理索引开始时间
        @apiSuccess {String} snapshots.indices.end_time 物理索引结束时间
        @apiSuccess {Int} snapshots.indices.doc_count 文档数量
        @apiSuccess {Int} snapshots.indices.store_size 存储大小 单位Byte
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
               {
                "archive_config_id": 1,
                "collector_config_id": 1,
                "collector_config_name": "xxxx",
                "bk_biz_id": 12,
                "snapshot_days": 12,
                "target_snapshot_repository_name": "目标快照仓库",
            }
            ],
            "code": 0,
            "message": ""
        }
        """
        self.valid_serializer(ListArchiveSerlalizer)
        response = super().list(request, *args, **kwargs)
        response.data["list"] = ArchiveHandler.list(response.data["list"])
        return response

    def create(self, request, *args, **kwargs):
        """
        @api {POST} /databus/archive/ 日志归档-创建归档
        @apiName create_archive
        @apiGroup Archive
        @apiDescription 创建归档
        @apiParam {Int} collector_config_id 采集配置id
        @apiParam {Int} bk_biz_id 业务id
        @apiParam {Int} snapshot_days 归档存储天数 0 为永久
        @apiParam {String} target_snapshot_repository_name 目标快照仓库
        @apiParamExample {json} 请求样例:
        {
            "collector_config_id": 1,
            "snapshot_days": 1,
            "target_snapshot_repository_name": "test",
            "bk_biz_id": 12
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(CreateArchiveSerlalizer)
        return Response(ArchiveHandler().create_or_update(data))

    def retrieve(self, request, *args, archive_config_id, **kwargs):
        """
        @api {GET} /databus/archive/$archive_config_id/ 日志归档-归档配置详情
        @apiName retrieve_archive
        @apiGroup Archive
        @apiDescription 归档配置详情
        @apiParam {Int} archive_config_id 归档配置id
        @apiParam {Int} page 分页
        @apiParam {Int} pagesize 分页
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "data": {
                "archive_config_id": 1,
                "collector_config_id": 1,
                "collector_config_name": "xxxx",
                "bk_biz_id": 12,
                "snapshot_days": 12,
                "target_snapshot_repository_name": "目标快照仓库",
                "snapshots": [
                    {
                        "snapshot_name": "xxxxx",
                        "table_id": "xxxx",
                        "indices": [
                            "table_id": "xxxx",
                            "cluster_id": 1,
                            "repository_name": "xxx",
                            "snapshot_name": "xxx",
                            "index_name": "xxxx",
                            "start_time": "2020-01-01 12:12:12",
                            "end_time": "2020-01-01 12:12:12",
                            "doc_count": 102020,
                            "store_size": 101200,
                        ]
                    }
                ]
            }
            "message": ""
        }
        """
        data = self.params_valid(PageSerializer)
        return Response(ArchiveHandler(archive_config_id).retrieve(**data))

    def destroy(self, request, *args, archive_config_id, **kwargs):
        """
        @api {DELETE} /databus/archive/$archive_config_id/ 日志归档-删除归档配置
        @apiName delete_archive
        @apiGroup Archive
        @apiDescription 删除归档
        @apiParam {Int} archive_config_id 归档配置id
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
        }
        """
        return Response(ArchiveHandler(archive_config_id).delete())

    def update(self, request, *args, archive_config_id, **kwargs):
        """
        @api {PUT} /databus/archive/$archive_config_id 日志归档-更新归档
        @apiName update_archive
        @apiGroup Archive
        @apiDescription 更新归档
        @apiParam {Int} archive_config_id 归档配置id
        @apiParam {Int} snapshot_days 归档存储天数 0 为永久
        @apiParamExample {json} 请求样例:
        {
            "snapshot_days": 1,
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(UpdateArchiveSerlalizer)
        return Response(ArchiveHandler(archive_config_id).create_or_update(data))

    @insert_permission_field(
        id_field=lambda d: d["_collector_config_id"],
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    @list_route(methods=["GET"])
    def list_archive(self, request):
        """
        @api {get} /databus/archive/list_archive/?bk_biz_id=$bk_biz_id 日志归档-归档下拉列表
        @apiName list_archive_switch
        @apiGroup Archive
        @apiDescription 归档下拉列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Int} archive_config_id 归档配置id
        @apiSuccess {String} collector_config_name 采集项名称
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                "archive_config_id": 1,
                "collector_config_name": "xxx"
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(ListArhiveSwitchSerlalizer)
        return Response(ArchiveHandler.list_archive(data["bk_biz_id"]))

    @detail_route(methods=["GET"])
    def state(self, request, archive_config_id):
        """
        @api {POST} /databus/archive/$archive_config_id/state/ 日志归档-归档状态查询
        @apiName archive_state
        @apiGroup Archive
        @apiDescription 归档状态查询
        @apiParam {Int} restore_config_ids 归档回溯ids
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "data": [
                {
                    "table_id": "xxx",
                    "snapshot_name": "xxxx",
                    "state": "SUCCESS"
                }
            ],
            "message": ""
        }
        """
        return Response(ArchiveHandler(archive_config_id).archive_state())
