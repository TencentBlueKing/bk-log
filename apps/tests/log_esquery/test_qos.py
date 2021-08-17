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
from collections import defaultdict
from unittest import TestCase
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.log_esquery.qos import build_qos_key, build_qos_limit_key, esquery_qos, qos_recover, QosThrottle


class FakeRedis:
    def __init__(self):
        self._zset = defaultdict(list)

    def get_value(self):
        return self._zset

    def zadd(self, key, mapping):
        for _key, value in mapping.items():
            self._zset[key].append((_key, value))

    def zrange(self, key, start, end, desc=True, withscores=True):
        self._zset[key].sort(key=lambda x: x[1], reverse=True)
        return self._zset[key][start:end]

    def delete(self, key):
        self._zset.pop(key)


class FakeCache:
    def __init__(self, *arg, **kwargs):
        self._dict = {}

    def has_key(self, key):
        return key in self._dict

    def set(self, key, value, timeout=0, nx=False):
        if nx and key in self._dict:
            return False
        self._dict[key] = value
        return True

    def delete(self, key):
        self._dict.pop(key, key)
        return True


fake_redis = FakeRedis()


@patch("django.core.cache.cache", FakeCache())
@patch("apps.log_esquery.qos.redis_client", fake_redis)
@patch("apps.log_search.permission.Permission.get_auth_info", return_value={"bk_app_code": "bk_monitorv3"})
class TestQos(TestCase):
    @override_settings(CACHES={"default": {"BACKEND": "apps.tests.log_esquery.test_qos.FakeCache"}})
    def test_throttle(self, *args, **kwargs):
        throttle = QosThrottle()
        index_set_request_1 = self._build_request(1)
        key = build_qos_key(index_set_request_1)
        esquery_qos(index_set_request_1)
        self.assertTrue(throttle.allow_request(index_set_request_1, None))
        esquery_qos(index_set_request_1)
        self.assertTrue(throttle.allow_request(index_set_request_1, None))
        esquery_qos(index_set_request_1)
        self.assertFalse(throttle.allow_request(index_set_request_1, None))
        self.assertEqual(len(fake_redis.get_value()[key]), 0)

    def test_recover(self, *args, **kwargs):
        index_set_request_1 = self._build_request(1)
        key = build_qos_key(index_set_request_1)
        # test not have exception
        esquery_qos(index_set_request_1)

        class FakeResponse(object):
            def __init__(self, exception=True):
                self.exception = exception

        self.assertEqual(len(fake_redis.get_value()[key]), 1)
        qos_recover(index_set_request_1, FakeResponse(False))
        self.assertEqual(len(fake_redis.get_value()[key]), 0)

        esquery_qos(index_set_request_1)
        self.assertEqual(len(fake_redis.get_value()[key]), 1)
        qos_recover(index_set_request_1, FakeResponse())
        self.assertEqual(len(fake_redis.get_value()[key]), 1)
        qos_recover(index_set_request_1, FakeResponse(False))

    def test_key_build(self, *args, **kwargs):
        index_set_request_1 = self._build_request(1)
        self.assertEqual(f"{settings.APP_CODE}_qos_/test_1", build_qos_key(index_set_request_1))
        index_set_request_indices = self._build_request(scenario_id="log", indices="index")
        self.assertEqual(f"{settings.APP_CODE}_qos_/test_log_index", build_qos_key(index_set_request_indices))
        self.assertEqual(
            f"{settings.APP_CODE}_qos_/test_log_index_limit", build_qos_limit_key(index_set_request_indices)
        )

    def _build_request(self, index_set_id=None, scenario_id="", indices=""):
        factory = APIRequestFactory()
        if index_set_id:
            request = factory.post("/test", {"index_set_id": index_set_id})
        else:
            request = factory.post("/test", {"indices": indices, "scenario_id": scenario_id})
        r = Request(request)
        r.parsers = (FormParser(), MultiPartParser())
        return r
