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

from apps.utils.drf import list_route
from apps.generic import ModelViewSet
from apps.log_databus.handlers.link import DataLinkHandler
from apps.log_databus.models import DataLinkConfig
from apps.log_databus.permission import SuperuserWritePermission
from apps.log_databus.serializers import (
    DataLinkCreateUpdateSerializer,
    ClusterListSerializer,
    DataLinkListSerializer,
)


class DataLinkViewSet(ModelViewSet):
    """
    数据链路
    """

    lookup_field = "data_link_id"
    model = DataLinkConfig

    permission_classes = [
        SuperuserWritePermission,
    ]

    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/link/?bk_biz_id=1 数据链路列表
        @apiName list_data_link
        @apiGroup link
        @apiSuccess {Int} data.data_link_id 数据链路id
        @apiSuccess {Int} data.link_group_name 链路集群名称
        @apiSuccess {Int} data.bk_biz_id 链路允许的业务id
        @apiSuccess {Int} data.kafka_cluster_id kafka集群id
        @apiSuccess {Int} data.transfer_cluster_id transfer集群id
        @apiSuccess {list} data.es_cluster_ids es集群id
        @apiSuccess {Bool} data.is_active 是否启用
        @apiSuccess {String} data.description 描述
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [{
                "data_link_id": 1,
                "link_group_name": "默认",
                "bk_biz_id": 0,
                "kafka_cluster_id": "kafka_01",
                "transfer_cluster_id": "transfer_01",
                "es_cluster_id": ["es_01", "es_02"],
                "is_active": true,
                "description": ""
            }],
            "result": true
        }
        """
        data = self.params_valid(DataLinkListSerializer)
        return Response(DataLinkHandler().list(data))

    def retrieve(self, request, data_link_id=None, *args, **kwargs):
        """
        @api {get} /databus/link/$data_link_id/ 数据链路详情
        @apiName retrieve_data_link
        @apiGroup link
        @apiParam {Int} data_link_id 数据链路id
        @apiSuccess {Int} data.data_link_id 数据链路id
        @apiSuccess {Int} data.link_group_name 链路集群名称
        @apiSuccess {Int} data.bk_biz_id 链路允许的业务id
        @apiSuccess {Int} data.kafka_cluster_id kafka集群id
        @apiSuccess {Int} data.transfer_cluster_id transfer集群id
        @apiSuccess {list} data.es_cluster_ids es集群id
        @apiSuccess {Bool} data.is_active 是否启用
        @apiSuccess {String} data.description 描述
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "data_link_id": 1,
                "link_group_name": "默认",
                "bk_biz_id": 0,
                "kafka_cluster_id": 1,
                "transfer_cluster_id": 2,
                "es_cluster_ids": ["es_01", "es_02"],
                "is_active": true,
                "description": ""
            },
            "result": true
        }
        """
        return Response(DataLinkHandler(data_link_id=data_link_id).retrieve())

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/link/ 数据链路创建
        @apiName create_data_link
        @apiDescription 创建数据链路
        @apiGroup link
        @apiParam {Int} link_group_name 链路集群名称
        @apiParam {Int} bk_biz_id 链路允许的业务id
        @apiParam {Int} kafka_cluster_id kafka集群id
        @apiParam {String} transfer_cluster_id transfer集群id
        @apiParam {list} es_cluster_ids es集群id
        @apiParam {Bool} is_active 是否启用
        @apiParam {String} description 描述
        @apiParamExample {json} 请求样例:
        {
            "link_group_name": "默认",
            "bk_biz_id": 0,
            "kafka_cluster_id": 1,
            "transfer_cluster_id": 2,
            "es_cluster_id": ["es_01", "es_02"],
            "is_active": true,
            "description": ""
        }
        @apiSuccess {Int} data.data_link_id 数据链路id
        @apiSuccess {Int} data.link_group_name 链路集群名称
        @apiSuccess {Int} data.bk_biz_id 链路允许的业务id
        @apiSuccess {Int} data.kafka_cluster_id kafka集群id
        @apiSuccess {Int} data.transfer_cluster_id transfer集群id
        @apiSuccess {list} data.es_cluster_ids es集群id
        @apiSuccess {Bool} data.is_active 是否启用
        @apiSuccess {String} data.description 描述
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "data_link_id": 1,
                "link_group_name": "默认",
                "bk_biz_id": 0,
                "kafka_cluster_id": 1,
                "transfer_cluster_id": 2,
                "es_cluster_id": ["es_01", "es_02"],
                "is_active": true,
                "description": ""
            },
            "result": true
        }
        """
        data = self.params_valid(DataLinkCreateUpdateSerializer)
        return Response(DataLinkHandler().update_or_create(data))

    def update(self, request, *args, data_link_id=None, **kwargs):
        """
        @api {put} /databus/link/$data_link_id/ 数据链路更新
        @apiName update_data_link
        @apiGroup link
        @apiDescription 更新数据链路
        @apiParam {Int} data_link_id 数据链路id
        @apiParam {Int} link_group_name 链路集群名称
        @apiParam {Int} bk_biz_id 链路允许的业务id
        @apiParam {Int} kafka_cluster_id kafka集群id
        @apiParam {String} transfer_cluster_id transfer集群id
        @apiParam {list} es_cluster_ids es集群id
        @apiParam {Bool} is_active 是否启用
        @apiParam {String} description 描述
        @apiParamExample {json} 请求样例:
        {
            "link_group_name": "默认",
            "bk_biz_id": 0,
            "kafka_cluster_id": 1,
            "transfer_cluster_id": 2,
            "es_cluster_id": ["es_01", "es_02"],
            "is_active": true,
            "description": ""
        }
        @apiSuccess {Int} data.data_link_id 数据链路id
        @apiSuccess {Int} data.link_group_name 链路集群名称
        @apiSuccess {Int} data.bk_biz_id 链路允许的业务id
        @apiSuccess {Int} data.kafka_cluster_id kafka集群id
        @apiSuccess {Int} data.transfer_cluster_id transfer集群id
        @apiSuccess {list} data.es_cluster_ids es集群id
        @apiSuccess {Bool} data.is_active 是否启用
        @apiSuccess {String} data.description 描述
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "data_link_id": 1,
                "link_group_name": "默认",
                "bk_biz_id": 0,
                "kafka_cluster_id": 1,
                "transfer_cluster_id": 2,
                "es_cluster_id": ["es_01", "es_02"],
                "is_active": true,
                "description": ""
            },
            "result": true
        }
        """
        data = self.params_valid(DataLinkCreateUpdateSerializer)
        return Response(DataLinkHandler(data_link_id=data_link_id).update_or_create(data))

    def destroy(self, request, data_link_id=None, *args, **kwargs):
        """
        @api {delete} /databus/link/$data_link_id/ 数据链路删除
        @apiName delete_data_link
        @apiGroup link
        @apiDescription 删除数据链路
        @apiParam {Int} data_link_id 数据链路id
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "success",
            "result": true
        }
        """
        return Response(DataLinkHandler(data_link_id=data_link_id).destroy())

    @list_route(methods=["GET"], url_path="get_cluster_list")
    def get_cluster_list(self, request):
        """
        @api {get} /databus/link/get_cluster_list/?cluster_type=$cluster_type 获取集群列表（transfer、kafka、es）
        @apiName get_cluster_list
        @apiGroup link
        @apiParam {String} $cluster_type 集群种类
        @apiSuccess {Int} data.cluster_id 集群id
        @apiSuccess {String} data.cluster_name 集群名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "cluster_id": 1,
                    "cluster_name": "kafka_cluster1"
                }
            ]
            "result": true
        }
        """
        data = self.params_valid(ClusterListSerializer)
        return Response(DataLinkHandler().get_cluster_list(data["cluster_type"]))
