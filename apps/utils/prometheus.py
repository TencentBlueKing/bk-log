# -*- coding: utf-8 -*-
import os
import socket
import types

from django.conf import settings
from django_prometheus.conf import NAMESPACE
from django_prometheus.middleware import Metrics

HOSTNAME = socket.gethostname()
STAGE = os.getenv("BKPAAS_ENVIRONMENT", "dev")


def register_metric(metric_cls, name, documentation, labelnames=(), **kwargs):
    """
    Prometheus 指标注册
    """
    labelnames = [*labelnames, "hostname", "stage", "bk_app_code"]
    metric = Metrics.get_instance().register_metric(
        metric_cls, name, documentation, labelnames, namespace=NAMESPACE, **kwargs
    )

    metric._origin_labels = metric.labels

    def labels(self, *labelvalues, **labelkwargs):
        labelkwargs.update({"hostname": HOSTNAME, "stage": STAGE, "bk_app_code": settings.APP_CODE})
        return self._origin_labels(*labelvalues, **labelkwargs)

    metric.labels = types.MethodType(labels, metric)
    return metric
