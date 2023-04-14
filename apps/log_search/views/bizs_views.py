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
from apps.utils.drf import detail_route, list_route
from apps.generic import APIViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import InstanceActionPermission
from apps.log_search.handlers.biz import BizHandler
from apps.log_search.handlers.meta import MetaHandler
from apps.log_search.serializers import (
    TopoSerializer,
    HostInstanceByIpListSerializer,
    NodeListSerializer,
    TemplateSerializer,
    TemplateTopoSerializer,
    DynamicGroupSerializer,
    GetDisplayNameSerializer,
)
from apps.utils.local import get_request_username


class BizsViewSet(APIViewSet):
    """
    业务
    """

    lookup_field = "bk_biz_id"

    def get_permissions(self):
        if self.action not in ["list", "list_clouds", "get_property"]:
            return [InstanceActionPermission([ActionEnum.VIEW_BUSINESS], ResourceEnum.BUSINESS)]
        return []

    def list(self, request):
        """
        @api {get} /bizs/  01_获取业务列表
        @apiName list_meta_biz
        @apiGroup 02_Biz
        @apiSuccess {Int} bk_biz_id 业务ID
        @apiSuccess {Int} bk_biz_name 业务名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "bk_biz_id": 1,
                    "bk_biz_name": "业务名称"
                }
            ],
            "result": true
        }
        """
        return Response(
            [
                {"bk_biz_id": business["bk_biz_id"], "bk_biz_name": business["project_name"]}
                for business in MetaHandler.get_user_projects(get_request_username())
            ]
        )

    @list_route(methods=["GET"], url_path="clouds")
    def list_clouds(self, request):
        """
        @api {get} /bizs/  05_获取云区域列表
        @apiName list_meta_biz
        @apiGroup 02_Biz
        @apiSuccess {Int} bk_cloud_id 云区域ID
        @apiSuccess {Int} bk_cloud_name 云区域名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "count": 1,
                "info": [
                    {
                        "bk_cloud_name": "default area",
                        "bk_cloud_id": 0
                    }
                ]
            ],
            "result": true
        }
        """
        return Response(BizHandler.list_clouds())

    @detail_route(methods=["GET"], url_path="topo")
    def topo(self, request, bk_biz_id=None):
        """
        @api {get} /bizs/$bk_biz_id/topo/ 02_获取业务TOPO
        @apiName list_biz_topo
        @apiGroup 02_Biz
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
        params = self.params_valid(TopoSerializer)
        return Response(BizHandler(bk_biz_id).get_instance_topo(params))

    @detail_route(methods=["POST"], url_path="node_service_instances")
    def node_service_instances(self, request, bk_biz_id):
        """
        @api {post} /bizs/$bk_biz_id/node_service_instances/  获取节点服务实例
        @apiName list_node_service_instances
        @apiGroup 02_Biz
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {List(json)} node_list 节点列表
        @apiParam {Int} node_list.bk_inst_id 实例id
        @apiParam {String} node_list.bk_inst_name 实例名称
        @apiParam {String} node_list.bk_obj_id 对象id
        @apiParam {String} node_list.bk_obj_name 对象名称
        @apiParam {Int} node_list.bk_biz_id 业务id
        @apiParamExample {json} 请求样例:
        {
            "node_list": [{
                "bk_inst_id": 2,
                "bk_inst_name": "蓝鲸",
                "bk_obj_id": "biz",
                "bk_obj_name": "业务",
                "bk_biz_id": 2
            }]
        }
        @apiSuccess {List(json)} data 返回数据
        @apiSuccess {String} data.bk_obj_id 对象类型
        @apiSuccess {Int} data.bk_inst_id 实例id
        @apiSuccess {String} data.bk_inst_name 实例名称
        @apiSuccess {Int} data.count 实例总数
        @apiSuccess {Int} data.instance_error_count 错误实例数目
        @apiSuccess {List(json)} data.labels 实例分类
        @apiSuccess {String} data.labels.first 第一种实例分类
        @apiSuccess {String} data.labels.second 第二种实例分类
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_obj_id": "biz",
                    "bk_inst_id": 2,
                    "bk_inst_name": "蓝鲸",
                    "count": 66,
                    "instance_error_count": 0,
                    "labels": [
                        {
                            "first": "Default",
                            "second": "Default"
                        },
                        {
                            "first": "PaaS",
                            "second": "esb"
                        }
                    ]
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        params = self.params_valid(NodeListSerializer)
        node_list = params["node_list"]
        return Response(BizHandler(bk_biz_id).get_service_instance(node_list=node_list))

    @detail_route(methods=["POST"], url_path="host_instance_by_ip")
    def host_instance_by_ip(self, request, bk_biz_id):
        """
        @api {post} /bizs/$bk_biz_id/host_instance_by_ip/  03_根据ip列表获取主机实例（静态拓扑）
        @apiName list_host_instances_by_ip
        @apiGroup 02_Biz
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {List(json)} ip_list ip列表
        @apiParam {String} ip_list.ip ip信息
        @apiParam {Int} ip_list.bk_cloud_id 云id (可选参数)
        @apiParamExample {json} 请求样例:
        {
            "ip_list": [{
                "ip": "127.0.0.1",
                "bk_cloud_id": 0
            }, {
                "ip": "127.0.0.1",
                "bk_cloud_id": 0
            }]
        }
        @apiSuccess {List(json)} data 返回数据
        @apiSuccess {String} data.ip ip
        @apiSuccess {Int} data.bk_cloud_id 云id
        @apiSuccess {String} data.bk_cloud_name 云名称
        @apiSuccess {String} data.agent_status agent状态 1：正常 2 异常 其它：不存在
        @apiSuccess {String} data.agent_status_name agent状态 正常, 异常, 不存在
        @apiSuccess {String} data.bk_os_type 蓝鲸操作系统类型
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [{
                "ip": "127.0.0.1",
                "bk_cloud_id": 0,
                "bk_cloud_name":"",
                "agent_status": "normal",
                "bk_os_type": "linux"
            }],
            "code": 0,
            "message": ""
        }
        """
        params = self.params_valid(HostInstanceByIpListSerializer)
        ip_list = params["ip_list"]
        return Response(BizHandler(int(bk_biz_id)).get_host_instance_by_ip_list(ip_list))

    @detail_route(methods=["POST"], url_path="host_instance_by_node")
    def host_instance_by_node(self, request, bk_biz_id):
        """
        @api {post} /bizs/$bk_biz_id/host_instance_by_node/ 04_根据节点获取拓扑情况（动态拓扑）
        @apiName list_host_instance_by_node
        @apiGroup 02_Biz
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {List(json)} node_list 节点列表
        @apiParam {Int} node_list.bk_inst_id 实例id
        @apiParam {String} node_list.bk_inst_name 实例名称
        @apiParam {String} node_list.bk_obj_id 对象id
        @apiParam {Int} node_list.bk_biz_id 业务id
        @apiParamExample {json} 请求样例:
        {
            "node_list": [{
                "bk_inst_id": 2,
                "bk_inst_name": "蓝鲸",
                "bk_obj_id": "biz",
                "bk_biz_id": 2
            }]
        }
        @apiSuccess {List(json)} data 返回数据
        @apiSuccess {String} data.bk_obj_id 对象类型
        @apiSuccess {Int} data.bk_inst_id 实例id
        @apiSuccess {String} data.bk_inst_name 实例名称
        @apiSuccess {Int} data.count 实例总数
        @apiSuccess {Int} data.agent_error_count agent错误实例数目
        @apiSuccess {Int} data.node_path 节点名称
        @apiSuccess {List(json)} data.labels 实例分类
        @apiSuccess {String} data.labels.first 第一种实例分类
        @apiSuccess {String} data.labels.second 第二种实例分类
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_obj_id": "biz",
                    "bk_inst_id": 2,
                    "bk_inst_name": "蓝鲸",
                    "count": 66,
                    "agent_error_count": 0,
                    "node_path": "蓝鲸",
                    "labels": [
                        {
                            "first": "Default",
                            "second": "Default"
                        },
                        {
                            "first": "PaaS",
                            "second": "esb"
                        }
                    ]
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        params = self.params_valid(NodeListSerializer)
        node_list = params["node_list"]
        return Response(BizHandler(int(bk_biz_id)).get_host_instance_by_node(node_list=node_list))

    @detail_route()
    def template_topo(self, request, bk_biz_id):
        """
        @api {get} /bizs/$bk_biz_id/template_topo/ 06_获取服务模板topo
        @apiName template_service
        @apiGroup 02_Biz
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "bk_biz_id": 215,
                "bk_biz_name": "功夫西游",
                "children": [
                    {
                        "bk_biz_id": 215,
                        "bk_obj_id": "SERVICE_TEMPLATE",
                        "bk_inst_id": 41677,
                        "bk_inst_name": "test2"
                    },
                    {
                        "bk_biz_id": 215,
                        "bk_obj_id": "SERVICE_TEMPLATE",
                        "bk_inst_id": 41585,
                        "bk_inst_name": "分发"
                    },
                    ]
            },
            "code": 0,
            "message": ""
        }
        """
        params = self.params_valid(TemplateTopoSerializer)
        return Response(BizHandler(int(bk_biz_id)).get_biz_template_topo(params["template_type"]))

    @detail_route()
    def get_nodes_by_template(self, request, bk_biz_id):
        """
        @api {get} /bizs/$bk_biz_id/get_nodes_by_template/ 07_获取模版topo情况
        @apiName get_nodes_by_template
        @apiParam {List} bk_inst_ids 服务模版id列表 用逗号分割 1,2,3,4,4,5
        @apiParam {String} template_type 模版类型 服务模版SERVICE_TEMPLATE 集群模版SET_TEMPLATE
        @apiGroup 02_Biz
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_obj_id": "module",
                    "bk_inst_id": 451496,
                    "bk_inst_name": "中文名称-分发",
                    "count": 0,
                    "node_path": "功夫西游/中文名称/中文名称-分发",
                    "agent_error_count": 0,
                    "labels": []
                },
                {
                    "bk_obj_id": "module",
                    "bk_inst_id": 451497,
                    "bk_inst_name": "测试123-分发",
                    "count": 0,
                    "node_path": "功夫西游/测试123/测试123-分发",
                    "agent_error_count": 0,
                    "labels": []
                }
                ],
            "code": 0,
            "message": ""
        }
        """
        params = self.params_valid(TemplateSerializer)
        return Response(
            BizHandler(int(bk_biz_id)).get_nodes_by_template(params["bk_inst_ids"].split(","), params["template_type"])
        )

    @detail_route(methods=["POST"], url_path="list_agent_status")
    def list_agent_status(self, request, bk_biz_id):
        """
        @api {post} /bizs/$$bk_biz_id/list_agent_status/ 08_获取节点对应agent数量及异常状态agent数量
        @apiName list_agent_status
        @apiGroup 02_Biz
        @apiParam  {List} node_list 实例列表
        @apiParam  {String} node_list.bk_obj_id 实例类型
        @apiParam  {Int} node_list.bk_inst_id 实例ID
        @apiParam  {String} node_list.bk_inst_name 实例名称
        @apiParam  {String} node_list.bk_biz_id 业务id
        @apiParamExample {json} 成功请求:
        {
            "node_list":[
                {
                    "bk_obj_id":"set",
                    "bk_inst_id":1,
                    "bk_inst_name":"test"
                    "bk_biz_id": 1
                }
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_obj_id": "set",
                    "bk_inst_id": 1,
                    "bk_inst_name": "test",
                    "count": 10,
                    "node_path": "test1/test2",
                    "agent_error_count": 1
                    "labels": []
                }
            ],
            "code": 0,
            "message": ""
        }
        """

        params = self.params_valid(NodeListSerializer)
        return Response(BizHandler(int(bk_biz_id)).list_agent_status(params["node_list"]))

    @detail_route()
    def list_dynamic_group(self, request, bk_biz_id):
        """
        @api {get} /bizs/$$bk_biz_id/list_dynamic_group/ 09_获取动态分组列表
        @apiName list_dynamic_group
        @apiGroup 02_Biz
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "count": 1,
                "list": [
                    {
                        "bk_biz_id": 2,
                        "name": "test1",
                        "last_time": "2020-11-24T13:02:22.564Z",
                        "bk_obj_id": "host",
                        "create_user": "admin",
                        "create_time": "2020-11-24T13:02:22.564Z",
                        "modify_user": "admin",
                        "id": "iamidbuug8nh0eohk9gduh29g"
                    }
                ]
            },
            "code": 0,
            "message": ""
        }
        """
        return Response(BizHandler(int(bk_biz_id)).list_dynamic_group())

    @detail_route(methods=["POST"])
    def get_dynamic_group(self, request, bk_biz_id):
        """
        @api {get} /bizs/$$bk_biz_id/get_dynamic_group/ 10_获取数据根据指定动态分组ID
        @apiName get_dynamic_group
        @apiGroup 02_Biz
        @apiParamExample {json} 成功请求:
        {
            "dynamic_group_id_list": ["iamidbuug8nh0eohk9gduh29g", "iamidbuug8nh0eohk9gduh2912"]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_host_name": "localhost",
                    "bk_host_id": 1,
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "127.0.0.1"
                }
            ],
            "code": 0,
            "message": ""
        }``
        """
        params = self.params_valid(DynamicGroupSerializer)
        return Response(BizHandler(int(bk_biz_id)).get_dynamic_group(params["dynamic_group_id_list"]))

    @list_route(methods=["GET"], url_path="get_property")
    def get_property(self, request):
        """
        @api {get} /bizs/get_property/ 10_获取业务属性列表
        @apiName get_property
        @apiGroup 02_Biz
        @apiParamExample {json} 成功请求:
        [{
            "biz_property_id": "bk_biz_developer",
            "biz_property_name": "开发人员",
            "biz_property_values": [
                "name_1"
            ]
        }]
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [{
                "biz_property_id": "bk_biz_developer",
                "biz_property_name": "开发人员",
                "biz_property_values": [
                    "name_1"
                ]
            }],
            "code": 0,
            "message": ""
        }``
        """

        return Response(BizHandler(bk_biz_id=None).list_biz_property())

    @detail_route(methods=["POST"], url_path="get_display_name")
    def get_display_name(self, request, bk_biz_id):
        """
        @api {post} /bizs/$$bk_biz_id/get_display_name/ 11_获取主机展示名称
        @apiName get_display_name
        @apiGroup 02_Biz
        @apiParamExample {json} 成功请求:
        {
            "host_list": [
                {
                    "bk_host_id": 1,
                },
                {
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "127.0.0.1"
                }
            ]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "bk_host_id": 1,
                    "display_name": "127.0.0.1"
                },
                {
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "127.0.0.1",
                    "display_name": "127.0.0.1"
                }
            ],
            "code": 0,
            "message": ""
        }``
        """
        params = self.params_valid(GetDisplayNameSerializer)
        return Response(BizHandler(int(bk_biz_id)).get_display_name(params["host_list"]))
