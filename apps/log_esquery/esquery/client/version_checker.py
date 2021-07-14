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

import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
import json

from apps.log_esquery.exceptions import UnKnowEsVersionException
from apps.utils.log import logger


class EsVersionChecker(object):
    def __init__(self, ip: str, port: str, username: str = None, password: str = None):
        self.default_number = "7.0.0"
        self._version: str = self.check_version(ip, port, username, password)

    def check_version(self, ip: str, port: str, username: str, password: str) -> str:
        url: str = "http://{}:{}".format(ip, port)
        auth: HTTPBasicAuth = HTTPBasicAuth(username=username, password=password)
        try:
            s = requests.Session()
            s.mount("http://", HTTPAdapter(max_retries=3))
            response = s.get(url, auth=auth, timeout=5)
            result = json.loads(response.content)
            if result:
                version = result.get("version")
                if version:
                    number = version.get("number")
                else:
                    number = self.default_number
            else:
                number = self.default_number
        except UnKnowEsVersionException as e:
            logger.error("wrong version checker，msg %s" % e)
            number = self.default_number
            return number
        return number

    @property
    def version(self) -> str:
        return self._version
