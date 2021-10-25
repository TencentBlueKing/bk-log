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

INTERVAL_TYPE = ["month", "week", "day", "hour", "10m", "5m", "1m"]
STORAGE_CLUSTER_TYPE = "elasticsearch"
INDEX_REGEX = r"\d{1,}_bklog_.*?_\d{8}_\d{1,}"

COMMON_INDEX_RE = r"^(v2_)?{}_(?P<datetime>\d+)_(?P<index>\d+)$"

COLUMN_DISPLAY_LIST = ["docs.count", "docs.deleted", "index", "pri", "pri.store.size", "rep", "store.size", "status"]
INDEX_FORMAT = "*_bklog_*"

COLLECTOR_IMPORT_PATHS = [
    "apps.log_measure.handlers.metric_collectors.business",
    "apps.log_measure.handlers.metric_collectors.cluster",
    "apps.log_measure.handlers.metric_collectors.collect",
    "apps.log_measure.handlers.metric_collectors.grafana",
    "apps.log_measure.handlers.metric_collectors.index",
    "apps.log_measure.handlers.metric_collectors.log_extract",
    "apps.log_measure.handlers.metric_collectors.third_party",
    "apps.log_measure.handlers.metric_collectors.user",
    "apps.log_measure.handlers.metric_collectors.es",
]

DJANGO_MONITOR_DATA_NAME = "django_monitor"
DATA_NAMES = ["metric", "search_history", "es_monitor", "django_monitor"]
