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

from django.utils.translation import ugettext as _
from django.conf import settings
from django.db.models import Count
from apps.log_extract.models import Tasks, Strategies
from apps.log_measure.constants import TIME_RANGE
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class LogExtractMetricCollector(object):
    @staticmethod
    @register_metric(
        "log_extract_strategy", description=_("日志提取策略"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def log_extract_strategy():
        groups = Strategies.objects.all().values("bk_biz_id").order_by().annotate(count=Count("strategy_id"))

        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "bk_biz_id": group["bk_biz_id"],
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for group in groups
        ]

        return metrics

    @staticmethod
    @register_metric(
        "log_extract_task", description=_("日志提取任务"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def log_extract_task():
        metrics = []
        for timedelta in TIME_RANGE:
            metrics.extend(LogExtractMetricCollector().log_extract_task_by_time_range(timedelta))

        return metrics

    @staticmethod
    def log_extract_task_by_time_range(timedelta: str):
        end_time = (
            arrow.get(MetricUtils.get_instance().report_ts).to(settings.TIME_ZONE).strftime("%Y-%m-%d %H:%M:%S%z")
        )
        timedelta_v = TIME_RANGE[timedelta]
        start_time = (
            datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S%z") - datetime.timedelta(minutes=timedelta_v)
        ).strftime("%Y-%m-%d %H:%M:%S%z")

        groups = (
            Tasks.objects.filter(created_at__range=[start_time, end_time])
            .values("bk_biz_id", "created_by")
            .order_by("bk_biz_id", "created_by")
            .annotate(count=Count("task_id"))
        )

        metrics = [
            # 各个业务, 各个用户使用量
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "bk_biz_id": group["bk_biz_id"],
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                    "target_username": group["created_by"],
                    "time_range": timedelta,
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for group in groups
        ]

        aggregation_datas = defaultdict(int)
        for group in groups:
            aggregation_datas[group["bk_biz_id"]] += group["count"]

        for bk_biz_id in aggregation_datas:
            # 各个业务提取配置总数
            metrics.append(
                Metric(
                    metric_name="total",
                    metric_value=aggregation_datas[bk_biz_id],
                    dimensions={
                        "bk_biz_id": bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                        "time_range": timedelta,
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )

        return metrics
