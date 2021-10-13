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
from celery.schedules import crontab
from celery.task import periodic_task
from django.utils import timezone

from apps.api import TransferApi
from apps.utils.log import logger
from apps.log_databus.models import RestoreConfig
from apps.log_search.handlers.index_set import IndexSetHandler


@periodic_task(run_every=crontab(minute="0", hour="1"))
def clean_expired_restore_index_set():
    now = timezone.now()
    expired_restores = RestoreConfig.objects.filter(expired_time__lt=now)
    for expired_restore in expired_restores:
        try:
            if expired_restore.index_set_id:
                index_set_handler = IndexSetHandler(expired_restore.index_set_id)
                index_set_handler.stop()
        except Exception as e:
            logger.error(f"clean expired restore ->[{expired_restore.restore_config_id}] index_set failed -> {e}")
            continue
        logger.info(
            f"clean expired restore ->[{expired_restore.restore_config_id}]"
            f" success index_set_id ->[{expired_restore.index_set_id}]"
        )


@periodic_task(run_every=crontab(minute="*/1"))
def check_restore_is_done_and_notice_user():
    not_done_restores = RestoreConfig.objects.filter(is_done=False)
    not_done_restores_by_meta_restore_id = {
        not_done_restore.meta_restore_id: not_done_restore for not_done_restore in not_done_restores
    }
    meta_restore_states = TransferApi.get_restore_result_table_snapshot_state(
        {"restore_ids": list(not_done_restores_by_meta_restore_id.keys())}
    )
    for meta_restore_state in meta_restore_states:
        not_done_restore = not_done_restores_by_meta_restore_id.get(meta_restore_state["restore_id"])
        # maybe data not consistent
        if meta_restore_state["total_doc_count"] <= meta_restore_state["complete_doc_count"]:
            try:
                not_done_restore.done(meta_restore_state["duration"])
            except Exception as e:
                logger.error(f"deal with restore done error -> [{e}]")
                continue
            logger.info(f"restore->[{not_done_restore.restore_config_id}] has done")
