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

from typing import List
from apps.utils.local import get_request_username
from apps.log_search.models import Scenario, UserIndexSetConfig
from apps.log_search.exceptions import SearchIndexNoTimeFieldException


class SearchSortBuilder(object):
    def __init__(self):
        pass

    @classmethod
    def sort_list(cls, **search_dict) -> list:
        index_set_id = search_dict.get("index_set_id")
        scenario_id = search_dict.get("scenario_id")
        time_field = search_dict.get("time_field")

        # 获取用户对sort的排序需求
        sort_list: List = search_dict.get("sort_list", [])
        if sort_list:
            return sort_list
        # 用户已设置排序规则
        username = get_request_username()
        scope = search_dict.get("search_type", "default")
        index_config_obj = UserIndexSetConfig.objects.filter(
            index_set_id=index_set_id, created_by=username, scope=scope, is_deleted=False
        )
        if index_config_obj.exists():
            sort_list = index_config_obj.first().sort_list
            if sort_list:
                return sort_list
        # if not custom sort setting
        # get fields
        default_sort_tag = search_dict.get("default_sort_tag")

        if time_field:
            sort_list: list = cls.with_time_field(time_field, scenario_id, default_sort_tag, scope)
            return sort_list
        raise SearchIndexNoTimeFieldException()

    @staticmethod
    def with_time_field(time_field, scenario_id, default_sort_tag, scope):
        if scope in ["trace_detail", "trace_scatter"]:
            return [[time_field, "asc"]]
        if scenario_id in [Scenario.BKDATA, Scenario.LOG]:
            if default_sort_tag is True:
                if scenario_id == Scenario.BKDATA:
                    return [[time_field, "desc"], ["gseindex", "desc"], ["_iteration_idx", "desc"]]
                if scenario_id == Scenario.LOG:
                    return [[time_field, "desc"], ["gseIndex", "desc"], ["iterationIndex", "desc"]]
        return [[time_field, "desc"]]
