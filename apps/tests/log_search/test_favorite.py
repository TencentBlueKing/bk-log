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
import random

from django.test import TestCase
from unittest.mock import patch

from apps.log_search.constants import FavoriteGroupType, FavoriteVisibleType
from apps.log_search.handlers.search.favorite_handlers import FavoriteGroupHandler, FavoriteHandler
from apps.log_search.models import FavoriteGroup
from apps.utils.lucene import LuceneSyntaxResolver

# 公共参数
SPACE_UID = "test_space_uid"
USERNAME_1 = "test_username_1"
USERNAME_2 = "test_username_2"
INDEX_SET_ID = 1

# 收藏参数
FAVORITE_NAME_1 = "test_favorite_1"
FAVORITE_NAME_2 = "test_favorite_2"
FAVORITE_NAME_3 = "test_favorite_3"
FAVORITE_NAME_4 = "test_favorite_4"
FAVORITE_NAME_5 = "test_favorite_5"

KEYWORD = """number: >=83063 OR title: "The Right Way" AND text: go OR gseIndex: [ 200 TO 600 ] \
AND log: blue~ AND time: /[L-N].*z*l{2}a/ AND a: b AND c: d OR (a: (b OR c AND d) OR x: y ) AND INFO AND ERROR"""

HOST_SCOPES = {"modules": [], "ips": "", "target_nodes": [], "target_node_type": ""}
ADDITION = [{"field": "cloudId", "operator": "is", "value": "0"}]
SEARCH_FIELDS = ["title"]
DISPLAY_FIELDS = ["time", "cloudId", "log"]

# 创建个人收藏参数
CREATE_PRIVATE_FAVORITE_PARAMS = {
    "name": FAVORITE_NAME_1,
    "index_set_id": INDEX_SET_ID,
    "host_scopes": HOST_SCOPES,
    "addition": ADDITION,
    "keyword": KEYWORD,
    "visible_type": FavoriteVisibleType.PRIVATE.value,
    "search_fields": SEARCH_FIELDS,
    "is_enable_display_fields": True,
    "display_fields": DISPLAY_FIELDS,
}

# 创建收藏，不填分组
CREATE_UNKNOWN_FAVORITE_PARAMS = {
    "name": FAVORITE_NAME_2,
    "index_set_id": INDEX_SET_ID,
    "host_scopes": HOST_SCOPES,
    "addition": ADDITION,
    "keyword": KEYWORD,
    "visible_type": FavoriteVisibleType.PUBLIC.value,
    "search_fields": SEARCH_FIELDS,
    "is_enable_display_fields": True,
    "display_fields": DISPLAY_FIELDS,
}

# 创建公开的收藏，组ID未知暂时置为0，测试代码里替换
USER1_CREATE_FAVORITE_PARAM = {
    "name": FAVORITE_NAME_3,
    "index_set_id": INDEX_SET_ID,
    "group_id": 0,
    "host_scopes": HOST_SCOPES,
    "addition": ADDITION,
    "keyword": KEYWORD,
    "visible_type": FavoriteVisibleType.PUBLIC.value,
    "search_fields": SEARCH_FIELDS,
    "is_enable_display_fields": True,
    "display_fields": DISPLAY_FIELDS,
}
USER2_CREATE_FAVORITE_PARAM = {
    "name": FAVORITE_NAME_4,
    "index_set_id": INDEX_SET_ID,
    "group_id": 0,
    "host_scopes": HOST_SCOPES,
    "addition": ADDITION,
    "keyword": KEYWORD,
    "visible_type": FavoriteVisibleType.PUBLIC.value,
    "search_fields": SEARCH_FIELDS,
    "is_enable_display_fields": True,
    "display_fields": DISPLAY_FIELDS,
}

