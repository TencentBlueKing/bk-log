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
from rest_framework import serializers
from rest_framework.response import Response

from apps.api import BkLogApi
from apps.generic import APIViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import (
    BusinessActionPermission,
    InstanceActionPermission,
    ViewBusinessPermission,
    insert_permission_field,
)
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_databus.exceptions import StorageCreateException, StorageNotExistException
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.serializers import (
    StorageBathcDetectSerializer,
    StorageCreateSerializer,
    StorageDetectSerializer,
    StorageListSerializer,
    StorageRepositorySerlalizer,
    StorageUpdateSerializer,
)
from apps.utils.drf import detail_route, list_route


class StorageViewSet(APIViewSet):
    lookup_field = "cluster_id"
    serializer_class = serializers.Serializer

    def get_permissions(self):
        if self.action == "create":
            return [BusinessActionPermission([ActionEnum.CREATE_ES_SOURCE])]
        if self.action == "update":
            return [InstanceActionPermission([ActionEnum.MANAGE_ES_SOURCE], ResourceEnum.ES_SOURCE)]
        return [ViewBusinessPermission()]

    @list_route(methods=["GET"], url_path="cluster_groups")
    @insert_permission_field(
        actions=[ActionEnum.MANAGE_ES_SOURCE],
        resource_meta=ResourceEnum.ES_SOURCE,
        id_field=lambda d: d["storage_cluster_id"],
        always_allowed=lambda d: d.get("bk_biz_id") == 0,
    )
    def list_cluster_groups(self, request, *args, **kwargs):
        """
        @api {get} /databus/storage/cluster_groups/?bk_biz_id=$bk_biz_id 11_字段提取-存储集群
        @apiName list_storage_cluster_groups
        @apiGroup 09_StorageCluster
        @apiDescription 拉取存储集群列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Int} storage_cluster_id 存储集群id
        @apiSuccess {String} storage_cluster_name 存储集群名称
        @apiSuccess {String} storage_type 存储集群类型（固定elasticsearch类型）
        @apiSuccess {Object} setup_config 存储设置参数
        @apiSuccess {Int} setup_config.retention_days_max 存储设置参数 最大天数
        @apiSuccess {Int} setup_config.retention_days_default 存储设置参数 默认天数
        @apiSuccess {Int} setup_config.number_of_replicas_max 存储设置参数 最大副本数量
        @apiSuccess {Int} setup_config.number_of_replicas_default 存储设置参数 默认副本书
        @apiSuccess {Array} admin 管理员
        @apiSuccess {String} description 描述
        @apiSuccess {Boolean} is_platform 是否是平台存储集群
        @apiSuccess {Boolean} enable_archive 是否启用归档
        @apiSuccess {Boolean} enable_assessment 是否启用评估
        @apiSuccess {Boolean} enable_hot_warm 是否启用冷热集群
        @apiSuccess {Int} storage_usage 存储使用量
        @apiSuccess {Int} storage_total 存储总理 bytes
        @apiSuccess {Int} index_count 索引数量
        @apiSuccess {Int} biz_count 业务数量

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "storage_cluster_id": 17,
                    "storage_cluster_name": "bklog-test",
                    "storage_version": "6.4.3",
                    "storage_type": "elasticsearch",
                    "priority": 0,
                    "registered_system": "bklog",
                    "bk_biz_id": 2,
                    "enable_hot_warm": false,
                    "setup_config": {
                        "retention_days_max": 7,
                        "retention_days_default": 7,
                        "number_of_replicas_max": 3,
                        "number_of_replicas_default": 1
                    },
                    "admin": [
                        "xxxxx"
                    ],
                    "description": "",
                    "enable_assessment": false,
                    "enable_archive": false,
                    "is_platform": false,
                    "storage_usage": 0,
                    "storage_total": 0,
                    "index_count": 0,
                    "biz_count": 0,
                    "storage_capacity": 0,
                    "storage_used": 0,
                    "permission": {
                        "manage_es_source": true
                    }
                },
            ],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(StorageListSerializer)
        return Response(
            StorageHandler().get_cluster_groups_filter(
                bk_biz_id=data["bk_biz_id"], enable_archive=data.get("enable_archive", False)
            )
        )

    @insert_permission_field(
        id_field=lambda d: d["cluster_config"]["cluster_id"],
        actions=[ActionEnum.MANAGE_ES_SOURCE],
        resource_meta=ResourceEnum.ES_SOURCE,
        always_allowed=lambda d: d.get("bk_biz_id") == 0,
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/storage/?bk_biz_id=$bk_biz_id 01_储存集群-列表
        @apiName list_storage
        @apiGroup 09_StorageCluster
        @apiDescription 查询集群列表，此界面不需要分页，is_editable为false时不能编辑
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Object} cluster_config 集群配置
        @apiSuccess {String} cluster_config.registered_system 注册系统
        @apiSuccess {String} cluster_config.domain_name 集群域名
        @apiSuccess {String} cluster_config.cluster_name 集群名称
        @apiSuccess {int} cluster_config.cluster_id 集群ID
        @apiSuccess {Object} cluster_config.custom_option 自定义标签
        @apiSuccess {Int} cluster_config.custom_option.bk_biz_id 业务ID
        @apiSuccess {int} cluster_config.port 端口
        @apiSuccess {String} cluster_type 集群类型
        @apiSuccess {Object} auth_info 凭据信息
        @apiSuccess {String} auth_info.username 用户
        @apiSuccess {String} auth_info.password 密码
        @apiSuccess {Bool} is_editable 是否可编辑（为false时不可编辑）
        @apiSuccess {Object} cluster_stats 集群状态 连接出错该对象不存在
        @apiSuccess {String} cluster_stats.status 集群状况 green yellow red
        @apiSuccess {Int} cluster_stats.indices_count 集群索引数量
        @apiSuccess {Int} cluster_stats.indices_doc_count 集群文档数量
        @apiSuccess {Int} cluster_stats.indices_store 集群存储大小 单位Byte
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "cluster_config": {
                        "domain_name": "127.0.0.1",
                        "port": 9200,
                        "schema": "http",
                        "is_ssl_verify": false,
                        "cluster_id": 17,
                        "cluster_name": "bklog-test",
                        "version": "6.4.3",
                        "custom_option": {
                            "bk_biz_id": 2,
                            "hot_warm_config": {
                                "is_enabled": false,
                                "hot_attr_name": "",
                                "hot_attr_value": "",
                                "warm_attr_name": "",
                                "warm_attr_value": ""
                            },
                            "visible_config": {
                                "visible_type": "current_biz"
                            },
                            "admin": [
                                "admin"
                            ],
                            "setup_config": {
                                "retention_days_max": 7,
                                "retention_days_default": 7,
                                "number_of_replicas_max": 3,
                                "number_of_replicas_default": 1
                            },
                            "description": "",
                            "enable_archive": false,
                            "enable_assessment": false
                        },
                        "registered_system": "bklog",
                        "creator": "admin",
                        "create_time": "2021-03-04 10:41:32+0800",
                        "last_modify_user": "admin",
                        "last_modify_time": "2021-04-30 15:06:43+0800",
                        "is_default_cluster": false,
                        "enable_hot_warm": false
                    },
                    "cluster_type": "elasticsearch",
                    "auth_info": {
                        "password": "",
                        "username": "elastic"
                    },
                    "is_editable": true,
                    "priority": 0,
                    "bk_biz_id": 2,
                    "visible_bk_biz": [],
                    "permission": {
                        "manage_es_source": true
                    }
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(StorageListSerializer)
        return Response(
            StorageHandler().list(bk_biz_id=data["bk_biz_id"], enable_archive=data.get("enable_archive", False))
        )

    def retrieve(self, request, *args, **kwargs):
        """
        @api {get} /databus/storage/$cluster_id/?bk_biz_id=$bk_biz_id 02_存储集群-详情
        @apiName retrieve_storage
        @apiGroup 09_StorageCluster
        @apiDescription 查询集群详情
        @apiParam {Int} cluster_id 集群ID
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Object} cluster_config 集群配置
        @apiSuccess {String} cluster_config.registered_system 注册系统
        @apiSuccess {String} cluster_config.domain_name 集群域名
        @apiSuccess {String} cluster_config.cluster_name 集群名称
        @apiSuccess {int} cluster_config.cluster_id 集群ID
        @apiSuccess {Object} cluster_config.custom_option 自定义标签
        @apiSuccess {Int} cluster_config.custom_option.bk_biz_id 业务ID
        @apiSuccess {int} cluster_config.port 端口
        @apiSuccess {String} cluster_type 集群类型
        @apiSuccess {Object} auth_info 凭据信息
        @apiSuccess {String} auth_info.username 用户
        @apiSuccess {String} auth_info.password 密码
        @apiSuccess {Bool} is_editable 是否可编辑（为false时不可编辑）
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "cluster_config": {
                    "domain_name": "service.consul",
                    "port": 9052,
                    "schema": "https",
                    "is_ssl_verify": true,
                    "cluster_id": 1,
                    "custom_option": {
                        "bk_biz_id": 5
                    },
                    "cluster_name": "default_influx",
                    "version": ""
                },
                "cluster_type": "elasticsearch",
                "auth_info": {
                    "password": "xxx",
                    "username": "xxx"
                },
                "is_editable ": true
            },
            "result": true
        }
        """
        data = self.params_valid(StorageListSerializer)
        cluster_list = StorageHandler().list(cluster_id=kwargs["cluster_id"], bk_biz_id=data.get("bk_biz_id"))
        if not cluster_list:
            raise StorageNotExistException()
        return Response(cluster_list[0])

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/storage/?bk_biz_id=$bk_biz_id 05_存储集群-创建
        @apiName create_storage
        @apiGroup 09_StorageCluster
        @apiParam {String} cluster_name 集群名称
        @apiParam {String} [bkbase_cluster_en_name] 集群英文名
        @apiParam {String} domain_name 集群域名（可以填入IP）
        @apiParam {Int} port 端口
        @apiParam {String} schema 协议
        @apiParam {Object} auth_info 凭据信息
        @apiParam {String} auth_info.username 用户
        @apiParam {String} auth_info.password 密码
        @apiParam {String} source_type 来源类型
        @apiParam {Object} visible_config 可见业务配置
        @apiParam {string} visible_config.visible_type 可见业务配置类型 current_biz 当前业务，all_biz 全部业务 biz_attr 业务属性multi_biz多个业务
        @apiParam {List} [visible_config.visible_bk_biz] multi_biz类型设置该参数
        @apiParam {Object} [visible_config.bk_biz_labels] biz_attr 类型设置该参数
        @apiParam {Boolean} [create_bkbase_cluster] 同步创建数据平台集群
        @apiSuccess {Object} setup_config 存储设置参数
        @apiSuccess {Int} setup_config.retention_days_max 存储设置参数 最大天数
        @apiSuccess {Int} setup_config.retention_days_default 存储设置参数 默认天数
        @apiSuccess {Int} setup_config.number_of_replicas_max 存储设置参数 最大副本数量
        @apiSuccess {Int} setup_config.number_of_replicas_default 存储设置参数 默认副本书
        @apiSuccess {List} admin 管理员
        @apiSuccess {String} [description] 描述
        @apiSuccess {Boolean} enable_archive 是否启用归档
        @apiSuccess {Boolean} enable_assessment 是否启用评估
        @apiParamExample {Json} 请求参数
        {
            "cluster_name": "ES集群",
            "domain_name": "xxx",
            "port": 9200,
            "schema": "http",
            "auth_info": {
                "username": "",
                "password": ""
            },
            "bk_biz_id": 1,
            "enable_hot_warm": True,
            "visible_config": {
                "visible_type": "current_biz"
            }
            "source_type": "other",
            "setup_config": {
                "retention_days_max": 7,
                "retention_days_default": 7,
                "number_of_replicas_max": 3,
                "number_of_replicas_default": 1,
                "es_shards_default": 1,
                "es_shards_max": 64
            },
            "admin": ["admin"],
            "description": "xxxx",
            "enable_archive": false,
            "enable_assessment": false
        }
        @apiSuccess {Int} data 集群ID
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": 18,
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(StorageCreateSerializer)

        connect_result, version_num_str = BkLogApi.connectivity_detect(  # pylint: disable=unused-variable
            params={
                "bk_biz_id": data["bk_biz_id"],
                "domain_name": data["domain_name"],
                "port": data["port"],
                "version_info": True,
                "schema": data["schema"],
                "es_auth_info": {
                    "username": data["auth_info"]["username"],
                    "password": data["auth_info"]["password"],
                },
            },
        )
        data.update(
            {
                "cluster_type": STORAGE_CLUSTER_TYPE,
                "custom_option": {
                    "bk_biz_id": data["bk_biz_id"],
                    "hot_warm_config": {
                        "is_enabled": data["enable_hot_warm"],
                        "hot_attr_name": data["hot_attr_name"],
                        "hot_attr_value": data["hot_attr_value"],
                        "warm_attr_name": data["warm_attr_name"],
                        "warm_attr_value": data["warm_attr_value"],
                    },
                    "source_type": data["source_type"],
                    "visible_config": data["visible_config"],
                    "setup_config": data["setup_config"],
                    "admin": data["admin"],
                    "description": data.get("description", ""),
                    "enable_archive": data["enable_archive"],
                    "enable_assessment": data["enable_assessment"],
                },
                "version": version_num_str,
            }
        )
        return Response(StorageHandler().create(data))

    def update(self, request, *args, **kwargs):
        """
        @api {put} /databus/storage/$cluster_id/?bk_biz_id=$bk_biz_id 06_存储集群-更新
        @apiName update_storage
        @apiGroup 09_StorageCluster
        @apiParam {String} domain_name 集群域名
        @apiParam {Int} port 端口
        @apiParam {String} schema 协议
        @apiParam {Object} auth_info 凭据信息
        @apiParam {String} auth_info.username 用户
        @apiParam {String} auth_info.password 密码
        @apiParam {String} cluster_name 集群名称
        @apiParam {List} [visible_bk_biz] 可见业务范围
        @apiParamExample {Json} 请求参数
        {
            "domain_name": "127.0.0.11",
            "port":9200,
            "schema": "http",
            "auth_info":{
                "username": "admin",
                "password": "admin"
            },
            "setup_config": {
                "retention_days_max": 7,
                "retention_days_default": 7,
                "number_of_replicas_max": 3,
                "number_of_replicas_default": 1,
                "es_shards_default": 1,
                "es_shards_max": 64
            },
            "visible_bk_biz: [1, 2, 3]
        }
        @apiSuccess {Int} data 集群ID
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "cluster_config": {
                    "is_ssl_verify": false,
                    "registered_system": "log-search-4",
                    "domain_name": "127.0.0.11",
                    "cluster_name": "log_cluster11",
                    "version": "",
                    "cluster_id": 19,
                    "custom_option": "{\"bk_biz_id\": \"8\"}",
                    "port": 9201,
                    "schema": ""
                },
                "auth_info": {
                    "username": "admin",
                    "password": "admin"
                },
                "cluster_type": "elasticsearch"
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(StorageUpdateSerializer)
        data.update(
            {
                "custom_option": {
                    "bk_biz_id": data["bk_biz_id"],
                    "hot_warm_config": {
                        "is_enabled": data["enable_hot_warm"],
                        "hot_attr_name": data["hot_attr_name"],
                        "hot_attr_value": data["hot_attr_value"],
                        "warm_attr_name": data["warm_attr_name"],
                        "warm_attr_value": data["warm_attr_value"],
                    },
                    "source_type": data["source_type"],
                    "visible_config": data["visible_config"],
                    "setup_config": data["setup_config"],
                    "admin": data["admin"],
                    "description": data.get("description", ""),
                    "enable_archive": data["enable_archive"],
                    "enable_assessment": data["enable_assessment"],
                },
                "cluster_id": kwargs["cluster_id"],
            }
        )
        data.pop("description", None)
        return Response(StorageHandler(kwargs["cluster_id"]).update(data))

    def destroy(self, request, cluster_id):
        """
        @api {DELETE} /databus/storage/$cluster_id/?bk_biz_id=$bk_biz_id 06_存储集群-删除
        @apiName delete_storage
        @apiGroup 09_StorageCluster
        @apiParam {Int} cluster_id 集群名称
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
            },
            "code": 0,
            "message": ""
        }
        """
        return Response(StorageHandler(cluster_id).destroy())

    @list_route(methods=["POST"], url_path="connectivity_detect")
    def connectivity_detect(self, request, *args, **kwargs):
        """
        @api {post} /databus/storage/connectivity_detect/ 07_存储集群-连通性测试
        @apiName connectivity_detect
        @apiGroup 09_StorageCluster
        @apiDescription 连通性测试
        @apiParam {Int} cluster_id 集群ID
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} domain_name 集群域名
        @apiParam {Int} port 端口
        @apiParam {String} schema 协议
        @apiParam {String} username 用户
        @apiParam {String} password 密码
        @apiParamExample {Json} 请求参数
        {
            "cluster_id": 3,
            "bk_biz_id": 5,
            "domain_name": "xx",
            "port": 9200,
            "schema": "http",
            "username": "xxx",
            "password": "xxx"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": true,
            "result": true
        }
        """
        data = self.params_valid(StorageDetectSerializer)
        cluster_id = None
        if data.get("cluster_id"):
            cluster_id = data["cluster_id"]
            del data["cluster_id"]

        return Response(StorageHandler(cluster_id).connectivity_detect(**data))

    @list_route(methods=["POST"], url_path="node_attrs")
    def node_attrs(self, request, *args, **kwargs):
        """
        @api {post} /databus/storage/node_attrs/ 获取集群中各节点属性
        @apiName list_node_attrs
        @apiGroup 09_StorageCluster
        @apiDescription 获取集群中各节点属性
        @apiParam {Int} cluster_id 集群ID
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} domain_name 集群域名
        @apiParam {Int} port 端口
        @apiParam {String} username 用户
        @apiParam {String} password 密码
        @apiParamExample {Json} 请求参数
        {
            "cluster_id": 3,
            "bk_biz_id": 5,
            "domain_name": "xx",
            "port": 9200,
            "username": "xxx",
            "password": "xxx"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": true,
            "result": true
        }
        """
        data = self.params_valid(StorageDetectSerializer)
        cluster_id = None
        if data.get("cluster_id"):
            cluster_id = data["cluster_id"]
            del data["cluster_id"]

        return Response(StorageHandler(cluster_id).list_node_attrs(**data))

    @list_route(methods=["GET"], url_path="log_cluster")
    @insert_permission_field(
        id_field=lambda d: d["storage_cluster_id"],
        actions=[ActionEnum.MANAGE_ES_SOURCE],
        resource_meta=ResourceEnum.ES_SOURCE,
        always_allowed=lambda d: d.get("bk_biz_id") == 0,
    )
    def list_log_cluster(self, request, *args, **kwargs):
        """
        @api {get} /databus/storage/log_cluster/?bk_biz_id=$bk_biz_id 12_第三方ES-存储集群
        @apiName list_log_cluster
        @apiGroup 09_StorageCluster
        @apiDescription 拉取第三方ES存储集群列表
        @apiParam {Int} bk_biz_id 业务ID
        @apiSuccess {Int} storage_cluster_id 存储集群id
        @apiSuccess {String} storage_cluster_name 存储集群名称
        @apiSuccess {String} storage_type 存储集群类型（固定elasticsearch类型）
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "storage_cluster_id": 3,
                    "storage_cluster_name": "es_cluster1",
                    "storage_type": "elasticsearch"
                },
                {
                    "storage_cluster_id": 8,
                    "storage_cluster_name": "es_demo3",
                    "storage_type": "elasticsearch"
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(StorageListSerializer)
        return Response(
            StorageHandler().get_cluster_groups(
                bk_biz_id=data["bk_biz_id"], is_default=False, enable_archive=data["enable_archive"]
            )
        )

    @list_route(methods=["POST"], url_path="batch_connectivity_detect")
    def batch_connectivity_detect(self, request, *args, **kwargs):
        """
        @api {post} /databus/storage/batch_connectivity_detect/?bk_biz_id=$bk_biz_id 存储集群-批量连通性测试
        @apiName batch_connectivity_detect
        @apiGroup 09_StorageCluster
        @apiDescription 批量连通性测试
        @apiParam {Array(Dict)} cluster_list 集群ID列表
        @apiParam {Int} cluster_list.status 连接状态
        @apiParam {Int} cluster_list.status_stats 集群状态
        @apiParam {Int} cluster_list.status_stats.node_count 集群状态
        @apiParam {Int} cluster_list.status_stats.indices_count 集群索引数量
        @apiParam {Int} cluster_list.status_stats.indices_docs_count 集群索引文档数量
        @apiParam {Int} cluster_list.status_stats.status 集群状态
        @apiParam {Int} cluster_list.status_stats.shards_pri 集群主切片数量
        @apiParam {Int} cluster_list.status_stats.shared_total 集群切片数量
        @apiParam {Int} cluster_list.status_stats.total_store 全部存储
        @apiParamExample {Json} 请求参数
        {
            "cluster_list": [3,8]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "3": {
                    "status": false,
                    "status_stats: {
                        "node_count": 2,
                        "indices_count": 32,
                        "indices_docs_count": 558327,
                        "indices_store": 775942893,
                        "status": "green",
                        "shards_pri": 19,
                        "shards_total": 20,
                        "total_store": 84280958976
                    }
                },
                "8": false
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(StorageBathcDetectSerializer)
        bk_biz_id = request.GET.get("bk_biz_id")
        if not bk_biz_id or not bk_biz_id.isdigit():
            raise StorageCreateException()
        return Response(StorageHandler.batch_connectivity_detect(data["cluster_list"], bk_biz_id))

    @detail_route(methods=["GET"], url_path="cluster_nodes")
    def cluster_nodes(self, request, cluster_id, *args, **kwargs):
        """
        @api {post} /databus/storage/$cluster_id/cluster_nodes 存储集群-集群节点信息
        @apiName cluster_nodes
        @apiGroup 09_StorageCluster
        @apiDescription 集群索引信息
        @apiParam {Int} cluster_id 集群ID
        @apiSuccess {String} name 节点名称
        @apiSuccess {String} ip 节点ip
        @apiSuccess {Int} cpu_use cpu使用率
        @apiSuccess {Int} disk_use 磁盘使用率
        @apiSuccess {Int} jvm_mem_use jvm堆内存使用率
        @apiSuccess {String} tag 节点类型 cold hot
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data":
            [
            {
                "name": "tests",
                "ip": "1.1.1.1",
                "cpu_use": 12,
                "disk_use": 12,
                "jvm_mem_use": 90,
                "tag": "cold"
            },
            ]
        }
        """
        return Response(StorageHandler(cluster_id).cluster_nodes())

    @detail_route(methods=["GET"], url_path="indices")
    def indices(self, request, cluster_id, *args, **kwargs):
        """
        @api {post} /databus/storage/$cluster_id/indices 存储集群-集群索引信息
        @apiName indices
        @apiGroup 09_StorageCluster
        @apiDescription 集群索引信息
        @apiParam {Int} cluster_id 集群ID
        @apiSuccess {List[Dict]} item
        @apiSuccess {List[Dict]} item.index_pattern 索引匹配名称
        @apiSuccess {List[Dict]} item.indices 物理索引信息
        @apiSuccess {String} health 索引健康状态 red green yellow
        @apiSuccess {String} status 索引状态
        @apiSuccess {String} pri 主分片数量
        @apiSuccess {String} rep 副本数量
        @apiSuccess {String} index 索引名称
        @apiSuccess {String} docs.count 文档数量
        @apiSuccess {String} docs.deleted 删除文档数量
        @apiSuccess {String} store.size 储存大小 Byte
        @apiSuccess {String} pri.store.size 主分片储存大小 Byte
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data":[
                {
                    "index_pattern": "2_bklog_test_beat_*",
                    "indices": [
                        {
                        "health": "green",
                        "status": "open",
                        "index": ".monitoring-kibana-6-2021.02.27",
                        "uuid": "NKNoWLsrSQ-a_VjJ9XzB3w",
                        "pri": "1",
                        "rep": "1",
                        "docs.count": "17279",
                        "docs.deleted": "0",
                        "store.size": "8",
                        "pri.store.size": "4"
                    }
                    ]
                }
                "other": {
                    "index_pattern": "other",
                    "indices": [
                        {
                        "health": "green",
                        "status": "open",
                        "index": ".monitoring-kibana-6-2021.02.27",
                        "uuid": "NKNoWLsrSQ-a_VjJ9XzB3w",
                        "pri": "1",
                        "rep": "1",
                        "docs.count": "17279",
                        "docs.deleted": "0",
                        "store.size": "8",
                        "pri.store.size": "4"
                    }
                    ]
                }
            ]
        }
        """
        return Response(StorageHandler(cluster_id).indices())

    @insert_permission_field(
        id_field=lambda d: d["cluster_id"], actions=[ActionEnum.MANAGE_ES_SOURCE], resource_meta=ResourceEnum.ES_SOURCE
    )
    @list_route(methods=["GET"], url_path="list_repository")
    def list_repository(self, request):
        """
        @api {GET} /databus/storage/list_repository/ 存储集群-集群快照仓库列表
        @apiName repository
        @apiGroup 09_StorageCluster
        @apiDescription 集群快照仓库列表
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccess {String} repository_name 仓库名称
        @apiSuccess {String} alias 仓库别名
        @apiSuccess {Int} cluster_id 集群id
        @apiSuccess {String} cluster_name 集群名称
        @apiSuccess {String} creator 创建人
        @apiSuccess {String} create_time 创建时间
        @apiSuccess {String} last_modify_user 上次修改人
        @apiSuccess {String} last_modify_time 上次修改时间
        @apiSuccess {String} type 仓库类型 cos hdfs file
        @apiSuccess {Dict} settings 仓库详细配置
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data":[
                    {
                        "repository_name": "test",
                        "cluster_id": 3,
                        "cluster_name": "test",
                        "alias": "test",
                        "creator": "xxx",
                        "create_time": "2021-04-30 09:49:27",
                        "last_modify_user": "xxxx",
                        "last_modify_time": "2021-04-30 09:49:27",
                        "type": "cos",
                }
            ]
        }
        """
        data = self.params_valid(StorageRepositorySerlalizer)
        return Response(StorageHandler().repository(bk_biz_id=data.get("bk_biz_id")))

    @insert_permission_field(
        id_field=lambda d: d["cluster_id"], actions=[ActionEnum.MANAGE_ES_SOURCE], resource_meta=ResourceEnum.ES_SOURCE
    )
    @detail_route(methods=["GET"], url_path="repository")
    def repository(self, request, cluster_id):
        """
        @api {GET} /databus/storage/$cluster_id/repository/ 存储集群-对应集群快照仓库列表
        @apiName detail_repository
        @apiGroup 09_StorageCluster
        @apiDescription 集群快照仓库列表
        @apiParam {Int} bk_biz_id 业务id
        @apiSuccess {String} repository_name 仓库名称
        @apiSuccess {String} alias 仓库别名
        @apiSuccess {Int} cluster_id 集群id
        @apiSuccess {String} cluster_name 集群名称
        @apiSuccess {String} creator 创建人
        @apiSuccess {String} create_time 创建时间
        @apiSuccess {String} last_modify_user 上次修改人
        @apiSuccess {String} last_modify_time 上次修改时间
        @apiSuccess {String} type 仓库类型 cos hdfs file
        @apiSuccess {Dict} settings 仓库详细配置
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data":[
                    {
                        "repository_name": "test",
                        "cluster_id": 3,
                        "alias": "test",
                        "creator": "xxx",
                        "create_time": "2021-04-30 09:49:27",
                        "last_modify_user": "xxx",
                        "last_modify_time": "2021-04-30 09:49:27",
                        "type": "cos",
                }
            ]
        }
        """
        data = self.params_valid(StorageRepositorySerlalizer)
        return Response(StorageHandler().repository(cluster_id=cluster_id, bk_biz_id=data["bk_biz_id"]))
