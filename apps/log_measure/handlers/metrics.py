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
from __future__ import absolute_import, unicode_literals

import socket
import time
from collections import defaultdict
from functools import wraps

import arrow
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count
from django.utils.translation import ugettext as _
from elasticsearch import Elasticsearch

from apps.api import TransferApi, NodeApi, CCApi
from apps.utils.log import logger
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_databus.models import CollectorConfig
from apps.log_measure.exceptions import EsConnectFailException
from apps.log_search.models import UserIndexSetSearchHistory, LogIndexSet, ProjectInfo
from bk_dataview.grafana import client as grafana_client


class Metric(object):
    """
    指标定义
    """

    def __init__(self, metric_name, metric_value, dimensions=None):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.dimensions = dimensions

    def to_prometheus_text(self, namespace=None, timestamp=""):
        if namespace:
            actual_metric_name = "{}_{}".format(namespace, self.metric_name)
        else:
            actual_metric_name = self.metric_name

        if self.dimensions:
            dimensions = ",".join('{}="{}"'.format(key, value) for key, value in self.dimensions.items())
            dimensions = "{" + dimensions + "}"
        else:
            dimensions = ""

        prometheus_text = "{metric_name}{dimensions} {metric_value} {timestamp}".format(
            metric_name=actual_metric_name,
            dimensions=dimensions,
            metric_value=self.metric_value,
            timestamp=timestamp * 1000,
        )
        return prometheus_text


def register_metric(namespace, description="", cache_time=0):
    def wrapped_view(func):
        def _wrapped_view(*args, **kwargs):
            cache_key = f"statistics_{namespace}"

            if cache_time:
                result = cache.get(cache_key)
                if result:
                    return result

            result = func(*args, **kwargs)

            if cache_time:
                cache.set(cache_key, result, cache_time)
            return result

        _wrapped_view.namespace = namespace
        _wrapped_view.description = description
        _wrapped_view.is_metric = True
        return wraps(func)(_wrapped_view)

    return wrapped_view


class BaseMetricCollector(object):
    def __init__(self, collect_interval=300):
        # 业务缓存
        biz_list = CCApi.get_app_list({"fields": ["bk_biz_id", "bk_biz_name"], "no_request": True}).get("info", [])
        self.biz_info = {int(business["bk_biz_id"]): business for business in biz_list}

        self.project_biz_info = {}

        for project in ProjectInfo.objects.all():
            self.project_biz_info[project.project_id] = self.biz_info.get(project.bk_biz_id)

        # 上报时间
        self.collect_interval = collect_interval
        timestamp = arrow.now().timestamp
        self.report_ts = timestamp // self.collect_interval * self.collect_interval

    @property
    def time_range(self):
        # 取整
        return arrow.get(self.report_ts - self.collect_interval).datetime, arrow.get(self.report_ts).datetime

    def get_biz_name(self, bk_biz_id):
        """
        根据业务ID获取业务名称
        """
        return self.biz_info[int(bk_biz_id)]["bk_biz_name"] if int(bk_biz_id) in self.biz_info else bk_biz_id

    def collect(self, namespaces=None, response_format="prometheus"):
        """
        采集入口
        """
        metric_methods = self.list_metric_methods(namespaces)
        metric_groups = []
        for metric_method in metric_methods:
            try:
                begin_time = time.time()
                metric_groups.append(
                    {
                        "namespace": metric_method.namespace,
                        "description": metric_method.description,
                        "metrics": metric_method(),
                    }
                )
                logger.info(
                    "[statistics_data] collect metric->[{}] took {} ms".format(
                        metric_method.namespace, int((time.time() - begin_time) * 1000)
                    ),
                )
            except Exception as e:
                logger.exception("[statistics_data] collect metric->[{}] failed: {}".format(metric_method.namespace, e))

        if response_format != "prometheus":
            return metric_groups

        metric_text_list = []
        # 转换为prometheus格式
        for group in metric_groups:
            metric_text_list.append("# {}".format(group["description"] or group["namespace"]))
            for metric in group["metrics"]:
                metric_text_list.append(
                    metric.to_prometheus_text(namespace=group["namespace"], timestamp=self.report_ts)
                )
        return "\n".join(metric_text_list)

    @property
    def registered_metrics(self):
        return [
            method
            for method in dir(self)
            if method != "registered_metrics"
            and callable(getattr(self, method))
            and getattr(getattr(self, method), "is_metric", None)
        ]

    def list_metric_methods(self, namespaces=None):
        """
        获取
        :param namespaces:
        :return:
        """
        namespaces = namespaces or []
        if isinstance(namespaces, str):
            namespaces = [namespaces]

        methods = []
        for metric in self.registered_metrics:
            method = getattr(self, metric)
            if not namespaces:
                methods.append(method)
            for namespace in namespaces:
                if method.namespace.startswith(namespace):
                    methods.append(method)
        return methods

    @classmethod
    def append_total_metric(cls, metrics):
        total = sum(metric.metric_value for metric in metrics)
        metrics.append(
            Metric(
                metric_name="total",
                metric_value=total,
            )
        )
        return metrics


