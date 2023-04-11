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
from django.utils.translation import ugettext_lazy as _

import requests
from django.conf import settings

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import CHECK_COLLECTOR_CUSTOM_CONFIG
from apps.log_databus.constants import EtlConfig, TRANSFER_METRICS, TABLE_TRANSFER
from apps.log_search.constants import TimeEnum
from config.domains import MONITOR_APIGATEWAY_ROOT
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import CleanStash
from bk_monitor.api.client import Client

logger = logging.getLogger()


class TransferChecker(Checker):
    CHECKER_NAME = "transfer checker"

    def __init__(self, collector_config, latest_log, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector_config_id = collector_config.collector_config_id
        self.bk_data_id = collector_config.bk_data_id
        self.latest_log = latest_log
        self.etl_config = collector_config.etl_config
        try:
            clean_stash = CleanStash.objects.get(collector_config_id=self.collector_config_id)
            self.etl_params = clean_stash.etl_params
        except CleanStash.DoesNotExist:
            self.etl_params = None

    def _run(self):
        if not self.latest_log:
            self.append_normal_info(_("kafka内没有数据, 跳过清洗检查"))
        else:
            self.clean_data()
        self.get_metrics()

    def clean_data(self):
        if self.etl_config == EtlConfig.BK_LOG_TEXT or not self.etl_config:
            self.append_normal_info(_("[测试清洗] 无清洗规则, 跳过检查清洗"))
            return
        etl_storage = EtlStorage.get_instance(etl_config=self.etl_config)
        success_count = 0
        for data in self.latest_log:
            fields = etl_storage.etl_preview(data, self.etl_params)
            if fields:
                self.append_normal_info(_("[测试清洗] data: [{fields}]").format(fields=fields))
                success_count += 1
        if success_count == 0:
            self.append_error_info(_("[测试清洗] 清洗数据失败"))

    def get_metrics(self):
        for metric_name in TRANSFER_METRICS:
            self.get_transfer_metric(metric_name)

    def get_transfer_metric(self, metric_name: str):
        app_code = settings.APP_CODE
        app_secret = settings.SECRET_KEY
        monitor_host = MONITOR_APIGATEWAY_ROOT

        if FeatureToggleObject.switch(CHECK_COLLECTOR_CUSTOM_CONFIG):
            transfer_custom_config = FeatureToggleObject.toggle(CHECK_COLLECTOR_CUSTOM_CONFIG).feature_config.get(
                "transfer_custom_config", {}
            )
            if not transfer_custom_config:
                return
            monitor_host = transfer_custom_config.get("monitor_host")
            bk_token = transfer_custom_config.get("bk_token")
            bk_biz_id = transfer_custom_config.get("bk_biz_id")

            end_time = int(time.time())
            start_time = end_time - TimeEnum.FIVE_MINUTE_SECOND.value
            params_temp = {
                "down_sample_range": "1m",
                "step": "auto",
                "start_time": start_time,
                "end_time": end_time,
                "expression": "a",
                "display": True,
                "query_configs": [
                    {
                        "data_source_label": "bk_monitor",
                        "data_type_label": "time_series",
                        "metrics": [{"field": metric_name, "method": "SUM", "alias": "a"}],
                        "table": "",
                        "group_by": [],
                        "display": True,
                        "where": [{"key": "id", "method": "eq", "value": [self.bk_data_id]}],
                        "interval": TimeEnum.ONE_MINUTE_SECOND.value,
                        "interval_unit": "s",
                        "time_field": "time",
                        "filter_dict": {},
                        "functions": [],
                    }
                ],
                "target": [],
                "bk_biz_id": bk_biz_id,
            }

            headers = {"Content-Type": "application/json", "Cookie": f"bk_token={bk_token}"}

            try:
                response = requests.post(
                    url=monitor_host + "time_series/unify_query/", data=json.dumps(params_temp), headers=headers
                )

                result = response.json()

                if not result["result"]:
                    message = _("[请求监控接口] [unify query] 获取 {metric_name} 数据失败, err: {err}").format(
                        metric_name=metric_name, err=result["message"]
                    )
                    logger.error(message)
                    self.append_warning_info(message)
                    return

                series = result["data"].get("series", [])
                if not series:
                    message = _("[请求监控接口] [unify query] 获取 {metric_name} 数据为空").format(metric_name=metric_name)
                    self.append_warning_info(message)
                    return

                value, __ = series[0]["datapoints"][-1]
                self.append_normal_info(
                    _("[请求监控接口] [unify query] {metric_name}: {value}").format(metric_name=metric_name, value=value)
                )
            except Exception as e:
                message = _("[请求监控接口] [unify query] 获取 {metric_name} 数据失败, err: {e}").format(
                    metric_name=metric_name, e=e
                )
                logger.error(message)
                self.append_warning_info(message)
        else:
            bk_monitor_client = Client(
                bk_app_code=app_code,
                bk_app_secret=app_secret,
                monitor_host=monitor_host,
                report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
                bk_username="admin",
            )
            params = {
                "sql": f"select sum({metric_name}) as {metric_name} from {TABLE_TRANSFER} \
                where time >= '1m' and id == {self.bk_data_id}"
            }
            try:
                result = bk_monitor_client.get_ts_data(data=params)
                for ts_data in result["list"]:
                    value = ts_data[metric_name]
                    if ts_data["id"] == self.bk_data_id:
                        self.append_normal_info(
                            _("[请求监控接口] [get_ts_data] {metric_name}: {value}").format(
                                metric_name=metric_name, value=value
                            )
                        )
                        return
                message = _("[请求监控接口] [get_ts_data] 获取 {metric_name} 数据为空").format(metric_name=metric_name)
                self.append_warning_info(message)

            except Exception as e:
                message = _("[请求监控接口] [get_ts_data] 获取 {metric_name} 数据失败, err: {e}").format(
                    metric_name=metric_name, e=e
                )
                logger.error(message)
                self.append_warning_info(message)
