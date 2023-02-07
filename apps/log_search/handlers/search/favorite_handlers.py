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
from collections import defaultdict
from typing import Optional
from dataclasses import asdict

from django.db.transaction import atomic

from apps.utils.local import get_request_username
from apps.models import model_to_dict
from apps.log_search.constants import (
    FavoriteVisibleType,
    FavoriteGroupType,
    FavoriteListOrderType,
    INDEX_SET_NOT_EXISTED,
)
from apps.log_search.exceptions import (
    FavoriteGroupNotExistException,
    FavoriteGroupNotAllowedDeleteException,
    FavoriteGroupAlreadyExistException,
    FavoriteNotExistException,
    FavoriteVisibleTypeNotAllowedModifyException,
    FavoriteAlreadyExistException,
    FavoriteNotAllowedAccessException,
)
from apps.log_search.models import Favorite, FavoriteGroup, FavoriteGroupCustomOrder, LogIndexSet
from apps.utils.lucene import LuceneParser, LuceneTransformer, LuceneSyntaxResolver, generate_query_string


class FavoriteHandler(object):
    data: Optional[Favorite] = None

    def __init__(self, favorite_id: int = None, space_uid: str = None) -> None:
        self.favorite_id = favorite_id
        self.space_uid = space_uid
        self.username = get_request_username()
        if favorite_id:
            try:
                self.data = Favorite.objects.get(pk=favorite_id)
                user_groups: dict = FavoriteGroup.get_user_groups(self.space_uid, self.username)
                if self.data.group_id not in user_groups:
                    raise FavoriteNotAllowedAccessException()
            except Favorite.DoesNotExist:
                raise FavoriteNotExistException()

    def retrieve(self) -> dict:
        """收藏详情"""
        result = model_to_dict(self.data)
        if LogIndexSet.objects.filter(index_set_id=result["index_set_id"]).exists():
            result["is_active"] = True
            result["index_set_name"] = LogIndexSet.objects.get(index_set_id=result["index_set_id"]).index_set_name
        else:
            result["is_active"] = False
            result["index_set_name"] = INDEX_SET_NOT_EXISTED

        result["query_string"] = generate_query_string(self.data.params)
        result["created_at"] = result["created_at"]
        result["updated_at"] = result["updated_at"]
        return result

    def list_group_favorites(self, order_type: str = FavoriteListOrderType.NAME_ASC.value) -> list:
        """收藏栏分组后且排序后的收藏列表"""
        # 获取排序后的分组
        groups = FavoriteGroupHandler(space_uid=self.space_uid).list()
        group_info = {i["id"]: i for i in groups}
        # 将收藏分组
        favorites = Favorite.get_user_favorite(space_uid=self.space_uid, username=self.username, order_type=order_type)
        favorites_by_group = defaultdict(list)
        for favorite in favorites:
            favorites_by_group[favorite["group_id"]].append(favorite)
        return [
            {
                "group_id": group["id"],
                "group_name": group_info[group["id"]]["name"],
                "group_type": group_info[group["id"]]["group_type"],
                "favorites": favorites_by_group[group["id"]],
            }
            for group in groups
        ]

    def list_favorites(self, order_type: str = FavoriteListOrderType.NAME_ASC.value) -> list:
        """管理界面列出根据name A-Z排序的所有收藏"""
        # 获取排序后的分组
        groups = FavoriteGroupHandler(space_uid=self.space_uid).list()
        group_info = {i["id"]: i for i in groups}
        favorites = Favorite.get_user_favorite(space_uid=self.space_uid, username=self.username, order_type=order_type)
        return [
            {
                "id": fi["id"],
                "name": fi["name"],
                "group_id": fi["group_id"],
                "group_name": group_info[fi["group_id"]]["name"],
                "index_set_id": fi["index_set_id"],
                "index_set_name": fi["index_set_name"],
                "visible_type": fi["visible_type"],
                "params": fi["params"],
                "search_fields": fi["params"].get("search_fields", []),
                "keyword": fi["params"].get("keyword", ""),
                "is_enable_display_fields": fi["is_enable_display_fields"],
                "display_fields": fi["display_fields"],
                "is_active": fi["is_active"],
                "created_by": fi["created_by"],
                "updated_by": fi["updated_by"],
                "updated_at": fi["updated_at"],
            }
            for fi in favorites
        ]

    @atomic
    def create_or_update(
        self,
        name: str,
        host_scopes: dict,
        addition: list,
        keyword: str,
        visible_type: str,
        search_fields: list,
        is_enable_display_fields: bool,
        display_fields: list,
        index_set_id: int = None,
        group_id: int = None,
    ) -> dict:
        # 构建params
        params = {"host_scopes": host_scopes, "addition": addition, "keyword": keyword, "search_fields": search_fields}
        space_uid = self.space_uid if self.space_uid else self.data.space_uid

        # 可见为个人时归类到个人组
        if visible_type == FavoriteVisibleType.PRIVATE.value:
            group_id = FavoriteGroup.get_or_create_private_group(space_uid=space_uid, username=self.username).id

        # 未传组ID的时候, 可见为个人的时候设置为个人组，可见为公开的时候将组置为未分组
        if not group_id:
            group_id = FavoriteGroup.get_or_create_ungrouped_group(space_uid=space_uid).id

        if self.data:
            # 公开收藏转个人收藏仅限于自己创建的
            if (
                self.data.visible_type == FavoriteVisibleType.PUBLIC.value
                and visible_type == FavoriteVisibleType.PRIVATE.value
            ):
                if self.data.created_by != get_request_username():
                    raise FavoriteVisibleTypeNotAllowedModifyException()
                else:
                    group_id = FavoriteGroup.get_or_create_private_group(
                        space_uid=space_uid, username=get_request_username()
                    ).id
            # 名称检查
            if self.data.name != name and Favorite.objects.filter(name=name, space_uid=space_uid).exists():
                raise FavoriteAlreadyExistException()

            update_model_fields = {
                "name": name,
                "group_id": group_id,
                "params": params,
                "visible_type": visible_type,
                "is_enable_display_fields": is_enable_display_fields,
                "display_fields": display_fields,
            }
            for key, value in update_model_fields.items():
                setattr(self.data, key, value)
            self.data.save()

        else:
            if Favorite.objects.filter(name=name, space_uid=space_uid).exists():
                raise FavoriteAlreadyExistException()
            self.data = Favorite.objects.create(
                space_uid=space_uid,
                index_set_id=index_set_id,
                name=name,
                group_id=group_id,
                params=params,
                visible_type=visible_type,
                is_enable_display_fields=is_enable_display_fields,
                display_fields=display_fields,
            )

        return model_to_dict(self.data)

    @staticmethod
    @atomic
    def batch_update(params: list):
        for param in params:
            FavoriteHandler(favorite_id=param["id"]).create_or_update(
                name=param["name"],
                host_scopes=param["host_scopes"],
                addition=param["addition"],
                keyword=param["keyword"],
                visible_type=param["visible_type"],
                search_fields=param["search_fields"],
                is_enable_display_fields=param["is_enable_display_fields"],
                display_fields=param["display_fields"],
                group_id=param["group_id"],
            )

    def delete(self):
        self.data.delete()

    @staticmethod
    def batch_delete(id_list: list):
        Favorite.objects.filter(id__in=id_list).delete()

    @staticmethod
    def get_search_fields(keyword: str) -> list:
        """获取检索语句中可以拆分的字段"""
        fields = [asdict(field) for field in LuceneParser(keyword=keyword).parsing()]

        return fields

    @staticmethod
    def generate_query_by_ui(keyword: str, params: list) -> str:
        """根据params里的参数名以及Value进行替换"""
        return LuceneTransformer().transform(keyword=keyword, params=params)

    @staticmethod
    def inspect(keyword) -> dict:
        return LuceneSyntaxResolver(keyword=keyword).resolve()


