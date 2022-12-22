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
from apps.utils.drf import list_route
from apps.generic import APIViewSet
from apps.log_extract.handlers.explorer import ExplorerHandler
from apps.log_extract import serializers
from bkm_ipchooser.serializers import topo_sers


class ExplorerViewSet(APIViewSet):
    @list_route(methods=["POST"])
    def list_file(self, request, *args, **kwargs):
        """
        @api {POST} /log_extract/explorer/list_file 01_explorer-文件列表
        @apiName list_user_visible_dir
        @apiGroup 18_extract
        @apiDescription 预览该用户在业务机器中可访问的文件
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {List} ip_list 业务机器
        @apiParam {String} ip_list.ip 业务机器ip
        @apiParam {Int} ip_list.bk_cloud_id 业务机器云区域id
        @apiParam {String} path 文件路径
        @apiParam {Boolean} [is_search_child] 是否搜索子目录
        @apiParam {String} time_range 时间跨度 ["1d", "1w", "1m", "all", "custom"]
        @apiParam {String} start_time 启始时间 2020-09-01 00:00
        @apiParam {String} end_time 结束时间 2020-09-01 00:00
        @apiSuccess {Int} total 记录条数
        @apiSuccess {list(json)} list 返回结果
        @apiSuccess {String} list.ip 业务机器IP
        @apiSuccess {String} list.path 文件路径
        @apiSuccess {String} list.mtime 文件最后修改时间
        @apiSuccess {String} list.size 文件大小(GB/MB/KB/B)
        @apiParamExample {json} 请求示例:
        {
            "bk_biz_id": 251,
            "ip_list": [{"ip": "xx.x.x.x", "bk_cloud_id": 1}],
            "path": "xx/xx/",
            "is_search_child": true,
            "time_range": "1d" (指的是一个自然天)
        }
        {
            "bk_biz_id": 251,
            "ip_list": [{"ip": "xx.x.x.x", "bk_cloud_id": 1}],
            "path": "xx/xx/",
            "is_search_child": true,
            "time_range": "custom",
            "start_time": "2020-09-01 00:00",
            "end_time": "2020-09-01 00:00"

        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data":{
                "total": 3,
                "list": [{
                    "ip": "x.x.x.x",
                    "path": "xx/xx/xx1",
                    "mtime": "2020-02-20 20:02:02",
                    "size": "1.2MB",
                    "type": "file"
                },
                {
                    "ip": "x.x.x.x",
                    "path": "xx/xx/xx2/",
                    "mtime": "--",
                    "size": "0",
                    "type": "dir"
                },
                {
                    "ip": "x.x.x.x",
                    "path": "xx/xx/xx2/xxx2",
                    "mtime": "2020-02-20 02:04:22",
                    "size": "1KB",
                    "type": "file"
                }]
            },
            "code": 0,
            "message": ""
        }
        """

        data = self.params_valid(serializers.ExplorerListSerializer)
        return Response(
            ExplorerHandler().list_files(
                bk_biz_id=data["bk_biz_id"],
                ip=data["ip_list"],
                request_dir=data["path"],
                is_search_child=data["is_search_child"],
                time_range=data["time_range"],
                start_time=data.get("start_time", ""),
                end_time=data.get("end_time", ""),
            )
        )

    @list_route(methods=["POST"], url_path="strategies")
    def list_strategies(self, request, *args, **kwargs):
        """
        @api {post} /log_extract/explorer/strategies/ 02_explorer-文件浏览策略
        @apiName list_accessible_strategies
        @apiGroup 18_extract
        @apiDescription 返回某用户在某业务下多个IP中可访问目录的交集
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {List[Dict]} ip_list 业务机器IP列表
        @apiSuccess {String} visible_dir 用户可访问的目录(用户在选定IP列表下可访问目录的交集)
        @apiParamExample  {json} 请求示例:
        {
            "bk_biz_id" 215,
            "ip_list": [{"ip": "x.x.x.x", "bk_cloud_id": 1}, {"ip": "xx.x.x.x", "bk_cloud_id": 1}]
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [{
                "visible_dir": "/data/user01/log1",
                "file_type": ['.txt','.log']
            },
            {
                "visible_dir": "/data/user01/log2",
                "file_type": ['.txt']
            }],
            "code": 0,
            "message": ""
        }
        """

        data = self.params_valid(serializers.ExplorerStrategiesSerializer)
        strategies = ExplorerHandler().get_strategies(bk_biz_id=data["bk_biz_id"], ip_list=data["ip_list"])
        return Response(strategies["allowed_dir_file_list"])

    @list_route(methods=["get"], url_path="topo")
    def list_accessible_topo(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/explorer/topo/?bk_biz_id=${bk_biz_id} 03_explorer-topo列表(过滤后)
        @apiName list_biz_topo
        @apiGroup 18_extract
        @apiParam {Int} bk_biz_id 业务ID
        @apiParamExample {json} 请求参数示例:
        {
            "bk_biz_id": 2
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
            "result": true,
            "data": [{
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "业务",
                "bk_obj_id": "biz",
                "child": [
                    [{
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "集群",
                        "bk_obj_id": "set",
                        "child": [{
                            "host_count": 0,
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "child": [
                                {
                                    "ip": "xx.xx.xx.xx",
                                    "plat_id": 0,
                                    "bk_cloud_id": 0,
                                    "os_type": "1",
                                    "children": [],
                                    "bk_biz_id": 100605,
                                    "id": "197",
                                    "name": "xx.xx.xx.xx"
                                }
                            ],
                            "bk_biz_id": 100605,
                            "id": "110",
                            "name": "gamesvr"
                        }],
                        "bk_inst_id": 2000000341,
                        "bk_inst_name": "lampard1",
                        "bk_biz_id": 100605,
                        "id": "21",
                        "name": "lampard1"
                    }]
                ],
                "bk_inst_id": 100605,
                "bk_inst_name": "cc3.0测试",
                "bk_biz_id": 100605,
                "id": "1",
                "name": "cc3.0测试"
            }],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(serializers.ExplorerListTopo)
        return Response(ExplorerHandler().list_accessible_topo(bk_biz_id=data["bk_biz_id"]))

    @list_route(methods=["POST"])
    def trees(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/explorer/tree/ 04_explorer-拓扑树列表(过滤后) 基于通用实现扩展
        @apiName trees
        @apiGroup 18_extract
        """
        data = self.params_valid(topo_sers.TreesRequestSer)
        return Response(ExplorerHandler().ipchooser_trees(scope_list=data["scope_list"]))

    @list_route(methods=["POST"])
    def query_hosts(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/explorer/query_hosts/ 04_explorer-查询主机列表(过滤后) 基于通用实现扩展
        @apiName query_hosts
        @apiGroup 18_extract
        """
        data = self.params_valid(topo_sers.QueryHostsRequestSer)
        return Response(ExplorerHandler().ipchooser_query_hosts(data=data))

    @list_route(methods=["POST"])
    def query_host_id_infos(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/explorer/query_host_id_infos/ 04_explorer-查询主机列表详请(过滤后) 基于通用实现扩展
        @apiName query_host_id_infos
        @apiGroup 18_extract
        """
        data = self.params_valid(topo_sers.QueryHostIdInfosRequestSer)
        return Response(ExplorerHandler().ipchooser_query_host_id_infos(data=data))
