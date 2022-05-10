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
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.log_extract.constants import DownloadStatus
from apps.log_extract.models import Tasks
from apps.log_extract.utils.packing import get_packed_dir_name, get_packed_file_name
from apps.log_extract.components.collections.packing_component import FilePackingComponent
from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)


class FilePackingComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be tested
        return FilePackingComponent

    def cases(self):
        BASE_URL = "apps.log_extract.components.collections.packing_component"
        EXECUTE_SCRIPT = BASE_URL + ".FileServer.execute_script"
        success_task_instance = {
            "job_instance_id": 123,
            "job_instance_name": "[BKLOG] Packing File By admin",
            "step_instance_id": 20036358098,
        }
        QUERY_TASK_RESULT = BASE_URL + ".FileServer.query_task_result"
        success_task_result = [
            {
                "status": 3,
                "step_results": [
                    {
                        "tag": "packing done",
                        "ip_logs": [
                            {
                                "total_time": 0.552,
                                "ip": "127.0.0.1",
                                "start_time": "2021-01-06 11:31:56",
                                "log_content": "xxxx",
                                "exit_code": 0,
                                "bk_cloud_id": 0,
                                "end_time": "2021-01-06 11:31:57",
                                "execute_count": 0,
                                "error_code": 0,
                            },
                            {
                                "total_time": 0.233,
                                "ip": "127.0.0.1",
                                "start_time": "2021-01-06 11:31:56",
                                "log_content": "xxxx",
                                "exit_code": 0,
                                "bk_cloud_id": 0,
                                "end_time": "2021-01-06 11:31:56",
                                "execute_count": 0,
                                "error_code": 0,
                            },
                        ],
                        "ip_status": 9,
                    }
                ],
                "is_finished": True,
                "step_instance_id": 20036358098,
                "name": "[BKLOG] Packing File By admin",
            }
        ]

        params = {
            "task_id": 111,
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
        Tasks.objects.create(**params)

        return [
            ComponentTestCase(
                patchers=[
                    Patcher(target=EXECUTE_SCRIPT, return_value=success_task_instance),
                    Patcher(target=QUERY_TASK_RESULT, return_value=success_task_result),
                ],
                name="success case",
                inputs={
                    "task_id": 111,
                    "packaging_dst_path": "/data/home/",
                    "file_path": ["/data/test/log1", "/data/test/log2"],
                    "ip_list": [{"ip": "1.1.1.1", "bk_cloud_id": "0"}, {"ip": "2.2.2.2", "bk_cloud_id": "0"}],
                    "bk_biz_id": 111,
                    "account": "root",
                    "is_filter": True,
                    "filter_type": "match_word",
                    "filter_content": {"keyword": "1"},
                    "input_is_distribution": True,
                },
                parent_data={},
                execute_assertion=ExecuteAssertion(
                    success=True,
                    outputs={
                        "task_instance_id": 123,
                        "distribution_source_file_list": [
                            {
                                "group_ids": "",
                                "account": "root",
                                "ip_list": [ip],
                                "files": [get_packed_dir_name("/tmp/bk_log_extract/", 111) + get_packed_file_name(111)],
                            }
                            for ip in [{"ip": "1.1.1.1", "bk_cloud_id": "0"}, {"ip": "2.2.2.2", "bk_cloud_id": "0"}]
                        ],
                    },
                ),
                schedule_assertion=[
                    ScheduleAssertion(
                        success=True,
                        outputs={
                            "task_instance_id": 123,
                            "distribution_source_file_list": [
                                {
                                    "group_ids": "",
                                    "account": "root",
                                    "ip_list": [ip],
                                    "files": [
                                        get_packed_dir_name("/tmp/bk_log_extract/", 111) + get_packed_file_name(111)
                                    ],
                                }
                                for ip in [{"ip": "1.1.1.1", "bk_cloud_id": "0"}, {"ip": "2.2.2.2", "bk_cloud_id": "0"}]
                            ],
                            "task_script_output": "xxxx",
                        },
                        schedule_finished=True,
                    ),
                ],
            )
        ]
