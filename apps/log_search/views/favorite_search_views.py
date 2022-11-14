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
from django.http import Http404
from rest_framework import serializers
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.iam.handlers.drf import ViewBusinessPermission
from apps.log_search.exceptions import FavoriteSearchNotExists
from apps.log_search.handlers.search.favorite_handlers import FavoriteHandlers
from apps.log_search.models import FavoriteSearch
from apps.log_search.serializers import FavoriteSearchListSerializer, FavoriteSearchSerializer
from apps.models import model_to_dict


class FavoriteSearchViewSet(APIViewSet):
    """
    检索收藏
    """

    serializer_class = serializers.Serializer
    model = FavoriteSearch
    queryset = FavoriteSearch.objects.all()
    permission_classes = (ViewBusinessPermission,)

    def list(self, request, *args, **kwargs):
        """
        @api {get} /search/favorite/?space_uid=$space_uid 01_检索收藏-列表
        @apiDescription 用户收藏的检索列表
        @apiName favorite_search
        @apiGroup 21_Favorite
        @apiParam {String} space_uid 空间唯一标识
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "favorite_search_id": 1,
                    "favorite_search_description": "收藏检索描述",
                    "index_set_id": 31,
                    "params": {
                        "keyword": "*",
                        "host_scopes": {
                            "modules": [
                                {
                                    "bk_inst_id": 25,
                                    "bk_obj_id": "module"
                                }
                            ],
                            "ips": "127.0.0.1,127.0.0.2"
                        },
                        "addition": [
                            {
                                "field": "cloudId",
                                "operator": "is",
                                "value": "0"
                            }
                        ]
                    },
                    "query_string": "keyword:* AND (ips:127.0.0.1)"
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(FavoriteSearchListSerializer)
        return Response(FavoriteHandlers().favorite_search(data.get("space_uid")))

    def create(self, request, *args, **kwargs):
        """
        @api {post} /search/favorite/ 02_检索收藏-创建
        @apiDescription 创建用户检索收藏
        @apiName create_favorite_search
        @apiGroup 21_Favorite
        @apiParam {Int} index_set_id 索引集id
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {Int} description 收藏描述
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} host_scopes 主机维度
        @apiParam {dict} host_scopes.modules 模块参数
        @apiParam {String} host_scopes.ips IP列表
        @apiParam {Json} addition 搜索条件
        @apiParamExample {json} 请求参数
        {
            "index_set_id": 12312,
            "space_uid": "bkcc__2",
            "description": "收藏描述",
            "keyword": "error",
            "host_scopes": {
                "modules": [
                    {
                        "bk_obj_id": "module",
                        "bk_inst_id": 4
                    },
                    {
                        "bk_obj_id": "set",
                        "bk_inst_id": 4
                    }
                ],
                "ips": "127.0.0.1,127.0.0.2"
            },
            "addition": [
                {
                    "field": "ip",
                    "operator": "is",
                    "value": "127.0.0.1"
                }
            ],
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        data = self.params_valid(FavoriteSearchSerializer)
        favorite_search = FavoriteHandlers().create(
            space_uid=data["space_uid"],
            index_set_id=data["index_set_id"],
            host_scopes=data["host_scopes"],
            addition=data["addition"],
            keyword=data["keyword"],
            description=data["description"],
        )
        return Response(model_to_dict(favorite_search, fields=["id"]))

    def destroy(self, request, *args, **kwargs):
        """
        @api {delete} /search/favorite/$favorite_search_id/ 03_检索收藏-删除
        @apiDescription 删除对应的检索收藏
        @apiName delete_favorite_search
        @apiGroup 21_Favorite
        @apiParam {Int} favorite_search_id
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        try:
            FavoriteHandlers(favorite_search_id=self.get_object().id).delete()
        except Http404:
            raise FavoriteSearchNotExists
        return Response()
