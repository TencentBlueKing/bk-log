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
from home_application.constants import REDIS_VARIABLES, QUEUES
from home_application.utils.redis import RedisClient


class RedisMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="Redis", description=_("Redis INFO"))
    def get_variables():
        data = []
        for varieable_name in REDIS_VARIABLES:
            status = False
            metric_value = RedisClient.get_instance().get_variables(varieable_name)
            if metric_value:
                status = True
            data.append(
                HealthzMetric(status=status, metric_name=varieable_name, metric_value=metric_value, dimensions={})
            )

        return data

    @staticmethod
    @register_healthz_metric(namespace="Redis", description=_("Redis PING"))
    def ping():
        data = []
        status = False
        metric_value = RedisClient.get_instance().ping()
        if metric_value:
            status = True
        data.append(HealthzMetric(status=status, metric_name="ping", metric_value=metric_value, dimensions={}))
        return data

    @staticmethod
    @register_healthz_metric(namespace="Redis", description=_("Redis HIT RATE"))
    def hit_rate():
        data = []
        status = False
        metric_value = RedisClient.get_instance().hit_rate()
        if metric_value:
            status = True
        data.append(HealthzMetric(status=status, metric_name="hit_rate", metric_value=metric_value, dimensions={}))
        return data

    @staticmethod
    @register_healthz_metric(namespace="Redis", description=_("Redis QUEUE"))
    def queue():
        data = []
        if not settings.BROKER_URL.startswith("redis://"):
            return data
        for queue_name in QUEUES:
            status = False
            metric_value = RedisClient.get_instance().queue_len(queue_name)
            # 队列长度可能为0
            if metric_value is not None:
                status = True
            data.append(
                HealthzMetric(
                    status=status,
                    metric_name="queue_len",
                    metric_value=metric_value,
                    dimensions={"queue_name": queue_name},
                )
            )

        return data
