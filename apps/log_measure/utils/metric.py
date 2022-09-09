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
import socket

import arrow

from elasticsearch import Elasticsearch

from apps.api import TransferApi
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_measure.exceptions import EsConnectFailException
from apps.log_search.models import Space
from apps.utils.cache import cache_one_hour
from bk_monitor.utils.metric import Metric


class MetricUtils(object):
    _instance = None

    def __init__(self, collect_interval=300):
        # 业务缓存
        spaces = Space.objects.all()
        # 业务缓存
        self.biz_info = {
            space.bk_biz_id: {"bk_biz_id": space.bk_biz_id, "bk_biz_name": space.space_name} for space in spaces
        }

        self.space_info = {space.space_uid: space for space in spaces}
        # 上报时间
        self.collect_interval = collect_interval
        timestamp = arrow.now().timestamp
        self.report_ts = timestamp
        if collect_interval:
            self.report_ts = timestamp // self.collect_interval * self.collect_interval

        # 将原本的MetricCollector方法上移
        self.cluster_infos = {
            cluster_info["cluster_config"]["cluster_id"]: cluster_info for cluster_info in self.list_cluster_info()
        }
        self._cluster_clients = {}

    @property
    def time_range(self):
        # 取整
        return arrow.get(self.report_ts - self.collect_interval).datetime, arrow.get(self.report_ts).datetime

    def get_biz_name(self, bk_biz_id):
        """
        根据业务ID获取业务名称
        """
        return self.biz_info[int(bk_biz_id)]["bk_biz_name"] if int(bk_biz_id) in self.biz_info else bk_biz_id

    # 将原本MetricCollector常用工具方法上移
    @staticmethod
    @cache_one_hour("cluster_info_es")
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
            hosts=[domain_name], http_auth=http_auth, scheme="http", port=port, verify_certs=False, timeout=10,
        )
        if not es_client.ping(params={"request_timeout": 10}):
            raise EsConnectFailException()

        self._cluster_clients[cluster_id] = es_client
        return es_client

    def append_total_metric(self, metrics):
        total = sum(metric.metric_value for metric in metrics)
        metrics.append(Metric(metric_name="total", metric_value=total, timestamp=self.report_ts))
        return metrics

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            cls._instance = MetricUtils(*args, **kwargs)
            return cls._instance

    @classmethod
    def del_instance(cls):
        cls._instance = None


def build_metric_id(data_name, namespace, prefix: str) -> str:
    return f"{data_name}##{namespace}##{prefix}"


def get_metric_id_info(metric_id: str) -> list:
    return metric_id.split("##")
