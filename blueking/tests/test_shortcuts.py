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
import json

from django.test import TestCase, RequestFactory

from blueking.component.shortcuts import get_client_by_user, get_client_by_request
from blueking.tests.utils.utils import tests_settings as TS  # noqa
from blueking.tests.utils.utils import get_user_model


class TestShortcuts(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_model = get_user_model()

    def test_get_client_by_request(self):
        request = self.factory.get("/")
        request.user = self.user_model(username=TS["bk_user"]["bk_username"])
        request.COOKIES = {"bk_token": TS["bk_user"]["bk_token"]}

        client = get_client_by_request(request)
        result = client.bk_login.get_user()
        self.assertTrue(result["result"], json.dumps(result))
        self.assertEqual(result["data"]["bk_username"], TS["bk_user"]["bk_username"])

    def test_get_client_by_user(self):
        user = self.user_model(username=TS["bk_user"]["bk_username"])
        client = get_client_by_user(user)
        result = client.bk_login.get_user()
        self.assertTrue(result["result"], json.dumps(result))
        self.assertEqual(result["data"]["bk_username"], TS["bk_user"]["bk_username"])

        client = get_client_by_user(TS["bk_user"]["bk_username"])
        result = client.bk_login.get_user()
        self.assertTrue(result["result"], json.dumps(result))
        self.assertEqual(result["data"]["bk_username"], TS["bk_user"]["bk_username"])
