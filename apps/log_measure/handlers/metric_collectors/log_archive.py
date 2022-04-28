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
from collections import defaultdict
from django.utils.translation import ugettext as _
from django.db.models import Count

from apps.log_databus.models import ArchiveConfig
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class ArchiveMetricCollector(object):
    @staticmethod
    @register_metric("log_archive", description=_("日志归档"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def archive_config():
        groups = (
            ArchiveConfig.objects.filter()
            .values("bk_biz_id", "target_snapshot_repository_name")
            .order_by("archive_config_id")
            .annotate(count=Count("archive_config_id"))
        )
        aggregation_datas = defaultdict(dict)
        for group in groups:
            bk_biz_id = group["bk_biz_id"]
            target_snapshot_repository_name = group["target_snapshot_repository_name"]
            aggregation_datas[bk_biz_id][target_snapshot_repository_name] = group["count"]

        metrics = []
        for bk_biz_id in aggregation_datas:
            metrics.append(
                # 各个业务业务归档数量
                Metric(
                    metric_name="count",
                    metric_value=sum(aggregation_datas[bk_biz_id].values()),
                    dimensions={
                        "target_bk_biz_id": bk_biz_id,
                        "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
            metrics.append(
                # 各个业务归档仓库数量
                Metric(
                    metric_name="repository_count",
                    metric_value=len(aggregation_datas[bk_biz_id].keys()),
                    dimensions={
                        "target_bk_biz_id": bk_biz_id,
                        "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        metrics.append(
            # 全业务归档配置数量
            Metric(
                metric_name="count_total",
                metric_value=sum(i["count"] for i in groups),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        metrics.append(
            # 全业务归档仓库数量
            Metric(
                metric_name="repository_count_total",
                metric_value=len({i["target_snapshot_repository_name"] for i in groups}),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
