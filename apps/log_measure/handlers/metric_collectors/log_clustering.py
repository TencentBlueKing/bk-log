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
from django.db.models import Count
from django.utils.translation import ugettext as _

from apps.log_clustering.models import ClusteringConfig
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class ClusteringMetricCollector(object):
    @staticmethod
    @register_metric("clustering", description=_("聚类计数"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def clustering_count():
        clustering_query_set = (
            ClusteringConfig.objects.filter(modify_flow__isnull=False)
            .values("bk_biz_id")
            .annotate(total=Count("bk_biz_id"))
            .order_by()
        )
        metrics = []
        total = 0
        for clustering_obj in clustering_query_set:

            metrics.append(
                Metric(
                    metric_name="count",
                    metric_value=clustering_obj["total"],
                    dimensions={
                        "bk_biz_id": clustering_obj["bk_biz_id"],
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(clustering_obj["bk_biz_id"]),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
            total += clustering_obj["total"]

        metrics.append(
            Metric(
                metric_name="total",
                metric_value=total,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
