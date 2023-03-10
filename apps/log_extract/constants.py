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
from django.utils.translation import ugettext_lazy as _

from apps.utils import ChoicesEnum


class DownloadStatus(ChoicesEnum):
    """
    过滤类型标识
    """

    INIT = "init"
    PIPELINE = "pipeline"
    PACKING = "packing"
    DISTRIBUTING = "distributing"
    DISTRIBUTING_PACKING = "distributing_packing"
    UPLOADING = "uploading"
    CSTONE_UPLOADING = "cstone_uploading"
    DOWNLOADABLE = "downloadable"
    COS_UPLOAD = "cos_upload"
    EXPIRED = "expired"
    FAILED = "failed"

    _choices_labels = (
        (INIT, _("初始化")),
        (PIPELINE, _("初始化任务调度")),
        (PACKING, _("文件打包中")),
        (DISTRIBUTING, _("文件分发中")),
        (DISTRIBUTING_PACKING, _("分发文件打包中")),
        (UPLOADING, _("文件上传中")),
        (CSTONE_UPLOADING, _("分发到网盘中")),
        (DOWNLOADABLE, _("已完成")),
        (EXPIRED, _("已过期")),
        (FAILED, _("文件提取异常")),
    )


class FilterType(ChoicesEnum):
    """
    过滤类型标识
    """

    MATCH_WORD = "match_word"
    LINE_RANGE = "line_range"
    TAIL_LINE = "tail_line"
    MATCH_RANGE = "match_range"
    _choices_labels = (
        (MATCH_WORD, _("按关键字过滤行")),
        (LINE_RANGE, _("按行数过滤")),
        (TAIL_LINE, _("获取最新n行")),
        (MATCH_RANGE, _("按关键字范围过滤行")),
    )


class TaskPipelineState(ChoicesEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    FINISHED = "FINISHED"
    _choices_labels = (
        (CREATED, _("未执行")),
        (RUNNING, _("执行中")),
        (FAILED, _("失败")),
        (SUSPENDED, _("暂停")),
        (REVOKED, _("已经终止")),
        (FINISHED, _("已经结束")),
    )


class KeywordType(ChoicesEnum):
    """
    关键字匹配类型
    """

    AND = "keyword_and"
    OR = "keyword_or"
    NOT = "keyword_not"

    _choices_labels = (
        (AND, _("与")),
        (OR, _("或")),
        (NOT, _("非")),
    )


class SelectType(ChoicesEnum):
    """
    目标选择类型标识
    """

    TOPO = "topo"
    MODULES = "module"
    _choices_labels = ((TOPO, _("按topo选择目标")), (MODULES, _("按module选择目标")))


class ExtractLinkType(ChoicesEnum):
    """链路类型"""

    if settings.FEATURE_TOGGLE["extract_cos"] == "on":
        COMMON = "common"
        QCLOUD_COS = "qcloud_cos"
        BK_REPO = "bk_repo"
        _choices_labels = ((COMMON, _("内网链路")), (QCLOUD_COS, _("腾讯云cos链路")), (BK_REPO, _("bk repo链路")))
    else:
        COMMON = "common"
        BK_REPO = "bk_repo"
        _choices_labels = ((COMMON, _("内网链路")), (BK_REPO, _("bk repo链路")))


class PreDateMode(ChoicesEnum):
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    ALL = "all"
    CUSTOM = "custom"
    _choices_labels = ((DAY, _("近一天")), (WEEK, _("近一周")), (MONTH, _("近一月")), (ALL, _("所有")), (CUSTOM, _("自定义")))


class ScheduleStatus(object):
    SUCCESS = "success"
    EXECUTING = "executing"


TASK_POLLING_INTERVAL = 5
MAX_SCHEDULE_TIMES = int(10 * 60 / TASK_POLLING_INTERVAL)

PREDATEMODE_CUSTOM_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 允许创建的目录前缀
ALLOWED_DIR_PREFIX = ("/",)
# 脚本路径, 调用组件渲染脚本内容使用
SCRIPT_PATH = "apps/log_extract/scripts/"
# 业务机器运行脚本的用户
ACCOUNT = {"linux": "root", "windows": settings.WINDOWS_ACCOUNT}
# 业务机器系统标号
LINUX = "1"
WINDOWS = "2"
# 过滤关键词最大长度
KEYWORD_MAX_LENGTH = 64

ALLOWED_TIME_RANGE = {"1d": "1", "1w": "7", "1m": "30", "all": None, "custom": "custom"}
GB_SIZE = 1024 * 1024 * 1024
MB_SIZE = 1024 * 1024
KB_SIZE = 1024

# 打包的临时目录
PACKING_PATH_LINUX = "/tmp/bk_log_extract/"
PACKING_PATH_WINDOWS = "/cygdrive/c/tmp/bk_log_extract/"

# 允许选择的过滤类型
ALLOWED_FILTER_TYPES = ("line_range", "match_word", "tail_line", "match_range")

TRANSIT_SERVER_DISTRIBUTION_PATH = settings.EXTRACT_DISTRIBUTION_DIR
TRANSIT_SERVER_PACKING_PATH = "/data/bk_log_extract/distribution_packing/"
BKREPO_CHILD_PACKING_PATH = "bk_log_extract/distribution"

# 前端轮询任务列表时间
POLLING_TIMEOUT = 5
# 搜索文件超时时间(s)
FILE_SEARCH_TIMEOUT = 60

# 1 为shell
JOB_SCRIPT_TYPE = 1

# 作业执行成功标识
JOB_SUCCESS_STATUS = 3

BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE = 500

# windows系统名称
WINDOWS_OS_NAME_LIST = settings.WINDOWS_OS_NAME_LIST
# 日志提取APPCODE
LOG_EXTRACT_APP_CODE = "bk_log_extract"
# 打包任务host容量不够脚本错误码
PACK_TASK_SCRIPT_NOT_HAVE_ENOUGH_CAP_ERROR_CODE = 3

BKLOG_TASK_LOG_REG_MATCH = r"<BKLOG>(.*?):(.*?)</BKLOG>"
BKLOG_LOG_KEY = 0
BKLOG_LOG_VALUE = 1

TASK_HOST_ID_INDEX = 2
TASK_IP_INDEX = 1
TASK_BK_CLOUD_ID_INDEX = 0

PIPELINE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# jobapi权限code
JOB_API_PERMISSION_CODE = 9900403
