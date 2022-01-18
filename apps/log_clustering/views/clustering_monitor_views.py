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

from apps.generic import APIViewSet
from apps.log_clustering.handlers.clustering_monitor import ClusteringMonitorHandler
from apps.log_clustering.serializers import UpdateStrategiesSerializer
from apps.utils.drf import detail_route


class ClusteringMonitorViewSet(APIViewSet):
    lookup_field = "index_set_id"

    @detail_route(methods=["POST"], url_path="update_strategies")
    def update_strategies(self, request, *args, index_set_id=None, **kwargs):
        """
        @api {post} /clustering_monitor/$index_set_id/update_strategies 6_聚类告警策略-更改
        @apiName update_strategies
        @apiGroup log_clustering
        @apiParam {str} pattern_level 聚类级别
        @apiParam {int} bk_biz_id 业务id
        @apiParam {List} actions 操作列表
        @apiParam {str} actions.signature 数据指纹
        @apiParam {str} actions.pattern pattern
        @apiParam {Int} [actions.strategy_id] 策略id 当更新与删除的时候必传
        @apiParam {Str} actions.action  update or create or delete 标识创建或更新
        @apiParam {Str} [actions.operator] 表达式
        @apiParam {Int} [actions.value] 阈值(暂留)
        @apiSuccessExample {json} 全部成功
        {
            "message":"",
            "code":0,
            "data":{
                "result":true,
                "operators":[
                    {
                        "signature:":"xxx",
                        "strategy_id":1,
                        "operator_result":true,
                        "operator_msg":""
                    }
                ]
            },
            "result":true
        }
        @apiSuccessExample {json} 部分成功
        {
            "message":"",
            "code":0,
            "data":{
                "result":false,
                "operators":[
                    {
                        "signature:":"xxx",
                        "strategy_id":1,
                        "operator_result":true,
                        "operator_msg":""
                    },
                    {
                        "signature:":"xxx",
                        "strategy_id":2,
                        "operator_result":false,
                        "operator_msg":"xxx"
                    }
                ]
            },
            "result":true
        }
        """
        params = self.params_valid(UpdateStrategiesSerializer)
        return Response(
            ClusteringMonitorHandler(index_set_id=index_set_id, bk_biz_id=params["bk_biz_id"]).update_strategies(
                pattern_level=params["pattern_level"], actions=params["actions"]
            )
        )

    @detail_route(methods=["get"], url_path="get_new_cls_strategy")
    def get_new_cls_strategy(self, request, *args, index_set_id=None, **kwargs):
        """
        @api {get} /clustering_monitor/$index_set_id/get_new_cls_strategy 7_聚类告警策略-查询新类告警
        @apiName get_new_cls_strategy
        @apiGroup log_clustering
        @apiSuccessExample {json} 开启新类告警
        {
            "message":"",
            "code":0,
            "data":{
                "is_active": true，
                "strategy_id": 1
            },
            "result":true
        }
        @apiSuccessExample {json} 未开启聚类
        {
            "message":"",
            "code":0,
            "data":{
                "is_active": false，
                "strategy_id": null
            },
            "result":true
        }
        """
        pass

    @detail_route(methods=["post"], url_path="update_new_cls_strategy")
    def update_new_cls_strategy(self, request, *args, index_set_id=None, **kwargs):
        """
        @api {get} /clustering_monitor/$index_set_id/update_new_cls_strategy 8_聚类告警策略-更新新类告警
        @apiName update_new_cls_strategy
        @apiGroup log_clustering
        @apiParam {int} bk_biz_id 业务id
        @apiParam {Int} [strategy_id] 策略id 当更新与删除的时候必传
        @apiParam {Str} action  update or create or delete 标识创建或更新
        @apiParam {Str} [operator] 表达式(暂留)
        @apiParam {Int} [value] 阈值(暂留)
        @apiSuccessExample {json} 成功
        {
            "message":"",
            "code":0,
            "data":{
                "strategy_id": 1
            },
            "result":true
        }
        """
        pass
