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
from blueapps.account.decorators import login_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response

from apps.generic import ModelViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import InstanceActionPermission
from apps.log_databus.handlers.itsm import ItsmHandler
from apps.log_databus.models import CollectorConfig
from apps.log_databus.serializers import CollectItsmCallbackSerializer, CollectItsmApplySerializer
from apps.utils.local import activate_request
from apps.utils.drf import list_route, detail_route


class ItsmViewSet(ModelViewSet):
    lookup_field = "collector_config_id"
    model = CollectorConfig
    http_method_names = ["get", "post"]

    def get_permissions(self):
        return [InstanceActionPermission([ActionEnum.VIEW_COLLECTION], ResourceEnum.COLLECTION)]

    def retrieve(self, request, *args, **kwargs):
        """
        @api {get} /databus/collect_itsm/$collector_config_id 查询采集ITSM状态
        @apiName collect_itsm_status
        @apiGroup collect_itsm
        @apiSuccess {String} data.description 描述
        @apiSuccess {String} collect_itsm_status 采集ITSM状态
        @apiSuccess {String} collect_itsm_status_display 采集ITSM状态显示名称
        @apiSuccess {String} ticket_url 采集ITSM流程地址
        @apiSuccess {String} expect_access_data 期待接入日期 2020-01-01
        @apiSuccess {String} single_log_size 单条日志大小(bytes)
        @apiSuccess {String} single_host_peak 单机流量峰值（kB/S）
        @apiSuccess {String} single_host_log_volume 单机增长日志量
        @apiSuccess {String} expect_host_size 预计接入主机数
        @apiSuccess {String} log_keep_days 日志保留天数
        @apiSuccess {String}  hot_data_days 热数据天数
        @apiSuccess {String}  capacity_description 容量说明
        @apiSuccess {String}  apply_reason 申请原因
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collect_itsm_status": "applying",
                "collect_itsm_status_display": "采集接入进行中",
                "ticket_url": "",
                "title": "【日志采集】功夫西游-test_test_test-20201203",
                "expect_access_data": "2020-01-01",
                "single_log_size": "10",
                "single_host_peak": "10",
                "single_host_log_volume": "10",
                "expect_host_size": "10",
                "log_keep_days": "10",
                "capacity_description": "aestdfasdfgasf",
                "apply_reason": "asdfsdaf",
                "can_use_independent_es_cluster": "false",
                "hot_data_days": "10"
            },
            "result": true
        }
        """
        return Response(ItsmHandler().collect_itsm_status(kwargs.get("collector_config_id")))

    @detail_route(methods=["post"])
    def apply_itsm_ticket(self, request, *args, **kwargs):
        """
        @api {post} /databus/collect_itsm/$collector_config_id/apply_itsm_ticket 创建采集ITSM单据
        @apiName create_itsm_ticket
        @apiGroup collect_itsm
        @apiParam {String} expect_access_data 期待接入日期 2020-01-01
        @apiParam {Int} single_log_size 单条日志大小(bytes)
        @apiParam {Int} single_host_peak 单机流量峰值（kB/S）
        @apiParam {Int} single_host_log_volume 单机增长日志量
        @apiParam {Int} expect_host_size 预计接入主机数
        @apiParam {Int} log_keep_days 日志保留天数
        @apiParam {Int}  hot_data_days 热数据天数
        @apiParam {Int}  expect_increment_log_size 预计增长日志量（GB/day）
        @apiParam {String}  capacity_description 容量说明
        @apiParam {String}  apply_reason 申请原因
        @apiParamExample {json} 请求样例:
        {
            "expect_access_data": "2020-01-01",
            "single_log_size": 10,
            "single_host_peak": 10,
            "single_host_log_volume": 10,
            "expect_host_size": 10,
            "log_keep_days": 10,
            "hot_data_days": 10,
            "expect_increment_log_size": 10,
            "capacity_description": "aestdfasdfgasf",
            "apply_reason": "asdfsdaf"
        }
        @apiSuccess {String} collect_itsm_status 采集ITSM状态
        @apiSuccess {String} collect_itsm_status_display 采集ITSM状态显示名称
        @apiSuccess {String} ticket_url 采集ITSM流程地址
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collect_itsm_status": "applying",
                "collect_itsm_status_display": "采集接入进行中",
                "ticket_url": "",
            },
            "result": true
        }
        """
        params = self.params_valid(CollectItsmApplySerializer)
        return Response(ItsmHandler().apply_itsm_ticket(kwargs.get("collector_config_id"), params))


@method_decorator(login_exempt, name="dispatch")
class ItsmCallbackViewSet(ModelViewSet):
    model = CollectorConfig

    @list_route(methods=["post"])
    def collect_itsm_callback(self, request):
        data = self.params_valid(CollectItsmCallbackSerializer)
        itsm_handler = ItsmHandler()
        request.user.username = CollectorConfig.objects.get(itsm_ticket_sn=data["sn"]).get_updated_by()
        activate_request(request, request.request_id)
        itsm_handler.verify_token(data["token"])
        itsm_handler.update_collect_itsm_status(data)
        return Response()
