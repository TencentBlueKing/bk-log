# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import re
import os
import time
from io import open

import mistune

from apps.utils.local import get_request_language_code
import version_log.config as config


def get_md_files_dir_with_language_code():
    """获取md文件夹路径"""
    return os.path.join(config.MD_FILES_DIR, get_request_language_code())


def get_html_file_path_with_language_code(version: str):
    """获取html文件路径"""
    return os.path.join(config.PARSED_HTML_FILES_DIR, "{}_{}.html".format(version, get_request_language_code()))


def get_parsed_html(log_version):
    """获取版本日志对应的html代码"""
    md_files_path = get_md_files_dir_with_language_code()
    # 根据版本号获取对应md文件
    filenames = [filename for filename in os.listdir(md_files_path)]
    md_filename = ""
    for filename in filenames:
        if log_version in filename:
            md_filename = filename
            break

    # 文件不存在
    if md_filename == "":
        return None

    md_file_path = os.path.join(md_files_path, md_filename)
    html_file_path = get_html_file_path_with_language_code(log_version)
    # 已有解析好的版本
    if os.path.isfile(html_file_path) and _is_html_file_generated_after_md_file(html_file_path, md_file_path):
        with open(html_file_path, encoding="utf-8") as f:
            html_text = f.read()
        return html_text
    # 没有解析好的版本
    return _md_parse_to_html_and_save(md_file_path, html_file_path)


def get_version_list():
    """
    获取md日志版本列表
    :return (版本号, 文件上传时间) 元组列表，列表根据版本号从大到小排列
    """
    md_files_dir = get_md_files_dir_with_language_code()
    if not os.path.isdir(md_files_dir):  # md文件夹不存在
        return None
    version_list = []
    for filename in os.listdir(md_files_dir):
        full_name = os.path.splitext(filename)[0]
        version, _, date_updated = full_name.partition("_")
        if date_updated == "":
            date_updated = _get_file_modified_date(os.path.join(md_files_dir, filename))
        else:
            date_updated = _transform_datetime_format(date_updated, config.FILE_TIME_FORMAT)
        version_values = _get_version_parsed_list(version)
        version_list.append(((version, date_updated), version_values))
    # 根据版本号按照从新版本到旧版本排序
    version_list.sort(key=lambda x: x[1], reverse=True)
    return [version_data[0] for version_data in version_list]


def is_later_version(version1, version2):
    """判断version1版本号是否大于version2, None属于最旧的级别"""
    if version1 is None:
        return False
    if version2 is None:
        return True
    version1_values = _get_version_parsed_list(version1)
    version2_values = _get_version_parsed_list(version2)
    return version1_values > version2_values


def get_latest_version():
    """返回最新版本号"""
    version_list = get_version_list()
    return version_list[0][0] if len(version_list) > 0 else None


def _get_version_parsed_list(version):
    """返回日志版本解析结果"""
    log_version_pattern = re.compile(r"(\d+)")  # noqa
    return [int(value) for value in re.findall(log_version_pattern, version)]


def _md_parse_to_html_and_save(md_file_path, html_file_path):
    """将存在的md文件解析并保存为html文件"""
    parser = mistune.Markdown(hard_wrap=True)
    with open(md_file_path, encoding="utf-8") as read_file, open(html_file_path, "w", encoding="utf-8") as write_file:
        md_version_log = read_file.read()
        html_version_log = parser(md_version_log)
        write_file.write(html_version_log)
    return html_version_log


def _is_filename_legal(filename):
    """判断文件名是否存在/合法"""
    return False if re.match(config.NAME_PATTERN, filename) is None else True


def _get_file_modified_date(file_path):
    """返回存在的文件的最后修改日期"""
    timestamp = os.stat(file_path).st_mtime
    return time.strftime("%Y.%m.%d", time.localtime(timestamp))


def _transform_datetime_format(date_str, format_in_file):
    """转换版本日期格式"""
    return time.strftime("%Y.%m.%d", time.strptime(date_str, format_in_file))


def _is_html_file_generated_after_md_file(html_file_path, md_file_path):  # pylint: disable=function-name-too-long
    """判断html文件是否在对应md文件修改后生成"""
    return os.stat(html_file_path).st_mtime > os.stat(md_file_path).st_mtime
