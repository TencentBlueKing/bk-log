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
from django.test import TestCase

from blueking.component.utils import get_signature


class TestUtils(TestCase):
    def test_get_signature(self):
        params = {
            "method": "GET",
            "path": "/blueking/component/",
            "app_secret": "test",
            "params": {"p1": 1, "p2": "abc"},
        }
        signature = get_signature(**params)
        self.assertEqual(signature, "S73XVZx3HvPRcak1z3k7jUkA7FM=")

        params = {
            "method": "POST",
            "path": "/blueking/component/",
            "app_secret": "test",
            "data": {"p1": 1, "p2": "abc"},
        }
        # python3 could sort the dict
        signature = get_signature(**params)
        self.assertIn(signature, ["qTzporCDYXqaWKuk/MNUXPT3A5U=", "PnmqLk/8PVpsLHDFkolCQoi5lmg="])
