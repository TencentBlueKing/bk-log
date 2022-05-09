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
import arrow
from django.db.models import Count
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model

from apps.log_search.models import UserIndexSetSearchHistory
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class UserMetricCollector(object):
    @staticmethod
    @register_metric("user_active", description=_("活跃用户"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def user_active():
        user_model = get_user_model()
        active_datetime = MetricUtils.get_instance().time_range[0]
        recent_login_users = user_model.objects.filter(last_login__gte=active_datetime)

        # 这里是因为登录获取的活跃用户不全，因此选择取其与检索活跃用户交集
        recent_search_users = UserIndexSetSearchHistory.objects.filter(created_at__gte=active_datetime)
        recent_active_users = {user.username for user in recent_login_users}.union(
            {user.created_by for user in recent_search_users}
        )

        metrics = [
            Metric(
                metric_name="count",
                metric_value=1,
                dimensions={"target_username": user},
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for user in recent_active_users
        ]

        metrics.append(
            Metric(
                metric_name="total",
                metric_value=len(recent_active_users),
                dimensions=None,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics

    @staticmethod
    @register_metric("unique_visitor", description=_("uv访问数"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def get_unique_visitor():
        user_index_set_search_history_group = (
            UserIndexSetSearchHistory.objects.filter(created_at__gte=arrow.now().replace(days=-1).datetime)
            .values("created_by")
            .annotate(total=Count("created_by"))
            .order_by()
        )
        metrics = []
        total = 0
        for user_index_set_search_history in user_index_set_search_history_group:
            metrics.append(
                Metric(
                    metric_name="count",
                    metric_value=user_index_set_search_history["total"],
                    dimensions={
                        "target_username": user_index_set_search_history["created_by"],
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
            total += user_index_set_search_history["total"]

        metrics.append(
            Metric(
                metric_name="total",
                metric_value=total,
                dimensions=None,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
