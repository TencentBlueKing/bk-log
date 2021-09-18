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
import os
import tarfile
import json
import datetime

import pytz
import arrow
from django.utils.translation import gettext as _
from django.utils import translation
from celery.schedules import crontab
from django.conf import settings
from django.utils.crypto import get_random_string
from celery.task import task, periodic_task

from apps.constants import RemoteStorageType
from apps.log_search.constants import (
    ASYNC_DIR,
    FEATURE_ASYNC_EXPORT_COMMON,
    ASYNC_EXPORT_EMAIL_TEMPLATE,
    ASYNC_EXPORT_FILE_EXPIRED_DAYS,
    ASYNC_EXPORT_EXPIRED,
    ASYNC_APP_CODE,
    FEATURE_ASYNC_EXPORT_NOTIFY_TYPE,
    FEATURE_ASYNC_EXPORT_STORAGE_TYPE,
    MAX_RESULT_WINDOW,
    MsgModel,
    ASYNC_EXPORT_EMAIL_ERR_TEMPLATE,
)
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler
from apps.log_search.models import Scenario, AsyncTask, LogIndexSet
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.utils.log import logger
from apps.utils.notify import NotifyType
from apps.utils.remote_storage import StorageType


@task(ignore_result=True, queue="async_export")
def async_export(
    search_handler: SearchHandler,
    sorted_fields: list,
    async_task_id: int,
    url_path: str,
    search_url_path: str,
    language: str,
):
    """
    异步导出任务
    @param search_handler {SearchHandler}
    @param sorted_fields {List}
    @param async_task_id {Int}
    @param url_path {Str}
    @param search_url_path {Str}
    @param language {Str}
    """
    random_hash = get_random_string(length=10)
    time_now = arrow.now().format("YYYYMMDDHHmmss")
    file_name = f"{ASYNC_APP_CODE}_{search_handler.index_set_id}_{time_now}_{random_hash}"
    tar_file_name = f"{file_name}.tar.gz"
    async_task = AsyncTask.objects.filter(id=async_task_id).first()
    async_export_util = AsyncExportUtils(
        search_handler=search_handler, sorted_fields=sorted_fields, file_name=file_name, tar_file_name=tar_file_name
    )
    try:
        if not async_task:
            logger.error(f"Can not find this: id: {async_task_id} record")
            raise BaseException(f"Can not find this: id: {async_task_id} record")

        try:
            async_export_util.export_package()
        except Exception as e:  # pylint: disable=broad-except
            async_task.failed_reason = f"export package error: {e}"
            logger.error(async_task.failed_reason)
            async_task.save()
            raise

        async_task.file_name = tar_file_name
        async_task.file_size = async_export_util.get_file_size()

        try:
            async_export_util.export_upload()
        except Exception as e:  # pylint: disable=broad-except
            async_task.failed_reason = f"export upload error: {e}"
            logger.error(async_task.failed_reason)
            async_task.save()
            raise

        try:
            url = async_export_util.generate_download_url(url_path=url_path)
        except Exception as e:  # pylint: disable=broad-except
            async_task.failed_reason = f"generate download url error: {e}"
            logger.error(async_task.failed_reason)
            async_task.save()
            raise

        async_task.download_url = url

        try:
            async_export_util.send_msg(
                index_set_id=search_handler.index_set_id,
                async_task=async_task,
                search_url_path=search_url_path,
                language=language,
            )
        except Exception as e:  # pylint: disable=broad-except
            async_task.failed_reason = f"send msg error: {e}"
            logger.error(async_task.failed_reason)
            async_task.save()
            raise

    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
        async_export_util.send_msg(
            index_set_id=search_handler.index_set_id,
            async_task=async_task,
            search_url_path=search_url_path,
            language=language,
            name=ASYNC_EXPORT_EMAIL_ERR_TEMPLATE,
            title_model=MsgModel.ABNORMAL,
        )
        return

    async_task.result = True
    async_task.save()
    async_export_util.clean_package()


@periodic_task(run_every=crontab(minute="0", hour="3"))
def clean_expired_task():
    """
    clean expired task file
    expired_time:  2days

    """
    day_ago = datetime.datetime.now(pytz.timezone("UTC")) - datetime.timedelta(days=ASYNC_EXPORT_FILE_EXPIRED_DAYS)
    # 获取过期的内网下载文件
    expired_task_list = AsyncTask.objects.filter(created_at__lt=day_ago, is_clean=False)
    # nfs文件需要进行定期清理操作
    storage_type = FeatureToggleObject.toggle(FEATURE_ASYNC_EXPORT_COMMON).feature_config.get(
        FEATURE_ASYNC_EXPORT_STORAGE_TYPE
    )

    if storage_type or storage_type == RemoteStorageType.NFS.value:
        # 删除NFS文件
        for expired_task in expired_task_list:
            target_file_dir = os.path.join(settings.EXTRACT_SAAS_STORE_DIR, expired_task.file_name)
            if os.path.isfile(target_file_dir):
                os.remove(os.path.abspath(target_file_dir))
            expired_task.is_clean = True
            expired_task.save()


