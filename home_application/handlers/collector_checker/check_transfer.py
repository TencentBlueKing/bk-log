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
from collections import defaultdict

from django.conf import settings
from config.domains import MONITOR_APIGATEWAY_ROOT
from apps.log_databus.handlers.etl_storage import EtlStorage
from bk_monitor.api.client import Client
from home_application.constants import CHECK_STORY_4, TABLE_TRANSFER, TRANSFER_METRICS
from home_application.handlers.collector_checker.base import BaseStory

logger = logging.getLogger()


class CheckTransferStory(BaseStory):
    name = CHECK_STORY_4

    def __init__(self, bk_data_id: int, latest_log: list = None, etl_config: str = "", etl_params: dict = None):
        super().__init__()
        self.bk_data_id = bk_data_id
        self.latest_log = latest_log
        self.etl_config = etl_config
        self.etl_params = etl_params

    def clean_data(self):
        etl_storage = EtlStorage.get_instance(etl_config=self.etl_config)
        success_count = 0
        for data in self.latest_log:
            fields = etl_storage.etl_preview(data, self.etl_params)
            if fields:
                self.report.add_info(f"[Transfer] [etl_preview] data: [{fields}]")
                success_count += 1
        if success_count == 0:
            self.report.add_error("[Transfer] [etl_preview] 清洗数据失败")

    def get_metrics(self):
        datas = []
        for metric_name in TRANSFER_METRICS:
            datas.append(self.get_transfer_metric(self.bk_data_id, metric_name))

    @staticmethod
    def get_transfer_metric(bk_data_id: int, metric_name: str):
        data = defaultdict(lambda: defaultdict(int))
        bk_monitor_client = Client(
            bk_app_code=settings.APP_CODE,
            bk_app_secret=settings.SECRET_KEY,
            monitor_host=MONITOR_APIGATEWAY_ROOT,
            report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
            bk_username="admin",
        )
        params = {
            "sql": f"select sum({metric_name}) as {metric_name} from {TABLE_TRANSFER} \
            where time >= '5m' and bk_data_id == {bk_data_id} group by task_data_id,target"
        }
        try:
            result = bk_monitor_client.get_ts_data(data=params)
            for ts_data in result["list"]:
                value = ts_data[metric_name]
                target = ts_data["target"]
                task_data_id = ts_data["task_data_id"]
                data[target][task_data_id] = value

        except Exception as e:
            message = f"[Transfer] [get_ts_data] 获取 {metric_name} 数据失败, err: {e}"
            logger.error(message)

        return data
