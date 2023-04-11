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
from django.utils.http import urlencode
from rest_framework.reverse import reverse

from apps.log_extract.handlers.explorer import ExplorerHandler
from apps.log_extract.handlers.tasks import TasksHandler
from apps.log_extract.models import Strategies, Tasks, ExtractLink
import random
from apps.log_extract import constants
from apps.tests.log_extract import test_explorer
from apps.utils.base_crypt import BaseCrypt
from apps.utils.local import get_request

BK_BIZ_ID = 215
USER = "admin"
BASE_URL = "/api/v1/log_extract/tasks"

IP_SET = {
    "linux01_linux": {"ip": "1.1.1.1", "bk_cloud_id": 0},  # linux
    "linux02_linux": {"ip": "1.1.1.2", "bk_cloud_id": 0},  # linux
    "windows_windows": {"ip": "1.1.1.3", "bk_cloud_id": 0},  # windows
    "temporary_temporary": {"ip": "1.1.1.4", "bk_cloud_id": 0},  # linux
}
STRATEGIES_LIST = [
    {
        "strategy_name": "test1-1",
        "user_list": [USER],
        "bk_biz_id": BK_BIZ_ID,
        "select_type": "module",
        "modules": [{"bk_inst_id": 0, "bk_inst_name": "linux", "bk_obj_id": "module", "bk_biz_id": "215"}],
        "visible_dir": ["/data/logs/"],
        "file_type": ["log"],
        "operator": USER,
    }
]
ALLOWED_FILTER_TYPES = ["line_range", "match_word", "tail_line", "match_range"]
FILTER_CONTENT = {
    "line_range": {"start_line": 0, "end_line": 1},
    "match_word": {"keyword": "test_word"},
    "tail_line": {"line_num": 1},
    "match_range": {"start": "word1", "end": "word2"},
}

CLONE_PARAM = {
    "preview_directory": "/data/",
    "preview_ip_list": [{"ip": "1.1.1.1", "bk_cloud_id": 0}],
    "preview_time_range": "1d",
    "preview_is_search_child": True,
}

CREATE_PARAMS_LIST = [
    {
        "bk_biz_id": BK_BIZ_ID,
        "ip_list": [IP_SET["linux01_linux"], IP_SET["linux02_linux"]],
        "file_path": ["/data/logs/a.log", "/data/logs/a.log"],
        "filter_type": "line_range",
        "filter_content": {},
    },
    {
        "bk_biz_id": BK_BIZ_ID,
        "ip_list": [IP_SET["linux01_linux"], IP_SET["linux02_linux"]],
        "file_path": ["/data/"],
        "filter_type": "tail_line",
        "filter_content": {},
    },
    {
        "bk_biz_id": BK_BIZ_ID,
        "ip_list": [IP_SET["linux02_linux"]],
        "file_path": ["/data/non-accessible_dir/non-accessible_file.file"],
        "filter_type": "match_word",
        "filter_content": {},
    },
    {
        "bk_biz_id": BK_BIZ_ID,
        "ip_list": [IP_SET["windows_windows"]],
        "file_path": ["/data/logs/a.log"],
        "filter_type": "match_range",
        "filter_content": {},
    },
]
CREATE_RESULT = [
    {"result": True},
    {"result": False, "code": "3626500"},
    {"result": False, "code": "3626500"},
    {"result": False, "code": "3626500"},
]


class PipelineMock(object):
    def __init__(self):
        self.result = 1


class TestTasks(TestCase):
    def setUp(self, *args, **kwargs):
        self.explorer = ExplorerHandler()
        self.tasks = TasksHandler()
        ExtractLink.objects.create(name="test", link_id=1, link_type="common", operator="admin", op_bk_biz_id=1)

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    @patch("apps.log_extract.handlers.explorer.ExplorerHandler.get_module_by_ip")
    @patch("apps.log_extract.handlers.tasks.task_service.run_pipeline")
    @patch("apps.log_extract.handlers.explorer.get_request_username")
    def test_create(self, get_request_username, run_pipeline, get_module_by_ip, *args, **kwargs):
        Strategies.objects.create(**STRATEGIES_LIST[0])
        request_path = BASE_URL + "/"
        get_request_username.return_value = USER
        task_list = []
        run_pipeline.return_value = PipelineMock()
        for index, params in enumerate(CREATE_PARAMS_LIST):
            params["filter_type"] = ALLOWED_FILTER_TYPES[random.randint(0, 3)]
            params["filter_content"] = FILTER_CONTENT[params["filter_type"]]
            params["link_id"] = 1
            params.update(CLONE_PARAM)
            host_info_list = []
            for ip in params["ip_list"]:
                host_info_list.append(test_explorer.TOPO_SET[ip["ip"]])
            get_module_by_ip.return_value = host_info_list
            data = json.dumps(params)
            response = self.client.post(request_path, data=data, content_type="application/json")
            content = json.loads(response.content)
            self.assertEqual(content["result"], CREATE_RESULT[index]["result"])
            if content["result"]:
                task_list.append(content["data"]["task_id"])
            if not content["result"]:
                self.assertEqual(content["code"], CREATE_RESULT[index]["code"])
        return task_list

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    @patch("apps.log_extract.handlers.tasks.TasksHandler.is_operator_or_creator")
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    def test_download(self, is_operator_or_creator, *args, **kwargs):
        task_list = self.test_create()
        Tasks.objects.filter(task_id__in=task_list).update(
            download_status=constants.DownloadStatus.DOWNLOADABLE.value, cos_file_name="test_file"
        )
        is_operator_or_creator.return_value = True
        for task_id in task_list:
            download_url = self.tasks.download(task_id)
            url_params = {"target_file": BaseCrypt().encrypt(b"test_file")}
            url_params = urlencode(url_params)
            url = reverse("tasks-download-file", request=get_request())
            self.assertEqual(f"{url}?{url_params}", download_url)
