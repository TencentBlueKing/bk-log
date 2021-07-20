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
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _

from apps.generic import ModelViewSet
from apps.utils.drf import list_route
from apps.bk_log_admin.serializers import AuditRecordSerializer
from apps.log_audit.models import UserOperationRecord
from apps.bk_log_admin.handlers.audit_record import AuditRecordHandler


class AuditRecordViewSet(ModelViewSet):
    model = UserOperationRecord

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "get_record": AuditRecordSerializer,
        }
        return action_serializer_map.get(self.action)

    @list_route(methods=["get"], url_path="record")
    def get_record(self, request, *args, **kwargs):
        """
        @api {get} /admin/audit/record?page=&pagesize=&record_type=xx&record_object_id=1&bk_biz_id= 01_获取操作记录
        @apiName get_audit_record
        @apiGroup 60_admin
        @apiDescription 获取操作记录
        @apiParam {String} record_type 操作种类
        @apiParam {Int} record_object_id 对应操作对象id
        @apiParam {Int} bk_biz_id 对应业务id
        @apiParam {Int} page 页数
        @apiParam {Int} pagesize 每页数量
        @apiSuccess {Int} total 总数
        @apiSuccess {List} results 操作记录列表
        @apiSuccess {Int} results.id ID
        @apiSuccess {Int} results.bk_biz_id 操作id
        @apiSuccess {String} results.content 操作内容
        @apiSuccess {Datetime} results.created_at 事件发生时间
        @apiSuccess {String} results.created_by 创建者
        @apiSuccess {Boolean} results.result 操作结果
        @apiSuccessExample {Json} 成功返回
        {
            "result":true,
            "data":{
                "total":1,
                "results":[
                    {
                        "id": 37,
                        "bk_biz_id": 1,
                        "content": "日志提取链路删除 操作对象：17 请求内容：空",
                        "created_by": "test1",
                        "created_at": "2021-03-16 23:05:13+0800",
                        "result": true
                    }
                ]
            },
            "code":0,
            "message":""
        }
        """
        if not request.GET.get("page") or not request.GET.get("pagesize"):
            raise ValueError(_("分页参数不能为空"))
        response = super().list(request, *args, **kwargs)
        response.data["list"] = [AuditRecordHandler.response_format(records) for records in response.data["list"]]
        return Response(response.data)
