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
from collections import defaultdict

import settings

logger = logging.getLogger()

HEALTHZ_REGISTERED_METRICS = defaultdict(list)


def register_healthz_metric(namespace: str, description: str = ""):
    """
    注册healthz健康检查metric
    """

    def wrapped_view(func):
        def _wrapped_view(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        if not settings.USE_REDIS and namespace == "Redis":
            return

        HEALTHZ_REGISTERED_METRICS[namespace].append(
            {"namespace": namespace, "description": description, "method": wraps(func)(_wrapped_view)}
        )

        return wraps(func)(_wrapped_view)

    return wrapped_view


class HealthzMetric(object):
    """健康检查指标类"""

    def __init__(self, status: bool, metric_name: str, metric_value: str, dimensions: dict = None):
        self.status = status
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.dimensions = dimensions

    def to_dict(self, namespace) -> dict:
        return {
            "status": self.status,
            "namespace": namespace,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "dimensions": self.dimensions,
        }


class HealthzMetricCollector(object):
    """
    健康检查指标采集器
    """

    def __init__(self, import_paths=None):
        if import_paths:
            for key in import_paths:
                importlib.import_module(key)

    def collect(self, include_namespaces=None, exclude_namespaces=None) -> defaultdict(list):
        """
        采集入口
        """
        namespace_metric_datas = defaultdict(list)
        register_namespace_metrics = self.metric_filter(
            include_namespaces=include_namespaces, exclude_namespaces=exclude_namespaces
        )
        metric_groups = []
        for namespace in register_namespace_metrics:
            for metric in register_namespace_metrics[namespace]:
                try:
                    begin_time = time.time()
                    metric_group = {
                        "namespace": metric["namespace"],
                        "description": metric["description"],
                        "metrics": metric["method"](),
                    }
                    logger.info(
                        "[healthz_data] collect metric [{}] took {} ms".format(
                            metric["namespace"], int((time.time() - begin_time) * 1000)
                        ),
                    )
                    metric_groups.append(metric_group)
                except Exception as e:  # pylint: disable=broad-except
                    logger.exception("[healthz_data] collect metric [{}] failed: {}".format(metric["namespace"], e))

        for group in metric_groups:
            for metric in group["metrics"]:
                metric = metric.to_dict(namespace=group["namespace"])
                namespace_metric_datas[group["namespace"]].append(metric)

        return namespace_metric_datas

    @classmethod
    def metric_filter(cls, include_namespaces=None, exclude_namespaces=None) -> defaultdict(list):
        metrics = defaultdict(list)
        for namespace in HEALTHZ_REGISTERED_METRICS:
            if exclude_namespaces and namespace not in exclude_namespaces:
                metrics[namespace].extend(HEALTHZ_REGISTERED_METRICS[namespace])
                continue
            if include_namespaces:
                if namespace in include_namespaces:
                    metrics[namespace].extend(HEALTHZ_REGISTERED_METRICS[namespace])
                continue
            metrics[namespace].extend(HEALTHZ_REGISTERED_METRICS[namespace])

        return metrics
