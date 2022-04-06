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
import logging
import sys

from blueapps.account.models import User

from apps.log_search.handlers.result_table import ResultTableHandler
from apps.utils.local import _local
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.log_search.exceptions import (
    MappingEmptyException,
    IndexDuplicateException,
    FieldsDateNotSameException,
    FieldsDateTypeNotSameException,
)
from apps.log_search.views.result_table_views import ResultTablesViewSet

logger = logging.getLogger("root")

BK_BIZ_ID = 2
SCENARIO_ID_ROW = "row"
SCENARIO_ID_ES = "es"
STORAGE_CLUSTER_ID = 1
RESULT_TABLE_ID = "2_bklog.test3333"
SUCCESS_STATUS_CODE = 200

PARAMS = {"bk_biz_id": BK_BIZ_ID, "page": 1, "pagesize": 2, "keyword": ""}

OVERRIDE_MIDDLEWARE = "apps.tests.middlewares.OverrideMiddleware"

RESULT_TABLE = [{"result_table_id": RESULT_TABLE_ID, "result_table_name_alias": "中文名称"}]

RESULT_TABLE_ITEM = {
    "date_candidate": [{"field_name": "date", "field_type": "date"}, {"field_name": "server_id", "field_type": "long"}],
    "fields": [],
    "storage_cluster_id": STORAGE_CLUSTER_ID,
    "storage_cluster_name": "",
    "bk_biz_id": BK_BIZ_ID,
}

MAPPING_LIST = [{"properties": {"date": {"type": "date"}, "log": {"type": "string"}, "server_id": {"type": "long"}}}]

CLUSTER_INFO = {"storage_cluster_id": STORAGE_CLUSTER_ID, "storage_cluster_name": "", "bk_biz_id": BK_BIZ_ID}

ADAPT_RESULT = {"message": "", "code": 0, "data": True, "result": True}


ADAPT_RESULT_TABLE_DATA = {
    "scenario_id": SCENARIO_ID_ES,
    "storage_cluster_id": STORAGE_CLUSTER_ID,
    "basic_indices": [{"index": "591_abc", "time_field": "dtEventTime", "time_field_type": "date"}],
    "append_index": {"index": "591_xxx", "time_field": "dtEventTime", "time_field_type": "date"},
}

LIST_RESULT_TABLE_FIELDS_DATA = {
    "result_table_id": RESULT_TABLE_ID,
    "scenario_id": SCENARIO_ID_ROW,
    "storage_cluster_id": STORAGE_CLUSTER_ID,
}


class TestResultTable(TestCase):
    """
    测试 ResultTablesViewSet 中的接口
    """

    def setUp(self) -> None:
        if User.objects.filter(username="admin").exists():
            return
        User.objects.create_superuser(username="admin")

    @patch("apps.api.BkLogApi.indices", return_value=RESULT_TABLE)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_list_result_tables(self, *args, **kwargs):
        """
        测试 api.v1.result_table
        """
        path = "/api/v1/result_table/"

        data = {
            "scenario_id": SCENARIO_ID_ROW,
            "bk_biz_id": BK_BIZ_ID,
            "storage_cluster_id": STORAGE_CLUSTER_ID,
            "result_table_id": RESULT_TABLE_ID,
        }

        response = self.client.get(path=path, data=data)

        content = json.loads(response.content)
        logger.info(" {func_name}:{content}".format(func_name=sys._getframe().f_code.co_name, content=content))
        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.assertEqual(content["data"], RESULT_TABLE)

    @patch("apps.api.BkLogApi.cluster", return_value=CLUSTER_INFO)
    @patch("apps.api.BkLogApi.mapping", return_value=MAPPING_LIST)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_list_result_table_fields(self, *args, **kwargs):
        """
        测试 api.v1.result_table.$result_table_id
        """
        # 拼接path
        path = "/api/v1/result_table/"
        result_table_id = RESULT_TABLE_ID
        params = {"scenario_id": SCENARIO_ID_ROW, "storage_cluster_id": STORAGE_CLUSTER_ID}

        path += (
            result_table_id + "/?" + "&".join(["=".join(list(map(str, [item[0], item[1]]))) for item in params.items()])
        )

        response = self.client.get(path=path)
        content = json.loads(response.content)
        logger.info(" {func_name}:{content}".format(func_name=sys._getframe().f_code.co_name, content=content))

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        date_candidate = content["data"]["date_candidate"]
        content["data"]["date_candidate"] = sorted(date_candidate, key=lambda x: x["field_name"])
        self.assertEqual(content["data"], RESULT_TABLE_ITEM)

    @patch(
        "apps.log_search.views.result_table_views.ResultTablesViewSet.params_valid",
        return_value=LIST_RESULT_TABLE_FIELDS_DATA,
    )
    @patch("apps.api.BkLogApi.mapping", return_value=[])
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_list_result_table_fields_exception(self, *args, **kwargs):
        """
        测试 api.v1.result_table.$result_table_id 中的异常

        """

        with self.assertRaises(MappingEmptyException):
            data = LIST_RESULT_TABLE_FIELDS_DATA
            ResultTableHandler(data["scenario_id"], data["storage_cluster_id"]).retrieve(data["result_table_id"])

    @patch("apps.api.BkLogApi.cluster", return_value=CLUSTER_INFO)
    @patch("apps.api.BkLogApi.mapping", return_value=MAPPING_LIST)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_adapt_result_table(self, *args, **kwargs):
        """
        测试 api.v1.result_table.adapt
        """

        path = "/api/v1/result_table/adapt/"

        response = self.client.post(
            path=path, data=json.dumps(ADAPT_RESULT_TABLE_DATA), content_type="application/json"
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.assertEqual(content, ADAPT_RESULT)

    @patch(
        "apps.log_search.views.result_table_views.ResultTablesViewSet.params_valid",
        return_value=ADAPT_RESULT_TABLE_DATA,
    )
    @patch("apps.api.BkLogApi.mapping", return_value=MAPPING_LIST)
    @patch("apps.api.BkLogApi.cluster", return_value={})
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_adapt_result_table_exception(self, *args, **kwargs):
        """
        测试 api.v1.result_table.adapt 中的异常
        """

        def get_request(self, data):
            self.client.post(path=path, data=json.dumps(data), content_type="application/json")

            return _local.request

        path = "/api/v1/result_table/adapt/"

        """
        测试 IndexDuplicateException
        """
        exception_data = ADAPT_RESULT_TABLE_DATA
        exception_data.update(
            {"append_index": {"index": "591_abc", "time_field": "dtEventTime", "time_field_type": "date"}}
        )
        request = get_request(self, exception_data)

        with self.assertRaises(IndexDuplicateException):
            ResultTablesViewSet().adapt(request)

        """
        测试 FieldsDateNotSameException
        """
        exception_data = ADAPT_RESULT_TABLE_DATA
        exception_data.update(
            {"append_index": {"index": "591_xxx", "time_field": "NoDtEventTime", "time_field_type": "date"}}
        )
        request = get_request(self, exception_data)

        with self.assertRaises(FieldsDateNotSameException):
            ResultTablesViewSet().adapt(request)

        """
        测试 FieldsDateTypeNotSameException
        """
        exception_data = ADAPT_RESULT_TABLE_DATA

        exception_data.update(
            {"append_index": {"index": "591_xxx", "time_field": "dtEventTime", "time_field_type": "NotDate"}}
        )
        request = get_request(self, exception_data)

        with self.assertRaises(FieldsDateTypeNotSameException):
            ResultTablesViewSet().adapt(request)
