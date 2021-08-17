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
from django.utils.translation import ugettext_lazy as _

# 告警历史查询最长时间
HISTORY_MAX_DAYS = 7
#  数据上报监控通用业务id
GLOBAL_BK_BIZ_ID = 0

# search数据上报聚合时间
USER_SEARCH_TIME_MINUTE = 1
USER_SEARCH_TIME_SECOND = 10

# 数据上报默认config对象字段名
BK_DATA_CUSTOM_REPORT_USER_INDEX_SET_HISTORY = "search_history"

# 运营数据饼状图分类
OPERATION_PIE_CHOICE_MAP = [
    {"label": _("大于30 s"), "min": 30000},
    {"label": _("10~30 s"), "min": 10000, "max": 30000},
    {"label": _("0~10 s"), "min": 0, "max": 10000},
]

MINUTE_GROUP_BY = "minute1440"
