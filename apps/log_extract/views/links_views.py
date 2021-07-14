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

from apps.generic import ModelViewSet
from apps.log_extract import models
from apps.log_extract import permission
from apps.log_extract import serializers
from apps.log_extract.handlers import link


class LinksViewSet(ModelViewSet):
    """
    日志提取配置链路
    """

    lookup_field = "link_id"
    model = models.ExtractLink
    permission_classes = [
        permission.SuperuserWritePermission,
    ]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "list": serializers.ExtractLinksSerializer,
        }
        return action_serializer_map.get(self.action)

    def list(self, request, *args, **kwargs):
        """
        @api {get} /log_extract/links/ 01_获取日志提取链路列表
        @apiName get_log_extract_link_list
        @apiGroup 61_links
        @apiSuccess {List} data 日志提取数据链路列表
        @apiSuccess {Int} data.data_link_id 日志提取数据链路id
        @apiSuccess {String} data.name 日志提取数据名称
        @apiSuccess {String} data.link_type 日志提取链路类型
        @apiSuccess {String} data.link_type_name 日志提取链路类型
        @apiSuccess {String} data.created_by 日志提取链路创建者
        @apiSuccess {String} data.created_at 日志提取链路创建时间
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "name": "默认链路",
                    "link_id": 1,
                    "link_type": "common",
                    "link_type_name": "内网链路",
                    "created_by": "admin",
                    "created_at": "2021-01-28 20:39:13"
                }
            ],
            "code": 0,
            "message": ""
        }
        """
        response = super().list(request, *args, **kwargs)
        return Response(response.data)

    def retrieve(self, request, link_id=None, *args, **kwargs):
        """
        @api {get} /log_extract/links/$link_id/ 02_获取日志提取链路详情
        @apiName get_log_extract_link
        @apiGroup 61_links
        @apiSuccess {Dict} data 日志提取链路详情
        @apiSuccess {String} data.data_link_id 日志提取数据链路id
        @apiSuccess {String} data.name 日志提取数据名称
        @apiSuccess {String} data.link_type 日志提取链路类型
        @apiSuccess {String} data.link_type_name 日志提取链路类型
        @apiSuccess {String} data.operator 日志提取链路执行人
        @apiSuccess {Int} data.op_bk_biz_id 日志提取执行bk_biz_id
        @apiSuccess {Int} data.qcloud_secret_id 日志提取腾讯云SecretId
        @apiSuccess {String} data.qcloud_secret_key 日志提取腾讯云SecretKey
        @apiSuccess {String} data.qcloud_cos_bucket 日志提取腾讯云Cos桶名称
        @apiSuccess {String} data.qcloud_cos_region 日志提取腾讯云Cos区域
        @apiSuccess {String} data.is_enable 日志提取链路是否启用
        @apiSuccess {List} data.hosts 日志提取链路关联中转机配置
        @apiSuccess {String} hosts.target_dir 中转机目录
        @apiSuccess {Int} hosts.bk_cloud_id 中转机云区域id
        @apiSuccess {String} hosts.ip 中转机IP
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "link_id": 1,
                "name": "111",
                "link_type": "common",
                "link_tyoe_name": "",
                "operator": "admin",
                "op_bk_biz_id": 1,
                "qcloud_secret_id": "1",
                "qcloud_secret_key": "xxx",
                "qcloud_cos_bucket": "test_bucket",
                "qcloud_cos_region": "test_region",
                "is_enable": true,
                "hosts": [
                    {
                        "target_dir": "/data/home/user00/cosdir/bklog-1259494283",
                        "bk_cloud_id": 1,
                        "ip": "127.0.0.1"
                    }
                ]
            },
            "code": 0,
            "message": ""
        }
        """
        return Response(link.LinkHandler(link_id=link_id).retrieve())

    def create(self, request, *args, **kwargs):
        """
        @api {post} /log_extract/links/ 03_新增日志提取链路
        @apiName create_log_extract_link
        @apiGroup 61_links
        @apiParam {String} name 日志提取链路名称
        @apiParam {String} link_type 日志提取链路类型
        @apiParam {String} operator 日志提取链路操作者
        @apiParam {Int} op_bk_biz_id 执行bk_biz_id
        @apiParam {String} qcloud_secret_id 腾讯云SecretId
        @apiParam {String} qcloud_secret_key 腾讯云SecretKey
        @apiParam {String} qcloud_cos_bucket 腾讯云Cos桶名称
        @apiParam {String} qcloud_cos_region 腾讯云Cos区域
        @apiParam {Boolean} is_enable 是否启用
        @apiParam {List} hosts 中转机列表
        @apiParam {String} host.target_dir 挂载目录
        @apiParam {Int} host.bk_cloud_id 主机云区域id
        @apiParam {String} host.ip 主机ip
        @apiParamExample {json} 内网链路请求:
        {
            "name": "111",
            "link_type": "common",
            "operator": "admin",
            "op_bk_biz_id": 1,
            "is_enable": 1,
            "hosts": [
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-1259494283",
                    "bk_cloud_id": 1,
                    "ip": "127.0.0.1"
                },
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-12594942834",
                    "bk_cloud_id": 2,
                    "ip": "127.0.0.1"
                }
            ]
        }
        @apiParamExample {json} 腾讯云链路请求:
        {
            "name": "111",
            "link_type": "qcloud_cos",
            "operator": "admin",
            "op_bk_biz_id": 1,
            "qcloud_secret_id": "123",
            "qcloud_secret_key": "hole",
            "qcloud_cos_bucket": "111",
            "qcloud_cos_region": "222",
            "is_enable": 1,
            "hosts": [
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-1259494283",
                    "bk_cloud_id": 1,
                    "ip": "127.0.0.1"
                },
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-12594942834",
                    "bk_cloud_id": 2,
                    "ip": "127.0.0.1"
                }
            ]
        }
        """
        data = self.params_valid(serializers.ExtractLinkAndHostsSerializer)
        return Response(
            link.LinkHandler().create_or_update(
                name=data["name"],
                link_type=data["link_type"],
                operator=data["operator"],
                op_bk_biz_id=data["op_bk_biz_id"],
                qcloud_secret_id=data.get("qcloud_secret_id", ""),
                qcloud_secret_key=data.get("qcloud_secret_key", ""),
                qcloud_cos_bucket=data.get("qcloud_cos_bucket", ""),
                qcloud_cos_region=data.get("qcloud_cos_region", ""),
                is_enable=data["is_enable"],
                hosts=data["hosts"],
            )
        )

    def update(self, request, link_id=None, *args, **kwargs):
        """
        @api {put} /log_extract/links/$link_id/ 04_更新日志提取链路
        @apiName update_log_extract_link
        @apiGroup 61_links
        @apiParam {Int} link_id 日志提取链路id
        @apiParam {String} name 日志提取链路名称
        @apiParam {String} link_type 日志提取链路类型
        @apiParam {String} operator 日志提取链路操作者
        @apiParam {Int} op_bk_biz_id 执行bk_biz_id
        @apiParam {String} qcloud_secret_id 腾讯云SecretId
        @apiParam {String} qcloud_secret_key 腾讯云SecretKey
        @apiParam {String} qcloud_cos_bucket 腾讯云Cos桶名称
        @apiParam {String} qcloud_cos_region 腾讯云Cos区域
        @apiParam {Boolean} is_enable 是否启用
        @apiParam {List} hosts 中转机列表
        @apiParam {String} host.target_dir 挂载目录
        @apiParam {Int} host.bk_cloud_id 主机云区域id
        @apiParam {String} host.ip 主机ip
        @apiParamExample {json} 内网链路请求:
        {
            "name": "111",
            "link_type": "common",
            "operator": "admin",
            "op_bk_biz_id": 1,
            "is_enable": 1,
            "hosts": [
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-1259494283",
                    "bk_cloud_id": 1,
                    "ip": "127.0.0.1"
                },
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-12594942834",
                    "bk_cloud_id": 2,
                    "ip": "127.0.0.1"
                }
            ]
        }
        @apiParamExample {json} 腾讯云链路请求:
        {
            "name": "111",
            "link_type": "qcloud_cos",
            "operator": "admin",
            "op_bk_biz_id": 1,
            "qcloud_secret_id": "123",
            "qcloud_secret_key": "hole",
            "qcloud_cos_bucket": "111",
            "qcloud_cos_region": "222",
            "is_enable": 1,
            "hosts": [
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-1259494283",
                    "bk_cloud_id": 1,
                    "ip": "127.0.0.1"
                },
                {
                    "target_dir": "/data/home/user00/cosdir/bklog-12594942834",
                    "bk_cloud_id": 2,
                    "ip": "127.0.0.1"
                }
            ]
        }
        """
        data = self.params_valid(serializers.ExtractLinkAndHostsSerializer)
        return Response(
            link.LinkHandler(link_id=link_id).create_or_update(
                name=data["name"],
                link_type=data["link_type"],
                operator=data["operator"],
                op_bk_biz_id=data["op_bk_biz_id"],
                qcloud_secret_id=data.get("qcloud_secret_id", ""),
                qcloud_secret_key=data.get("qcloud_secret_key", ""),
                qcloud_cos_bucket=data.get("qcloud_cos_bucket", ""),
                qcloud_cos_region=data.get("qcloud_cos_region", ""),
                is_enable=data["is_enable"],
                hosts=data["hosts"],
            )
        )

    def destroy(self, request, link_id=None, *args, **kwargs):
        """
        @api {delete} /log_extract/links/$link_id/ 05_删除日志提取链路
        @apiName delete_log_extract_link
        @apiGroup 61_links
        @apiSuccess {Bool} data 返回结果
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": true,
            "code": 0,
            "message": ""
        }
        """
        return Response(link.LinkHandler(link_id=link_id).destroy())
