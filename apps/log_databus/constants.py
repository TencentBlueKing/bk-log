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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.utils import ChoicesEnum

META_PARAMS_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
RESTORE_INDEX_SET_PREFIX = "restore_"

BKLOG_RESULT_TABLE_PATTERN = fr"(\d*?_{settings.TABLE_ID_PREFIX}_.*)_.*_.*"

NOT_FOUND_CODE = "[404]"

# ESB返回节点管理check_task_ready API 404异常或非json内容
CHECK_TASK_READY_NOTE_FOUND_EXCEPTION_CODE = "1306201"

COLLECTOR_CONFIG_NAME_EN_REGEX = r"^[A-Za-z0-9_]+$"


class EsSourceType(ChoicesEnum):
    OTHER = "other"
    PRIVATE = "private"
    AWS = "aws"
    QCLOUD = "qcloud"
    ALIYUN = "aliyun"
    GOOGLE = "google"

    _choices_labels = (
        (OTHER, _("其他")),
        (AWS, _("AWS")),
        (QCLOUD, _("腾讯云")),
        (ALIYUN, _("阿里云")),
        (GOOGLE, _("google")),
        (PRIVATE, _("私有自建")),
    )


class StrategyKind(ChoicesEnum):
    CLUSTER_NODE = "cluster_node"
    COLLECTOR_CAP = "collector_cap"

    _choices_labels = ((CLUSTER_NODE, _("集群节点")), (COLLECTOR_CAP, _("采集项容量")))


class CollectItsmStatus(ChoicesEnum):
    NOT_APPLY = "not_apply"
    APPLYING = "applying"
    FAIL_APPLY = "fail_apply"
    SUCCESS_APPLY = "success_apply"

    _choices_labels = (
        (NOT_APPLY, _("未申请采集接入")),
        (APPLYING, _("采集接入进行中")),
        (FAIL_APPLY, _("采集接入失败")),
        (SUCCESS_APPLY, _("采集接入完成")),
    )


STORAGE_CLUSTER_TYPE = "elasticsearch"
KAFKA_CLUSTER_TYPE = "kafka"
TRANSFER_CLUSTER_TYPE = "transfer"
REGISTERED_SYSTEM_DEFAULT = "_default"
ETL_DELIMITER_IGNORE = "i"
ETL_DELIMITER_DELETE = "d"
ETL_DELIMITER_END = "e"
# 添加空闲机获取
BK_SUPPLIER_ACCOUNT = "0"
# 添加ES默认schema
DEFAULT_ES_SCHEMA = "http"
META_DATA_ENCODING = "utf-8"

# ADMIN请求用户名
ADMIN_REQUEST_USER = "admin"

# 创建bkdata_data_id 配置
BKDATA_DATA_SCENARIO = "custom"
BKDATA_DATA_SCENARIO_ID = 47
BKDATA_TAGS = []
BKDATA_DATA_SOURCE_TAGS = ["server"]
BKDATA_DATA_REGION = "inland"
BKDATA_DATA_SOURCE = "data_source"
BKDATA_DATA_SENSITIVITY = "private"
BKDATA_PERMISSION = "permission"

# 创建bkdata_data_id允许错误最大数，超过该数值则需要人工介入
MAX_CREATE_BKDATA_DATA_ID_FAIL_COUNT = 3

# 获取biz_topo请求level
SEARCH_BIZ_INST_TOPO_LEVEL = -1

# 获取internal_topo并插入的默认节点位置
INTERNAL_TOPO_INDEX = 0

# biz_topo空闲节点默认index
BIZ_TOPO_INDEX = 0

# 高级清洗创建索引集默认时间格式
DEFAULT_TIME_FORMAT = _("微秒（microsecond）")
# 高级清洗默认创建业务应用型索引集
DEFAULT_CATEGORY_ID = "application_check"
DEFAULT_ETL_CONFIG = "bkdata_clean"

# 同步清洗最长ttl时间 60*10
MAX_SYNC_CLEAN_TTL = 600


class AsyncStatus(object):
    RUNNING = "RUNNING"
    DONE = "DONE"


FIELD_TEMPLATE = {
    "field_name": "",
    "alias_name": "",
    "field_type": "",
    "description": "",
    "is_analyzed": False,
    "is_dimension": False,
    "is_time": False,
    "is_delete": True,
    "is_built_in": False,
}


class TargetObjectTypeEnum(ChoicesEnum):
    """
    CMDB对象类型，可选 `SERVICE`, `HOST`
    """

    SERVICE = "SERVICE"
    HOST = "HOST"

    _choices_labels = (
        (HOST, _("主机")),
        (SERVICE, _("服务实例")),
    )


class TargetNodeTypeEnum(ChoicesEnum):
    """
    CMDB节点类型，可选 `TOPO`, `INSTANCE`
    """

    TOPO = "TOPO"
    INSTANCE = "INSTANCE"
    SERVICE_TEMPLATE = "SERVICE_TEMPLATE"
    SET_TEMPLATE = "SET_TEMPLATE"

    _choices_labels = (
        (TOPO, _("TOPO")),
        (INSTANCE, _("主机实例")),
        (SERVICE_TEMPLATE, _("服务模板")),
        (SET_TEMPLATE, _("集群模板")),
    )


class CleanProviderEnum(ChoicesEnum):
    """
    清洗能力
    """

    TRANSFER = "transfer"
    BKDATA = "bkdata"

    _choices_labels = (
        (TRANSFER, _("Transfer")),
        (BKDATA, _("数据平台")),
    )


class CollectStatus(object):
    """
    采集任务状态-结合以下两种状态
    subscription_instance_status.instances[0].status
     - PENDING
     - RUNNING
     - SUCCESS
     - FAILED
    subscription_instance_status.instances[0].host_statuses.status
     - RUNNING
     - TERMINATED
     - UNKNOWN
    """

    PREPARE = "PREPARE"
    SUCCESS = "SUCCESS"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    PENDING = "PENDING"
    TERMINATED = "TERMINATED"  # SUCCESS + 空
    UNKNOWN = "UNKNOWN"


class LogPluginInfo(object):
    """
    采集插件信息
    """

    NAME = "bkunifylogbeat"
    VERSION = "latest"


class ActionStatus(object):
    START = "START"
    INSTALL = "INSTALL"


class RunStatus(object):
    RUNNING = _("部署中")
    SUCCESS = _("正常")
    FAILED = _("失败")
    PARTFAILED = _("部分失败")
    TERMINATED = _("已停用")
    UNKNOWN = _("未知")
    PREPARE = _("准备中")


class EtlConfig(object):
    BK_LOG_TEXT = "bk_log_text"
    BK_LOG_JSON = "bk_log_json"
    BK_LOG_DELIMITER = "bk_log_delimiter"
    BK_LOG_REGEXP = "bk_log_regexp"


# 节点属性字段过滤黑名单
NODE_ATTR_PREFIX_BLACKLIST = [
    "ml.",
    "xpack.",
]

BKDATA_ES_TYPE_MAP = {
    "integer": "int",
    "long": "long",
    "keyword": "string",
    "text": "text",
    "double": "double",
    "object": "text",
    "nested": "text",
}

ETL_PARAMS = {"retain_original_text": True, "separator_regexp": "", "separator": ""}
