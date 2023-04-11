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
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Count

from apps.api import TransferApi
from apps.log_databus.models import ArchiveConfig, RestoreConfig
from apps.log_measure.utils.metric import MetricUtils
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class ArchiveMetricCollector(object):
    @staticmethod
    @register_metric("log_archive", description=_("日志归档"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def archive_config():
        metrics = []
        groups = (
            ArchiveConfig.objects.filter()
            .values("bk_biz_id")
            .order_by("bk_biz_id", "archive_config_id")
            .annotate(count=Count("archive_config_id"))
        )
        for group in groups:
            metrics.append(
                # 各个业务业务归档配置数量
                Metric(
                    metric_name="count",
                    metric_value=group["count"],
                    dimensions={
                        "bk_biz_id": group["bk_biz_id"],
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        metrics.append(
            # 全业务归档配置数量
            Metric(
                metric_name="total",
                metric_value=sum(i["count"] for i in groups),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        repository_count = defaultdict(int)
        # cluster_info, 存放cluster_id -> bk_biz_id
        cluster_info = defaultdict(int)
        clusters = TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE})
        if not clusters:
            return metrics
        for cluster in clusters:
            bk_biz_id = cluster.get("cluster_config", {}).get("custom_option", {}).get("bk_biz_id")
            if not bk_biz_id:
                bk_biz_id = settings.BLUEKING_BK_BIZ_ID
            cluster_info[cluster["cluster_config"]["cluster_id"]] = bk_biz_id

        repositories = TransferApi.list_es_snapshot_repository({"cluster_ids": [i for i in cluster_info]})
        if not repositories:
            return metrics
        for repo in repositories:
            bk_biz_id = cluster_info[repo["cluster_id"]]
            repository_count[bk_biz_id] += 1

        # 获取各个业务归档仓库列表
        for bk_biz_id, count in repository_count.items():
            metrics.append(
                # 各个业务业务归档配置数量
                Metric(
                    metric_name="repository_count",
                    metric_value=count,
                    dimensions={
                        "bk_biz_id": bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        # 归档仓库总数
        metrics.append(
            Metric(
                metric_name="repository_total",
                metric_value=sum(repository_count.values()),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics

    @staticmethod
    @register_metric("log_restore", description=_("日志回溯"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def restore_config():
        metrics = []
        groups = (
            RestoreConfig.objects.filter()
            .values("bk_biz_id")
            .order_by("bk_biz_id", "restore_config_id")
            .annotate(count=Count("restore_config_id"))
        )
        for group in groups:
            metrics.append(
                # 各个业务业务回溯配置数量
                Metric(
                    metric_name="count",
                    metric_value=group["count"],
                    dimensions={
                        "bk_biz_id": group["bk_biz_id"],
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        metrics.append(
            # 全业务回溯配置数量
            Metric(
                metric_name="total",
                metric_value=sum(i["count"] for i in groups),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
