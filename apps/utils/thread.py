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

import threading

from apps.utils.local import get_request, activate_request


class FuncThread(threading.Thread):
    def __init__(self, func, params, result_key, results, use_request=True):
        self.func = func
        self.params = params
        self.result_key = result_key
        self.results = results
        self.use_request = use_request
        if use_request:
            self.requests = get_request()
        super().__init__()

    def run(self):
        if self.use_request:
            activate_request(self.requests)
        if self.params:
            self.results[self.result_key] = self.func(self.params)
        else:
            self.results[self.result_key] = self.func()


class MultiExecuteFunc(object):
    """
    基于多线程的批量并发执行函数
    """

    def __init__(self):
        self.results = {}
        self.task_list = []

    def append(self, result_key, func, params=None, use_request=True):
        if result_key in self.results:
            raise ValueError(f"result_key: {result_key} is duplicate. Please rename it.")
        task = FuncThread(
            func=func, params=params, result_key=result_key, results=self.results, use_request=use_request
        )
        self.task_list.append(task)
        task.start()

    def run(self):
        for task in self.task_list:
            task.join()
        return self.results
