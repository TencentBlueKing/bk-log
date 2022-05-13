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
from __future__ import absolute_import, unicode_literals
from functools import wraps
import importlib
import time
import logging

logger = logging.getLogger()

HEALTHZ_REGISTERED_METRICS = []


def register_healthz_metric(namespace: str, metric_name: str, description: str=""):
    """
    注册healthz健康检查metric
    """
    def wrapped_view(func):
        def _wrapped_view(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        HEALTHZ_REGISTERED_METRICS.append(
            {
                "namespace": namespace,
                "metric_name": metric_name,
                "description": description,
                "method": wraps(func)(_wrapped_view)
            }
        )

        return wraps(func)(_wrapped_view)

    return wrapped_view


class HealthzMetric(object):
    def __init__(self, metric_name, metric_value, dimensions=None, timestamp=None):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.dimensions = dimensions
        self.timestamp = timestamp

    def to_report(self, namespace=None):
        if self.dimensions:
            dimensions = {key: str(value) for key, value in self.dimensions.items()}
        else:
            dimensions = {}

        return {
            "metric_name": self._get_actual_metric_name(namespace),
            "metric_value": self.metric_value,
            "dimension": dimensions,
            "timestamp": self.timestamp,
        }

    def _get_actual_metric_name(self, namespace=None):
        if namespace:
            return "{}/{}".format(namespace, self.metric_name)
        return self.metric_name


class HealthzMetricCollector(object):
    """
    健康检查指标采集器
    """

    def __init__(self, import_paths=None):
        if import_paths:
            for key in import_paths:
                importlib.import_module(key)

    def collect(self, include_namespaces=None, exclude_namespaces=None) -> list:
        """
        采集入口
        """
        metric_datas = []
        register_metrics = self.metric_filter(
            include_namespaces=include_namespaces, exclude_namespaces=exclude_namespaces
        )
        metric_groups = []
        for metric in register_metrics:
            try:
                begin_time = time.time()
                metric_groups.append(
                    {
                        "namespace": metric["namespace"],
                        "metric_name": metric["metric_name"],
                        "description": metric["description"],
                        "metrics": metric["method"](),
                    }
                )
                logger.info(
                    "[healthz_data] collect metric [{}]-[{}] took {} ms".format(
                        metric["namespace"], metric["metric_name"], int((time.time() - begin_time) * 1000)
                    ),
                )
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(
                    "[healthz_data] collect metric [{}]-[{}] failed: {}".format(
                        metric["namespace"], metric["metric_name"], e
                    )
                )

        for group in metric_groups:
            for metric in group["metrics"]:
                metric_datas.append(metric.to_report(namespace=group["namespace"]))

        return metric_datas

    @classmethod
    def metric_filter(cls, include_namespaces=None, exclude_namespaces=None):
        metrics = []
        for metric in HEALTHZ_REGISTERED_METRICS:
            if exclude_namespaces and metric["namespace"] not in exclude_namespaces:
                metrics.append(metric)
            if include_namespaces and metric["namespace"] in include_namespaces:
                metrics.append(metric)
                continue
            metrics.append(metric)

        return metrics
