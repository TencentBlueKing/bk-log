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
from django.core.management.base import BaseCommand
from home_application.handlers.healthz import HealthzHandler
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--include", type=str, default="", help="include namespaces")
        parser.add_argument("--exclude", type=str, default="", help="exclude namespaces")

    def handle(self, **options):
        include_namespaces = options.get("include")
        if include_namespaces:
            include_namespaces = include_namespaces.split(",")
        else:
            include_namespaces = []
        exclude_namespaces = options.get("exclude")
        if exclude_namespaces:
            exclude_namespaces = exclude_namespaces.split(",")
        else:
            exclude_namespaces = []
        print(_("\n开始healthz检查, 预计等待1分钟\n"))
        print(
            HealthzHandler().get_data(
                format_type="console", include_namespaces=include_namespaces, exclude_namespaces=exclude_namespaces
            )
        )
