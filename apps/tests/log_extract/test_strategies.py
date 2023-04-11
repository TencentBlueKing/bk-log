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

from django.test import TestCase, override_settings
from django.conf import settings

from apps.log_extract.models import Strategies
from apps.tests.log_extract import test_explorer
from apps.utils.local import activate_request

USER = "admin"
BK_BIZ_ID = 100605
BASE_URL = "/api/v1/log_extract/strategies"
STRATEGIES_LIST_RESULT = {
    "result": True,
    "data": [
        {
            "strategy_id": 1,
            "strategy_name": "test1-1",
            "user_list": [USER],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "topo",
            "modules": [
                {"bk_inst_id": 2000000991, "bk_inst_name": "linux01", "bk_obj_id": "module", "bk_biz_id": "215"}
            ],
            "visible_dir": ["/data/logs/linux/"],
            "file_type": ["linux1"],
            "operator": USER,
            "created_at": 1,
            "created_by": USER,
            "updated_at": 1,
            "updated_by": USER,
        },
    ],
    "code": 0,
    "message": "",
}

PAGINATE_PARAMS = {"bk_biz_id": BK_BIZ_ID}

STRATEGIES_CREATE_PARAMS = {
    "strategy_name": "test1-1",
    "user_list": [USER],
    "visible_dir": ["/data/logs/linux/"],
    "file_type": ["linux1"],
    "select_type": "topo",
    "modules": [{"bk_inst_id": 2000000991, "bk_inst_name": "linux01", "bk_obj_id": "module", "bk_biz_id": "215"}],
    "bk_biz_id": BK_BIZ_ID,
    "operator": USER,
}


@patch("apps.iam.handlers.drf.BusinessActionPermission.has_permission")
class TestStrategies(TestCase):
    def setUp(self, *args, **kwargs):
        activate_request(test_explorer.Request())

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    @patch("apps.log_extract.handlers.explorer.get_request_username")
    @patch(
        "apps.log_extract.handlers.explorer.ExplorerHandler.get_module_by_ip",
        return_value=[{"bk_inst_id": 2000000991, "bk_inst_name": "linux01", "bk_obj_id": "module", "bk_biz_id": "215"}],
    )
    def test_list(self, get_request_username, *args, **kwargs):
        get_request_username.return_value = USER
        strategy = Strategies.objects.create(**STRATEGIES_CREATE_PARAMS)
        updated_at = strategy.updated_at.strftime(settings.REST_FRAMEWORK["DATETIME_FORMAT"] + "+0800")
        created_at = strategy.created_at.strftime(settings.REST_FRAMEWORK["DATETIME_FORMAT"] + "+0800")
        STRATEGIES_LIST_RESULT["data"][0].update({"updated_at": updated_at})
        STRATEGIES_LIST_RESULT["data"][0].update({"created_at": created_at})
        STRATEGIES_LIST_RESULT["data"][0].update({"strategy_id": strategy.strategy_id})
        request_path = BASE_URL + "/"
        response = self.client.get(request_path, data=PAGINATE_PARAMS)
        content = json.loads(response.content)
        for index, strategy in enumerate(STRATEGIES_LIST_RESULT["data"]):
            self.assertEqual(content["data"][index]["modules"], STRATEGIES_LIST_RESULT["data"][index]["modules"])
            self.assertEqual(
                content["data"][index]["visible_dir"], STRATEGIES_LIST_RESULT["data"][index]["visible_dir"]
            )
            self.assertEqual(content["data"][index]["file_type"], STRATEGIES_LIST_RESULT["data"][index]["file_type"])

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    @patch("apps.log_search.handlers.meta.MetaHandler.get_user", lambda: {"operator": USER})
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    @patch(
        "apps.log_extract.handlers.explorer.ExplorerHandler.get_module_by_ip",
        return_value=[{"bk_inst_id": 2000000991, "bk_inst_name": "linux01", "bk_obj_id": "module", "bk_biz_id": "215"}],
    )
    @patch("apps.iam.handlers.drf.BusinessActionPermission.has_permission", return_value=True)
    def test_create(self, *args, **kwargs):
        request_path = BASE_URL + "/"
        data = json.dumps(STRATEGIES_CREATE_PARAMS)
        response = self.client.post(path=request_path, data=data, content_type="application/json")
        content = json.loads(response.content)
        self.assertEqual(content["result"], True)

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    def test_destroy(self, destroy, *args, **kwargs):
        strategy = Strategies.objects.create(
            bk_biz_id=100605,
            strategy_name="test_strategy",
            user_list=[USER],
            select_type="topo",
            modules=[{"bk_inst_id": 100605, "bk_inst_name": "CC3.0 test", "bk_obj_id": "biz", "bk_biz_id": 100605}],
            visible_dir=["/data/test/log/biz_100605"],
            file_type=["log"],
            created_by=USER,
            updated_by=USER,
        )
        destroy.return_value = True
        request_path = BASE_URL + "/" + str(strategy.strategy_id) + "/"
        response = self.client.delete(path=request_path)
        content = json.loads(response.content)
        self.assertEqual(content["result"], True)
