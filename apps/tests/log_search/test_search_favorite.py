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
from unittest.mock import patch
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import reverse, status
from rest_framework.test import APITestCase, override_settings

from apps.log_search.models import FavoriteSearch

logger = logging.getLogger()

User = get_user_model()
MOCK_USER_NAME = "test_user"
BK_BIZ_ID = 1
SPACE_UID = 2
GROUP_ID_MAINTAINER = 11
GROUP_ID_DEVELOPER = 12
GROUP_ID_PRODUCTOR = 13

BIZ_LIST = [
    {
        "bk_biz_id": BK_BIZ_ID,
        "bk_biz_maintainer": f"user11,user12,{MOCK_USER_NAME}",
        "bk_biz_developer": "user21",
        "bk_biz_productor": "",
    }
]

CMDB_PROJECTS = {BK_BIZ_ID: SPACE_UID}

CMDB_GROUPS = {
    SPACE_UID: {
        "bk_biz_maintainer": GROUP_ID_MAINTAINER,
        "bk_biz_developer": GROUP_ID_DEVELOPER,
        "bk_biz_productor": GROUP_ID_PRODUCTOR,
    }
}

CMDB_USERS = {GROUP_ID_MAINTAINER: {"user11": 11, "user12": 12}, GROUP_ID_DEVELOPER: {"user21": 21}}

CMDB_POLICYS = {GROUP_ID_MAINTAINER: {settings.ACTION_PROJECT_RETRIEVE: True}}

CREATE_FAVORITE_DATA = {
    "index_set_id": 1,
    "space_uid": SPACE_UID,
    "description": "this is des",
    "keyword": "*",
    "host_scopes": {"modules": [], "ips": "127.0.0.1"},
    "addition": [],
}


def get_test_user(**kwargs):
    return User.objects.create(**kwargs)


# @patch("blueapps.account.components.bk_ticket.middlewares.LoginRequiredMiddleware.process_view", return_value=None)
@patch("blueapps.account.components.bk_token.middlewares.LoginRequiredMiddleware.process_view", return_value=None)
@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "login_db": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }
)
class TestSearchFavorite(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_test_user(username=MOCK_USER_NAME)

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        self.client.logout()

    def test_list(self, *args):
        query_params = {"space_uid": SPACE_UID}
        url = reverse.reverse("apps.log_search:favorite-list")
        response = self.client.get(url, data=query_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 0)

        query_params = {"space_uid": "bkcc__2345"}
        response = self.client.get(url, data=query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"], [])

    def test_create(self, *args, **kwargs):
        url = reverse.reverse("apps.log_search:favorite-list")
        response = self.client.post(url, data=json.dumps(CREATE_FAVORITE_DATA), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertTrue(result["result"])
        favorite_id = result["data"]["id"]
        exists = FavoriteSearch.objects.filter(id=favorite_id).exists()
        self.assertTrue(exists)

    def test_delete(self, *args):
        create_url = reverse.reverse("apps.log_search:favorite-list")
        response = self.client.post(create_url, data=json.dumps(CREATE_FAVORITE_DATA), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertTrue(result["result"])
        favorite_id = result["data"]["id"]
        delete_url = reverse.reverse("apps.log_search:favorite-detail", kwargs={"pk": favorite_id})
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        delete_result = json.loads(delete_response.content)
        self.assertTrue(delete_result["result"])
        delete_exists = FavoriteSearch.objects.filter(id=favorite_id).exists()
        self.assertFalse(delete_exists)

        delete_url = reverse.reverse("apps.log_search:favorite-detail", kwargs={"pk": favorite_id})
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        delete_result = json.loads(delete_response.content)
        self.assertFalse(delete_result["result"])
