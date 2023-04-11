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

from home_application.handlers.metrics import register_healthz_metric, HealthzMetric, NamespaceData
from home_application.utils.rabbitmq import RabbitMQClient
from home_application.constants import QUEUES


class RabbitMQMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="rabbitmq")
    def check():
        namespace_data = NamespaceData(namespace="rabbitmq", status=False, data=[])
        if not settings.BROKER_URL.startswith("amqp://"):
            namespace_data.status = True
            namespace_data.message = _("没有使用rabbitmq作为broker, 跳过该检查")
            return namespace_data

        ping_result = RabbitMQMetric().ping()
        namespace_data.data.append(ping_result)
        if ping_result.status:
            namespace_data.status = True
        else:
            namespace_data.message = ping_result.message
            return namespace_data

        queue_len_result = RabbitMQMetric().get_queue_data()
        namespace_data.data.extend(queue_len_result)
        if not all([i.status for i in queue_len_result]):
            namespace_data.status = False
            namespace_data.message = "queue_len is out of limit"

        return namespace_data

    @staticmethod
    def ping():
        result = RabbitMQClient().get_instance().ping()
        return HealthzMetric(
            status=result["status"],
            metric_name="ping",
            metric_value=result["data"],
            message=result["message"],
            suggestion=result["suggestion"],
        )

    @staticmethod
    def get_queue_data():
        data = []
        for queue_name in QUEUES:
            result = RabbitMQClient.get_instance().queue_len(queue_name)
            data.append(
                HealthzMetric(
                    status=result["status"],
                    metric_value=result["data"],
                    message=result["message"],
                    metric_name="queue_len",
                    dimensions={"queue_name": queue_name},
                )
            )

        return data
