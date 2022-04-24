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
import json

from django.test import TestCase

from blueking.component import collections
from blueking.component.client import BaseComponentClient, ComponentClientWithSignature
from blueking.tests.utils.utils import tests_settings as TS  # noqa


class TestBaseComponentClient(TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        cls.ComponentClient = BaseComponentClient
        cls.ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)

    def test_api_get(self):
        client = self.ComponentClient(
            TS["valid_app"]["bk_app_code"],
            TS["valid_app"]["bk_app_secret"],
            common_args={
                "bk_username": TS["bk_user"]["bk_username"],
            },
        )
        result = client.bk_login.get_user()
        self.assertTrue(result["result"], json.dumps(result))
        self.assertTrue(result["data"]["bk_username"], TS["bk_user"]["bk_username"])

    def test_api_post(self):
        client = self.ComponentClient(
            TS["valid_app"]["bk_app_code"],
            TS["valid_app"]["bk_app_secret"],
            common_args={
                "bk_username": TS["bk_user"]["bk_username"],
            },
        )
        result = client.bk_login.get_batch_users({"bk_username_list": [TS["bk_user"]["bk_username"]]})
        self.assertTrue(result["result"], json.dumps(result))
        self.assertTrue(result["data"][TS["bk_user"]["bk_username"]]["bk_username"], TS["bk_user"]["bk_username"])

    def test_set_bk_api_ver(self):
        client = self.ComponentClient(
            TS["valid_app"]["bk_app_code"],
            TS["valid_app"]["bk_app_secret"],
            common_args={
                "bk_username": TS["bk_user"]["bk_username"],
            },
        )
        client.set_bk_api_ver("")
        result = client.bk_login.get_user({"username": TS["bk_user"]["bk_username"]})
        self.assertTrue(result["result"], json.dumps(result))
        self.assertTrue(result["data"]["username"], TS["bk_user"]["bk_username"])


class TestComponentClientWithSignature(TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        cls.ComponentClient = ComponentClientWithSignature
        cls.ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)

    def test_api(self):
        client = self.ComponentClient(
            TS["valid_app"]["bk_app_code"],
            TS["valid_app"]["bk_app_secret"],
            common_args={
                "bk_username": TS["bk_user"]["bk_username"],
            },
        )
        result = client.bk_login.get_user()
        self.assertTrue(result["result"], json.dumps(result))
        self.assertTrue(result["data"]["bk_username"], TS["bk_user"]["bk_username"])

    def test_api_post(self):
        client = self.ComponentClient(
            TS["valid_app"]["bk_app_code"],
            TS["valid_app"]["bk_app_secret"],
            common_args={
                "bk_username": TS["bk_user"]["bk_username"],
            },
        )
        result = client.bk_login.get_batch_users({"bk_username_list": [TS["bk_user"]["bk_username"]]})
        self.assertTrue(result["result"], json.dumps(result))
        self.assertTrue(result["data"][TS["bk_user"]["bk_username"]]["bk_username"], TS["bk_user"]["bk_username"])
