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
"""
import arrow

from django.utils.translation import ugettext as _

from apps.log_search.models import UserIndexSetSearchHistory, LogIndexSet
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class BusinessMetricCollector(object):
    @staticmethod
    @register_metric("business_active", description=_("活跃业务"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def business_active():
        # 一个星期内检索过日志的，才被认为是活跃业务

        history_ids = UserIndexSetSearchHistory.objects.filter(
            created_at__gte=arrow.now().replace(days=-7).datetime
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
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for project_id in project_ids
            if MetricUtils.get_instance().project_biz_info.get(project_id)
        ]

        return metrics
