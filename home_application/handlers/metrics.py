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

from django.utils.translation import ugettext as _

from home_application.constants import HEALTHZ_METRICS_IMPORT_PATHS

logger = logging.getLogger()

HEALTHZ_REGISTERED_METRICS = dict()


def register_healthz_metric(namespace: str):
    """
    注册healthz健康检查metric
    """

    def wrapped_view(func):
        def _wrapped_view(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        HEALTHZ_REGISTERED_METRICS[namespace] = wraps(func)(_wrapped_view)

        return wraps(func)(_wrapped_view)

    return wrapped_view


class HealthzMetric(object):
    """健康检查指标, 单个数据类"""

    def __init__(
        self,
        status: bool,
        metric_name: str,
        metric_value: str = "",
        dimensions: dict = None,
        message: str = "",
        suggestion: str = "",
    ):
        self.status = status
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.dimensions = dimensions
        self.message = message
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "dimensions": self.dimensions,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class NamespaceData(object):
    """Namespace级别的数据类"""

    def __init__(self, namespace: str, status: bool = False, data: list = None, message: str = "ok") -> None:
        self.namespace = namespace
        self.status = status
        self.data = data if data else []
        self.message = message

    def to_dict(self):
        dict_datas = []
        for i in self.data:
            dict_datas.append(i.to_dict())

        return {"namespace": self.namespace, "status": self.status, "data": dict_datas, "message": self.message}


class HealthzMetricCollector(object):
    """健康检查指标采集器"""

    def __init__(self, include_namespaces: list = None, exclude_namespaces: list = None):
        self.register_metrics = defaultdict(list)
        self.data = {"status": False, "data": defaultdict(dict), "message": ""}
        for key in HEALTHZ_METRICS_IMPORT_PATHS:
            importlib.import_module(key)
        if include_namespaces:
            for namespace in include_namespaces:
                if HEALTHZ_REGISTERED_METRICS.get(namespace):
                    self.register_metrics[namespace] = HEALTHZ_REGISTERED_METRICS[namespace]
                else:
                    self.data["data"][namespace] = NamespaceData(
                        namespace=namespace, message=_(f"不支持的命名空间[{namespace}]")
                    )
            return
        for namespace in HEALTHZ_REGISTERED_METRICS:
            if namespace in exclude_namespaces:
                continue
            self.register_metrics[namespace] = HEALTHZ_REGISTERED_METRICS[namespace]

    def collect(self) -> defaultdict(list):
        """
        采集入口
        """
        for namespace in self.register_metrics:
            try:
                begin_time = time.time()
                namespace_data = self.register_metrics[namespace]()
                logger.info(
                    "[healthz_data] collect metric [{}] took {} ms".format(
                        namespace, int((time.time() - begin_time) * 1000)
                    ),
                )
                self.data["data"][namespace] = namespace_data.to_dict()
            except Exception as e:  # pylint: disable=broad-except
                logger.exception("[healthz_data] collect metric [{}] failed: {}".format(namespace, e))

        if self.data["data"]:
            self.data["status"] = [i["status"] for i in self.data["data"].values()].count(True) == len(
                self.data["data"]
            )
        if self.data["status"]:
            self.data["message"] = "health check success"
        else:
            failed_namespaces = []
            for namespace, value in self.data["data"].items():
                if not value["status"]:
                    failed_namespaces.append(namespace)
            self.data["message"] = "health check failed, please check these namespace: {}".format(
                ",".join(failed_namespaces)
            )

        return self.data
