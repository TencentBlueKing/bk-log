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
from apps.api import GseApi
from home_application.constants import DEFAULT_BK_USERNAME, CHECK_STORY_2, KAFKA_SSL_CONFIG_ITEMS
from home_application.handlers.collector_checker.base import BaseStory

logger = logging.getLogger()


class CheckRouteStory(BaseStory):
    name = CHECK_STORY_2

    def __init__(self, bk_data_id: int):
        super().__init__()
        self.bk_data_id = bk_data_id

        self.kafka = []

    def check(self):
        self.get_route()

    def get_route(self):
        query_route_params = {
            "condition": {"channel_id": self.bk_data_id},
            "operation": {"operator_name": DEFAULT_BK_USERNAME},
        }
        try:
            query_route_data = GseApi.query_route(query_route_params)
            if query_route_data[0].get("metadata", {}).get("channel_id", 0):
                routes = query_route_data[0]["route"]
                for r in routes:
                    stream_id = r["stream_to"]["stream_to_id"]
                    query_stream_to_params = {
                        "condition": {"stream_to_id": stream_id},
                        "operation": {"operator_name": DEFAULT_BK_USERNAME},
                    }
                    try:
                        query_stream_to_data = GseApi.query_stream_to(query_stream_to_params)
                        if query_stream_to_data[0].get("stream_to_id", 0) == stream_id:
                            stream_name = query_stream_to_data[0]["name"]
                            report_mode = query_stream_to_data[0]["report_mode"]
                            if report_mode != "kafka":
                                continue
                            addrs = query_stream_to_data[0].get(report_mode, {}).get("storage_address", [])
                            if not addrs:
                                continue
                            for addr in addrs:
                                kafka_info = {
                                    "route_name": r["name"],
                                    "stream_name": stream_name,
                                    "kafka_topic_name": r["stream_to"]["kafka"]["topic_name"],
                                    "ip": addr["ip"],
                                    "port": addr["port"],
                                }
                                for item in KAFKA_SSL_CONFIG_ITEMS:
                                    if query_stream_to_data[0].get(item):
                                        kafka_info[item] = query_stream_to_data[0][item]
                                self.kafka.append(kafka_info)
                    except Exception as e:
                        message = f"[请求GseAPI] [query_stream_to] 获取stream[{stream_id}]失败, err: {e}"
                        logger.error(message)
                        self.report.add_error(message)

        except Exception as e:
            message = f"[请求GseAPI] [query_route] 获取route[bk_data_id: {self.bk_data_id}]失败, err: {e}"
            logger.error(message)
            self.report.add_error(message)

        if not self.kafka:
            self.report.add_error(f"bk_data_id[{self.bk_data_id}]对应的route为空")

        for r in self.kafka:
            self.report.add_info(
                "route_name: {}, stream_name: {}, topic_name: {}, ip: {}, port: {}".format(
                    r["route_name"], r["stream_name"], r["kafka_topic_name"], r["ip"], r["port"]
                )
            )
