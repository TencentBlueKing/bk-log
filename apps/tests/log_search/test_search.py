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
import arrow

from django.test import TestCase
from unittest.mock import patch

from apps.log_search.constants import LOG_ASYNC_FIELDS
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler

INDEX_SET_ID = 0
SEARCH_DICT = {"size": 100000}

HITS = [
    {
        "_index": "v2_215_bklog_test_samuel_0527010_20210527_1",
        "_source": {
            "dtEventTimeStamp": str(int(arrow.now().float_timestamp * 1000)),
            "gseIndex": 1111,
            "iterationIndex": 0,
            "log": "Mon Jun  7 17:08:41 CST 2021",
            "path": "/tmp/samuel_test/out.txt",
            "serverIp": "127.0.0.1",
            "target_day": "",
            "target_month": "Jun",
            "target_time": "7",
            "target_week": "Mon",
            "target_year": "CST",
            "target_zone": "17:08:41",
            "time": str(int(arrow.now().float_timestamp * 1000)),
        },
    }
    for x in range(10000)
]

SEARCH_RESULT = {
    "took": 100,
    "_scroll_id": str(int(arrow.now().float_timestamp * 1000)),
    "hits": {
        "hits": HITS,
        "total": 100000,
    },
}


@patch(
    "apps.log_search.handlers.search.mapping_handlers.MappingHandlers.is_nested_field",
    lambda _, __: False,
)
@patch("apps.utils.core.cache.cmdb_host.CmdbHostCache.get", lambda _, __: {})
class TestSearchHandler(TestCase):
    @patch(
        "apps.log_search.handlers.search.mapping_handlers.MappingHandlers.is_nested_field",
        lambda _, __: False,
    )
    @patch(
        "apps.log_search.handlers.search.mapping_handlers.MappingHandlers.get_all_fields_by_index_id",
        lambda _: ([], []),
    )
    @patch(
        "apps.log_search.handlers.search.search_handlers_esquery.SearchHandler._init_indices_str",
        lambda _, index_set_id: "",
    )
    @patch(
        "apps.log_search.handlers.search.search_handlers_esquery.SearchHandler._init_time_field",
        lambda _, index_set_id, scenario_id: ("dtEventTimeStamp", "time", "s"),
    )
    @patch(
        "apps.log_search.handlers.search.mapping_handlers.MappingHandlers._get_time_field", lambda _: "dtEventTimeStamp"
    )
    def setUp(self) -> None:
        self.search_handler = SearchHandler(index_set_id=INDEX_SET_ID, search_dict=SEARCH_DICT, pre_check_enable=False)

    @patch("apps.api.BkLogApi.search", lambda _, data_api_retry_cls: SEARCH_RESULT)
    @patch(
        "apps.log_search.handlers.search.mapping_handlers.MappingHandlers.is_nested_field",
        lambda _, __: False,
    )
    def test_search_after_result(self):
        search_after_result = self.search_handler.search_after_result(
            search_result=SEARCH_RESULT, sorted_fields=LOG_ASYNC_FIELDS
        )

        logs_result = []
        for result in search_after_result:
            logs_result.extend(result["list"])
        self.assertEqual(len(logs_result), 90000)

    @patch("apps.api.BkLogApi.scroll", lambda _, data_api_retry_cls: SEARCH_RESULT)
    @patch(
        "apps.log_search.handlers.search.mapping_handlers.MappingHandlers.is_nested_field",
        lambda _, __: False,
    )
    def test_scroll_result(self):
        scroll_result = self.search_handler.scroll_result(scroll_result=SEARCH_RESULT)

        logs_result = []
        for result in scroll_result:
            logs_result.extend(result["list"])

        self.assertEqual(len(logs_result), 90000)
