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
from apps.utils import ChoicesEnum

from django.utils.translation import ugettext_lazy as _

CONTENT_PATTERN_INDEX = 1
LATEST_PUBLISH_STATUS = "latest"
PATTERN_SIGNATURE_INDEX = 5
PATTERN_INDEX = 2

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
NEW_CLASS_QUERY_TIME_RANGE = "1d"

CLUSTERING_CONFIG_EXCLUDE = ["sample_set_id", "model_id"]
CLUSTERING_CONFIG_DEFAULT = "default_clustering_config"

DEFAULT_CLUSTERING_FIELDS = "log"
DEFAULT_IS_CASE_SENSITIVE = 0

SAMPLE_SET_SLEEP_TIMER = 15 * 60


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

    @classmethod
    def get_choices(cls) -> tuple:
        return (
            cls.LEVEL_09.value,
            cls.LEVEL_07.value,
            cls.LEVEL_05.value,
            cls.LEVEL_03.value,
            cls.LEVEL_01.value,
        )
