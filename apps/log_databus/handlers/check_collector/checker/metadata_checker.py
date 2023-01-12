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
import json
import logging
import time

import requests
from django.conf import settings

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import CHECK_COLLECTOR_CUSTOM_CONFIG
from apps.log_databus.constants import META_DATA_CRON_REFRESH_TASK_NAME_LIST
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker
from apps.log_search.constants import TimeEnum
from bk_monitor.api.client import Client
from config.domains import MONITOR_APIGATEWAY_ROOT

logger = logging.getLogger()


class MetaDataChecker(Checker):
    CHECKER_NAME = "meta data checker"

    def __init__(self, bk_token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bk_token = bk_token
        self.request_headers = {"Content-Type": "application/json", "Cookie": f"bk_token={self.bk_token}"}
        app_code = settings.APP_CODE
        app_secret = settings.SECRET_KEY
        monitor_host = MONITOR_APIGATEWAY_ROOT
        self.bk_monitor_client = Client(
            bk_app_code=app_code,
            bk_app_secret=app_secret,
            monitor_host=monitor_host,
            report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
            bk_username="admin",
        )

    def _run(self):
        self.check_cron_refresh_task()

    def check_cron_refresh_task(self):
        for task_name in META_DATA_CRON_REFRESH_TASK_NAME_LIST:
            params = self._build_unify_query_params(task_name)
            try:
                monitor_url = settings.MONITOR_URL
                if FeatureToggleObject.switch(CHECK_COLLECTOR_CUSTOM_CONFIG):
                    meta_data_custom_config = FeatureToggleObject.toggle(
                        CHECK_COLLECTOR_CUSTOM_CONFIG
                    ).feature_config.get("meta_data_custom_config")
                    monitor_url = meta_data_custom_config.get("monitor_url") or monitor_url
                url = f"{monitor_url}/rest/v2/grafana/time_series/unify_query/"
                response = requests.post(url=url, data=json.dumps(params), headers=self.request_headers, verify=False)
                if response.status_code != 200:
                    self.append_error_info(f"task name: {task_name} have error : {response.text}")
                    continue
                series = response.json().get("series", [])
                if not series:
                    self.append_error_info(f"task name: {task_name} not have execute history")
                    continue
                datapoints = series[0].get("datapoints", [])
                if not datapoints:
                    self.append_error_info(f"task name: {task_name} not have execute history")
                    continue
                if len(datapoints) != int(TimeEnum.ONE_HOUR_SECOND.value / TimeEnum.ONE_MINUTE_SECOND.value):
                    self.append_error_info(f"task name: {task_name} execute have omissions")
            except Exception as e:
                self.append_error_info(str(e))
                continue

    @staticmethod
    def _build_unify_query_params(task_name):
        end_time = int(time.time())
        start_time = end_time - TimeEnum.ONE_HOUR_SECOND.value

        return {
            "bk_biz_id": settings.BLUEKING_BK_BIZ_ID,
            "query_configs": [
                {
                    "data_source_label": "custom",
                    "data_type_label": "time_series",
                    "metrics": [{"field": "bkmonitor_cron_task_execute_count_total", "method": "AVG", "alias": "a"}],
                    "table": "custom_report_aggate.base",
                    "index_set_id": None,
                    "group_by": ["task_name"],
                    "where": [{"key": "task_name", "method": "eq", "value": [task_name]}],
                    "interval": TimeEnum.ONE_MINUTE_SECOND.value,
                    "interval_unit": "s",
                    "time_field": None,
                    "filter_dict": {},
                    "functions": [],
                }
            ],
            "expression": "a",
            "alias": "a",
            "name": "AVG(bkmonitor_cron_task_execute_count_total)",
            "start_time": start_time,
            "end_time": end_time,
            "slimit": 500,
            "down_sample_range": "4s",
        }
