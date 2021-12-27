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

from apps.feature_toggle.handlers.toggle import FeatureToggleObject


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(list(zip(columns, row))) for row in cursor.fetchall()]


def array_group(data, key, group=0):
    if not data or len(data) == 0:
        return {}

    result = {}
    for item in data:
        if isinstance(item, dict):
            attr = item.get(key, None)
        else:
            attr = getattr(item, key, None)

        if attr is None:
            return {}

        if group != 0:
            if attr not in result:
                if isinstance(item, dict):
                    item["_nums"] = 1
                else:
                    item._nums = 1
            else:
                if isinstance(item, dict):
                    item["_nums"] = result[attr]["_nums"] + 1
                else:
                    item._nums = result[attr]._nums + 1

            result[attr] = item

        else:
            if attr not in result:
                result[attr] = []
            result[attr].append(item)
    return result


def array_hash(data, key, value):
    """
    获取一个DB对象的HASH结构
    """
    if not data or len(data) == 0:
        return {}

    result = {}
    for item in data:
        if isinstance(item, dict):
            attr = item.get(key, None)
        else:
            attr = getattr(item, key, None)

        if attr is None:
            return False

        if isinstance(item, dict):
            result[attr] = item.get(value, None)
        else:
            result[attr] = getattr(item, value, None)

    return result


def array_chunk(data, size=100):
    return [data[i : i + size] for i in range(0, len(data), size)]


def get_toggle_data():
    toggle_list = FeatureToggleObject.toggle_list(**{"is_viewed": True})
    data = {
        # 实时日志最大长度
        "REAL_TIME_LOG_MAX_LENGTH": 20000,
        # 超过此长度删除部分日志
        "REAL_TIME_LOG_SHIFT_LENGTH": 10000,
        # 特性开关
        "FEATURE_TOGGLE": json.dumps({toggle.name: toggle.status for toggle in toggle_list}),
        "FEATURE_TOGGLE_WHITE_LIST": json.dumps(
            {
                toggle.name: toggle.biz_id_white_list
                for toggle in toggle_list
                if isinstance(toggle.biz_id_white_list, list)
            }
        ),
    }
    return data
