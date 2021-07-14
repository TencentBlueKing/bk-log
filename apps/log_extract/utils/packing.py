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
import time
from typing import List

from django.conf import settings

from apps.log_extract import constants
from apps.log_extract.constants import KeywordType


def get_packed_dir_name(path, task_id):
    """拼接本次任务打包路径
    @param path:
    @param task_id:
    @return:
    """
    file_name = time.strftime("%Y%m%d", time.localtime()) + "_" + str(task_id)
    return "".join([path, file_name, "/"])


def get_packed_file_name(task_id):
    """
    拼接打包后文件名
    @param task_id: 任务ID
    @return: str：拼接后的文件名
    """
    app_code = settings.APP_CODE
    app_code = app_code.replace("-", "_")
    task_time = time.strftime("%Y%m%d%H%M", time.localtime())
    return "_".join([app_code, task_time, str(task_id)]) + ".tgz"


def get_filter_content(filter_type, filter_content):
    executed_filter_content = {}
    if filter_type == constants.FilterType.MATCH_WORD.value:
        executed_filter_content["filter_cond1"] = filter_content.get("keyword")
        executed_filter_content["filter_cond2"] = get_keyword_type(filter_content.get("keyword_type"))
    elif filter_type == constants.FilterType.LINE_RANGE.value:
        executed_filter_content["filter_cond1"] = filter_content.get("start_line")
        executed_filter_content["filter_cond2"] = filter_content.get("end_line")
    elif filter_type == constants.FilterType.TAIL_LINE.value:
        executed_filter_content["filter_cond1"] = filter_content.get("line_num")
    elif filter_type == constants.FilterType.MATCH_RANGE.value:
        executed_filter_content["filter_cond1"] = filter_content.get("start")
        executed_filter_content["filter_cond2"] = filter_content.get("end")
        filter_condition_list = executed_filter_content["filter_cond1"].replace('"', '\\"').split(",")
        filter_condition_list = get_keyword(executed_filter_content["filter_cond2"], filter_condition_list)
        executed_filter_content["filter_cond1"] = " ".join(filter_condition_list)
    return executed_filter_content


def get_keyword_type(keyword_type: str):
    if keyword_type in [KeywordType.OR.value, KeywordType.AND.value, KeywordType.NOT.value]:
        return keyword_type
    return ""


def get_keyword(keyword_type: str, keyword: List[str]):
    if keyword_type in [KeywordType.OR.value, KeywordType.AND.value]:
        return list(map(lambda word: f"/{word}/", keyword))
    return keyword
