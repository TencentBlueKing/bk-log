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
import logging

from django.conf import settings

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import CHECK_COLLECTOR_TRANSFER_URL
from apps.log_databus.constants import EtlConfig, TRANSFER_METRICS, TABLE_TRANSFER
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
            self.append_normal_info("kafka内没有数据, 跳过清洗检查")
        else:
            self.clean_data()
        self.get_metrics()

    def clean_data(self):
        if self.etl_config == EtlConfig.BK_LOG_TEXT or not self.etl_config:
            self.append_normal_info("[测试清洗] 无清洗规则, 跳过检查清洗")
            return
        etl_storage = EtlStorage.get_instance(etl_config=self.etl_config)
        success_count = 0
        for data in self.latest_log:
            fields = etl_storage.etl_preview(data, self.etl_params)
            if fields:
                self.append_normal_info(f"[测试清洗] data: [{fields}]")
                success_count += 1
        if success_count == 0:
            self.append_error_info("[测试清洗] 清洗数据失败")

    def get_metrics(self):
        for metric_name in TRANSFER_METRICS:
            self.get_transfer_metric(metric_name)

    def get_transfer_metric(self, metric_name: str):
        monitor_host = MONITOR_APIGATEWAY_ROOT

        if FeatureToggleObject.switch(CHECK_COLLECTOR_TRANSFER_URL):
            monitor_host = FeatureToggleObject.toggle(CHECK_COLLECTOR_TRANSFER_URL).feature_config or monitor_host

        bk_monitor_client = Client(
            bk_app_code=settings.APP_CODE,
            bk_app_secret=settings.SECRET_KEY,
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
                    self.append_normal_info(f"[请求监控接口] [get_ts_data] {metric_name}: {value}")
                    return
            message = f"[请求监控接口] [get_ts_data] 获取 {metric_name} 数据为空"
            self.append_warning_info(message)

        except Exception as e:
            message = f"[请求监控接口] [get_ts_data] 获取 {metric_name} 数据失败, err: {e}"
            logger.error(message)
            self.append_warning_info(message)
