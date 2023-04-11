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
from django.utils.translation import ugettext_lazy as _

from apps.api import GseApi
from apps.log_databus.constants import DEFAULT_BK_USERNAME, DEFAULT_GSE_API_PLAT_NAME, KAFKA_SSL_CONFIG_ITEMS
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker

logger = logging.getLogger()


class RouteChecker(Checker):
    CHECKER_NAME = "route checker"

    def __init__(self, bk_data_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bk_data_id = bk_data_id
        self.route = []
        self.kafka = []

    def _run(self):
        self.get_route()

    def get_route(self):
        self.query_route()
        for r in self.route:
            self.query_stream_to(r)
        if not self.kafka:
            self.append_error_info(_("bk_data_id[{bk_data_id}]对应的route为空").format(bk_data_id=self.bk_data_id))
        for r in self.kafka:
            self.append_normal_info(
                "route_name: {}, stream_name: {}, topic_name: {}, ip: {}, port: {}".format(
                    r["route_name"], r["stream_name"], r["kafka_topic_name"], r["ip"], r["port"]
                )
            )

    def query_route(self):
        params = {
            "condition": {"channel_id": self.bk_data_id},
            "operation": {"operator_name": DEFAULT_BK_USERNAME},
        }
        try:
            data = GseApi.query_route(params)
            if data[0].get("metadata", {}).get("channel_id", 0):
                self.route = data[0]["route"]
        except Exception as e:
            message = _("[请求GseAPI] [query_route] 获取route[bk_data_id: {bk_data_id}]失败, err: {e}").format(
                bk_data_id=self.bk_data_id, e=e
            )
            logger.error(message)
            self.append_error_info(message)

    def query_stream_to(self, route_info):
        stream_id = route_info["stream_to"]["stream_to_id"]
        params = {
            "condition": {"stream_to_id": stream_id, "plat_name": DEFAULT_GSE_API_PLAT_NAME},
            "operation": {"operator_name": DEFAULT_BK_USERNAME},
        }
        try:
            data = GseApi.query_stream_to(params)
            if data[0].get("metadata", {}).get("stream_to_id", 0) == stream_id:
                stream_to = data[0].get("stream_to", {})
                stream_name = stream_to["name"]
                report_mode = stream_to["report_mode"]
                if report_mode != "kafka":
                    return
                addrs = stream_to.get(report_mode, {}).get("storage_address", [])
                if not addrs:
                    return
                for addr in addrs:
                    kafka_info = {
                        "route_name": route_info["name"],
                        "stream_name": stream_name,
                        "kafka_topic_name": route_info["stream_to"]["kafka"]["topic_name"],
                        "ip": addr["ip"],
                        "port": addr["port"],
                    }
                    for item in KAFKA_SSL_CONFIG_ITEMS:
                        if data[0].get(item):
                            kafka_info[item] = data[0][item]
                    self.kafka.append(kafka_info)
        except Exception as e:
            message = _("[请求GseAPI] [query_stream_to] 获取stream[{stream_id}]失败, err: {e}").format(
                stream_id=stream_id, e=e
            )
            logger.error(message)
            self.append_error_info(message)
