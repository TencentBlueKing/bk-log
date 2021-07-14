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
from datetime import timedelta
from unittest.mock import MagicMock

from django.test import TestCase
from django.utils import timezone

from apps.log_extract.constants import DownloadStatus
from apps.log_extract.models import Tasks
from apps.log_extract.utils.packing import get_packed_dir_name
from apps.log_extract.components.collections.distribution_component import (
    FileDistributionComponent,
)
from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)


class HostPatch(object):
    def __init__(self):
        self.ip = "1.1.1.1"
        self.bk_cloud_id = 1

    def all(self):
        return [self]


class LinkPatch(object):
    patch_target = "apps.log_extract.models.ExtractLink.objects.filter"

    def __init__(self):
        self.extractlinkhost_set = HostPatch()


class FileDistributionComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be tested
        return FileDistributionComponent

    def cases(self):
        BASE_URL = "apps.log_extract.components.collections.distribution_component"
        FILE_DISTRIBUTION = BASE_URL + ".FileServer.file_distribution"
        success_task_instance = {
            "job_instance_id": 123,
            "job_instance_name": "[BKLOG] File Distribution By admin",
        }

        QUERY_TASK_RESULT = BASE_URL + ".FileServer.query_task_result"
        success_task_result = [
            {
                "status": 3,
                "step_results": [
                    {
                        "tag": "",
                        "ip_logs": [
                            {
                                "total_time": 2.63,
                                "ip": "127.0.0.1",
                                "start_time": "2021-01-06 11:32:00",
                                "log_content": "",
                                "exit_code": None,
                                "bk_cloud_id": 0,
                                "end_time": "2021-01-06 11:32:02",
                                "execute_count": 0,
                                "error_code": 0,
                            }
                        ],
                        "ip_status": 9,
                    }
                ],
                "is_finished": True,
                "step_instance_id": 20036358108,
                "name": "[BKLOG] File Distribution By admin",
            }
        ]

        params = {
            "task_id": 123,
            "bk_biz_id": 111,
            "ip_list": ["1:1.1.1.1"],
            "file_path": ["/data/test"],
            "filter_type": "match_word",
            "filter_content": {},
            "download_status": DownloadStatus.INIT.value,
            "expiration_date": timezone.now() + timedelta(days=1),
            "remark": "test",
            "preview_directory": "/data",
            "preview_ip": "1.1.11.1",
            "preview_time_range": "1d",
            "preview_is_search_child": True,
        }
        link_objects = MagicMock()
        test_link = LinkPatch()
        link_objects.return_value.first.return_value = test_link

        Tasks.objects.create(**params)
        return [
            ComponentTestCase(
                patchers=[
                    Patcher(target=FILE_DISTRIBUTION, return_value=success_task_instance),
                    Patcher(target=QUERY_TASK_RESULT, return_value=success_task_result),
                    Patcher(target=LinkPatch.patch_target, side_effect=link_objects),
                ],
                name="success case",
                inputs={
                    "task_id": "123",
                    "username": "/data/home/",
                    "bk_biz_id": 111,
                    "operator": "admin",
                    "account": "admin",
                    "file_source_list": [],
                },
                parent_data={},
                execute_assertion=ExecuteAssertion(
                    success=True,
                    outputs={
                        "task_instance_id": 123,
                        "distribution_ip": test_link.extractlinkhost_set.all(),
                        "transit_server_file_path": [get_packed_dir_name("/data/bk_log_extract/distribution/", 123)],
                        "transit_server_packing_file_path": "/data/bk_log_extract/distribution_packing/",
                    },
                ),
                schedule_assertion=[
                    ScheduleAssertion(
                        success=True,
                        outputs={
                            "task_instance_id": 123,
                            "distribution_ip": test_link.extractlinkhost_set.all(),
                            "transit_server_file_path": [
                                get_packed_dir_name("/data/bk_log_extract/distribution/", 123)
                            ],
                            "transit_server_packing_file_path": "/data/bk_log_extract/distribution_packing/",
                        },
                        schedule_finished=True,
                    ),
                ],
            ),
        ]
