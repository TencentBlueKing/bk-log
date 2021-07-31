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
import functools
import json

from opentelemetry.instrumentation.django import _DjangoMiddleware
from opentelemetry.sdk.trace import Span


def _patch_instrumentation_django():
    if hasattr(_DjangoMiddleware, "process_view"):
        setattr(_DjangoMiddleware, "process_view", lambda _, __, ___, ____, _____: None)

    process_response = getattr(_DjangoMiddleware, "process_response")

    @functools.wraps(process_response)
    def wrap_process_response(*args, **kwargs):
        this, request, response = args
        cur_span: Span = request.META[this._environ_span_key]
        if hasattr(response, "data"):
            result = response.data
        else:
            try:
                result = json.loads(response.content)
            except Exception:  # pylint: disable=broad-except
                return process_response(*args, **kwargs)
        cur_span.set_attribute("result_code", result.get("code", 0))
        cur_span.set_attribute("error", not result.get("result", True))
        cur_span.set_attribute("result_message", result.get("message", ""))
        return process_response(*args, **kwargs)

    setattr(_DjangoMiddleware, "process_response", wrap_process_response)


def patch():
    _patch_instrumentation_django()
