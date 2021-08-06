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
from django.conf import settings

from celery.schedules import crontab
from celery.task import periodic_task

from apps.utils.log import logger
from apps.utils.bk_data_auth import BkDataAuthHandler
from apps.log_search.models import LogIndexSetData, LogIndexSet, Scenario
from apps.log_databus.models import BKDataClean


@periodic_task(run_every=crontab(minute="*/30"))
def sync_auth_status():
    """
    数据平台索引集申请单据状态同步
    """
    if settings.RUN_VER == "open":
        return 0

    authorized_rt_list = BkDataAuthHandler().list_authorized_rt_by_token()

    # 获取所有数据平台类型的索引集
    bkdata_index_set_ids = LogIndexSet.objects.filter(scenario_id=Scenario.BKDATA).values_list(
        "index_set_id", flat=True
    )

    # 获取状态为"审批中"的的索引集，并将token有权限的RT的状态置为NORMAL
    updated_count = LogIndexSetData.objects.filter(
        index_set_id__in=bkdata_index_set_ids,
        apply_status=LogIndexSetData.Status.PENDING,
        result_table_id__in=authorized_rt_list,
    ).update(
        apply_status=LogIndexSetData.Status.NORMAL,
    )

    logger.info(f"[sync_auth_status] {updated_count} rows of apply_status changed to NORMAL")

    update_bkdata_clean_count = BKDataClean.objects.filter(result_table_id__in=authorized_rt_list).update(
        is_authorized=True
    )
    logger.info(f"[sync_bkdata_clean] {update_bkdata_clean_count} rows of is_authorized to True")
    return updated_count
