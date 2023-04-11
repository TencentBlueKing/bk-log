# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import importlib
import time
import logging
import arrow

from bk_monitor.utils.metric import REGISTERED_METRICS

logger = logging.getLogger("bk_monitor")


class MetricCollector(object):
    """
    实际采集
    """

    def __init__(self, collector_import_paths=None):
        if collector_import_paths and not REGISTERED_METRICS:
            for key in collector_import_paths:
                importlib.reload(importlib.import_module(key))

    def collect(self, namespaces=None, data_names=None, time_filter_enable=True):
        """
        采集入口
        """
        metric_methods = self.metric_filter(
            namespaces=namespaces, time_filter_enable=time_filter_enable, data_names=data_names
        )
        metric_groups = []
        for metric_method in metric_methods:
            try:
                begin_time = time.time()
                metric_groups.append(
                    {
                        "prefix": metric_method["prefix"],
                        "namespace": metric_method["namespace"],
                        "description": metric_method["description"],
                        "metrics": metric_method["method"](),
                        "data_name": metric_method["data_name"],
                    }
                )
                logger.info(
                    "[statistics_data] collect metric->[{}] took {} ms".format(
                        metric_method["namespace"], int((time.time() - begin_time) * 1000)
                    ),
                )
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(
                    "[statistics_data] collect metric->[{}] failed: {}".format(metric_method["namespace"], e)
                )

        return metric_groups

    @classmethod
    def metric_filter(cls, namespaces=None, data_names=None, time_filter_enable=True):
        metric_methods = []
        time_now = arrow.now()
        time_now_minute = 60 * time_now.hour + time_now.minute
        for metric_id, metric in REGISTERED_METRICS.items():
            if data_names and metric["data_name"] not in data_names:
                continue

            if namespaces and metric["namespace"] not in namespaces:
                continue

            # 如果register_metric 有设置time_filter字段以及该字段符合当前时间所属周期才会被添加
            if time_filter_enable and metric["time_filter"] and time_now_minute % metric["time_filter"]:
                continue
            metric_methods.append(metric)
        return metric_methods
