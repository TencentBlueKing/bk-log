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


def convert_filters_to_collector_condition(filters_config, delimiter=""):
    """
    将下发的过滤参数转换为页面显示的condition参数
    :param filters_config: [[{"index": "1", "key": "xx", "op": "="}]]
    :param delimiter: 分隔符
    """
    try:
        separator_filters = []
        # 如果是逻辑或，会拆成多个配置下发
        logic_op = "and" if len(filters_config) <= 1 else "or"
        for filter_item in filters_config:
            for condition_item in filter_item["conditions"]:
                separator_filters.append(
                    {
                        "fieldindex": condition_item["index"],
                        "word": condition_item["key"],
                        "op": condition_item["op"],
                        "logic_op": logic_op,
                    }
                )
    except (IndexError, KeyError, ValueError):
        separator_filters = []

    match_content = ""
    if separator_filters and separator_filters[0]["fieldindex"] == "-1":
        _type = "match"
        match_content = separator_filters[0].get("word", "")
        separator_filters = []
    elif not separator_filters:
        _type = "match"
    else:
        _type = "separator"
    return {
        "separator": delimiter,
        "separator_filters": separator_filters,
        "type": _type,
        "match_type": "include",  # 目前只支持include
        "match_content": match_content,
    }


def build_es_option_type(field_type, es_version="5.X") -> dict:
    default_config = {"es_type": field_type}
    if es_version.startswith("5."):
        default_config["es_include_in_all"] = True
    return default_config
