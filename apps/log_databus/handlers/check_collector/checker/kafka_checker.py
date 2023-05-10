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
from django.utils.translation import ugettext as _

from django.conf import settings
from kafka import KafkaConsumer, TopicPartition

from apps.log_databus.constants import (
    KAFKA_TEST_GROUP,
    DEFAULT_KAFKA_SECURITY_PROTOCOL,
    KAFKA_SSL_MECHANISM,
    KAFKA_SSL_USERNAME,
    KAFKA_SSL_PASSWORD,
    KAFKA_SSL_PROTOCOL,
)
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker

logger = logging.getLogger()


class KafkaChecker(Checker):
    CHECKER_NAME = "kafka checker"

    def __init__(self, kafka_info_list: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kafka_info_list = kafka_info_list
        self.latest_log = []

    def _run(self):
        if not self.kafka_info_list:
            self.append_normal_info(_("没有kafka, 跳过检查"))
            return
        for kafka_info in self.kafka_info_list:
            self.get_kafka_test_group_latest_log(kafka_info)

    def get_kafka_test_group_latest_log(self, kafka_info: dict):
        """
        使用测试消费组, 判断kafka指定的[topic:partition]是否有数据
        """
        log_content = []
        host = kafka_info.get("ip", settings.DEFAULT_KAFKA_HOST)
        if "consul" in host and settings.DEFAULT_KAFKA_HOST:
            host = settings.DEFAULT_KAFKA_HOST
        port = kafka_info.get("port", 9092)
        topic = kafka_info.get("kafka_topic_name", "")
        try:
            consumer = KafkaConsumer(
                topic,
                group_id=KAFKA_TEST_GROUP,
                bootstrap_servers=f"{host}:{port}",
                security_protocol=kafka_info.get(KAFKA_SSL_PROTOCOL, DEFAULT_KAFKA_SECURITY_PROTOCOL),
                sasl_mechanism=kafka_info.get(KAFKA_SSL_MECHANISM, None),
                sasl_plain_username=kafka_info.get(KAFKA_SSL_USERNAME, None),
                sasl_plain_password=kafka_info.get(KAFKA_SSL_PASSWORD, None),
            )

            message_count = 10
            consumer.poll(message_count)

            # 获取topic分区信息
            topic_partitions = consumer.partitions_for_topic(topic)
            if not topic_partitions:
                self.append_error_info(_("获取topic[{topic}] partition信息失败").format(topic=topic))
                return

            for _partition in topic_partitions:
                # 获取该分区最大偏移量
                tp = TopicPartition(topic=topic, partition=_partition)
                end_offset = consumer.end_offsets([tp])[tp]
                if not end_offset:
                    continue

                # 设置消息消费偏移量
                if end_offset >= message_count:
                    consumer.seek(tp, end_offset - message_count)
                else:
                    consumer.seek_to_beginning()

                # 消费消息
                for _msg in consumer:
                    try:
                        log_content.insert(0, json.loads(_msg.value.decode()))
                    except Exception as e:  # pylint: disable=broad-except
                        logger.error(f"消费数据失败, err: {str(e)}")
                    if len(log_content) == message_count:
                        self.latest_log.extend(log_content)
                        consumer.close()
                        return
                    if _msg.offset == end_offset - 1:
                        break

            consumer.close()

        except Exception as e:  # pylint: disable=broad-except
            message = _("创建kafka消费者失败, err: {e}").format(e=e)
            logger.error(message)
            self.append_error_info(message)

        if not log_content:
            self.append_error_info(_("{host}:{port}, topic: {topic}, 无数据").format(host=host, port=port, topic=topic))
        else:
            self.append_normal_info(_("{host}:{port}, topic: {topic}, 有数据").format(host=host, port=port, topic=topic))