GROUP_NAME_1 = "test_group_1"
GROUP_NAME_2 = "test_group_2"
# -------------------------------------------------------------------------------------------- #
KEYWORD_FIELDS = [
    {"pos": 0, "name": "number", "type": "Word", "operator": ">=", "value": "83063"},
    {"pos": 19, "name": "title", "type": "Phrase", "operator": "=", "value": '"The Right Way"'},
    {"pos": 46, "name": "text", "type": "Word", "operator": "~=", "value": "go"},
    {"pos": 58, "name": "gseIndex", "type": "Range", "operator": "[]", "value": "[ 200 TO 600 ]"},
    {"pos": 87, "name": "log", "type": "Fuzzy", "operator": "~=", "value": "blue~"},
    {"pos": 102, "name": "time", "type": "Regex", "operator": "~=", "value": "/[L-N].*z*l{2}a/"},
    {"pos": 129, "name": "a(1)", "operator": "~=", "type": "Word", "value": "b"},
    {"pos": 138, "name": "c", "operator": "~=", "type": "Word", "value": "d"},
    {"pos": 147, "name": "a(2)", "operator": "()", "type": "FieldGroup", "value": "(b OR c AND d)"},
    {"pos": 168, "name": "x", "operator": "~=", "type": "Word", "value": "y"},
    {"pos": 179, "name": "全文检索(1)", "operator": "~=", "type": "Word", "value": "INFO"},
    {"pos": 188, "name": "全文检索(2)", "operator": "~=", "type": "Word", "value": "ERROR"},
]
UPDATE_QUERY_PARAMS = [
    {
        "pos": 0,
        "value": "10000",
    },
    {
        "pos": 19,
        "value": '"hello"',
    },
    {
        "pos": 46,
        "value": "hello",
    },
    {
        "pos": 58,
        "value": "[100 TO 200]",
    },
    {
        "pos": 87,
        "value": "bk~",
    },
    {
        "pos": 102,
        "value": "/[L-N]/",
    },
    {
        "pos": 129,
        "value": "bb",
    },
    {
        "pos": 138,
        "value": "dd",
    },
    {
        "pos": 147,
        "value": "(bb OR cc AND dd)",
    },
    {
        "pos": 168,
        "value": "yy",
    },
    {
        "pos": 179,
        "value": "hello1",
    },
    {
        "pos": 188,
        "value": "hello2",
    },
]
EXPECT_NEW_QUERY = """number: >=10000 OR title: "hello" AND text: hello OR gseIndex: [100 TO 200] \
AND log: bk~0.5 AND time: /[L-N]/ AND a: bb AND c: dd OR (a: (bb OR cc AND dd) OR x: yy) AND hello1 AND hello2"""

ILLEGAL_KEYWORD = """log:: ERROR AND log: [TO 200] AND time: [100 TO OR log: TO 100]"""
INSPECT_KEYWORD_RESULT = {
    "is_legal": False,
    "is_resolved": True,
    "message": "非法RANGE语法\n异常字符",
    "keyword": "log: ERROR AND log: [* TO 200] AND time: [100 TO *] OR log: [* TO 100]",
}


