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
from __future__ import absolute_import, unicode_literals

import time
from functools import wraps

import arrow
from django.core.cache import cache
from django.utils.translation import ugettext as _
from elasticsearch import Elasticsearch

from apps.api import TransferApi, NodeApi
from apps.log_esquery.utils.es_client import es_socket_ping
from apps.utils.log import logger
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_databus.models import CollectorConfig
from apps.log_measure.exceptions import EsConnectFailException
from apps.log_search.models import Space


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
        spaces = Space.objects.all()
        # 业务缓存
        self.biz_info = {
            space.bk_biz_id: {"bk_biz_id": space.bk_biz_id, "bk_biz_name": space.space_name} for space in spaces
        }

        self.space_info = {space.space_uid: space for space in spaces}

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
            except Exception as e:  # pylint: disable=broad-except
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

        es_socket_ping(host=domain_name, port=port)

        http_auth = (username, password) if username and password else None
        es_client = Elasticsearch(
            hosts=[domain_name],
            http_auth=http_auth,
            scheme="http",
            port=port,
            verify_certs=False,
            timeout=10,
        )
        if not es_client.ping(params={"request_timeout": 10}):
            raise EsConnectFailException()

        self._cluster_clients[cluster_id] = es_client
        return es_client

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
                    "bk_biz_id": biz_mapping[group["subscription_id"]]["bk_biz_id"],
                    "bk_biz_name": self.get_biz_name(biz_mapping[group["subscription_id"]]["bk_biz_id"]),
                    "category_id": biz_mapping[group["subscription_id"]]["category_id"],
                    "collector_config_id": biz_mapping[group["subscription_id"]]["collector_config_id"],
                },
            )
            for group in groups
        ]

        metrics = self.append_total_metric(metrics)

        return metrics
