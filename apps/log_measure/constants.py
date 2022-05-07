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
from django.conf import settings

from bk_monitor.constants import EVENT_TYPE, TIME_SERIES_TYPE
from config.domains import MONITOR_APIGATEWAY_ROOT
from bk_monitor.handler.monitor import BKMonitor

BK_MONITOR_CLIENT = BKMonitor(
    app_id=settings.APP_CODE,
    app_token=settings.SECRET_KEY,
    monitor_host=MONITOR_APIGATEWAY_ROOT,
    report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
    bk_username="admin",
    bk_biz_id=settings.BLUEKING_BK_BIZ_ID,
)

INTERVAL_TYPE = ["month", "week", "day", "hour", "10m", "5m", "1m"]
STORAGE_CLUSTER_TYPE = "elasticsearch"
INDEX_REGEX = r"\d{1,}_bklog_.*?_\d{8}_\d{1,}"

COMMON_INDEX_RE = r"^(v2_)?{}_(?P<datetime>\d+)_(?P<index>\d+)$"

RESULT_TABLE_ID_RE = r"^(v2_)?(?P<result_table_id>\w+)_(?P<datetime>\d+)_(?P<index>\d+)$"

COLUMN_DISPLAY_LIST = ["docs.count", "docs.deleted", "index", "pri", "pri.store.size", "rep", "store.size", "status"]
INDEX_FORMAT = "*_bklog_*"

COLLECTOR_IMPORT_PATHS = [
    "apps.log_measure.handlers.metric_collectors.business",
    "apps.log_measure.handlers.metric_collectors.cluster",
    "apps.log_measure.handlers.metric_collectors.es",
    "apps.log_measure.handlers.metric_collectors.grafana",
    "apps.log_measure.handlers.metric_collectors.log_archive",
    "apps.log_measure.handlers.metric_collectors.log_clustering",
    "apps.log_measure.handlers.metric_collectors.log_databus",
    "apps.log_measure.handlers.metric_collectors.log_extract",
    "apps.log_measure.handlers.metric_collectors.log_search",
    "apps.log_measure.handlers.metric_collectors.third_party",
    "apps.log_measure.handlers.metric_collectors.user",
]

BK_LOG_EVENT_DATA_NAME = "bk_log_event"
DJANGO_MONITOR_DATA_NAME = "django_monitor"
# 初始化所有数据源列表
DATA_NAMES = [
    {"name": "metric", "custom_report_type": TIME_SERIES_TYPE},
    {"name": "search_history", "custom_report_type": TIME_SERIES_TYPE},
    {"name": "es_monitor", "custom_report_type": TIME_SERIES_TYPE},
    {"name": "django_monitor", "custom_report_type": TIME_SERIES_TYPE},
    {"name": "bk_log_event", "custom_report_type": EVENT_TYPE},
]
