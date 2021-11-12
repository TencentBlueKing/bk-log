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
from rest_framework import serializers
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.log_bcs.handlers.bcs_handler import BcsHandler
from apps.log_bcs.serializers import OpenBcsLogSerializer
from apps.utils.drf import detail_route


class BcsViewSet(APIViewSet):
    lookup_field = "bk_biz_id"
    serializer_class = serializers.Serializer

    @detail_route(methods=["POST"])
    def open_bcs_log(self, request, bk_biz_id):
        """
        @api {POST} /bcs/$bk_biz_id/open_bcs_log/ 开启bcs日志采集
        @apiName open_bcs_log
        @apiGroup Bcs
        @apiDescription 开启bcs日志采集
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} cluster_id 集群ID
        @apiParam {String} project_id 项目ID
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": null,
            "code": 0,
            "message": ""
        }
        """
        params = self.params_valid(OpenBcsLogSerializer)
        return Response(BcsHandler().register_bklog_to_bcs(params["cluster_id"], params["project_id"], bk_biz_id))

    @detail_route(methods=["GET"])
    def list_cluster(self, request, bk_biz_id):
        """
        @api {get} /bcs/$bk_biz_id/list_cluster/ bcs集群列表
        @apiName list_bcs_cluster
        @apiGroup Bcs
        @apiDescription 拉取业务下的bcs集群列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {String} area_name 区域名称
        @apiSuccess {String} project_name 项目名称
        @apiSuccess {String} project_id 项目ID
        @apiSuccess {String} cluster_id 集群ID
        @apiSuccess {Bool} has_open_log 是否开启日志采集
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "area_name": "区域",
                    "project_name": "蓝鲸监控",
                    "project_id": "f2e651a2b44a4eabb918d079d0da04c8",
                    "cluster_id": "BCS-K8S-40000",
                    "environment": "prod",
                    "status": "normal",
                    "has_open_log": true
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        return Response(BcsHandler().list_bcs_cluster(bk_biz_id))
