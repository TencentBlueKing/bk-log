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
import logging
import os
from contextlib import contextmanager

from django.conf import settings

logger = logging.getLogger("bk_dataview")


@contextmanager
def os_env(**kwargs):
    """临时修改环境变量"""
    _environ = os.environ.copy()

    # 添加settings变量
    for name in dir(settings):
        if not name.isupper():
            continue

        value = getattr(settings, name, "")
        # 环境变量只允许字符串
        if not isinstance(value, str):
            continue

        os.environ[f"SETTINGS_{name}"] = value

    # 添加自定义变量
    for k, v in kwargs.items():
        if not k.isupper():
            continue
        os.environ[k] = str(v)

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(_environ)


def requests_curl_log(resp, *args, **kwargs):
    """记录requests curl log"""
    # 添加日志信息
    curl_req = "REQ: curl -X {method} '{url}'".format(method=resp.request.method, url=resp.request.url)

    if resp.request.body:
        curl_req += " -d '{body}'".format(body=resp.request.body)

    if resp.request.headers:
        for key, value in resp.request.headers.items():
            # ignore headers
            if key in ["User-Agent", "Accept-Encoding", "Connection", "Accept", "Content-Length"]:
                continue
            if key == "Cookie" and value.startswith("x_host_key"):
                continue

            curl_req += " -H '{k}: {v}'".format(k=key, v=value)

    if resp.headers.get("Content-Type").startswith("application/json"):
        resp_text = resp.content
    else:
        resp_text = f"Bin...(total {len(resp.content)} Bytes)"

    curl_resp = "RESP: [{}] {:.2f}ms {}".format(resp.status_code, resp.elapsed.total_seconds() * 1000, resp_text)

    logger.info("%s\n \t %s", curl_req, curl_resp)
