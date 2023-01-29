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
from apps.log_search.exceptions import FavoriteGroupNotExistException, FavoriteNotExistException
from apps.log_search.handlers.search.favorite_handlers import FavoriteHandler, FavoriteGroupHandler
from apps.log_search.models import Favorite, FavoriteGroup
from apps.log_search.serializers import (
    FavoriteGroupListSerializer,
    CreateFavoriteGroupSerializer,
    UpdateFavoriteGroupSerializer,
    UpdateFavoriteGroupOrderSerializer,
    FavoriteListSerializer,
    CreateFavoriteSerializer,
    UpdateFavoriteSerializer,
    GetSearchFieldsSerializer,
    GenerateQuerySerializer,
    BatchUpdateFavoriteSerializer,
    BatchDeleteFavoriteSerializer,
    InspectSerializer,
)
from apps.utils.drf import list_route


class FavoriteViewSet(APIViewSet):
    """
    检索收藏
    """

    lookup_field = "id"
    serializer_class = serializers.Serializer
    model = Favorite
    queryset = Favorite.objects.all()
    permission_classes = (ViewBusinessPermission,)

    def retrieve(self, request, id, *args, **kwargs):
        """
        @api {get} /search/favorite/$id/ 01_收藏-详情
        @apiDescription 收藏详情
        @apiName favorite_retrieve
        @apiGroup 21_Favorite
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data":
                {
                    "id": 1,
                    "created_at": "2022-10-16T18:43:52.559141Z",
                    "created_by": "test_user_1",
                    "updated_at": "2022-10-16T18:43:52.559207Z",
                    "updated_by": "test_user_1",
                    "is_deleted": false,
                    "deleted_at": null,
                    "deleted_by": null,
                    "space_uid": "space_uid",
                    "index_set_id": 4,
                    "name": "test_favorite_1",
                    "group_id": 1,
                    "group_name": "group_name",
                    "params": {
                        "host_scopes": {},
                        "addition": [],
                        "keyword": null,
                        "search_fields": []
                    },
                    "visible_type": "private",
                    "display_fields": []
                }
            "result": true
        }
        """
        return Response(FavoriteHandler(favorite_id=id).retrieve())

    def list(self, request, *args, **kwargs):
        """
        @api {get} /search/favorite/?space_uid=$space_uid 01_收藏-列表
        @apiDescription 用户的收藏列表
        @apiName favorite_list
        @apiGroup 21_Favorite
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {String} order_type 排序方式
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": 1,
                    "created_at": "2022-10-16T18:43:52.559141Z",
                    "created_by": "test_user_1",
                    "updated_at": "2022-10-16T18:43:52.559207Z",
                    "updated_by": "test_user_1",
                    "is_deleted": false,
                    "deleted_at": null,
                    "deleted_by": null,
                    "space_uid": "space_uid",
                    "index_set_id": 4,
                    "name": "test_favorite_1",
                    "group_id": 1,
                    "group_name": "group_name",
                    "params": {
                        "host_scopes": {},
                        "addition": [],
                        "keyword": null,
                        "search_fields": []
                    },
                    "visible_type": "private",
                    "display_fields": []
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(FavoriteListSerializer)
        return Response(FavoriteHandler(space_uid=data.get("space_uid")).list_favorites(order_type=data["order_type"]))

    @list_route(methods=["GET"])
    def list_by_group(self, request, *args, **kwargs):
        """
        @api {get} /search/favorite/list_by_group/?space_uid=$space_uid&order_type=$order_type 01_收藏-获取各个收藏组下的收藏列表
        @apiDescription 用户分组后的收藏列表
        @apiName favorite_list_by_group
        @apiGroup 21_Favorite
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {String} order_type 排序方式
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "group_id": 1,
                    "group_name": "private",
                    "favorites": [
                        {
                            "id": 1,
                            "created_at": "2022-10-16T18:43:52.559141Z",
                            "created_by": "test_user_1",
                            "updated_at": "2022-10-16T18:43:52.559207Z",
                            "updated_by": "test_user_1",
                            "is_deleted": false,
                            "deleted_at": null,
                            "deleted_by": null,
                            "space_uid": "space_uid",
                            "index_set_id": 1,
                            "name": "test_favorite_1",
                            "group_id": 1,
                            "params": {
                                "host_scopes": {},
                                "addition": [],
                                "keyword": null,
                                "search_fields": []
                            },
                            "visible_type": "private",
                            "display_fields": []
                        }
                    ]
                },
                {
                    "group_id": 2,
                    "group_name": "unknown",
                    "favorites": []
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(FavoriteListSerializer)
        return Response(
            FavoriteHandler(space_uid=data.get("space_uid")).list_group_favorites(order_type=data["order_type"])
        )

    def create(self, request, *args, **kwargs):
        """
        @api {post} /search/favorite/ 02_检索收藏-创建
        @apiDescription 创建用户检索收藏
        @apiName create_favorite_search
        @apiGroup 21_Favorite
        @apiParam {Int} index_set_id 索引集id
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {String} name 收藏名
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} host_scopes 主机维度
        @apiParam {dict} host_scopes.modules 模块参数
        @apiParam {String} host_scopes.ips IP列表
        @apiParam {Json} addition 搜索条件
        @apiParam {List} search_fields 检索字段
        @apiParam {List} display_fields 展示字段
        @apiParamExample {json} 请求参数
        {
            "index_set_id": 12312,
            "space_uid": "bkcc__2",
            "name": "收藏名",
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
            "search_fields": ["log"]
            "display_fields": ["log", "ip", "time"]
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data":
            {
                "id": 1,
                "created_at": "2022-10-16T18:43:52.559141Z",
                "created_by": "test_user_1",
                "updated_at": "2022-10-16T18:43:52.559207Z",
                "updated_by": "test_user_1",
                "is_deleted": false,
                "deleted_at": null,
                "deleted_by": null,
                "space_uid": "space_uid",
                "index_set_id": 1,
                "name": "test_favorite_1",
                "group_id": 1,
                "params": {
                    "host_scopes": {},
                    "addition": [],
                    "keyword": null,
                    "search_fields": []
                },
                "visible_type": "private",
                "is_enable_display_fields": True,
                "display_fields": []
            },
            "result": true
        }
        """
        data = self.params_valid(CreateFavoriteSerializer)
        favorite_search = FavoriteHandler(space_uid=data["space_uid"]).create_or_update(
            name=data["name"],
            index_set_id=data["index_set_id"],
            host_scopes=data["host_scopes"],
            addition=data["addition"],
            keyword=data["keyword"],
            visible_type=data["visible_type"],
            search_fields=data["search_fields"],
            is_enable_display_fields=data["is_enable_display_fields"],
            display_fields=data["display_fields"],
            group_id=data["group_id"],
        )
        return Response(favorite_search)

    def update(self, request, *args, **kwargs):
        """
        @api {PUT} /search/favorite/ 02_检索收藏-修改
        @apiDescription 修改用户检索收藏
        @apiName update_favorite_search
        @apiGroup 21_Favorite
        @apiParam {String} name 收藏名
        @apiParam {String} keyword 搜索关键字
        @apiParam {Json} host_scopes 主机维度
        @apiParam {dict} host_scopes.modules 模块参数
        @apiParam {String} host_scopes.ips IP列表
        @apiParam {Json} addition 搜索条件
        @apiParam {List} search_fields 检索字段
        @apiParam {List} display_fields 展示字段
        @apiParamExample {json} 请求参数
        {
            "index_set_id": 12312,
            "space_uid": "bkcc__2",
            "name": "收藏名",
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
            "search_fields": ["log"],
            "is_enable_display_fields": True,
            "display_fields": ["log", "ip", "time"]
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data":
                {
                    "id": 1,
                    "created_at": "2022-10-16T18:43:52.559141Z",
                    "created_by": "test_user_1",
                    "updated_at": "2022-10-16T18:43:52.559207Z",
                    "updated_by": "test_user_1",
                    "is_deleted": false,
                    "deleted_at": null,
                    "deleted_by": null,
                    "space_uid": "space_uid",
                    "index_set_id": 1,
                    "name": "test_favorite_1",
                    "group_id": 1,
                    "params": {
                        "host_scopes": {},
                        "addition": [],
                        "keyword": null,
                        "search_fields": []
                    },
                    "visible_type": "private",
                    "is_enable_display_fields": True,
                    "display_fields": []
                },
                "result": true
            }
        """
        data = self.params_valid(UpdateFavoriteSerializer)
        favorite_search = FavoriteHandler(favorite_id=kwargs["id"]).create_or_update(
            name=data["name"],
            host_scopes=data["host_scopes"],
            addition=data["addition"],
            keyword=data["keyword"],
            visible_type=data["visible_type"],
            search_fields=data["search_fields"],
            is_enable_display_fields=data["is_enable_display_fields"],
            display_fields=data["display_fields"],
            group_id=data["group_id"],
        )
        return Response(favorite_search)

    @list_route(methods=["POST"], url_path="batch_update")
    def batch_update(self, request, *args, **kwargs):
        """
        @api {POST} /search/favorite/ 02_检索收藏-批量修改
        @apiDescription 修改用户检索收藏
        @apiName batch_update_favorite_search
        @apiGroup 21_Favorite
        @apiParam {List} params 批量更新参数
        @apiParam {String} params.name 收藏名
        @apiParam {String} params.keyword 搜索关键字
        @apiParam {Json} params.host_scopes 主机维度
        @apiParam {dict} params.host_scopes.modules 模块参数
        @apiParam {String} params.host_scopes.ips IP列表
        @apiParam {Json} params.addition 搜索条件
        @apiParam {List} params.search_fields 检索字段
        @apiParam {List} params.display_fields 展示字段
        @apiParamExample {json} 请求参数
        {
            "params": [
                {
                    "id": 1,
                    "index_set_id": 12312,
                    "space_uid": "bkcc__2",
                    "name": "收藏名",
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
                    "search_fields": ["log"],
                    "is_enable_display_fields": True,
                    "display_fields": ["log", "ip", "time"]
                }
            ]
        }

        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": ""，
            "result": true
            }
        """
        data = self.params_valid(BatchUpdateFavoriteSerializer)
        FavoriteHandler().batch_update(data["params"])
        return Response()

    def destroy(self, request, *args, **kwargs):
        """
        @api {delete} /search/favorite/$favorite_id/ 03_检索收藏-删除
        @apiDescription 删除对应的收藏
        @apiName delete_favorite_search
        @apiGroup 21_Favorite
        @apiParam {Int} favorite_id
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        try:
            FavoriteHandler(favorite_id=self.get_object().id).delete()
        except Http404:
            raise FavoriteNotExistException
        return Response()

    @list_route(methods=["POST"], url_path="batch_delete")
    def batch_delete(self, request, *args, **kwargs):
        """
        @api {POST} /search/favorite/ 02_检索收藏-批量删除
        @apiDescription 批量删除用户检索收藏
        @apiName batch_delete_favorite_search
        @apiGroup 21_Favorite
        @apiParam {List} id_list 收藏id列表
        @apiParamExample {json} 请求参数
        {
            "id_list": [1， 2]
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": ""，
            "result": true
            }
        """
        data = self.params_valid(BatchDeleteFavoriteSerializer)
        FavoriteHandler().batch_delete(data["id_list"])
        return Response()

    @list_route(methods=["POST"], url_path="get_search_fields")
    def get_search_fields(self, request, *args, **kwargs):
        """
        @api {POST} /search/favorite/get_search_fields/ 03_检索收藏-获取检索语句字段
        @apiDescription 获取检索语句字段
        @apiName get_search_fields
        @apiGroup 21_Favorite
        @apiParam {string} keyword
        @apiParamExample {json} 请求参数
        {
            "keyword": 'number: >=83063 AND title: "The Right Way"'
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "name": "number",
                    "type": "Word",
                    "operator": ">=",
                    "value": "83063"
                },
                {
                    "name": "title",
                    "type": "Phrase",
                    "operator": "=",
                    "value": '"The Right Way"'
                },
            ],
            "result": true
        }
        """
        data = self.params_valid(GetSearchFieldsSerializer)
        return Response(FavoriteHandler().get_search_fields(keyword=data["keyword"]))

    @list_route(methods=["POST"], url_path="generate_query")
    def generate_query(self, request, *args, **kwargs):
        """
        @api {POST} /search/favorite/generate_query/ 03_检索收藏-根据search_fields以及value生成新的query
        @apiDescription 生成检索语句字段
        @apiName generate_query
        @apiGroup 21_Favorite
        @apiParam {string} keyword
        @apiParam {list} params
        @apiParamExample {json} 请求参数
        {
            "keyword": 'number: >=83063 AND title: "The Right Way"'
            "params": [
                {
                    "pos": 1,
                    "name": number,
                    "value": 11111
                },
                {
                    "pos": 17,
                    "name": title,
                    "value": '"The"'
                }
            ]
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": 'number: >=11111 AND title: "The"'
            "result": true
        }
        """
        data = self.params_valid(GenerateQuerySerializer)
        return Response(FavoriteHandler().generate_query_by_ui(keyword=data["keyword"], params=data["params"]))

    @list_route(methods=["POST"], url_path="inspect")
    def inspect(self, request, *args, **kwargs):
        """
        @api {POST} /search/favorite/inspect/ 03_检索收藏-检查语法是否合理，并提供转换后的keyword
        @apiDescription 语法检查以及转换
        @apiName inspect
        @apiGroup 21_Favorite
        @apiParam {string} keyword
        @apiParamExample {json} 请求参数
        {
            "keyword": 'AAA BBB'
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": {
                "is_legal": false,
                "keyword": 'AAA AND BBB'
            }
            "result": true
        }
        """
        data = self.params_valid(InspectSerializer)
        return Response(FavoriteHandler().inspect(keyword=data["keyword"]))


class FavoriteGroupViewSet(APIViewSet):
    """
    检索收藏组
    """

    lookup_field = "id"
    serializer_class = serializers.Serializer
    model = FavoriteGroup
    queryset = FavoriteGroup.objects.all()
    permission_classes = (ViewBusinessPermission,)

    def list(self, request, *args, **kwargs):
        """
        @api {get} /search/favorite_group/?space_uid=$space_uid 01_检索收藏组-列表
        @apiDescription 用户收藏组列表
        @apiName favorite_group
        @apiGroup 21_Favorite
        @apiParam {String} space_uid 空间唯一标识
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "id": 1,
                    "created_at": "2022-10-14T03:13:40.458735Z",
                    "created_by": "test_user",
                    "updated_at": "2022-10-14T03:13:40.458776Z",
                    "updated_by": "test_user",
                    "is_deleted": false,
                    "deleted_at": null,
                    "deleted_by": null,
                    "name": "private",
                    "group_type": "private",
                    "space_uid": "bkcc__2"
                }
            ],
            "result": true
        }
        """
        data = self.params_valid(FavoriteGroupListSerializer)
        return Response(FavoriteGroupHandler(space_uid=data.get("space_uid")).list())

    def create(self, request, *args, **kwargs):
        """
        @api {post} /search/favorite_group/ 02_检索收藏组-创建
        @apiDescription 创建公开收藏组
        @apiName create_favorite_group
        @apiGroup 21_Favorite
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {String} name 收藏组名
        @apiParamExample {json} 请求参数
        {
            "space_uid": "bkcc__2",
            "name": "收藏组名"
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": {
                    "id": 1,
                    "created_at": "2022-10-14T03:13:40.458735Z",
                    "created_by": "test_user",
                    "updated_at": "2022-10-14T03:13:40.458776Z",
                    "updated_by": "test_user",
                    "is_deleted": false,
                    "deleted_at": null,
                    "deleted_by": null,
                    "name": "private",
                    "group_type": "private",
                    "space_uid": "bkcc__2"
                },
            "result": true
        }
        """
        data = self.params_valid(CreateFavoriteGroupSerializer)
        favorite_search = FavoriteGroupHandler(space_uid=data["space_uid"]).create_or_update(name=data["name"])
        return Response(favorite_search)

    def update(self, request, *args, **kwargs):
        """
        @api {PUT} /search/favorite_group/$group_id/ 02_检索收藏组-修改
        @apiDescription 修改收藏组名
        @apiName create_favorite_group
        @apiGroup 21_Favorite
        @apiParam {String} name 收藏组名
        @apiParamExample {json} 请求参数
        {
            "name": "收藏组名"
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": {
                    "id": 1,
                    "created_at": "2022-10-14T03:13:40.458735Z",
                    "created_by": "test_user",
                    "updated_at": "2022-10-14T03:13:40.458776Z",
                    "updated_by": "test_user",
                    "is_deleted": false,
                    "deleted_at": null,
                    "deleted_by": null,
                    "name": "private",
                    "group_type": "private",
                    "space_uid": "bkcc__2"
                },
            "result": true
        }
        """
        data = self.params_valid(UpdateFavoriteGroupSerializer)
        favorite_search = FavoriteGroupHandler(group_id=kwargs["id"]).create_or_update(name=data["name"])
        return Response(favorite_search)

    def destroy(self, request, *args, **kwargs):
        """
        @api {delete} /search/favorite_group/$group_id/ 03_检索收藏组-删除
        @apiDescription 删除公开收藏组
        @apiName delete_favorite_group
        @apiGroup 21_Favorite
        @apiParam {Int} group_id
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        try:
            FavoriteGroupHandler(group_id=self.get_object().id).delete()
        except Http404:
            raise FavoriteGroupNotExistException
        return Response()

    @list_route(methods=["POST"], url_path="update_order")
    def update_order(self, request, *args, **kwargs):
        """
        @api {POST} /search/favorite_group/update_order/ 02_检索收藏组-修改组排序
        @apiDescription 修改收藏组排序
        @apiName update_order
        @apiGroup 21_Favorite
        @apiParam {String} space_uid 空间唯一标识
        @apiParam {List} group_order 收藏组排序
        @apiParamExample {json} 请求参数
        {
            "space_uid": "bkcc__2"
            "group_order": [4,3,2,1]
        }
        @apiSuccessExample {json} 成功返回：
        {
            "message": "",
            "code": 0,
            "data": {
                    "username": xxx,
                    "group_order": [4,3,2,1]
                },
            "result": true
        }
        """
        data = self.params_valid(UpdateFavoriteGroupOrderSerializer)
        group_order = FavoriteGroupHandler(space_uid=data["space_uid"]).update_group_order(
            group_order=data["group_order"]
        )
        return Response(group_order)
