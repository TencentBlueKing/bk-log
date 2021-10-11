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


def deal_collector_scenario_param(params):
    filters = []
    condition_type = params["conditions"]["type"]
    if condition_type == "separator":
        condition = params["conditions"].get("separator_filters", [])
        filter_bucket = []
        for (index, item) in enumerate(condition):
            item["op"] = item["op"] if item["op"] in ["=", "!="] else "="
            if index == 0 or item.get("logic_op", "and") == "and":
                if item.get("word"):
                    filter_bucket.append({"index": item["fieldindex"], "key": item["word"], "op": item["op"]})
            else:
                if len(filter_bucket) > 0:
                    filters.append({"conditions": filter_bucket})
                    filter_bucket = []

                if item.get("word"):
                    filter_bucket.append({"index": item["fieldindex"], "key": item["word"], "op": item["op"]})
        if len(filter_bucket) > 0:
            filters.append({"conditions": filter_bucket})
    elif condition_type == "match":
        key = params["conditions"].get("match_content", "")
        if key:
            filters.append({"conditions": [{"index": "-1", "key": key, "op": "="}]})  # 目前只支持include
            params["conditions"].update({"separator": "|"})
    return filters, params


def build_es_option_type(field_type, es_version="5.X") -> dict:
    default_config = {"es_type": field_type}
    if es_version.startswith("5."):
        default_config["es_include_in_all"] = True
    return default_config
