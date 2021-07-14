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

from unittest import mock
from urllib import parse

from django.test import TestCase

from apps.utils.bk_data_auth import BkDataAuthHandler

USER_PERMISSION_SCOPES = [{"result_table_id": "2_system_inode"}, {"result_table_id": "2_system_cpu"}]

TOKEN_PERMISSIONS = {
    "permissions": [
        {
            "status": "active",
            "data_token_id": 592,
            "scope_id_key": "result_table_id",
            "updated_by": "admin",
            "created_at": "2020-04-26 17:35:50",
            "description": None,
            "scope_name_key": "result_table_name",
            "updated_at": "2020-04-26 17:35:50",
            "created_by": "admin",
            "scope_display": {"result_table_name": "2_test_table_1"},
            "scope": {
                "result_table_name": "2_test_table_1",
                "result_table_id": "2_test_table_1",
                "description": "测试表1",
            },
            "object_class": "result_table",
            "id": 4297,
            "scope_object_class": "result_table",
            "action_id": "result_table.query_data",
        },
        {
            "status": "active",
            "data_token_id": 592,
            "scope_id_key": "result_table_id",
            "updated_by": "admin",
            "created_at": "2020-04-26 17:35:50",
            "description": None,
            "scope_name_key": "result_table_name",
            "updated_at": "2020-04-26 17:35:50",
            "created_by": "admin",
            "scope_display": {"result_table_name": "2_test_table_2"},
            "scope": {
                "result_table_name": "2_test_table_2",
                "result_table_id": "2_test_table_2",
                "description": "测试表2",
            },
            "object_class": "result_table",
            "id": 4298,
            "scope_object_class": "result_table",
            "action_id": "result_table.delete_data",
        },
        {
            "status": "active",
            "data_token_id": 592,
            "scope_id_key": "result_table_id",
            "updated_by": "admin",
            "created_at": "2020-04-26 17:35:50",
            "description": None,
            "scope_name_key": "result_table_name",
            "updated_at": "2020-04-26 17:35:50",
            "created_by": "admin",
            "scope_display": {"result_table_name": "2_test_table_3"},
            "scope": {
                "result_table_name": "2_test_table_3",
                "result_table_id": "2_test_table_3",
                "description": "测试表3",
            },
            "object_class": "result_table",
            "id": 4299,
            "scope_object_class": "result_table",
            "action_id": "result_table.query_data",
        },
    ]
}


class TestBkDataAuthHandler(TestCase):
    @mock.patch("apps.utils.bk_data_auth.BkDataAuthApi.get_user_perm_scope")
    def test_list_authorized_rt_by_user(self, get_user_perm_scope):
        get_user_perm_scope.return_value = USER_PERMISSION_SCOPES
        handler = BkDataAuthHandler("admin")
        result_tables = handler.list_authorized_rt_by_user()
        self.assertListEqual(result_tables, list({"2_system_inode", "2_system_cpu"}))

    @mock.patch("apps.utils.bk_data_auth.BkDataAuthApi.get_auth_token")
    def test_list_authorized_rt_by_token(self, get_auth_token):
        get_auth_token.return_value = TOKEN_PERMISSIONS
        handler = BkDataAuthHandler("admin")
        result_tables = handler.list_authorized_rt_by_token()
        self.assertListEqual(result_tables, list({"2_test_table_1", "2_test_table_3"}))

    @mock.patch("apps.utils.bk_data_auth.BkDataAuthApi.get_user_perm_scope")
    def test_filter_unauthorized_rt_by_user(self, get_user_perm_scope):
        get_user_perm_scope.return_value = USER_PERMISSION_SCOPES
        handler = BkDataAuthHandler("admin")

        with self.settings(FEATURE_TOGGLE={"bkdata_token_auth": "on"}):
            result_tables = handler.filter_unauthorized_rt_by_user(["2_system_inode", "2_test_table_1"])
            self.assertListEqual(result_tables, ["2_test_table_1"])

        with self.settings(FEATURE_TOGGLE={"bkdata_token_auth": "off"}):
            result_tables = handler.filter_unauthorized_rt_by_user(["2_system_inode", "2_test_table_1"])
            self.assertListEqual(result_tables, [])

    @mock.patch("apps.utils.bk_data_auth.BkDataAuthApi.get_auth_token")
    def test_filter_unauthorized_rt_by_token(self, get_auth_token):
        get_auth_token.return_value = TOKEN_PERMISSIONS
        handler = BkDataAuthHandler("admin")

        with self.settings(FEATURE_TOGGLE={"bkdata_token_auth": "on"}):
            result_tables = handler.filter_unauthorized_rt_by_token(
                ["2_system_inode", "2_test_table_1", "2_test_table_2"]
            )
            self.assertListEqual(result_tables, ["2_system_inode", "2_test_table_2"])

        with self.settings(FEATURE_TOGGLE={"bkdata_token_auth": "off"}):
            result_tables = handler.filter_unauthorized_rt_by_token(
                ["2_system_inode", "2_test_table_1", "2_test_table_2"]
            )
            self.assertListEqual(result_tables, [])

    def test_get_auth_url(self):
        with self.settings(BKDATA_URL="http://test.bkdata.com", BKDATA_DATA_TOKEN_ID=1234):
            url = BkDataAuthHandler.get_auth_url(["2_rt_1", "2_rt_2"], "test_state_string")

        result = parse.urlsplit(url)
        params = dict(parse.parse_qsl(result.query))
        self.assertEqual(result.netloc, "test.bkdata.com")
        self.assertEqual(params["scopes"], "2_rt_1,2_rt_2")
        self.assertEqual(params["state"], "test_state_string")
        self.assertEqual(params["data_token_id"], "1234")
