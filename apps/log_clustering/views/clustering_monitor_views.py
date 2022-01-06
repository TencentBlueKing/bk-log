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
from apps.generic import APIViewSet
from apps.utils.drf import detail_route


class ClusteringMonitorViewSet(APIViewSet):
    lookup_field = "index_set_id"

    @detail_route(methods=["POST"], url_path="update_labels")
    def update_labels(self, request, *args, index_set_id=None, **kwargs):
        """
        @api {post} /clustering_monitor/$index_set_id/update_labels 5_聚类告警标签-更改
        @apiName update_labels
        @apiGroup log_clustering
        """
        pass

    @detail_route(methods=["POST"], url_path="update_strategies")
    def update_strategies(self, request, *args, index_set_id=None, **kwargs):
        """
        @api {post} /clustering_monitor/$index_set_id/update_strategies 6_聚类告警策略-更改
        @apiName update_strategies
        @apiGroup log_clustering
        @apiParam {List} actions 操作列表
        @apiParam {str} pattern_level 聚类级别
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
            "data":[
                {
                    "signature:":"xxx",
                    "strategy_id":1,
                    "operator_result":true,
                    "operator_msg": ""
                }
            ],
            "result":true
        }
        @apiSuccessExample {json} 部分成功
        {
            "message":"",
            "code":0,
            "data":[
                {
                    "signature:":"xxx",
                    "strategy_id":1,
                    "operator_result":true,
                    "operator_msg": ""
                },
                {
                    "signature:":"xxx",
                    "strategy_id":2,
                    "operator_result":false,
                    "operator_msg": "xxx"
                }
            ],
            "result":false
        }
        """
        pass
