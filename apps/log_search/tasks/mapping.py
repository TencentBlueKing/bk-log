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
from concurrent.futures import ThreadPoolExecutor
from celery.schedules import crontab
from celery.task import periodic_task, task

from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler
from apps.utils.lock import share_lock
from apps.utils.log import logger
from apps.exceptions import ApiResultError
from apps.log_search.constants import BkDataErrorCode
from apps.log_search.models import LogIndexSet


@periodic_task(run_every=crontab(minute="*/10"))
@share_lock()
def sync_index_set_mapping_cache():
    logger.info("[sync_index_set_mapping_cache] start")
    index_set_id_list = LogIndexSet.objects.filter(is_active=True).values_list("index_set_id", flat=True)

    def sync_mapping_cache(index_set_id):
        logger.info("[sync_index_set_mapping_cache] index_set({}) start".format(index_set_id))
        try:
            SearchHandler(index_set_id=index_set_id, search_dict={}).fields()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("[sync_index_set_mapping_cache] index_set({}) sync failed: {}".format(index_set_id, e))
            return
        logger.info("[sync_index_set_mapping_cache] index_set({}) sync success".format(index_set_id))

    with ThreadPoolExecutor() as executor:
        executor.map(sync_mapping_cache, index_set_id_list)
    logger.info("[sync_index_set_mapping_cache] end")


@periodic_task(run_every=crontab(minute="0", hour="2"))
def sync_index_set_mapping_snapshot():
    logger.info("[sync_index_set_mapping_snapshot] start")
    index_set_list = LogIndexSet.objects.filter(is_active=True)

    for index_set in index_set_list:
        try:
            index_set.sync_fields_snapshot(pre_check_enable=False)
        except ApiResultError as e:
            # 当数据平台返回为无法获取元数据报错情况
            if e.code in [BkDataErrorCode.STORAGE_TYPE_ERROR, BkDataErrorCode.COULD_NOT_GET_METADATA_ERROR]:
                index_set.is_active = False
                index_set.save()
            logger.exception(
                f"[sync_index_set_mapping_snapshot] index_set({index_set.index_set_id} call mapping error: {e})"
            )
            continue

        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "[sync_index_set_mapping_snapshot] index_set({}) sync failed: {}".format(index_set.index_set_id, e)
            )
            continue
        logger.info("[sync_index_set_mapping_snapshot] index_set({}) sync success".format(index_set.index_set_id))

    logger.info("[sync_index_set_mapping_snapshot] end")


@task(ignore_result=True)
def sync_single_index_set_mapping_snapshot(index_set_id=None):  # pylint: disable=function-name-too-long
    try:
        index_set_obj = LogIndexSet.objects.get(index_set_id=index_set_id)
    except LogIndexSet.DoesNotExist:
        logger.exception(f"[sync_single_index_set_mapping_snapshot]index_set({index_set_id}) not exist")
    else:
        try:
            index_set_obj.sync_fields_snapshot()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                f"[sync_single_index_set_mapping_snapshot] index_set({index_set_obj.index_set_id}) sync failed: {e}"
            )
        logger.info(f"[sync_single_index_set_mapping_snapshot] index_set({index_set_obj.index_set_id}) sync success")