class MetricCollector(BaseMetricCollector):
    def __init__(self, *args, **kwargs):
        super(MetricCollector, self).__init__(*args, **kwargs)
        self.cluster_infos = {
            cluster_info["cluster_config"]["cluster_id"]: cluster_info for cluster_info in self.list_cluster_info()
        }
        self._cluster_clients = {}

    @staticmethod
    def list_cluster_info(cluster_id=None):
        """
        获取集群列表
        """
        params = {"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True}
        if cluster_id:
            params.update({"cluster_id": cluster_id})
        return TransferApi.get_cluster_info(params)

    def get_es_client_by_id(self, cluster_id):
        """
        根据集群ID获取ES客户端
        """
        cluster_info = self.cluster_infos.get(cluster_id)
        if not cluster_info:
            return None
        return self.get_es_client(cluster_info)

    def get_es_client(self, cluster_info):
        """
        根据集群信息获取ES客户端
        """
        cluster_id = cluster_info["cluster_config"]["cluster_id"]
        if cluster_id in self._cluster_clients:
            return self._cluster_clients[cluster_id]

        self._cluster_clients[cluster_id] = None

        cluster_config = cluster_info["cluster_config"]
        domain_name = cluster_config["domain_name"]
        port = cluster_config["port"]
        auth_info = cluster_info.get("auth_info", {})
        username = auth_info.get("username")
        password = auth_info.get("password")

        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        es_address: tuple = (str(domain_name), int(port))
        cs.settimeout(2)
        status: int = cs.connect_ex(es_address)
        if status != 0:
            raise EsConnectFailException()
        cs.close()

        http_auth = (username, password) if username and password else None
        es_client = Elasticsearch(
            hosts=[domain_name],
            http_auth=http_auth,
            scheme="http",
            port=port,
            verify_certs=True,
            timeout=10,
        )
        if not es_client.ping(params={"request_timeout": 10}):
            raise EsConnectFailException()

        self._cluster_clients[cluster_id] = es_client
        return es_client

    @register_metric("business_active", _("活跃业务"))
    def business_active(self):
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
                    "target_biz_id": self.project_biz_info[project_id]["bk_biz_id"],
                    "target_biz_name": self.project_biz_info[project_id]["bk_biz_name"],
                },
            )
            for project_id in project_ids
            if self.project_biz_info.get(project_id)
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("user_active", _("活跃用户"))
    def user_active(self):
        user_model = get_user_model()
        recent_login_users = user_model.objects.filter(last_login__gte=self.time_range[0])
        metrics = [
            Metric(metric_name="count", metric_value=1, dimensions={"username": user.username})
            for user in recent_login_users
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("collector_config", _("采集配置"))
    def collector_config(self):
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
                    "target_biz_id": group["bk_biz_id"],
                    "target_biz_name": self.get_biz_name(group["bk_biz_id"]),
                },
            )
            for group in groups
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("collector_host", _("采集主机"), cache_time=60 * 60)
    def collect_host(self):
        configs = CollectorConfig.objects.filter(is_active=True).values(
            "bk_biz_id", "subscription_id", "category_id", "collector_config_id"
        )

        biz_mapping = {
            config["subscription_id"]: {
                "bk_biz_id": config["bk_biz_id"],
                "category_id": config["category_id"],
                "collector_config_id": config["collector_config_id"],
            }
            for config in configs
            if config["subscription_id"]
        }

        groups = NodeApi.get_subscription_instance_status(
            {"subscription_id_list": list(biz_mapping.keys()), "no_request": True}
        )

        metrics = [
            Metric(
                metric_name="count",
                metric_value=len(group["instances"]),
                dimensions={
                    "target_biz_id": biz_mapping[group["subscription_id"]]["bk_biz_id"],
                    "target_biz_name": self.get_biz_name(biz_mapping[group["subscription_id"]]["bk_biz_id"]),
                    "category_id": biz_mapping[group["subscription_id"]]["category_id"],
                    "collector_config_id": biz_mapping[group["subscription_id"]]["collector_config_id"],
                },
            )
            for group in groups
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("index_set", _("索引集"))
    def index_set(self):
        groups = (
            LogIndexSet.objects.values("project_id", "scenario_id").order_by().annotate(count=Count("index_set_id"))
        )

        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "target_biz_id": self.project_biz_info[group["project_id"]]["bk_biz_id"],
                    "target_biz_name": self.project_biz_info[group["project_id"]]["bk_biz_name"],
                    "scenario_id": group["scenario_id"],
                },
            )
            for group in groups
            if self.project_biz_info.get(group["project_id"])
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("third_party_es", _("第三方ES"))
    def third_party_es(self):
        clusters = TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True})
        groups = defaultdict(int)
        for cluster in clusters:
            if cluster["cluster_config"]["registered_system"] == "_default":
                continue
            bk_biz_id = cluster["cluster_config"]["custom_option"]["bk_biz_id"]
            if not bk_biz_id:
                continue
            groups[bk_biz_id] += 1

        metrics = [
            Metric(
                metric_name="count",
                metric_value=count,
                dimensions={"target_biz_id": bk_biz_id, "target_biz_name": self.get_biz_name(bk_biz_id)},
            )
            for bk_biz_id, count in groups.items()
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("cluster_health", _("集群健康度"))
    def cluster_health(self):
        metrics = []
        for cluster_info in self.cluster_infos.values():
            try:
                es_client = self.get_es_client(cluster_info)
                if not es_client:
                    continue

                health_data = es_client.cluster.health(params={"request_timeout": 10})
                dimensions = {
                    "origin_cluster_name": health_data["cluster_name"],
                    "cluster_id": cluster_info.get("cluster_config").get("cluster_id"),
                    "cluster_name": cluster_info.get("cluster_config").get("cluster_name"),
                }
                for key in [
                    "number_of_nodes",
                    "number_of_data_nodes",
                    "active_primary_shards",
                    "active_shards",
                    "relocating_shards",
                    "initializing_shards",
                    "unassigned_shards",
                    "delayed_unassigned_shards",
                    "number_of_pending_tasks",
                    "number_of_in_flight_fetch",
                    "task_max_waiting_in_queue_millis",
                    "active_shards_percent_as_number",
                ]:
                    if key not in health_data:
                        continue
                    metrics.append(
                        Metric(
                            metric_name=key,
                            metric_value=health_data[key],
                            dimensions=dimensions,
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
                    )
                )
            except Exception as e:
                logger.exception("fail to collect cluster_health metric for cluster->{}, {}".format(cluster_info, e))
        return metrics

    @register_metric("cluster_node", _("集群节点"))
    def cluster_node(self):
        metrics = []
        for cluster_info in self.cluster_infos.values():
            try:
                es_client = self.get_es_client(cluster_info)
                if not es_client:
                    continue

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
                    }
                    for key in ["shards", "disk.indices", "disk.used", "disk.avail", "disk.total", "disk.percent"]:
                        if key not in allocation:
                            continue
                        metrics.append(
                            Metric(
                                metric_name=key.replace(".", "_"),
                                metric_value=allocation[key],
                                dimensions=dimensions,
                            )
                        )

                nodes = es_client.cat.nodes(format="json", params={"request_timeout": 10})

                for node in nodes:
                    dimensions = {
                        "node_ip": node["ip"],
                        "node": node["name"],
                        "cluster_id": cluster_info.get("cluster_config").get("cluster_id"),
                        "cluster_name": cluster_info.get("cluster_config").get("cluster_name"),
                    }
                    for key in ["heap.percent", "ram.percent", "cpu", "load_1m", "load_5m", "load_15m"]:
                        if key not in node:
                            continue
                        metrics.append(
                            Metric(
                                metric_name=key.replace(".", "_"),
                                metric_value=node[key],
                                dimensions=dimensions,
                            )
                        )

            except Exception as e:
                logger.exception("fail to collect cluster_node metric for cluster->{}, {}".format(cluster_info, e))
        return metrics

    @register_metric("grafana_dashboard", _("Grafana 仪表盘"), cache_time=60 * 60)
    def grafana_dashboard(self):
        metrics = []
        all_organization = grafana_client.get_all_organization().json()
        for org in all_organization:
            org_name = org["name"]
            if not org_name.isdigit():
                continue
            if int(org_name) not in self.biz_info:
                continue

            dashboards = grafana_client.search_dashboard(org_id=org["id"]).json()

            metrics.append(
                Metric(
                    metric_name="count",
                    metric_value=len(dashboards),
                    dimensions={"target_biz_id": int(org_name), "target_biz_name": self.get_biz_name(org_name)},
                )
            )

            panel_count = 0
            for dashboard in dashboards:
                dashboard_info = (
                    grafana_client.get_dashboard_by_uid(org_id=org["id"], dashboard_uid=dashboard["uid"])
                    .json()
                    .get("dashboard", {})
                )
                for panel in dashboard_info.get("panels", []):
                    if panel["type"] == "row":
                        # 如果是行类型，需要统计嵌套数量
                        panel_count += len(panel.get("panels", []))
                    else:
                        panel_count += 1

            metrics.append(
                Metric(
                    metric_name="panel_count",
                    metric_value=panel_count,
                    dimensions={"target_biz_id": int(org_name), "target_biz_name": self.get_biz_name(org_name)},
                )
            )

        return metrics

    @register_metric("log_extract_strategy", _("日志提取策略"))
    def log_extract_strategy(self):
        from apps.log_extract.models import Strategies

        groups = Strategies.objects.all().values("bk_biz_id").order_by().annotate(count=Count("strategy_id"))

        metrics = [
            Metric(
                metric_name="count",
                metric_value=group["count"],
                dimensions={
                    "target_biz_id": group["bk_biz_id"],
                    "target_biz_name": self.get_biz_name(group["bk_biz_id"]),
                },
            )
            for group in groups
        ]

        metrics = self.append_total_metric(metrics)

        return metrics

    @register_metric("log_extract_task", _("日志提取任务"))
    def log_extract_task(self):
        from apps.log_extract.models import Tasks

        groups = Tasks.objects.all().values("bk_biz_id", "created_by").order_by().annotate(count=Count("task_id"))

        # 每个业务的任务数
        biz_count_groups = defaultdict(int)

        # 每个业务的用户数
        user_count_groups = defaultdict(int)

        for group in groups:
            biz_count_groups[group["bk_biz_id"]] += group["count"]
            user_count_groups[group["bk_biz_id"]] += 1

        metrics = [
            Metric(
                metric_name="count",
                metric_value=count,
                dimensions={"target_biz_id": bk_biz_id, "target_biz_name": self.get_biz_name(bk_biz_id)},
            )
            for bk_biz_id, count in biz_count_groups.items()
        ]

        metrics = self.append_total_metric(metrics)

        metrics += [
            Metric(
                metric_name="user_count",
                metric_value=count,
                dimensions={"target_biz_id": bk_biz_id, "target_biz_name": self.get_biz_name(bk_biz_id)},
            )
            for bk_biz_id, count in user_count_groups.items()
        ]

        return metrics
