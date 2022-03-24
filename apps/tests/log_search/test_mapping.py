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
from unittest.mock import patch

from apps.log_search.handlers.search.mapping_handlers import MappingHandlers
from apps.log_search.models import Scenario

INDICES = ""
INDEX_SET_ID = 0
SCENARIO_ID = ""
STORAGE_CLUSTER_ID = 1
TIME_FIELD = ""
START_TIME = ""
END_TIME = ""

BKDATA_ASYNC_FIELDS_LIST = [
    {"field_name": "dtEventTimeStamp", "es_doc_values": True},
    {"field_name": "ip", "es_doc_values": True},
    {"field_name": "gseindex", "es_doc_values": True},
    {"field_name": "_iteration_idx", "es_doc_values": True},
]

BKDATA_CONTAINER_ASYNC_FIELDS_LIST = [
    {"field_name": "dtEventTimeStamp", "es_doc_values": True},
    {"field_name": "container_id", "es_doc_values": True},
    {"field_name": "gseindex", "es_doc_values": True},
    {"field_name": "_iteration_idx", "es_doc_values": True},
]

LOG_ASYNC_FIELDS_LIST = [
    {"field_name": "dtEventTimeStamp", "es_doc_values": True},
    {"field_name": "serverIp", "es_doc_values": True},
    {"field_name": "gseIndex", "es_doc_values": True},
    {"field_name": "iterationIndex", "es_doc_values": True},
]

FAILED_LOG_ASYNC_FIELDS = [
    {"field_name": "dtEventTimeStamp", "es_doc_values": True},
    {"field_name": "serverIp", "es_doc_values": True},
    {"field_name": "gseindex", "es_doc_values": True},
]


class TestMappingHandler(TestCase):
    def setUp(self) -> None:
        self.mapping_handlers = MappingHandlers(
            indices=INDICES,
            index_set_id=INDEX_SET_ID,
            scenario_id=SCENARIO_ID,
            storage_cluster_id=STORAGE_CLUSTER_ID,
            time_field=TIME_FIELD,
            start_time=START_TIME,
            end_time=END_TIME,
        )

    def test_generate_async_export_reason(self):
        self.assertEqual(
            "缺少必备字段: dtEventTimeStamp, ip, gseindex, _iteration_idx or dtEventTimeStamp,"
            + " container_id, gseindex, _iteration_idx",
            MappingHandlers._generate_async_export_reason(Scenario.BKDATA, {})["async_export_usable_reason"],
        )
        self.assertEqual(
            "缺少必备字段: dtEventTimeStamp, serverIp, gseIndex, iterationIndex",
            MappingHandlers._generate_async_export_reason(Scenario.LOG, {})["async_export_usable_reason"],
        )

    @patch("apps.feature_toggle.handlers.toggle.FeatureToggleObject.switch", lambda _: True)
    def test_async_export_fields(self):
        self.assertTrue(
            MappingHandlers.async_export_fields(BKDATA_ASYNC_FIELDS_LIST, Scenario.BKDATA)["async_export_usable"]
        )
        self.assertTrue(
            MappingHandlers.async_export_fields(BKDATA_CONTAINER_ASYNC_FIELDS_LIST, Scenario.BKDATA)[
                "async_export_usable"
            ]
        )
        self.assertTrue(MappingHandlers.async_export_fields(LOG_ASYNC_FIELDS_LIST, Scenario.LOG)["async_export_usable"])
        self.assertTrue(MappingHandlers.async_export_fields([], Scenario.ES)["async_export_usable"])

        self.assertFalse(
            MappingHandlers.async_export_fields(FAILED_LOG_ASYNC_FIELDS, Scenario.LOG)["async_export_usable"]
        )
