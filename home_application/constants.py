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

HEALTHZ_METRICS_IMPORT_PATHS = [
    "home_application.handlers.healthz_metrics.service_module",
    "home_application.handlers.healthz_metrics.version",
    "home_application.handlers.healthz_metrics.mysql",
    "home_application.handlers.healthz_metrics.redis",
    "home_application.handlers.healthz_metrics.rabbitmq",
    "home_application.handlers.healthz_metrics.kafka",
    "home_application.handlers.healthz_metrics.es",
    "home_application.handlers.healthz_metrics.third_party",
]

# MySQL metrics from command show global variables
MYSQL_VARIABLES = ["version", "server_id", "max_connections"]

# MySQL metrics from command show global status
MYSQL_STATUS = ["Threads_connected", "slow_queries", "Questions"]

# Redis metrics from info
REDIS_VARIABLES = [
    "redis_version",
    "connected_clients",
    "instantaneous_ops_per_sec",
    "latest_fork_usec",
    "mem_fragmentation_ratio",
    "evicted_keys",
]

QUEUES = [
    "default",
    "celery",
    "pipeline_additional_task",
    "pipeline_additional_task_priority",
    "service_schedule",
    "service_schedule_priority",
    "pipeline",
    "pipeline_priority",
    "async_export",
]

ALARM_QUEUE_LEN = 10000

DEFAULT_SUBSCRIPTION_ID = 1
DEFAULT_SYSTEM_ID = 1

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

DEFAULT_BK_DATA_ID = 1
DEFAULT_BK_USERNAME = "admin"
DEFAULT_EXECUTE_SCRIPT_ACCOUNT = "root"

# API_FORMAT_CONTENT_TYPE
API_FORMAT_CONTENT_TYPE = "text/plain; charset=UTF-8"
