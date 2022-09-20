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

from kafka import KafkaConsumer, TopicPartition

from django.conf import settings
from apps.log_databus.exceptions import KafkaPartitionException, KafkaConnectException


class KafkaConsumerHandle(object):
    def __init__(self, server, port, topic, username=None, password=None):
        self.server = server
        self.port = int(port)
        self.topic = topic
        self.kafka_server = server + ":" + str(port)
        try:
            if username:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.kafka_server,
                    security_protocol="SASL_PLAINTEXT",
                    sasl_mechanism="PLAIN",
                    sasl_plain_username=username,
                    sasl_plain_password=password,
                    request_timeout_ms=1000,
                    consumer_timeout_ms=1000,
                )
                return
            self.consumer = KafkaConsumer(
                self.topic, bootstrap_servers=self.kafka_server, request_timeout_ms=1000, consumer_timeout_ms=1000
            )
        except Exception as e:  # pylint: disable=broad-except
            raise KafkaConnectException(KafkaConnectException.MESSAGE.format(error=e))

    def get_latest_log(self):
        """
        读取kafka的数据
        :return:
        """
        message_count = 10
        self.consumer.poll(settings.DEFAULT_KAFKA_POLL_TIMEOUT)

        # 获取topic分区信息
        topic_partitions = self.consumer.partitions_for_topic(self.topic)
        if not topic_partitions:
            raise KafkaPartitionException()

        log_content = []
        for _partition in topic_partitions:

            # 获取该分区最大偏移量
            tp = TopicPartition(topic=self.topic, partition=_partition)
            end_offset = self.consumer.end_offsets([tp])[tp]
            if not end_offset:
                continue

            # 设置消息消费偏移量
            if end_offset >= message_count:
                self.consumer.seek(tp, end_offset - message_count)
            else:
                self.consumer.seek_to_beginning()

            # 消费消息
            for _msg in self.consumer:
                try:
                    log_content.insert(0, json.loads(_msg.value.decode()))
                except Exception:  # pylint: disable=broad-except
                    pass
                if len(log_content) == message_count:
                    self.consumer.close()
                    return log_content
                if _msg.offset == end_offset - 1:
                    break

        self.consumer.close()
        return log_content
