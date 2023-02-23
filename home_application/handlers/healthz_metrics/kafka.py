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
from home_application.handlers.metrics import register_healthz_metric, HealthzMetric, NamespaceData
from home_application.utils.kafka import KafkaClient
from django.utils.translation import ugettext_lazy as _


class KafkaMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="kafka")
    def check() -> NamespaceData:
        namespace_data = NamespaceData(namespace="kafka", status=False, data=[])
        ping_result = KafkaMetric().ping()
        namespace_data.data.append(ping_result)
        if ping_result.status:
            namespace_data.status = True
        else:
            namespace_data.message = ping_result.message
            return namespace_data

        namespace_data.data.extend(KafkaMetric().get_offsets())

        return namespace_data

    @staticmethod
    def ping():
        result = KafkaClient.get_instance().ping()
        return HealthzMetric(
            status=result["status"],
            metric_name="ping",
            metric_value=result["data"],
            message=result["message"],
            suggestion=_("确认Kafka集群是否可用"),
        )

    @staticmethod
    def get_offsets():
        data = []
        consumer_groups = KafkaClient.get_instance().get_consumer_groups()
        if not consumer_groups:
            return data
        for group in consumer_groups:
            group_name = group[0]
            consumer_offsets = KafkaClient.get_instance().get_consumer_group_offsets(group_name=group_name)
            if not consumer_offsets:
                continue
            for topic_partition, offset_metadata in consumer_offsets.items():
                topic = topic_partition.topic
                partition = topic_partition.partition
                offset = offset_metadata.offset
                data.append(
                    HealthzMetric(
                        status=True,
                        metric_name="consumer_offsets",
                        metric_value=offset,
                        dimensions={"topic": topic, "partition": partition},
                    )
                )
            # 这里break是为了节省时间, 只要有一个成功的结果就行
            break

        return data
