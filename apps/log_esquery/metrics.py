# -*- coding: utf-8 -*-
from prometheus_client import Histogram, Counter
from prometheus_client.utils import INF

from apps.utils.prometheus import register_metric


ESQUERY_SEARCH_LATENCY = register_metric(
    Histogram,
    name="esquery_search_latency",
    documentation="search latency of esquery search API",
    labelnames=("index_set_id", "indices", "scenario_id", "storage_cluster_id", "status"),
    buckets=(0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 20.0, 30.0, 60.0, INF),
)


ESQUERY_SEARCH_COUNT = register_metric(
    Counter,
    name="esquery_search_count",
    documentation="search count of esquery search API",
    labelnames=("index_set_id", "indices", "scenario_id", "storage_cluster_id", "status"),
)
