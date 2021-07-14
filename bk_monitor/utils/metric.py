# -*- coding: utf-8 -*-
from functools import wraps

from django.conf import settings

from bk_monitor.constants import TimeFilterEnum

REGISTERED_METRICS = []


def register_metric(namespace, data_name, description="", time_filter=TimeFilterEnum.MINUTE1):
    """
    注册对应metric
    """

    def wrapped_view(func):
        def _wrapped_view(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        REGISTERED_METRICS.append(
            {
                "namespace": namespace,
                "data_name": data_name,
                "description": description,
                "method": wraps(func)(_wrapped_view),
                "time_filter": time_filter,
            }
        )

        return wraps(func)(_wrapped_view)

    return wrapped_view


class Metric(object):
    """
    指标定义
    """

    def __init__(self, metric_name, metric_value, dimensions=None, timestamp=None):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.dimensions = dimensions
        self.timestamp = timestamp

    def to_bkmonitor_report(self, namespace=None):
        if self.dimensions:
            dimensions = {key: str(value) for key, value in self.dimensions.items()}
        else:
            dimensions = {}

        if self.timestamp:
            return {
                "metrics": {self._get_actual_metric_name(namespace): self.metric_value},
                "target": settings.APP_CODE,
                "dimension": dimensions,
                "timestamp": int(self.timestamp * 1000),
            }
        else:
            return {
                "metrics": {self._get_actual_metric_name(namespace): self.metric_value},
                "target": settings.APP_CODE,
                "dimension": dimensions,
            }

    def _get_actual_metric_name(self, namespace=None):
        if namespace:
            return "{}_{}".format(namespace, self.metric_name)
        return self.metric_name
