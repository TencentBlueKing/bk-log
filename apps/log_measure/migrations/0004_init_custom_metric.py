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

from django.db import migrations
from django.conf import settings

from apps.utils.log import logger
from apps.log_measure.constants import DATA_NAMES
from config.domains import MONITOR_APIGATEWAY_ROOT
from bk_monitor.handler.monitor import BKMonitor


def forwards_func(apps, schema_editor):
    try:
        Migration.bk_monitor_client.custom_metric().migrate(data_name_list=Migration.data_names)
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"custom_metric migrate error: {e}")


class Migration(migrations.Migration):
    data_names = DATA_NAMES

    bk_monitor_client = BKMonitor(
        app_id=settings.APP_CODE,
        app_token=settings.SECRET_KEY,
        monitor_host=MONITOR_APIGATEWAY_ROOT,
        report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
        bk_username="admin",
        bk_biz_id=settings.BLUEKING_BK_BIZ_ID,
    )

    dependencies = [("log_measure", "0003_auto_20200605_1357")]

    operations = [migrations.RunPython(forwards_func)]
