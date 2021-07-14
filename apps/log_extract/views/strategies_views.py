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
from apps.utils.drf import list_route
from rest_framework.response import Response

from apps.iam import ActionEnum
from apps.iam.handlers.drf import BusinessActionPermission
from apps.log_search.handlers.biz import BizHandler
from apps.log_extract import serializers
from apps.log_extract.handlers.strategies import StrategiesHandler
from apps.generic import ModelViewSet
from apps.log_extract.models import Strategies


class StrategiesViewSet(ModelViewSet):
    model = Strategies
    queryset = Strategies.objects.all()
    lookup_field = "strategy_id"
    http_method_names = ["head", "get", "post", "put", "delete"]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "list": serializers.StrategiesSerializer,
        }
        return action_serializer_map.get(self.action)

    def get_permissions(self):
        return [BusinessActionPermission([ActionEnum.MANAGE_EXTRACT_CONFIG])]

    def list(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/strategies/?bk_biz_id=${bk_biz_id} 11_strategies-策略列表
        @apiName list_strategies
        @apiGroup 18_extract
        @apiParam {Int} bk_biz_id 业务ID (用于判断该用户是否为该业务的管理人员)
        @apiSuccess {Int} strategy_id 策略ID
        @apiSuccess {Int} strategy_name 策略名称
        @apiSuccess {List} user_list 用户组ID列表
        @apiSuccess {Int} bk_biz_id 授权的业务ID
        @apiSuccess {String} select_type 目标选择类型
        @apiSuccess {List(json)} modules 授权的模板实例列表
        @apiSuccess {Int} modules.bk_inst_id 模块ID
        @apiSuccess {String} modules.bk_inst_name 模块名
        @apiSuccess {String} modules.bk_obj_id 选择目标ID
        @apiSuccess {Int} modules.bk_biz_id 模块所属业务的ID
        @apiSuccess {List} visible_dirs 授权的目录列表
        @apiSuccess {List} file_types 授权的文件类型
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_biz_id": 105,
                    "strategy_id": 1,
                    "strategy_name": "105业务",
                    "user_list": [
                        "1"
                    ],
                    "modules": [
                        {
                            "bk_inst_id": 2000000266,
                            "bk_inst_name": "集群2000000266",
                            "bk_obj_id": "set",
                            "bk_biz_id": 100605
                        }
                    ],
                    "select_type": "topo",
                    "visible_dir": [
                        "/data/log/cc/",
                        "/data/cc/"
                    ],
                    "file_type": [
                        ".log"
                    ]
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        self.params_valid(serializers.ListStrategiesSerializer)
        response = super().list(request, *args, **kwargs)

        return Response(response.data)

    def create(self, request, *args, **kwargs):
        """
        @api {post} /log_extract/strategies/ 12_strategies-创建策略
        @apiName create_strategies
        @apiGroup 18_extract
        @apiDescription 设置用户访问策略
        @apiParam {Int} strategy_name 策略名称
        @apiParam {List} user_list 用户组ID
        @apiParam {Int} bk_biz_id 授权的业务ID
        @apiParam {String} select_type 目标选择类型
        @apiParam {List(json)} modules 授权的模板实例列表
        @apiParam {Int} modules.bk_inst_id 模块ID
        @apiParam {String} modules.bk_inst_name 模块名
        @apiParam {String} modules.bk_obj_id 选择目标ID
        @apiParam {Int} modules.bk_biz_id 模块所属业务的ID
        @apiParam {List} visible_dirs 授权的目录列表
        @apiParam {List} file_type 授权的文件类型
        @apiParam {String} operator 执行人
        @apiParamExample {json} 请求示例:
        {
            "strategy_name":"cc3.0测试",
            "user_list": [
                "1",
                "2"
            ],
            "bk_biz_id": 100605,
            "select_type": "module",
            "modules": [
                {
                    "bk_inst_id": 2000000266,
                    "bk_inst_name": "可用模块1",
                    "bk_obj_id": "module",
                    "bk_biz_id": 100605
                },
                {
                    "bk_inst_id": 2000000179,
                    "bk_inst_name": "直连agent",
                    "bk_obj_id": "module",
                    "bk_biz_id": 100605
                }
            ],
            "visible_dir": [
                "/data/log/aa/",
                "/data/log/bb/",
                "/data/log/cc/"
            ],
            "file_type": [
                ".log"
            ],
            "operator": "xx"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(serializers.UpdateOrCreateStrategiesSerializer)
        return Response(StrategiesHandler().update_or_create(**data))

    def update(self, request, *args, strategy_id=None, **kwargs):
        """
        @api {put} /log_extract/strategies/${strategy_id}/ 13_strategies-更新策略
        @apiName update_strategies
        @apiGroup 18_extract
        @apiDescription 根据策略ID更新策略内容
        @apiParam {Int} strategy_id 策略ID
        @apiParam {Int} strategy_name 策略名称
        @apiParam {List} user_list 用户组ID
        @apiParam {Int} bk_biz_id 授权的业务ID
        @apiParam {String} select_type 目标选择类型
        @apiParam {List(json)} modules 授权的模块列表
        @apiParam {Int} modules.bk_inst_id 模块ID
        @apiParam {String} modules.bk_inst_name 模块名
        @apiParam {String} modules.bk_obj_id 选择目标ID
        @apiParam {Int} modules.bk_biz_id 模块所属业务的ID
        @apiParam {List} visible_dirs 授权的目录列表
        @apiParam {List} file_types 授权的文件类型
        @apiParam {String} operator 执行人
        @apiParamExample {json} 请求示例:
        {
            "strategy_name": "策略1",
            "user_list": [1,2],
            "bk_biz_id": 215,
            "select_type": "module",
            "modules": [{
                "bk_inst_id": 0,
                "bk_inst_name": "模块名",
                "bk_obj_id": "module",
                "bk_biz_id": 2152
            }],
            "visible_dir": ["a-dir","b_dir"],
            "file_type": ["a-type","b-type"],
            "operator": "xx"
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [],
            "code": 0,
            "message": ""
        }
        """

        data = self.params_valid(serializers.UpdateOrCreateStrategiesSerializer)
        return Response(StrategiesHandler(strategy_id=self.get_object().strategy_id).update_or_create(**data))

    def destroy(self, request, *args, strategy_id=None, **kwargs):
        """
        @api {delete} /log_extract/strategies/${strategy_id}/ 14_strategies-删除策略
        @apiName delete_strategies
        @apiGroup 18_extract
        @apiDescription 根据策略ID删除策略
        @apiParam {Int} strategy_id 策略ID
        @apiParam {Int} bk_biz_id 业务ID (用于判断该用户是否为该业务下的管理人员)
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {},
            "code": 0,
            "message": ""
        }
        """
        return Response(StrategiesHandler(strategy_id=self.get_object().strategy_id).delete_strategies())

    @list_route(methods=["GET"], url_path="topo")
    def topo(self, request):
        """
        @api {get} /log_extract/strategies/topo/?bk_biz_id=$bk_biz_id 15_strategies-获取TOPO
        @apiName list_extract_biz_topo
        @apiGroup 18_extract
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} instance_type 拉取的叶子节点的类型 可选参数 `host, service` (静态拓扑使用)
        @apiParam {Bool} remove_empty_nodes 是否删除空节点 可选参数（配合instance_type一起传）(静态拓扑使用)
        @apiParamExample {json} 请求参数示例:
        {
            "bk_biz_id": 2,
            "instance_type": "host",
            "remove_empty_nodes": true
        }
        @apiSuccess {List(json)} data 返回数据
        @apiSuccess {Int} data.bk_inst_id 实例id
        @apiSuccess {String} data.bk_inst_name 实例名称
        @apiSuccess {String} data.bk_obj_id 对象id
        @apiSuccess {String} data.bk_obj_name 对象名称
        @apiSuccess {Int} data.default 默认值
        @apiSuccess {String} data.child.name 前端展示字段
        @apiSuccess {List(json)} data.child 子拓扑数据 (可能有无限多层子拓扑，注意循环时需要一直循环子拓扑)
        @apiSuccess {Int} data.child.bk_inst_id 实例id（动态/静态拓扑使用）
        @apiSuccess {String} data.child.bk_inst_name 实例名称（动态/静态拓扑使用）
        @apiSuccess {String} data.child.bk_obj_id 对象id（动态/静态拓扑使用）
        @apiSuccess {String} data.child.bk_obj_name 对象名称（动态/静态拓扑使用）
        @apiSuccess {Int} data.child.default 默认值（动态/静态拓扑使用）
        @apiSuccess {String} data.child.name 前端展示字段 （动态/静态拓扑使用）
        @apiSuccess {Int} data.child.bk_biz_id 业务id (静态拓扑使用)
        @apiSuccess {Int} data.child.bk_cloud_id 云id (静态拓扑使用)
        @apiSuccess {String} data.child.id id信息 (静态拓扑使用)
        @apiSuccess {String} data.child.ip ip信息 (静态拓扑使用)
        @apiSuccess {String} data.child.os_type 操作系统类型 (静态拓扑使用)
        @apiSuccess {Int} data.child.plat_id 地区id (静态拓扑使用)
        @apiSuccess {String} data.child.name 前端展示字段 (静态拓扑使用)
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "bk_inst_id": 2,
                    "bk_inst_name": "蓝鲸",
                    "bk_obj_id": "biz",
                    "bk_obj_name": "业务",
                    "default": 0,
                    "name": "蓝鲸",
                    "child": [
                        "bk_inst_id": 3,
                        "bk_inst_name": "故障自愈",
                        "bk_obj_id": "set",
                        "bk_obj_name": "集群",
                        "name": "故障自愈",
                        "child": [
                            "bk_biz_id": 2,
                            "bk_cloud_id": 0,
                            "id": 6,
                            "ip": "127.0.0.1",
                            "bk_obj_id": "module",
                            "bk_obj_name": "模块",
                            "name": "127.0.0.1",
                            "child": []
                        ],
                        "default": 0,
                    ]
                }
            ],
            "result": true
        }
        """
        params = self.params_valid(serializers.StrategiesTopoSerializer)
        return Response(BizHandler(params["bk_biz_id"]).get_instance_topo(params, is_inner=True))
