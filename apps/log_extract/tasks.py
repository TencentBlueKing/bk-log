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
import os
from django.utils.translation import ugettext_lazy as _

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.utils import timezone
from pipeline.exceptions import InvalidOperationException
from pipeline.service import task_service
from apps.utils.log import logger
from apps.log_extract import exceptions
from apps.log_extract.constants import DownloadStatus, ExtractLinkType
from apps.log_extract.models import Tasks


@periodic_task(run_every=crontab(minute="0", hour="2"))  # pylint: disable=function-name-too-long
def periodic_clear_timeout_pipeline_task():
    # 异常的下载状态
    abnormal_download_status = [
        DownloadStatus.INIT.value,
        DownloadStatus.PIPELINE.value,
        DownloadStatus.PACKING.value,
        DownloadStatus.DISTRIBUTING.value,
        DownloadStatus.DISTRIBUTING_PACKING.value,
        DownloadStatus.UPLOADING.value,
    ]

    # 处理已完成但超过时间还为下载的任务
    expired_task_list = Tasks.objects.filter(expiration_date__lte=timezone.now()).exclude(
        download_status__in=abnormal_download_status
    )
    expired_task_list.update(download_status=DownloadStatus.EXPIRED.value)

    task_expired_time = int(settings.PIPELINE_TASKS_EXPIRED_TIME)
    timeout_pipeline_task = Tasks.objects.filter(
        created_at__lte=timezone.now() + timezone.timedelta(hours=-task_expired_time),
        download_status__in=abnormal_download_status,
    ).values("pipeline_id", "download_status", "task_id")

    # 清理过期的内网下载文件
    for expired_task in expired_task_list:
        if expired_task.get_link_type() == ExtractLinkType.COMMON.value:
            target_file_dir = os.path.join(settings.EXTRACT_SAAS_STORE_DIR, expired_task.cos_file_name)
            os.remove(os.path.abspath(target_file_dir))

    for task in timeout_pipeline_task:
        try:
            task_service.revoke_pipeline(task["pipeline_id"])
        except InvalidOperationException as e:
            logger.exception(
                _("[periodic_clear_timeout_pipeline_task]撤销超时pipeline任务失败：{}, task_id=>{}, pipeline_id=>{}").format(
                    e, task["task_id"], task["pipeline_id"]
                )
            )
            raise exceptions.PipelineRevoked(
                exceptions.PipelineRevoked.MESSAGE.format(
                    exceptions=e, task_id=task["task_id"], pipeline_id=task["pipeline_id"]
                )
            )
        # 更新任务下载状态
        Tasks.objects.filter(pipeline_id=task["pipeline_id"]).update(
            download_status=DownloadStatus.FAILED.value,
            task_process_info="task timeout, origin status is {}".format(task["download_status"]),
        )
