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
import datetime
from collections import defaultdict

import arrow
from django.db.models import Count

from django.utils.translation import ugettext as _
from django.conf import settings

from apps.log_databus.models import CollectorConfig, ArchiveConfig
from apps.log_search.models import UserIndexSetSearchHistory, LogIndexSet, Scenario
from apps.log_extract.models import Tasks
from apps.log_clustering.models import ClusteringConfig
from apps.log_measure.constants import TIME_RANGE, INDEX_SCENARIO
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


FUNCTION_MODEL = {
    "log_collector": CollectorConfig,
    "log_archive": ArchiveConfig,
    "log_extract": Tasks,
    "log_clustering": ClusteringConfig,
}


class BusinessMetricCollector(object):
    @staticmethod
    @register_metric(
        "business_active", prefix="bklog", description=_("活跃业务"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def business_active():
        metrics = []
        for timedelta in TIME_RANGE:
            metrics.extend(BusinessMetricCollector().business_active_by_time_range(timedelta))

        return metrics

    @staticmethod
    def business_active_by_time_range(timedelta: str):
        # 一个星期内检索过日志的，才被认为是活跃业务
        end_time = (
            arrow.get(MetricUtils.get_instance().report_ts).to(settings.TIME_ZONE).strftime("%Y-%m-%d %H:%M:%S%z")
        )
        timedelta_v = TIME_RANGE[timedelta]
        start_time = (
            datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S%z") - datetime.timedelta(minutes=timedelta_v)
        ).strftime("%Y-%m-%d %H:%M:%S%z")

        history_ids = UserIndexSetSearchHistory.objects.filter(
            created_at__range=[start_time, end_time],
        ).values_list("index_set_id", flat=True)

        project_ids = set(
            LogIndexSet.objects.filter(index_set_id__in=set(history_ids)).values_list("project_id", flat=True)
        )

        metrics = [
            Metric(
                metric_name="count",
                metric_value=1,
                dimensions={
                    "target_bk_biz_id": MetricUtils.get_instance().project_biz_info[project_id]["bk_biz_id"],
                    "target_bk_biz_name": MetricUtils.get_instance().project_biz_info[project_id]["bk_biz_name"],
                    "time_range": timedelta,
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for project_id in project_ids
            if MetricUtils.get_instance().project_biz_info.get(project_id)
        ]
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=len(project_ids),
                dimensions={"time_range": timedelta},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics

    @staticmethod
    @register_metric("business", description=_("业务"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def business():
        project_biz_info = MetricUtils.get_instance().project_biz_info
        metrics = [
            Metric(
                metric_name="total",
                metric_value=len(project_biz_info),
                dimensions=None,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        ]
        for bk_biz_id in MetricUtils.get_instance().biz_info:
            metrics.append(
                Metric(
                    metric_name="bk_biz_info",
                    metric_value=1,
                    dimensions={
                        "target_bk_biz_id": bk_biz_id,
                        "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )

        return metrics

    @staticmethod
    @register_metric(
        "business_collector", description=_("有配置日志采集业务"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def business_collector():
        collector_config_group = (
            CollectorConfig.objects.all().values("bk_biz_id").annotate(total=Count("bk_biz_id")).order_by()
        )
        metrics = []
        total = 0
        for collector_config in collector_config_group:
            metrics.append(
                Metric(
                    metric_name="count",
                    metric_value=collector_config["total"],
                    dimensions={
                        "target_bk_biz_id": collector_config["bk_biz_id"],
                        "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(collector_config["bk_biz_id"]),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
            total += collector_config["total"]

        metrics.append(
            Metric(
                metric_name="total",
                metric_value=total,
                dimensions=None,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics

    @staticmethod
    @register_metric("biz_usage", description=_("功能使用的业务数"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def biz_usage():
        metrics = []
        for function_name in FUNCTION_MODEL:
            metrics.extend(BusinessMetricCollector().function_biz_usage(function_name))

        metrics.extend(BusinessMetricCollector().index_set_function_biz_usage())
        metrics.extend(BusinessMetricCollector().trace_biz_usage())

        return metrics

    @staticmethod
    def function_biz_usage(function_name: str):
        groups = (
            FUNCTION_MODEL[function_name]
            .objects.all()
            .values("bk_biz_id")
            .annotate(count=Count("bk_biz_id"))
            .order_by("bk_biz_id")
        )
        metrics = [
            Metric(
                metric_name="count",
                metric_value=len(groups),
                dimensions={"function": function_name},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        ]
        return metrics

    @staticmethod
    def index_set_function_biz_usage():
        groups = (
            LogIndexSet.objects.values("project_id", "scenario_id")
            .order_by("project_id", "scenario_id")
            .annotate(count=Count("project_id"))
        )
        metrics = []
        aggregation_datas = defaultdict(list)
        for group in groups:
            if MetricUtils.get_instance().project_biz_info.get(group["project_id"]):
                bk_biz_id = MetricUtils.get_instance().project_biz_info[group["project_id"]]["bk_biz_id"]
                if group["scenario_id"] == Scenario.LOG:
                    continue
                function_name = INDEX_SCENARIO[group["scenario_id"]]
                aggregation_datas[function_name].append(bk_biz_id)
        for function_name in aggregation_datas:
            unique_bk_biz_id_list = list(set(aggregation_datas[function_name]))
            metrics.append(
                Metric(
                    metric_name="count",
                    metric_value=len(unique_bk_biz_id_list),
                    dimensions={"function": function_name},
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        return metrics

    @staticmethod
    def trace_biz_usage():
        groups = (
            LogIndexSet.objects.values("project_id")
            .filter(is_trace_log=True)
            .order_by("project_id")
            .annotate(count=Count("project_id"))
        )
        metrics = []
        bk_biz_id_list = []
        for group in groups:
            if MetricUtils.get_instance().project_biz_info.get(group["project_id"]):
                bk_biz_id = MetricUtils.get_instance().project_biz_info[group["project_id"]]["bk_biz_id"]
                bk_biz_id_list.append(bk_biz_id)
        unique_bk_biz_id_list = list(set(bk_biz_id_list))
        metrics.append(
            Metric(
                metric_name="count",
                metric_value=len(unique_bk_biz_id_list),
                dimensions={
                    "function": "log_trace",
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
