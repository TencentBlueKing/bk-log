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

from apps.generic import ModelViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import insert_permission_field, InstanceActionForDataPermission, ViewBusinessPermission
from apps.log_databus.handlers.archive import ArchiveHandler
from apps.log_databus.models import RestoreConfig, ArchiveConfig
from apps.log_databus.serializers import (
    RestoreArchiveSerlalizer,
    ListRestoreSerlalizer,
    UpdateRestoreArchiveSerlalizer,
    BatchGetStateSerlalizer,
)
from apps.utils.drf import list_route


class RestoreViewSet(ModelViewSet):
    lookup_field = "restore_config_id"
    model = RestoreConfig
    search_fields = ("created_by", "updated_by")
    ordering_fields = ("updated_at", "updated_by")

    def get_permissions(self):
        if self.action in ["create"]:
            return [
                InstanceActionForDataPermission(
                    "archive_config_id",
                    [ActionEnum.MANAGE_COLLECTION],
                    ResourceEnum.COLLECTION,
                    get_instance_id=ArchiveConfig.get_collector_config_id,
                )
            ]
        if self.action in ["destroy", "update"]:
            return [
                InstanceActionForDataPermission(
                    "restore_config_id",
                    [ActionEnum.MANAGE_COLLECTION],
                    ResourceEnum.COLLECTION,
                    get_instance_id=RestoreConfig.get_collector_config_id,
                )
            ]
        return [ViewBusinessPermission()]

    def create(self, request, *args, **kwargs):
        """
        @api {POST} /databus/restore/ 日志归档-创建归档回溯
        @apiName create_archive_restore
        @apiGroup Archive
        @apiDescription 创建归档回溯
        @apiParam {Int} archive_config_id 归档配置id
        @apiParam {Int} bk_biz_id 业务id
        @apiParam {String} index_set_name 索引集名称
        @apiParam {String} start_time 数据开始时间 2021-10-01 01:01:00
        @apiParam {String} end_time 数据开始时间 2021-10-01 01:01:00
        @apiParam {String} expired_time 数据开始时间 2021-10-01 01:01:00
        @apiParam {List} notice_user 通知用户数组
        @apiParamExample {json} 请求样例:
        {
            "archive_config_id": 1,
            "bk_biz_id": 1,
            "index_set_name": "test",
            "start_time": "2001-01-01 01:01:01",
            "end_time": "2001-01-01 01:01:01",
            "expired_time": "2001-01-01 01:01:01",
            "notice_user": ["xxxx", "xxxx", "xxxx"],
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(RestoreArchiveSerlalizer)
        archive_config_id = data.get("archive_config_id")
        data.pop("archive_config_id")
        return Response(ArchiveHandler(archive_config_id=archive_config_id).restore(**data))

    @insert_permission_field(
        id_field=lambda d: d["index_set_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.SEARCH_LOG],
        resource_meta=ResourceEnum.INDICES,
    )
    @insert_permission_field(
        id_field=lambda d: d["_collector_config_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/restore/?bk_biz_id=$bk_biz_id&page=$page&pagesize=$page_size 日志归档-归档回溯列表
        @apiName list_restore
        @apiGroup Archive
        @apiDescription 归档回溯列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Int} page 第几页
        @apiParam {Int} pagesize 每页大小
        @apiSuccess {Int} index_set_id 索引集id
        @apiSuccess {Int} index_set_name 索引集名称
        @apiSuccess {Int} total_store_size 存储大小 单位Byte
        @apiSuccess {String} start_time 数据开始时间 2021-10-01 01:01:00
        @apiSuccess {String} end_time 数据开始时间 2021-10-01 01:01:00
        @apiSuccess {String} expired_time 数据开始时间 2021-10-01 01:01:00
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "total": 1,
                "list": [
                    "index_set_name": "xxxx",
                    "index_set_id": 1,
                    "start_time": "2020-01-01 12:12:12",
                    "end_time": "2020-01-01 12:12:12",
                    "expired_time": "2020-01-01 12:12:12",
                    "collector_config_name": "xxx",
                    "total_store_size": 101200,
                ]
            },
            "code": 0,
            "message": ""
        }
        """
        self.valid_serializer(ListRestoreSerlalizer)
        response = super().list(request, *args, **kwargs)
        response.data["list"] = ArchiveHandler.list_restore(response.data["list"])
        return response

    def update(self, request, restore_config_id):
        """
        @api {PUT} /databus/restore/$restore_config_id/ 日志归档-更新归档回溯
        @apiName update_archive_restore
        @apiGroup Archive
        @apiDescription 更新归档回溯
        @apiParam {Int} restore_config_id 归档回溯id
        @apiParam {String} expired_time 数据开始时间 2021-10-01 01:01:00
        @apiParamExample {json} 请求样例:
        {
            "restore_config_id": 1,
            "expired_time": "2001-01-01 01:01:01",
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(UpdateRestoreArchiveSerlalizer)
        return Response(ArchiveHandler.update_restore(restore_config_id, data.get("expired_time")))

    def destroy(self, request, *args, restore_config_id, **kwargs):
        """
        @api {DELETE} /databus/restore/$restore_config_id 日志归档-删除归档回溯
        @apiName delete_archive_restore
        @apiGroup Archive
        @apiDescription 删除归档回溯
        @apiParam {Int} restore_config_id 归档回溯id
        @apiParamExample {json} 请求样例:
        {
            "restore_config_id": 1,
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "message": ""
        }
        """
        return Response(ArchiveHandler.delete_restore(restore_config_id))

    @list_route(methods=["POST"])
    def batch_get_state(self, request):
        """
        @api {POST} /databus/restore/batch_get_state/ 日志归档-回溯状态查询
        @apiName restore_batch_get_state
        @apiGroup Archive
        @apiDescription 回溯状态查询
        @apiParam {Int} restore_config_ids 归档回溯ids
        @apiParamExample {json} 请求样例:
        {
            "restore_config_ids": [1, 2, ,3 ,4, 4],
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "code": 0,
            "data": [
                {
                    "restore_config_id": 1,
                    "table_id": "xxx",
                    "restore_id": 1,
                    "complete_doc_count": 10,
                    "total_doc_count": 1
                }
            ],
            "message": ""
        }
        """
        data = self.params_valid(BatchGetStateSerlalizer)
        return Response(ArchiveHandler.batch_get_restore_state(data["restore_config_ids"]))
