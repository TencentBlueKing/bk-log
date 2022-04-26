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
from django.utils.translation import ugettext as _
from django.db.models import Count

from apps.log_search.models import LogIndexSet
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class IndexMetricCollector(object):
    @staticmethod
    @register_metric("index_set", description=_("索引集"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def index_set():
        groups = (
            LogIndexSet.objects.values("project_id", "scenario_id").order_by().annotate(count=Count("index_set_id"))
        )

        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "target_bk_biz_id": MetricUtils.get_instance().project_biz_info[group["project_id"]]["bk_biz_id"],
                    "target_bk_biz_name": MetricUtils.get_instance().project_biz_info[group["project_id"]][
                        "bk_biz_name"
                    ],
                    "scenario_id": group["scenario_id"],
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for group in groups
            if MetricUtils.get_instance().project_biz_info.get(group["project_id"])
        ]

        return metrics