class AsyncExportUtils(object):
    """
    async export utils(export_package, export_upload, generate_download_url, send_msg, clean_package)
    """

    def __init__(self, search_handler: SearchHandler, sorted_fields: list, file_name: str, tar_file_name: str):
        """
        @param search_handler: the handler cls to search
        @param sorted_fields: the fields to sort search result
        @param file_name: the export file name
        @param tar_file_name: the file name which will be tar
        """
        self.search_handler = search_handler
        self.sorted_fields = sorted_fields
        self.file_name = file_name
        self.tar_file_name = tar_file_name
        self.file_path = f"{ASYNC_DIR}/{self.file_name}"
        self.tar_file_path = f"{ASYNC_DIR}/{self.tar_file_name}"
        self.storage = self.init_remote_storage()
        self.notify = self.init_notify_type()

    def export_package(self):
        """
        检索结果文件打包
        """
        if not (os.path.exists(ASYNC_DIR) and os.path.isdir(ASYNC_DIR)):
            os.makedirs(ASYNC_DIR)

        result = self.search_handler.pre_get_result(sorted_fields=self.sorted_fields, size=MAX_RESULT_WINDOW)
        with open(self.file_path, "a+", encoding="utf-8") as f:
            result_list = self.search_handler._deal_query_result(result_dict=result).get("origin_log_list")
            for item in result_list:
                f.write("%s\n" % json.dumps(item))
            if self.search_handler.scenario_id == Scenario.ES:
                generate_result = self.search_handler.scroll_result(result)
            else:
                generate_result = self.search_handler.search_after_result(result, self.sorted_fields)
            self.write_file(f, generate_result)

        with tarfile.open(self.tar_file_path, "w:gz") as tar:
            tar.add(self.file_path, arcname=self.file_name)

    def export_upload(self):
        """
        文件上传
        """
        self.storage.export_upload(file_path=self.tar_file_path, file_name=self.tar_file_name)

    def generate_download_url(self, url_path: str):
        """
        生成url
        """
        return self.storage.generate_download_url(url_path=url_path, file_name=self.tar_file_name)

    def send_msg(
        self,
        index_set_id: int,
        async_task: AsyncTask,
        search_url_path: str,
        language: str,
        name: str = ASYNC_EXPORT_EMAIL_TEMPLATE,
        title_model: str = MsgModel.NORMAL,
    ):
        """
        发送邮件
        """
        index_set_obj = LogIndexSet.objects.get(index_set_id=index_set_id)

        platform = settings.EMAIL_TITLE["en"] if translation.get_language() == "en" else settings.EMAIL_TITLE["zh"]

        title = self.notify.title(
            self.generate_title_template(title_model=title_model),
            platform=platform,
            index_set_name=index_set_obj.index_set_name,
        )

        content = self.notify.content(
            name=name,
            file={
                "platform": platform,
                "created_at": arrow.now().format("YYYY-MM-DD HH:mm:ss"),
                "index_set_name": index_set_obj.index_set_name,
                "index": ",".join([index["result_table_id"].replace(".", "_") for index in index_set_obj.indexes]),
                "create_by": async_task.created_by,
                "size": async_task.file_size,
                "request_param": json.dumps(async_task.request_param),
                "search_url": search_url_path,
                "download_url": async_task.download_url,
            },
            language=language,
        )
        self.notify.send(receivers=async_task.created_by, title=title, content=content)

    @classmethod
    def generate_title_template(cls, title_model):
        title_template_map = {
            MsgModel.NORMAL: _("【{platform}】{index_set_name} 检索导出"),
            MsgModel.ABNORMAL: _("【{platform}】{index_set_name} 检索导出失败"),
        }
        return title_template_map.get(title_model, title_template_map.get(MsgModel.NORMAL))

    def clean_package(self):
        """
        清空产生的临时文件
        """
        os.remove(self.file_path)
        os.remove(self.tar_file_path)

    @classmethod
    def init_remote_storage(cls):
        toggle = FeatureToggleObject.toggle(FEATURE_ASYNC_EXPORT_COMMON).feature_config
        storage_type = toggle.get(FEATURE_ASYNC_EXPORT_STORAGE_TYPE)
        storage = StorageType.get_instance(storage_type)
        if not storage_type or storage_type == RemoteStorageType.NFS.value:
            return storage(settings.EXTRACT_SAAS_STORE_DIR)
        return storage(
            toggle.get("qcloud_secret_id"),
            toggle.get("qcloud_secret_key"),
            toggle.get("qcloud_cos_region"),
            toggle.get("qcloud_cos_bucket"),
            ASYNC_EXPORT_EXPIRED,
        )

    def get_file_size(self):
        """
        获取文件大小 单位：m，保留小数2位
        """
        return round(os.path.getsize(self.tar_file_path) / float(1024 * 1024), 2)

    @classmethod
    def init_notify_type(cls):
        notify_type = FeatureToggleObject.toggle(FEATURE_ASYNC_EXPORT_COMMON).feature_config.get(
            FEATURE_ASYNC_EXPORT_NOTIFY_TYPE
        )

        return NotifyType.get_instance(notify_type=notify_type)()

    @classmethod
    def write_file(cls, f, result):
        """
        将对应数据写到文件中
        """
        for res in result:
            origin_result_list = res.get("origin_log_list")
            for item in origin_result_list:
                f.write("%s\n" % json.dumps(item))
