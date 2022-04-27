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
import time
import arrow
import datetime

from django.utils.translation import ugettext as _
from django.conf import settings

from apps.utils.db import array_group
from apps.log_search.models import LogIndexSet
from apps.log_search.models import UserIndexSetSearchHistory
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class LogSearchMetricCollector(object):
    @staticmethod
    @register_metric("log_search", description=_("日志检索"), data_name="log_search", time_filter=TimeFilterEnum.MINUTE1)
    def search_count():
        end_time = arrow.get(int(time.time())).to(settings.TIME_ZONE).strftime("%Y-%m-%d %H:%M:%S%z")
        start_time = (
            datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S%z") - datetime.timedelta(minutes=2)
        ).strftime("%Y-%m-%d %H:%M:%S%z")

        history_objs = (
            UserIndexSetSearchHistory.objects.filter(
                is_deleted=False,
                search_type="default",
                created_at__range=[start_time, end_time],
            )
            .order_by("id")
            .values("id", "index_set_id", "duration", "created_by", "created_at", "search_type")
        )
        index_set_list = [history_obj["index_set_id"] for history_obj in history_objs]
        index_sets = array_group(
            LogIndexSet.get_index_set(index_set_ids=index_set_list, show_indices=False), "index_set_id", group=True
        )

        metrics = [
            Metric(
                metric_name="search_count",
                metric_value=history_obj["duration"],
                dimensions={
                    "index_set_id": history_obj["index_set_id"],
                    "index_set_name": index_sets[history_obj["index_set_id"]]["index_set_name"],
                    "target_username": history_obj["created_by"],
                    "target_bk_biz_id": index_sets[history_obj["index_set_id"]]["bk_biz_id"],
                    "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(
                        index_sets[history_obj["index_set_id"]]["bk_biz_id"]
                    ),
                },
                timestamp=arrow.get(history_obj["created_at"]).float_timestamp,
            )
            for history_obj in history_objs
        ]

        return metrics
