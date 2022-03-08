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
from bk_monitor_report import MonitorReporter
from django.apps import AppConfig
from django.conf import settings

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.utils.function import ignored
from apps.utils.log import logger


class MeasureConfig(AppConfig):
    name = "apps.log_measure"
    verbose_name = "measure"

    def ready(self):
        if settings.DEBUG or not FeatureToggleObject.switch("monitor_report"):
            return
        with ignored(Exception):
            from bk_monitor.models import MonitorReportConfig

            from apps.log_measure.constants import DJANGO_MONITOR_DATA_NAME

            monitor_report_config = None
            try:
                monitor_report_config = MonitorReportConfig.objects.get(
                    data_name=DJANGO_MONITOR_DATA_NAME, is_enable=True
                )
            except MonitorReportConfig.DoesNotExist:
                logger.info(f"f{DJANGO_MONITOR_DATA_NAME} data_name init failed")
                return
            reporter = MonitorReporter(
                data_id=monitor_report_config.data_id,
                access_token=monitor_report_config.access_token,
                target=settings.APP_CODE,
                url=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/v2/push/",
            )
            reporter.start()