# 类全局使用USERNAME_1
@patch("apps.models.get_request_username", lambda: USERNAME_1)
@patch("apps.log_search.handlers.search.favorite_handlers.get_request_username", lambda: USERNAME_1)
class TestFavorite(TestCase):
    def setUp(self) -> None:
        # 存放USER1，USER2各自创建的公开组ID，方便后续函数使用
        self.public_group = dict()

    def test_favorite(self):
        # Step1: 用户1拉取组列表，会自动创建一个个人组和当前SPACE_UID下的未分类组
        self.assertEqual(len(FavoriteGroupHandler(space_uid=SPACE_UID).list()), 2)
        # Step2: 两个用户各自创建一个公开组
        self._test_user1_create_group()
        self._test_user2_create_group()
        # Step3: 用户1拉取组列表，此时应该能拉到4个组（1个人组，2公开组，1未分组）
        objs = FavoriteGroupHandler(space_uid=SPACE_UID).list()
        self.assertEqual(len(objs), 4)
        # Step4: 检查组名
        self._test_assert_private_and_ungrouped_group_name(objs)
        # Step5: 修改组名
        self._test_update_group(objs)
        # Step6: 创建收藏
        self._test_user1_create_favorite()
        self._test_user2_create_favorite()
        # Step7: 查看各个用户的收藏
        self._test_user1_list_favorites()
        self._test_user2_list_favorites()
        # Step8: 调整组排序，查看组排序下收藏
        self._test_user1_optimate_group_order()
        # Step9: 删除组
        self._test_delete_group()

    def _test_user1_create_group(self):
        """USER1 创建组"""
        obj = FavoriteGroupHandler(space_uid=SPACE_UID).create_or_update(name=GROUP_NAME_1)
        self.assertEqual(GROUP_NAME_1, obj["name"])
        self.public_group[USERNAME_1] = obj["id"]

    def _test_user2_create_group(self):
        """USER2 创建组"""
        with patch("apps.models.get_request_username", lambda: USERNAME_2):
            obj = FavoriteGroupHandler(space_uid=SPACE_UID).create_or_update(name=GROUP_NAME_2)
            self.assertEqual(GROUP_NAME_2, obj["name"])
            self.public_group[USERNAME_2] = obj["id"]

    def _test_assert_private_and_ungrouped_group_name(self, objs: list):
        """
        个人组名为private
        未分类组名为unknown
        """
        for obj in objs:
            if obj["group_type"] in [FavoriteGroupType.PRIVATE.value, FavoriteGroupType.UNGROUPED.value]:
                self.assertEqual(obj["name"], FavoriteGroupType.get_choice_label(obj["group_type"]))

    def _test_update_group(self, objs: list):
        """测试修改组名"""
        for obj in objs:
            if obj["group_type"] == FavoriteGroupType.PUBLIC.value:
                new_obj = FavoriteGroupHandler(space_uid=SPACE_UID, group_id=obj["id"]).create_or_update(
                    name=obj["name"] + obj["name"]
                )
                self.assertEqual(new_obj["name"], obj["name"] + obj["name"])

    def _test_user1_create_favorite(self):
        """USER1 创建收藏，个人组1个，未分组1个，公开1个"""
        private_favorite = FavoriteHandler(space_uid=SPACE_UID).create_or_update(**CREATE_PRIVATE_FAVORITE_PARAMS)
        self.assertEqual(CREATE_PRIVATE_FAVORITE_PARAMS["name"], private_favorite["name"])
        self.assertEqual(
            FavoriteGroup.objects.get(pk=private_favorite["group_id"]).group_type, FavoriteGroupType.PRIVATE.value
        )
        unknown_favorite = FavoriteHandler(space_uid=SPACE_UID).create_or_update(**CREATE_UNKNOWN_FAVORITE_PARAMS)
        self.assertEqual(CREATE_UNKNOWN_FAVORITE_PARAMS["name"], unknown_favorite["name"])
        self.assertEqual(
            FavoriteGroup.objects.get(pk=unknown_favorite["group_id"]).group_type, FavoriteGroupType.UNGROUPED.value
        )
        USER1_CREATE_FAVORITE_PARAM["group_id"] = self.public_group[USERNAME_1]
        public_favorite = FavoriteHandler(space_uid=SPACE_UID).create_or_update(**USER1_CREATE_FAVORITE_PARAM)
        self.assertEqual(USER1_CREATE_FAVORITE_PARAM["name"], public_favorite["name"])
        self.assertEqual(
            FavoriteGroup.objects.get(pk=public_favorite["group_id"]).group_type, FavoriteGroupType.PUBLIC.value
        )
        self.assertEqual(FavoriteGroup.objects.get(pk=public_favorite["group_id"]).created_by, USERNAME_1)

    def _test_user2_create_favorite(self):
        """USER2 创建收藏，公开1个"""
        with patch("apps.models.get_request_username", lambda: USERNAME_2):
            USER2_CREATE_FAVORITE_PARAM["group_id"] = self.public_group[USERNAME_2]
            public_favorite = FavoriteHandler(space_uid=SPACE_UID).create_or_update(**USER2_CREATE_FAVORITE_PARAM)
            self.assertEqual(USER2_CREATE_FAVORITE_PARAM["name"], public_favorite["name"])
            self.assertEqual(
                FavoriteGroup.objects.get(pk=public_favorite["group_id"]).group_type, FavoriteGroupType.PUBLIC.value
            )
            self.assertEqual(FavoriteGroup.objects.get(pk=public_favorite["group_id"]).created_by, USERNAME_2)

    def _test_user1_list_favorites(self):
        """可见的收藏数，USER1 4个"""
        self.assertEqual(len(FavoriteHandler(space_uid=SPACE_UID).list_favorites()), 4)

        groups = FavoriteGroupHandler(space_uid=SPACE_UID).list()
        self.assertEqual(groups[0]["group_type"], FavoriteGroupType.PRIVATE.value)
        self.assertEqual(groups[-1]["group_type"], FavoriteGroupType.UNGROUPED.value)

    @patch("apps.models.get_request_username", lambda: USERNAME_2)
    @patch("apps.log_search.handlers.search.favorite_handlers.get_request_username", lambda: USERNAME_2)
    def _test_user2_list_favorites(self):
        """可见的收藏数，USER2 3个"""
        self.assertEqual(len(FavoriteHandler(space_uid=SPACE_UID).list_favorites()), 3)

    def _test_user1_optimate_group_order(self):
        group_order = FavoriteGroupHandler(space_uid=SPACE_UID).get_group_order()
        random.shuffle(group_order)
        FavoriteGroupHandler(space_uid=SPACE_UID).update_group_order(group_order)

        favorites_by_group = FavoriteHandler(space_uid=SPACE_UID).list_group_favorites()
        self.assertEqual(group_order, [i["group_id"] for i in favorites_by_group])

    def _test_delete_group(self):
        """删除公共组，公共组的收藏会归类到未分组"""
        FavoriteGroupHandler(space_uid=SPACE_UID, group_id=self.public_group[USERNAME_1]).delete()
        FavoriteGroupHandler(space_uid=SPACE_UID, group_id=self.public_group[USERNAME_2]).delete()
        # 只能看到一个个人组和一个未分组
        favorites_by_group = FavoriteHandler(space_uid=SPACE_UID).list_group_favorites()
        self.assertEqual(len(favorites_by_group), 2)

        for i in favorites_by_group:
            favorites = i["favorites"]
            if i["group_name"] == FavoriteGroupType.PRIVATE.value:
                self.assertEqual(len(favorites), 1)
            if i["group_name"] == FavoriteGroupType.UNGROUPED.value:
                # 剩3个收藏
                self.assertEqual(len(favorites), 3)
                # 2个由USER1创建
                self.assertEqual([j["created_by"] for j in favorites].count(USERNAME_1), 2)
                # 1个由USER2创建
                self.assertEqual([j["created_by"] for j in favorites].count(USERNAME_2), 1)


class TestLucene(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_get_search_fields(self):
        """测试获取Lucene Query字段"""
        search_fields_result = FavoriteHandler().get_search_fields(keyword=KEYWORD)
        for i in range(len(KEYWORD_FIELDS)):
            self.assertDictEqual(search_fields_result[i], KEYWORD_FIELDS[i])

    def test_update_query(self):
        """测试更新Lucene Query"""
        self.assertEqual(FavoriteHandler().generate_query_by_ui(KEYWORD, UPDATE_QUERY_PARAMS), EXPECT_NEW_QUERY)

    def test_inspect(self):
        """测试解析关键字"""
        inspect_result = LuceneSyntaxResolver(keyword=ILLEGAL_KEYWORD).resolve()
        self.assertEqual(inspect_result["is_legal"], INSPECT_KEYWORD_RESULT["is_legal"])
        self.assertEqual(inspect_result["is_resolved"], INSPECT_KEYWORD_RESULT["is_resolved"])
        self.assertEqual(inspect_result["keyword"], INSPECT_KEYWORD_RESULT["keyword"])
        self.assertEqual(
            sorted(inspect_result["message"].split("\n")), sorted(INSPECT_KEYWORD_RESULT["message"].split("\n"))
        )
