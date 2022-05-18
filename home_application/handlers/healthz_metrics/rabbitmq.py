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
import settings

from django.utils.translation import ugettext as _

from home_application.handlers.metrics import register_healthz_metric, HealthzMetric
from home_application.utils.rabbitmq import RabbitMQClient
from home_application.constants import QUEUES


class RabbitMQMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="RabbitMQ", description=_("RabbitMQ QUEUE"))
    def get_queue_data():
        data = []
        if not settings.BROKER_URL.startswith("amqp://"):
            return data

        queues = RabbitMQClient().get_queues()
        if queues is None:
            data.append(HealthzMetric(status=False, metric_name="queue_len", metric_value=0, dimensions={}))
            return data

        for queue in queues:
            if queue["name"] not in QUEUES:
                continue
            for item in ["messages", "messages_ready", "messages_unacknowledged"]:
                value = queue.get(item, 0)
                data.append(
                    HealthzMetric(
                        status=True,
                        metric_name=f"queue_{item}_len",
                        metric_value=value,
                        dimensions={"vhost": queue["vhost"], "queue": queue["name"]},
                    )
                )

        return data
