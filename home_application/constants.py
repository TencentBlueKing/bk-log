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
from django.utils.translation import ugettext as _
from apps.utils import ChoicesEnum

HEALTHZ_METRICS_IMPORT_PATHS = [
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

DEFAULT_SUBSCRIPTION_ID = 1
DEFAULT_SYSTEM_ID = 1

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

DEFAULT_BK_DATA_ID = 1
DEFAULT_BK_USERNAME = "admin"
DEFAULT_EXECUTE_SCRIPT_ACCOUNT = "root"

JOB_SUCCESS_STATUS = 9
JOB_FAILED_AGENT_EXCEPTION = 310
JOB_STATUS = {
    JOB_SUCCESS_STATUS: _("成功"),
    JOB_FAILED_AGENT_EXCEPTION: _("Agent异常"),
}


RETRY_TIMES = 5
WAIT_FOR_RETRY = 20

CHECK_STORY_1 = "检查Agent以及进程状态"
CHECK_STORY_2 = "检查路由配置是否正确"
CHECK_STORY_3 = "检查kafka内是否有数据"
CHECK_STORY_4 = "检查Transfer"
CHECK_STORY_5 = "检查ES"

CHECK_STORIES = [CHECK_STORY_1, CHECK_STORY_2, CHECK_STORY_3, CHECK_STORY_4, CHECK_STORY_5]

KAFKA_TEST_GROUP = "kafka_test_group"
DEFAULT_KAFKA_SECURITY_PROTOCOL = "PLAINTEXT"
DEFAULT_KAFKA_SASL_MECHANISM = "PLAIN"

TABLE_TRANSFER = "pushgateway_transfer_metircs.base"

# transfer metrics
TRANSFER_METRICS = [
    "transfer_pipeline_backend_handled_total",
    "transfer_pipeline_frontend_handled_total",
    "transfer_pipeline_processor_handled_total",
    "transfer_pipeline_backend_dropped_total",
    "transfer_pipeline_frontend_dropped_total",
    "transfer_pipeline_processor_dropped_total",
    "transfer_kafka_request_latency_milliseconds_bucket",
    "transfer_kafka_request_latency_milliseconds_sum",
    "transfer_kafka_request_latency_milliseconds_count",
]


class ScriptType(ChoicesEnum):
    SHELL = 1
    BAT = 2
    PERL = 3
    PYTHON = 4
    POWERSHELL = 5

    _choices_labels = (
        (SHELL, _("shell")),
        (BAT, _("bat")),
        (PERL, _("perl")),
        (PYTHON, _("python")),
        (POWERSHELL, _("powershell")),
    )


CHECK_AGENT_STEP = {
    "bin_file": _("检查二进制文件是否存在"),
    "process": _("检查进程是否存在"),
    "config": _("检查配置是否正确"),
    "hosted": _("检查采集插件是否被gse_agent托管"),
    "socket": _("检查socket文件是否存在"),
    "healthz": _("执行healthz自检查查看结果"),
}
