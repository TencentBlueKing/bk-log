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
from abc import ABC, abstractmethod

from apps.log_databus.handlers.check_collector.base import CheckCollectorRecord


class Checker(ABC):
    CHECKER_NAME = ""

    def __init__(self, check_collector_record: CheckCollectorRecord):
        self.record = check_collector_record

    @abstractmethod
    def _run(self):
        raise NotImplementedError

    def run(self):
        self._run()

    def append_normal_info(self, info: str):
        self.record.append_normal_info(info=info, prefix=self.CHECKER_NAME)

    def append_warning_info(self, info: str):
        self.record.append_warning_info(info=info, prefix=self.CHECKER_NAME)

    def append_error_info(self, info: str):
        self.record.append_error_info(info=info, prefix=self.CHECKER_NAME)
