# -*- coding: utf-8 -*-
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
                        "created_by": "samuelsheng",
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