class FavoriteGroupHandler(object):
    data: Optional[FavoriteGroup] = None

    def __init__(self, group_id: int = None, space_uid: str = None) -> None:
        self.group_id = group_id
        self.space_uid = space_uid
        self.username = get_request_username()
        if group_id:
            try:
                self.data = FavoriteGroup.objects.get(pk=group_id)
            except FavoriteGroup.DoesNotExist:
                raise FavoriteGroupNotExistException()

    def retrieve(self) -> dict:
        return model_to_dict(self.data)

    def list(self) -> list:
        """获取所有收藏组"""
        group_order = self.get_group_order()
        groups = FavoriteGroup.get_user_groups(space_uid=self.space_uid, username=self.username)
        # 排序后输出
        return [groups[i] for i in group_order]

    @atomic
    def create_or_update(self, name: str) -> dict:
        """创建和修改都是针对公开组的"""
        space_uid = self.space_uid if self.space_uid else self.data.space_uid
        group_type = FavoriteGroupType.PUBLIC.value
        # 检查name是否可用
        if self.data and self.data.name != name or not self.data:
            if FavoriteGroup.objects.filter(name=name, space_uid=space_uid).exists():
                raise FavoriteGroupAlreadyExistException()

        # 修改
        if self.data:
            self.data.name = name
            self.data.save()
        # 创建
        else:
            # get_group_order中包含get_or_create同步个人组和未分类组的逻辑
            group_order = self.get_group_order()
            self.data = FavoriteGroup.objects.create(name=name, group_type=group_type, space_uid=space_uid)
            # 同时追加到用户自定义组的末尾
            group_order.insert(-1, self.data.id)
            self.update_group_order(group_order)

        return model_to_dict(self.data)

    @atomic
    def delete(self) -> None:
        """删除公开分组，并将组内收藏移到未分组"""
        # 只有公开组可以被删除
        if self.data.group_type != FavoriteGroupType.PUBLIC.value:
            raise FavoriteGroupNotAllowedDeleteException()
        # 将该组的收藏全部归到未分组
        unknown_group_id = FavoriteGroup.get_or_create_ungrouped_group(space_uid=self.data.space_uid)
        Favorite.objects.filter(group_id=self.group_id).update(group_id=unknown_group_id.id)
        self.data.delete()

    def get_group_order(self) -> list:
        """获取用户组排序"""
        private_group = FavoriteGroup.get_or_create_private_group(space_uid=self.space_uid, username=self.username)
        ungrouped_group = FavoriteGroup.get_or_create_ungrouped_group(space_uid=self.space_uid)
        obj, __ = FavoriteGroupCustomOrder.objects.get_or_create(
            space_uid=self.space_uid,
            username=self.username,
            defaults={"group_order": [private_group.id, ungrouped_group.id]},
        )

        # 同步组排序内容，不会触发很频繁，只有创建了公共的组才会同步
        order_group_ids = obj.group_order
        all_group_ids = list(FavoriteGroup.get_user_groups(space_uid=self.space_uid, username=self.username).keys())
        # 组内元素相同直接返回
        if sorted(all_group_ids) == sorted(order_group_ids):
            return order_group_ids

        # 保持原有排序，删掉不存在的收藏组，追加缺少的收藏组
        group_ids = [group_id for group_id in order_group_ids if group_id in all_group_ids]
        missing_ids = list(set(all_group_ids).difference(set(order_group_ids)))
        # 永远保证最后一个组为未分组
        new_group_ids = group_ids[:-1]
        new_group_ids.extend(missing_ids)
        new_group_ids.append(group_ids[-1])

        # 更新用户排序
        obj.group_order = new_group_ids
        obj.save()

        return obj.group_order

    def update_group_order(self, group_order: list) -> dict:
        """更新用户组排序"""
        obj = FavoriteGroupCustomOrder.objects.get(space_uid=self.space_uid, username=self.username)
        obj.group_order = group_order
        obj.save()
        return model_to_dict(obj)
