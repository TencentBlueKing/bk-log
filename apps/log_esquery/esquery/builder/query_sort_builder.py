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

from apps.log_esquery.type_constants import type_sort_multi_dict_list, type_sort_multi_list


class QuerySortBuilder(object):
    DESC = "desc"
    ASC = "asc"

    def __init__(self, sort_list: type_sort_multi_list):
        self._sort_final_list: type_sort_multi_dict_list = self.build_sort_list(sort_list)

    @property
    def sort_list(self) -> type_sort_multi_dict_list:
        return self._sort_final_list

    def build_sort_list(self, sort_list: type_sort_multi_list) -> type_sort_multi_dict_list:
        sort_final_list: type_sort_multi_dict_list = []
        for item in sort_list:
            sort_field, order = item
            if order not in [self.DESC, self.ASC]:
                order = self.DESC
            sort_final_list.append({sort_field: {"order": order}})
        return sort_final_list
