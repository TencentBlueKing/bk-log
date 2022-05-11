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

import datetime

import arrow

from django.db.models import Count
from django.utils.translation import ugettext as _
from django.conf import settings

from apps.utils.db import array_group
from apps.log_search.models import LogIndexSet, FavoriteSearch, UserIndexSetSearchHistory, AsyncTask
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class LogSearchMetricCollector(object):
    @staticmethod
    @register_metric("log_search", description=_("日志检索"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def search_count():
        end_time = (
            arrow.get(MetricUtils.get_instance().report_ts).to(settings.TIME_ZONE).strftime("%Y-%m-%d %H:%M:%S%z")
        )
        start_time = (
            datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S%z") - datetime.timedelta(minutes=5)
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
        # 带标签数据
        metrics = [
            Metric(
                metric_name="count",
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
        # 搜索总数
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=history_objs.count(),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics

    @staticmethod
    @register_metric("search_favorite", description=_("检索收藏"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def favorite_count():
        favorite_objs = (
            FavoriteSearch.objects.filter(
                is_deleted=False,
            )
            .order_by("id")
            .values("id", "search_history_id", "project_id", "created_at")
        )
        history_objs = (
            UserIndexSetSearchHistory.objects.filter(
                is_deleted=False,
                id__in=[i["search_history_id"] for i in favorite_objs],
            )
            .order_by("id")
            .values("id", "index_set_id")
        )
        index_set_list = [history_obj["index_set_id"] for history_obj in history_objs]
        index_sets = array_group(
            LogIndexSet.get_index_set(index_set_ids=index_set_list, show_indices=False), "index_set_id", group=True
        )
        aggregation_datas = defaultdict(lambda: defaultdict(int))
        for index_set_id in index_set_list:
            bk_biz_id = index_sets[index_set_id]["bk_biz_id"]
            aggregation_datas[bk_biz_id][index_set_id] += 1

        # 收藏带标签数据
        metrics = [
            Metric(
                metric_name="count",
                metric_value=aggregation_datas[bk_biz_id][index_set_id],
                dimensions={
                    "index_set_id": index_set_id,
                    "index_set_name": index_sets[index_set_id]["index_set_name"],
                    "target_bk_biz_id": bk_biz_id,
                    "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for bk_biz_id in aggregation_datas
            for index_set_id in aggregation_datas[bk_biz_id]
        ]
        # 收藏总数
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=favorite_objs.count(),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics


class LogExportMetricCollector(object):
    @staticmethod
    @register_metric("log_export", description=_("日志导出"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def export_count():
        end_time = (
            arrow.get(MetricUtils.get_instance().report_ts).to(settings.TIME_ZONE).strftime("%Y-%m-%d %H:%M:%S%z")
        )
        start_time = (
            datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S%z") - datetime.timedelta(minutes=60)
        ).strftime("%Y-%m-%d %H:%M:%S%z")

        history_objs = (
            AsyncTask.objects.filter(
                created_at__range=[start_time, end_time],
            )
            .values("bk_biz_id", "index_set_id", "export_type", "created_by", "created_at")
            .order_by("bk_biz_id", "index_set_id", "export_type", "created_by")
            .annotate(count=Count("id"))
        )
        index_set_list = [history_obj["index_set_id"] for history_obj in history_objs]
        index_sets = array_group(
            LogIndexSet.get_index_set(index_set_ids=index_set_list, show_indices=False), "index_set_id", group=True
        )
        # 带标签数据
        metrics = [
            Metric(
                metric_name="count",
                metric_value=history_obj["count"],
                dimensions={
                    "index_set_id": history_obj["index_set_id"],
                    "index_set_name": index_sets[history_obj["index_set_id"]]["index_set_name"],
                    "target_username": history_obj["created_by"],
                    "export_type": history_obj["export_type"],
                    "target_bk_biz_id": history_obj["bk_biz_id"],
                    "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(history_obj["bk_biz_id"]),
                },
                timestamp=arrow.get(history_obj["created_at"]).float_timestamp,
            )
            for history_obj in history_objs
        ]
        # 导出总数
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=history_objs.count(),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics


class IndexSetMetricCollector(object):
    @staticmethod
    @register_metric("index_set", description=_("索引集"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def index_set():
        metrics = []
        groups = (
            LogIndexSet.objects.values("project_id", "scenario_id", "is_active")
            .order_by("project_id", "scenario_id", "is_active")
            .annotate(count=Count("index_set_id"))
        )
        aggregation_index_set = defaultdict(int)
        aggregation_active_index_set = defaultdict(int)
        for group in groups:
            if MetricUtils.get_instance().project_biz_info.get(group["project_id"]):
                bk_biz_id = MetricUtils.get_instance().project_biz_info[group["project_id"]]["bk_biz_id"]
                metrics.append(
                    # 带bk_biz_id, scenario_id, is_active标签的数据
                    Metric(
                        metric_name="count",
                        metric_value=group["count"],
                        dimensions={
                            "target_bk_biz_id": bk_biz_id,
                            "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                            "scenario_id": group["scenario_id"],
                            "is_active": group["is_active"],
                        },
                        timestamp=MetricUtils.get_instance().report_ts,
                    )
                )
                aggregation_index_set[bk_biz_id] += group["count"]
                if group["is_active"]:
                    aggregation_active_index_set[bk_biz_id] += group["count"]

        metrics.append(
            # 总的索引集数量
            Metric(
                metric_name="total",
                metric_value=sum(aggregation_index_set.values()),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        metrics.append(
            # 有效的索引集数量
            Metric(
                metric_name="active_total",
                metric_value=sum(aggregation_active_index_set.values()),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics
