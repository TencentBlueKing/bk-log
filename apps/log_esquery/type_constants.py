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

from typing import List, Dict, Any, Tuple, Union

type_index_set_string = str  # pylint: disable=invalid-name
type_index_set_list = List[str]  # pylint: disable=invalid-name
type_scenario_id = str  # pylint: disable=invalid-name
type_start_time = str  # pylint: disable=invalid-name
type_end_time = str  # pylint: disable=invalid-name
type_time_range = str  # pylint: disable=invalid-name
type_keyword = str  # pylint: disable=invalid-name
type_ips = str  # pylint: disable=invalid-name
type_host_scopes = Dict[str, Any]  # pylint: disable=invalid-name
type_a_addition = Dict[str, Any]  # pylint: disable=invalid-name
type_addition = List[type_a_addition]  # pylint: disable=invalid-name
type_begin = int  # pylint: disable=invalid-name
type_size = int  # pylint: disable=invalid-name
type_search_dict = Dict[str, Any]  # pylint: disable=invalid-name
type_time_range_dict = Dict[str, Any]  # pylint: disable=invalid-name
type_sort_tuple = Union[List[str], Tuple[str, str]]  # pylint: disable=invalid-name
type_sort_multi_list = List[type_sort_tuple]  # pylint: disable=invalid-name
type_sort_dict = Dict[str, Dict[str, str]]  # pylint: disable=invalid-name
type_sort_multi_dict_list = List[type_sort_dict]  # pylint: disable=invalid-name
type_mapping_dict = Dict[str, Any]  # pylint: disable=invalid-name
