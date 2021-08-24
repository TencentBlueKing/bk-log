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
from django.utils.translation import ugettext_lazy as _

from apps.utils import ChoicesEnum


class NotifyType(ChoicesEnum):
    """
    支持的通知方式
    """

    EMAIL = "email"

    _choices_labels = ((EMAIL, _("邮件")),)

    @classmethod
    def get_choice_label(cls, key: str) -> dict:
        # 获取提醒方式，默认值为email
        choice_dict = dict(cls.get_choices())
        return choice_dict.get(key, choice_dict[cls.EMAIL.value])


class RemoteStorageType(ChoicesEnum):
    """
    支持的远程存储方式
    """

    COS = "cos"
    NFS = "nfs"

    _choices_labels = ((COS, _("腾讯云对象存储")), (NFS, _("远程文件系统")))

    @classmethod
    def get_choice_label(cls, key: str) -> dict:
        # 获取提醒方式，默认值为nfs
        choice_dict = dict(cls.get_choices())
        return choice_dict.get(key, choice_dict[cls.NFS.value])


class UserOperationTypeEnum(ChoicesEnum):
    COLLECTOR = "collector"
    STORAGE = "storage"
    INDEX_SET = "index_set"
    SEARCH = "search"
    ETL = "etl"
    EXPORT = "export"
    LOG_EXTRACT_STRATEGY = "log_extract_strategy"
    LOG_EXTRACT_LINKS = "log_extract_links"
    LOG_EXTRACT_TASKS = "log_extract_tasks"

    _choices_labels = (
        (COLLECTOR, _("采集项")),
        (STORAGE, _("存储集群")),
        (INDEX_SET, _("索引集")),
        (SEARCH, _("检索配置")),
        (ETL, _("清洗配置")),
        (EXPORT, _("导出")),
        (LOG_EXTRACT_STRATEGY, _("日志提取策略")),
        (LOG_EXTRACT_LINKS, _("日志提取链路")),
        (LOG_EXTRACT_TASKS, _("日志提取任务")),
    )


class UserOperationActionEnum(ChoicesEnum):
    CREATE = "create"
    UPDATE = "update"
    DESTROY = "destroy"
    RETRY = "retry"
    START = "start"
    STOP = "stop"
    REPLACE_CREATE = "replace_create"
    REPLACE_UPDATE = "replace_update"
    CONFIG = "config"

    _choices_labels = (
        (CREATE, _("创建")),
        (UPDATE, _("更新")),
        (DESTROY, _("删除")),
        (RETRY, _("任务重试")),
        (START, _("启动")),
        (STOP, _("停止")),
        (REPLACE_CREATE, _("新建并替换")),
        (REPLACE_UPDATE, _("替换")),
        (CONFIG, _("配置")),
    )
