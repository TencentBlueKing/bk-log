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
from django.utils.translation import ugettext as _

from home_application.handlers.metrics import register_healthz_metric, HealthzMetric
from home_application.utils.kafka import KafkaClient


class KafkaMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="Kafka", description=_("Kafka consumer group offsets"))
    def get_offsets():
        data = []
        consumer_groups = KafkaClient.get_instance().get_consumer_groups()
        if not consumer_groups:
            return data
        for group in consumer_groups:
            group_name = group[0]
            status = False
            consumer_offsets = KafkaClient.get_instance().get_consumer_group_offsets(group_name=group_name)
            if not consumer_offsets:
                data.append(HealthzMetric(status=status, metric_name="consumer_offsets", metric_value=0, dimensions={}))
                continue
            for topic_partition, offset_metadata in consumer_offsets.items():
                topic = topic_partition.topic
                partition = topic_partition.partition
                offset = offset_metadata.offset
                status = True
                data.append(
                    HealthzMetric(
                        status=status,
                        metric_name="consumer_offsets",
                        metric_value=offset,
                        dimensions={"topic": topic, "partition": partition},
                    )
                )

        return data
