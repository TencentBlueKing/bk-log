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

from django.conf import settings
from celery.schedules import crontab
from celery.task import periodic_task

from apps.log_measure.utils.metric import MetricUtils
from apps.log_measure.constants import COLLECTOR_IMPORT_PATHS

from config.domains import MONITOR_APIGATEWAY_ROOT
from bk_monitor.handler.monitor import BKMonitor


@periodic_task(run_every=crontab(minute="*/1"), queue="bk_monitor_report")
def bk_monitor_report():
    # todo 由于与菜单修改有相关性 暂时先改成跟原本monitor开关做联动
    if settings.FEATURE_TOGGLE["monitor_report"] == "off":
        return

    # 这里是为了兼容调度器由于beat与worker时间差异导致的微小调度异常
    time.sleep(2)
    bk_monitor_client = BKMonitor(
        app_id=settings.APP_CODE,
        app_token=settings.SECRET_KEY,
        monitor_host=MONITOR_APIGATEWAY_ROOT,
        report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
        bk_username="admin",
        bk_biz_id=settings.BLUEKING_BK_BIZ_ID,
    )
    bk_monitor_client.custom_metric().report(collector_import_paths=COLLECTOR_IMPORT_PATHS)
    # 此处是为了释放对应util资源 非必须
    MetricUtils.del_instance()
