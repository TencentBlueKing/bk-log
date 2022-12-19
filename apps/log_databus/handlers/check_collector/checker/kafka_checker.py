# -*- coding: utf-8 -*-
import json
import logging

from django.conf import settings
from kafka import KafkaConsumer, TopicPartition

from apps.log_databus.constants import (
    KAFKA_TEST_GROUP,
    DEFAULT_KAFKA_SECURITY_PROTOCOL,
    KAFKA_SSL_MECHANISM,
    KAFKA_SSL_USERNAME,
    KAFKA_SSL_PASSWORD,
)
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker
from home_application.constants import KAFKA_SSL_PROTOCOL

logger = logging.getLogger()


class KafkaChecker(Checker):
    CHECKER_NAME = "kafka checker"

    def __init__(self, kafka_info_list: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kafka_info_list = kafka_info_list
        self.latest_log = []

    def _run(self):
        if not self.kafka_info_list:
            self.append_normal_info("没有kafka, 跳过检查")
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
                self.append_error_info(f"获取topic[{topic}] partition信息失败")
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
            message = f"创建kafka消费者失败, err: {str(e)}"
            logger.error(message)
            self.append_error_info(message)

        if not log_content:
            self.append_error_info(f"{host}:{port}, topic: {topic}, 无数据")
        else:
            self.append_normal_info(f"{host}:{port}, topic: {topic}, 有数据")
