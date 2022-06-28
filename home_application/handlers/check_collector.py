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
import sys

from apps.log_databus.models import CollectorConfig
from home_application.constants import CHECK_STORIES
from home_application.handlers.collector_checker import sc


class CollectorCheckHandler(object):
    status = False
    data = []
    steps = dict()

    def __init__(self, collector_config_id, hosts, debug):
        try:
            self.collector_config = CollectorConfig.objects.get(collector_config_id=collector_config_id)
        except CollectorConfig.DoesNotExist:
            print(f"不存在的采集项ID: {collector_config_id}")
            sys.exit(1)
        self.hosts = hosts
        self.debug = debug

    def run(self):
        self.data = sc.run()

    def command_format(self):
        is_success = "失败"
        if len(self.data) == CHECK_STORIES:
            is_success = "成功"
        print(f"\n采集项检查{is_success}\n\n")
        for story_m in self.data:
            print("-" * 100)
            icon = "[-]" if story_m.has_problem() else "[+]"
            print(f"{icon} {story_m.name}")
            for story_error in story_m.error:
                print(f"error: {story_error}")
            for story_warning in story_m.warning:
                print(f"warning: {story_warning}")
            if self.debug:
                for story_info in story_m.info:
                    print(story_info)
            print("")
