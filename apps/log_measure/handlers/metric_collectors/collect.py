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
import re
from collections import defaultdict
from typing import List
from django.utils.translation import ugettext as _
from django.db.models import Count

from apps.api import NodeApi
from apps.utils.thread import MultiExecuteFunc
from apps.log_databus.models import CollectorConfig
from apps.log_measure.constants import INDEX_FORMAT, COMMON_INDEX_RE
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class CollectMetricCollector(object):
    @staticmethod
    @register_metric("collector_config", description=_("采集配置"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def collector_config():
        groups = (
            CollectorConfig.objects.filter(is_active=True)
            .values("bk_biz_id")
            .order_by()
            .annotate(count=Count("collector_config_id"))
        )

        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "target_bk_biz_id": group["bk_biz_id"],
                    "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for group in groups
        ]
        return metrics

    @staticmethod
    @register_metric(
        "collector_capacity", description=_("采集项容量"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60
    )
    def collector_capacity():
        has_table_id_collects: List[CollectorConfig] = CollectorConfig.objects.filter(
            table_id__isnull=False,
        ).all()
        metrics = []

        table_id_map_indices = defaultdict(list)
        all_indices = CollectMetricCollector._get_all_cluster_indices()
        for indices in all_indices:
            for collect in has_table_id_collects:
                index_re = re.compile(COMMON_INDEX_RE.format(collect.table_id))
                if index_re.match(indices.get("index", "")):
                    table_id_map_indices[collect.table_id].append(indices)

        for collect in has_table_id_collects:
            cur_cap = sum([float(indices["store.size"]) for indices in table_id_map_indices.get(collect.table_id, [])])
            metrics.append(
                Metric(
                    metric_name="capacity",
                    metric_value=cur_cap,
                    dimensions={
                        "collector_config_id": collect.collector_config_id,
                        "collector_config_name": collect.collector_config_name,
                        "target_bk_biz_id": collect.bk_biz_id,
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        return metrics

    @staticmethod
    def _get_all_cluster_indices():
        multi_execute_func = MultiExecuteFunc()
        util = MetricUtils.get_instance()

        def _get_indices(cluster):
            es_client = util.get_es_client(cluster)
            if not es_client:
                return []
            return es_client.cat.indices(INDEX_FORMAT, format="json", bytes="mb")

        for cluster_id, cluster in util.cluster_infos.items():
            multi_execute_func.append(str(cluster_id), _get_indices, cluster, use_request=False)
        result = multi_execute_func.run()
        return [indices for cluster_indices in result.values() for indices in cluster_indices]

    @staticmethod
    @register_metric("collector_host", description=_("采集主机"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def collect_host():
        configs = CollectorConfig.objects.filter(is_active=True).values(
            "bk_biz_id", "subscription_id", "collector_config_id", "collector_config_name"
        )

        subscription_id_dict = {}
        collector_config_dict = {}
        for config in configs:
            if config["subscription_id"]:
                subscription_id_dict[config["subscription_id"]] = config["collector_config_id"]

            collector_config_dict[config["collector_config_id"]] = {
                "bk_biz_id": config["bk_biz_id"],
                "collector_config_name": config["collector_config_name"],
            }

        groups = NodeApi.get_subscription_instance_status(
            {"subscription_id_list": list(subscription_id_dict.keys()), "no_request": True}
        )

        biz_collector_dict = defaultdict(int)
        total = 0
        for group in groups:
            instance_count = len(group["instances"])
            biz_collector_dict[subscription_id_dict[group["subscription_id"]]] += instance_count
            total += instance_count
        metrics = [
            Metric(
                metric_name="count",
                metric_value=count,
                dimensions={
                    "collector_config_id": collector_config_id,
                    "collector_config_name": collector_config_dict[collector_config_id]["collector_config_name"],
                    "target_bk_biz_id": collector_config_dict[collector_config_id]["bk_biz_id"],
                    "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(
                        collector_config_dict[collector_config_id]["bk_biz_id"]
                    ),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for collector_config_id, count in biz_collector_dict.items()
        ]

        metrics.append(
            Metric(
                metric_name="total",
                metric_value=total,
                dimensions=None,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
