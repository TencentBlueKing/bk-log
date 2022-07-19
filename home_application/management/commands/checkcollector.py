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
import os
from django.core.management.base import BaseCommand
from home_application.handlers.check_collector import CollectorCheckHandler


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--collector_config_id", type=str, default="", help="采集项ID")
        parser.add_argument("--hosts", type=str, default="", help="主机")
        parser.add_argument("--debug", type=bool, default=False, help="是否开启DEBUG")

    def handle(self, **options):
        collector_config_id = options.get("collector_config_id")
        hosts = options.get("hosts")
        debug = options.get("debug")
        os.system("clear")
        print("*" * 100)
        print("采集项健康状态检查工具\n")
        c = CollectorCheckHandler(collector_config_id=collector_config_id, hosts=hosts, debug=debug)
        c.run()
        c.command_format()
