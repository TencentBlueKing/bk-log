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

DEFAULT_NEW_CLS_HOURS = 24

CONTENT_PATTERN_INDEX = 1
LATEST_PUBLISH_STATUS = "latest"
PATTERN_SIGNATURE_INDEX = 5
PATTERN_INDEX = 0
ORIGIN_LOG_INDEX = 3

HOUR_MINUTES = 60
PERCENTAGE_RATE = 100
MIN_COUNT = 0
DOUBLE_PERCENTAGE = 100
EX_MAX_SIZE = 10000
IS_NEW_PATTERN_PREFIX = "is_new_class"
AGGS_FIELD_PREFIX = "__dist"
NEW_CLASS_FIELD_PREFIX = "dist"

NEW_CLASS_SENSITIVITY_FIELD = "sensitivity"
NEW_CLASS_QUERY_FIELDS = ["signature"]
NEW_CLASS_QUERY_TIME_RANGE = "customized"

CLUSTERING_CONFIG_EXCLUDE = ["sample_set_id", "model_id"]
CLUSTERING_CONFIG_DEFAULT = "default_clustering_config"

DEFAULT_CLUSTERING_FIELDS = "log"
DEFAULT_IS_CASE_SENSITIVE = 0

SAMPLE_SET_SLEEP_TIMER = 15 * 60

DEFULT_FILTER_NOT_CLUSTERING_OPERATOR = "is not"

NOTICE_RECEIVER = "user"

#  查找策略page_size 设置
DEFAULT_PAGE = 1
MAX_STRATEGY_PAGE_SIZE = 100

DEFAULT_SCENARIO = "other_rt"
DEFAULT_LABEL = [_("日志平台日志聚类告警")]
DEFAULT_NOTIFY_RECEIVER_TYPE = "user"
DEFAULT_NOTICE_WAY = {"3": ["rtx"], "2": ["rtx"], "1": ["rtx"]}
DEFAULT_NO_DATA_CONFIG = {"level": 2, "continuous": 10, "is_enabled": False, "agg_dimension": []}
DEFAULT_EXPRESSION = "a"
DEFAULT_DATA_SOURCE_LABEL = "bk_log_search"
DEFAULT_DATA_SOURCE_LABEL_BKDATA = "bk_data"
DEFAULT_DATA_TYPE_LABEL = "log"
DEFAULT_DATA_TYPE_LABEL_BKDATA = "time_series"
DEFAULT_AGG_METHOD_BKDATA = "COUNT"
DEFAULT_AGG_INTERVAL = 60
DEFAULT_TIME_FIELD = "dtEventTimeStamp"
DEFAULT_ALGORITHMS = [
    {"type": "Threshold", "level": 2, "config": [[{"method": "gte", "threshold": 1}]], "unit_prefix": ""}
]
DEFAULT_CLUSTERING_ITEM_NAME = _("日志聚类新类(近24H)")
DEFAULT_METRIC = "event_time"
DEFAULT_DETECTS = [
    {
        "level": 2,
        "expression": "",
        "trigger_config": {"count": 1, "check_window": 5},
        "recovery_config": {"check_window": 5},
        "connector": "and",
    }
]
DEFAULT_ACTION_TYPE = "notice"
DEFAULT_ACTION_CONFIG = {
    "alarm_start_time": "00:00:00",
    "alarm_end_time": "23:59:59",
    "alarm_interval": 1440,
    "send_recovery_alarm": False,
}

NOT_NEED_EDIT_NODES = ["format_signature"]

DEFAULT_PATTERN_MONITOR_MSG = """{{content.level}}
{{content.begin_time}}
{{content.time}}
{{content.duration}}
{{content.target_type}}
{{content.data_source}}
{{content.content}}
{{content.current_value}}
{{content.biz}}
{{content.target}}
{{content.dimension}}
{{content.detail}}
日志示例: {{ json.loads(alarm.related_info)["__clustering_field__"] }}
更多日志: {{ json.loads(alarm.related_info)["bklog_link"] }}
"""

DEFAULT_PATTERN_RECOVER_MSG = """{{content.level}}
{{content.begin_time}}
{{content.time}}
{{content.duration}}
{{content.target_type}}
{{content.data_source}}
{{content.content}}
{{content.current_value}}
{{content.biz}}
{{content.target}}
{{content.dimension}}
{{content.detail}}
日志示例: {{ json.loads(alarm.related_info)["__clustering_field__"] }}
更多日志: {{ json.loads(alarm.related_info)["bklog_link"] }}
"""


class StrategiesType(object):
    NEW_CLS_strategy = "new_cls_strategy"
    NORMAL_STRATEGY = "normal_strategy"


class YearOnYearEnum(ChoicesEnum):
    NOT = 0
    ONE_HOUR = 1
    TWO_HOUR = 2
    THREE_HOUR = 3
    SIX_HOUR = 6
    HALF_DAY = 12
    ONE_DAY = 24

    _choices_labels = (
        (NOT, _("不比对")),
        (ONE_HOUR, _("1小时前")),
        (TWO_HOUR, _("2小时前")),
        (THREE_HOUR, _("3小时前")),
        (SIX_HOUR, _("6小时前")),
        (HALF_DAY, _("12小时前")),
        (ONE_DAY, _("24小时前")),
    )


class PatternEnum(ChoicesEnum):
    LEVEL_01 = "01"
    LEVEL_03 = "03"
    LEVEL_05 = "05"
    LEVEL_07 = "07"
    LEVEL_09 = "09"

    _choices_labels = (
        (LEVEL_01, "LEVEL_01"),
        (LEVEL_03, "LEVEL_03"),
        (LEVEL_05, "LEVEL_05"),
        (LEVEL_07, "LEVEL_07"),
        (LEVEL_09, "LEVEL_09"),
    )


class ActionEnum(ChoicesEnum):
    CREATE = "create"
    DELETE = "delete"

    @classmethod
    def get_choices(cls) -> tuple:
        return (
            cls.CREATE.value,
            cls.DELETE.value,
        )


# 日志聚类失败重试次数
MAX_FAILED_REQUEST_RETRY = 3


class SubscriptionTypeEnum(ChoicesEnum):
    EMAIL = "email"
    WECHAT = "wechat"

    _choices_labels = (
        (EMAIL, _("邮件")),
        (WECHAT, _("企业微信")),
    )


class YearOnYearChangeEnum(ChoicesEnum):
    ALL = "all"
    RISE = "rise"
    DECLINE = "decline"

    _choices_labels = (
        (ALL, _("所有")),
        (RISE, _("上升")),
        (DECLINE, _("下降")),
    )


class LogColShowTypeEnum(ChoicesEnum):
    PATTERN = "pattern"
    LOG = "log"

    _choices_labels = (
        (PATTERN, _("PATTERN模式")),
        (LOG, _("采样日志")),
    )


class FrequencyTypeEnum(ChoicesEnum):
    MINUTE = 1
    DAY = 2
    WEEK = 3
