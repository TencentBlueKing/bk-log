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


from django.test import TestCase

from apps.log_search.handlers.search import aggs_handlers

SOURCE_HISTOGRAM_DICT = {
    "tags.result_code": {
        "labels": ["16:48", "16:49", "16:50", "16:51", "16:52", "16:53"],
        "datasets": [
            {"label": 904, "data": [{"label": "2021-06-22 11:10:00", "value": 1, "count": 0}]},
            {
                "label": 905,
                "data": [
                    {"label": "2021-06-22 11:10:00", "value": 1, "count": 1},
                    {"label": "2021-06-22 11:20:00", "value": 0, "count": 0},
                ],
            },
            {
                "label": 906,
                "data": [
                    {"label": "2021-06-22 11:10:00", "value": 0, "count": 0},
                    {"label": "2021-06-22 11:20:00", "value": 0, "count": 0},
                ],
            },
        ],
    }
}

DST_HISTOGRAM_DICT = {
    "tags.result_code": {
        "labels": ["16:48", "16:49", "16:50", "16:51", "16:52", "16:53"],
        "datasets": [
            {"label": 904, "data": [{"label": "2021-06-22 11:10:00", "value": 1, "count": 0}]},
            {
                "label": 905,
                "data": [
                    {"label": "2021-06-22 11:10:00", "value": 1, "count": 1},
                    {"label": "2021-06-22 11:20:00", "value": 0, "count": 0},
                ],
            },
        ],
    }
}


class TestAggsHandlers(TestCase):
    def setUp(self) -> None:
        self.aggs_view_adapter = aggs_handlers.AggsViewAdapter()

    def test_del_empty_histogram(self):
        print(self.aggs_view_adapter._del_empty_histogram(SOURCE_HISTOGRAM_DICT))
        self.assertEqual(self.aggs_view_adapter._del_empty_histogram(SOURCE_HISTOGRAM_DICT), DST_HISTOGRAM_DICT)
