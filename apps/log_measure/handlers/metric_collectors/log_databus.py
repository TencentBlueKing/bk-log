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
import time
from collections import defaultdict
from typing import List
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Count

from config.domains import MONITOR_APIGATEWAY_ROOT

from apps.api import NodeApi
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import SCENARIO_BKDATA
from apps.log_databus.constants import DEFAULT_ETL_CONFIG, EtlConfig
from apps.log_search.constants import CollectorScenarioEnum, TimeEnum
from apps.log_search.models import LogIndexSet
from apps.utils.db import array_group, array_chunk
from apps.utils.thread import MultiExecuteFunc
from apps.utils.log import logger
from apps.log_databus.models import CollectorConfig, BKDataClean
from apps.log_measure.constants import (
    INDEX_FORMAT,
    COMMON_INDEX_RE,
    TABLE_BKUNIFYBEAT_TASK,
    FIELD_CRAWLER_RECEIVED,
    FIELD_CRAWLER_STATE,
    MAX_RETRY_QUERY_SUBSCRIPTION_TIMES,
    TIME_WAIT_QUERY_SUBSCRIPTION_EXCEPTION,
    MAX_QUERY_SUBSCRIPTION,
)
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric
from bk_monitor.api.client import Client


class CollectMetricCollector(object):
    @staticmethod
    @register_metric("collector_config", description=_("采集配置"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def collector_config():
        groups = (
            CollectorConfig.objects.filter()
            .values("bk_biz_id", "is_active", "collector_scenario_id")
            .order_by("bk_biz_id", "is_active", "collector_scenario_id")
            .annotate(count=Count("collector_config_id"))
        )
        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "is_active": group["is_active"],
                    "collect_scenario": group["collector_scenario_id"],
                    "bk_biz_id": group["bk_biz_id"],
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for group in groups
        ]
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=sum([i["count"] for i in groups]),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics

    @staticmethod
    @register_metric(
        "custom_collector_config", description=_("自定义采集配置"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def custom_collector_config():
        """
        custom_collector_config
        @return:
        """
        groups = (
            CollectorConfig.objects.filter(collector_scenario_id=CollectorScenarioEnum.CUSTOM.value)
            .values("bk_biz_id", "custom_type")
            .order_by("bk_biz_id", "custom_type")
            .annotate(count=Count("collector_config_id"))
        )
        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "custom_type": group["custom_type"],
                    "bk_biz_id": group["bk_biz_id"],
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(group["bk_biz_id"]),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for group in groups
        ]
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=sum([i["count"] for i in groups]),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics

    @staticmethod
    @register_metric(
        "collector_capacity",
        prefix="es",
        description=_("采集项容量"),
        data_name="metric",
        time_filter=TimeFilterEnum.MINUTE5,
    )
    def collector_capacity():
        """
        collector_capacity
        @return:
        """
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
            cur_cap = sum(
                [
                    float(indices.get("store.size", 0))
                    for indices in table_id_map_indices.get(collect.table_id, [])
                    if indices.get("store.size")
                ]
            )
            docs_count = sum(
                [
                    int(indices.get("docs.count", 0))
                    for indices in table_id_map_indices.get(collect.table_id, [])
                    if indices.get("docs.count")
                ]
            )
            metrics.append(
                Metric(
                    metric_name="store_sum",
                    metric_value=cur_cap,
                    dimensions={
                        "collector_config_id": collect.collector_config_id,
                        "collector_config_name": collect.collector_config_name,
                        "bk_biz_id": collect.bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(collect.bk_biz_id),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
            # 指标docs.count
            metrics.append(
                Metric(
                    metric_name="docs_count",
                    metric_value=docs_count,
                    dimensions={
                        "collector_config_id": collect.collector_config_id,
                        "collector_config_name": collect.collector_config_name,
                        "bk_biz_id": collect.bk_biz_id,
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(collect.bk_biz_id),
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
    @register_metric(
        "row", prefix="bkunifylogbeat", description=_("采集行数"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5
    )
    def collector_line():
        """
        collector_line
        @return:
        """
        metrics = []
        crawler_received_data = CollectMetricCollector().get_crawler_metric_data(FIELD_CRAWLER_RECEIVED)
        crawler_state_data = CollectMetricCollector().get_crawler_metric_data(FIELD_CRAWLER_STATE)
        for task_data_id in crawler_received_data:
            _received_count = crawler_received_data[task_data_id]
            _state_count = crawler_state_data[task_data_id]
            metrics.append(
                Metric(
                    metric_name="count",
                    metric_value=_received_count - _state_count,
                    dimensions={"task_data_id": task_data_id},
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )

        return metrics

    @staticmethod
    def get_crawler_metric_data(field):
        """
        get_crawler_metric_data
        @param field:
        @return:
        """
        data = defaultdict(int)
        bk_monitor_client = Client(
            bk_app_code=settings.APP_CODE,
            bk_app_secret=settings.SECRET_KEY,
            monitor_host=MONITOR_APIGATEWAY_ROOT,
            report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
            bk_username="admin",
        )
        params = {
            "sql": f"select sum({field}) as {field} from {TABLE_BKUNIFYBEAT_TASK} \
            where time >= '5m' group by task_data_id"
        }
        try:
            result = bk_monitor_client.get_ts_data(data=params)
            for ts_data in result["list"]:
                value = ts_data[field]
                task_data_id = ts_data["task_data_id"]
                data[task_data_id] = value

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get {field} data, err: {e}")
        return data

    @staticmethod
    @register_metric("business_host", description=_("业务主机"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def business_unique_host():
        metrics = []
        total_host = 0
        active_host = 0
        # 监控没办法执行select from (select from), 只能查两次
        received_result = CollectMetricCollector()._get_unique_host_crawler(FIELD_CRAWLER_RECEIVED)
        state_result = CollectMetricCollector()._get_unique_host_crawler(FIELD_CRAWLER_STATE)
        for target in received_result:
            total_host += 1
            if received_result[target] - state_result[target] > 0:
                active_host += 1
        metrics.append(
            Metric(
                metric_name="count",
                metric_value=active_host,
                dimensions={
                    "is_active": True,
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        metrics.append(
            Metric(
                metric_name="count",
                metric_value=total_host - active_host,
                dimensions={
                    "is_active": False,
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        return metrics

    @staticmethod
    def _get_unique_host_crawler(field: str):
        aggregation_datas = defaultdict(int)
        bk_monitor_client = Client(
            bk_app_code=settings.APP_CODE,
            bk_app_secret=settings.SECRET_KEY,
            monitor_host=MONITOR_APIGATEWAY_ROOT,
            report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
            bk_username="admin",
        )
        start_time = MetricUtils.get_instance().report_ts - TimeEnum.ONE_HOUR_SECOND.value
        end_time = MetricUtils.get_instance().report_ts
        params = {
            "down_sample_range": "5s",
            "start_time": start_time,
            "end_time": end_time,
            "expression": "a",
            "display": True,
            "query_configs": [
                {
                    "data_source_label": "custom",
                    "data_type_label": "time_series",
                    "metrics": [{"field": field, "method": "SUM", "alias": "a"}],
                    "table": TABLE_BKUNIFYBEAT_TASK,
                    "group_by": ["target"],
                    "display": True,
                    "where": [],
                    "interval": TimeEnum.ONE_HOUR_SECOND.value,
                    "interval_unit": "s",
                    "time_field": "time",
                    "filter_dict": {},
                    "functions": [],
                }
            ],
            "target": [],
            "bk_biz_id": str(settings.BLUEKING_BK_BIZ_ID),
        }
        try:
            result = bk_monitor_client.unify_query(data=params)
            for ts_data in result["series"]:
                target = ts_data["dimensions"]["target"]
                try:
                    row_count = ts_data["datapoints"][0][0]
                    if not row_count:
                        row_count = 0
                except Exception:  # pylint: disable=broad-except
                    row_count = 0
                aggregation_datas[target] = row_count

        except Exception as e:  # pylint: disable=broad-except
            logger.error("failed to unify_query, params: {}, err: {}".format(params, e))
        return aggregation_datas


class CleanMetricCollector(object):
    @staticmethod
    @register_metric("clean_config", description=_("清洗配置"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60)
    def clean_config():
        """
        clean_config
        @return:
        """
        metrics = []
        clean_config_count = defaultdict(int)
        bk_data_clean_config_count = defaultdict(int)

        for bk_biz_id, clean_configs in CleanMetricCollector.get_clean_config().items():
            aggregation_datas = defaultdict(lambda: defaultdict(int))
            index_set_list = [i["index_set_id"] for i in clean_configs]
            index_sets = array_group(
                LogIndexSet.get_index_set(index_set_ids=index_set_list, show_indices=False), "index_set_id", group=True
            )
            for clean_config in clean_configs:
                if clean_config["etl_config"] == DEFAULT_ETL_CONFIG:
                    bk_data_clean_config_count[bk_biz_id] += 1
                else:
                    clean_config_count[bk_biz_id] += 1
                aggregation_datas[clean_config["index_set_id"]][clean_config["etl_config"]] += 1
            for index_set_id in aggregation_datas:
                if not index_sets.get(index_set_id):
                    continue
                for etl_config in aggregation_datas[index_set_id]:
                    metrics.append(
                        # 上报以索引, 清洗类型为维度的数据
                        Metric(
                            metric_name="count",
                            metric_value=aggregation_datas[index_set_id][etl_config],
                            dimensions={
                                "bk_biz_id": bk_biz_id,
                                "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                                "index_set_id": index_set_id,
                                "index_set_name": index_sets[index_set_id]["index_set_name"],
                                "clean_type": etl_config,
                            },
                            timestamp=MetricUtils.get_instance().report_ts,
                        )
                    )
        # 上报两个清洗总数
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=sum(clean_config_count.values()),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )
        metrics.append(
            Metric(
                metric_name="bk_data_total",
                metric_value=sum(bk_data_clean_config_count.values()),
                dimensions={},
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        return metrics

    @staticmethod
    def get_clean_config() -> defaultdict:
        """
        获取全业务清洗列表
        @return:
        """
        cleans = defaultdict(list)
        collector_configs = (
            CollectorConfig.objects.filter(
                bk_biz_id__in=[bk_biz_id for bk_biz_id in MetricUtils.get_instance().biz_info]
            )
            .exclude(index_set_id__isnull=True)
            .exclude(etl_config__isnull=True)
            .exclude(etl_config=EtlConfig.BK_LOG_TEXT)
        )
        for collector_config in collector_configs:
            cleans[collector_config.bk_biz_id].append(
                {
                    "bk_data_id": collector_config.bk_data_id,
                    "collector_config_name": collector_config.collector_config_name,
                    "result_table_id": collector_config.table_id.replace(".", "_"),
                    "collector_config_id": collector_config.collector_config_id,
                    "etl_config": collector_config.etl_config,
                    "index_set_id": collector_config.index_set_id,
                }
            )

        if not FeatureToggleObject.switch(name=SCENARIO_BKDATA):
            return cleans
        bk_data_cleans = BKDataClean.objects.filter(
            bk_biz_id__in=[bk_biz_id for bk_biz_id in MetricUtils.get_instance().biz_info]
        )
        for bk_data_clean in bk_data_cleans:
            collector_config = CollectorConfig.objects.filter(
                collector_config_id=bk_data_clean.collector_config_id
            ).first()
            if not collector_config:
                logger.error("can not find this collector_config {}".format(bk_data_clean.collector_config_id))
                continue

            cleans[collector_config.bk_biz_id].append(
                {
                    "bk_data_id": bk_data_clean.raw_data_id,
                    "collector_config_name": collector_config.collector_config_name,
                    "result_table_id": bk_data_clean.result_table_id,
                    "collector_config_id": bk_data_clean.collector_config_id,
                    "etl_config": DEFAULT_ETL_CONFIG,
                    "index_set_id": bk_data_clean.log_index_set_id,
                }
            )

        return cleans

    @staticmethod
    @register_metric(
        "host", prefix="bkunifylogbeat", description=_("采集主机"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60
    )
    def collect_host():
        """
        collect_host
        @return:
        """
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

        groups = get_subscription_instance_count(list(subscription_id_dict.keys()))

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
                    "bk_biz_id": collector_config_dict[collector_config_id]["bk_biz_id"],
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(
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


def get_subscription_instance_count(subscription_id_list: list) -> list:
    """
    有失败重试以及限制了单次查询订阅ID的函数
    @param subscription_id_list:
    @return:
    """
    groups = []

    def _get_subscription_instance(subscription_id_list_slice: list):
        group = None
        for __ in range(MAX_RETRY_QUERY_SUBSCRIPTION_TIMES):
            try:
                group = NodeApi.get_subscription_instance_status(
                    {"subscription_id_list": subscription_id_list_slice, "no_request": True}
                )
                if group:
                    break
            except Exception:  # pylint: disable=broad-except
                time.sleep(TIME_WAIT_QUERY_SUBSCRIPTION_EXCEPTION)
        return group

    for i in array_chunk(subscription_id_list, MAX_QUERY_SUBSCRIPTION):
        group = _get_subscription_instance(i)
        if group:
            groups.extend(group)

    return groups
