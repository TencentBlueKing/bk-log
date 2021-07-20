# -*- coding: utf-8 -*-
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
