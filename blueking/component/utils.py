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
import json
import base64
import hmac
import hashlib

from .compat import str


def get_signature(method, path, app_secret, params=None, data=None):
    """generate signature"""
    kwargs = {}
    if params:
        kwargs.update(params)
    if data:
        data = json.dumps(data) if isinstance(data, dict) else data
        kwargs["data"] = data
    kwargs = "&".join(["{}={}".format(k, v) for k, v in sorted(kwargs.items(), key=lambda x: x[0])])
    orignal = "{}{}?{}".format(method, path, kwargs)
    app_secret = app_secret.encode("utf-8") if isinstance(app_secret, str) else app_secret
    orignal = orignal.encode("utf-8") if isinstance(orignal, str) else orignal
    signature = base64.b64encode(hmac.new(app_secret, orignal, hashlib.sha1).digest())
    return signature if isinstance(signature, str) else signature.decode("utf-8")
