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

from apps.log_esquery.type_constants import type_addition


class QueryFilterBuilder(object):
    def __init__(self, addition: type_addition):
        self._filter_dict_list: type_addition = []
        self.set_filter_dict_list(addition)

    @property
    def filter_dict_list(self):
        return self._filter_dict_list

    # 构建索引集的filter，传入DSL构建器
    def set_filter_dict_list(self, addition: type_addition):
        for item in addition:
            if item.get("field") and (item.get("value") or isinstance(item.get("value"), str)):
                self._filter_dict_list.append(
                    {
                        "field": item["field"],
                        "operator": item["operator"],
                        "value": item["value"],
                        "condition": item.get("condition", "and"),
                        "type": item.get("type", "field"),
                    }
                )
