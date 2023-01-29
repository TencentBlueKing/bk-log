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
from django.conf import settings

from apps.utils.log import logger
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.utils.metric import register_metric, Metric
from bk_monitor.constants import TimeFilterEnum


class ClusterMetricCollector(object):
    @staticmethod
    @register_metric("cluster_health", description=_("集群健康度"), data_name="metric", time_filter=TimeFilterEnum.MINUTE10)
    def cluster_health():
        metrics = []
        for cluster_info in MetricUtils.get_instance().cluster_infos.values():
            try:
                es_client = MetricUtils.get_instance().get_es_client(cluster_info)
                if not es_client:
                    continue

                # 获取业务ID
                bk_biz_id = cluster_info.get("cluster_config", {}).get("custom_option", {}).get("bk_biz_id")
                if not bk_biz_id:
                    bk_biz_id = settings.BLUEKING_BK_BIZ_ID

                health_data = es_client.cluster.health(params={"request_timeout": 10})
                dimensions = {
                    "bk_biz_id": bk_biz_id,
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    "origin_cluster_name": health_data["cluster_name"],
                    "cluster_id": cluster_info.get("cluster_config").get("cluster_id"),
                    "cluster_name": cluster_info.get("cluster_config").get("cluster_name"),
                }
                # 获取集群shards状态
                for key in [
                    "active_shards",
                    "unassigned_shards",
                ]:
                    if key not in health_data:
                        continue
                    metrics.append(
                        Metric(
                            metric_name=key,
                            metric_value=health_data[key],
                            dimensions=dimensions,
                            timestamp=MetricUtils.get_instance().report_ts,
                        )
                    )

                # 状态字段需要单独处理
                status_mapping = {
                    "green": 0,
                    "yellow": 1,
                    "red": 2,
                }
                metrics.append(
                    Metric(
                        metric_name="status",
                        metric_value=status_mapping[health_data["status"]],
                        dimensions=dimensions,
                        timestamp=MetricUtils.get_instance().report_ts,
                    )
                )
            except Exception as e:  # pylint: disable=broad-except
                logger.exception("fail to collect cluster_health metric for cluster->{}, {}".format(cluster_info, e))
        return metrics

    @staticmethod
    @register_metric(
        "cluster_node", prefix="es", description=_("集群节点"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def cluster_node():
        metrics = []
        cluster_count = defaultdict(int)
        for cluster_info in MetricUtils.get_instance().cluster_infos.values():
            try:
                es_client = MetricUtils.get_instance().get_es_client(cluster_info)
                if not es_client:
                    continue
                bk_biz_id = (
                    cluster_info.get("cluster_config", {}).get("custom_option", {}).get("bk_biz_id")
                    or settings.BLUEKING_BK_BIZ_ID
                )
                allocations = es_client.cat.allocation(format="json", bytes="mb", params={"request_timeout": 10})

                for allocation in allocations:
                    if allocation["node"] == "UNASSIGNED":
                        # 未分配的节点忽略
                        continue

                    dimensions = {
                        "node_ip": allocation["ip"],
                        "node": allocation["node"],
                        "cluster_id": cluster_info.get("cluster_config").get("cluster_id"),
                        "cluster_name": cluster_info.get("cluster_config").get("cluster_name"),
                        "bk_biz_id": bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    }
                    for key in ["shards", "disk.indices", "disk.used", "disk.avail", "disk.total", "disk.percent"]:
                        if key not in allocation:
                            continue
                        metrics.append(
                            Metric(
                                metric_name=key.replace(".", "_"),
                                metric_value=int(allocation[key]),
                                dimensions=dimensions,
                                timestamp=MetricUtils.get_instance().report_ts,
                            )
                        )
                    # add disk_use_rate
                    if allocation.get("disk.used") and allocation.get("disk.total"):
                        metrics.append(
                            Metric(
                                metric_name="disk_use_rate",
                                metric_value=int(allocation["disk.used"]) / int(allocation["disk.total"]),
                                dimensions=dimensions,
                                timestamp=MetricUtils.get_instance().report_ts,
                            )
                        )

                nodes = es_client.cat.nodes(format="json", params={"request_timeout": 10})

                for node in nodes:
                    # cluster_count 统计实例数
                    cluster_count[bk_biz_id] += 1
                    dimensions = {
                        "node_ip": node["ip"],
                        "node": node["name"],
                        "cluster_id": cluster_info.get("cluster_config").get("cluster_id"),
                        "cluster_name": cluster_info.get("cluster_config").get("cluster_name"),
                        "bk_biz_id": bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    }
                    for key in ["heap.percent", "ram.percent", "cpu", "load_1m", "load_5m", "load_15m"]:
                        if key not in node:
                            continue
                        metrics.append(
                            Metric(
                                metric_name=key.replace(".", "_"),
                                metric_value=float(node[key]),
                                dimensions=dimensions,
                                timestamp=MetricUtils.get_instance().report_ts,
                            )
                        )

            except Exception as e:  # pylint: disable=broad-except
                logger.exception("fail to collect cluster_node metric for cluster->{}, {}".format(cluster_info, e))

        for bk_biz_id, count in cluster_count.items():
            metrics.append(
                # 各个业务集群数
                Metric(
                    metric_name="cluster_count",
                    metric_value=count,
                    dimensions={
                        "bk_biz_id": bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
        metrics.append(
            # 集群总数
            Metric(
                metric_name="cluster_total",
                metric_value=sum(cluster_count.values()),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics
