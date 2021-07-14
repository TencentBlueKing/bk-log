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

import html
import re

from typing import Any

from apps.log_esquery.constants import WILDCARD_PATTERN


class QueryStringBuilder(object):
    def __init__(self, query_string: str):
        self._query_string: str = query_string

    @property
    def query_string(self):
        return self.special_check(self.html_unescape(self._query_string))

    # html 转码
    def html_unescape(self, query_string: str) -> str:
        if query_string:
            return html.unescape(query_string)
        return ""

    # 特殊字符检查
    def special_check(self, query_string: str) -> str:
        _query_string: str
        regx: Any = re.compile(r"[+\-=&|><!(){}\[\]^\"~*?:/]|AND|OR|TO|NOT")
        if query_string.strip() == "":
            return WILDCARD_PATTERN
        if regx.search(query_string):
            return query_string
        return f"{WILDCARD_PATTERN}{query_string}{WILDCARD_PATTERN}"
