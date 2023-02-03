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
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import BaseException, ErrorCode

# =================================================
# 日志聚类模块
# =================================================


class BaseClusteringException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_CLUSTERING
    MESSAGE = _("日志聚类模块异常")


class ClusteringClosedException(BaseClusteringException):
    ERROR_CODE = "001"
    MESSAGE = _("聚类未开放")


class NodeConfigException(BaseClusteringException):
    ERROR_CODE = "002"
    MESSAGE = _("获取node config异常{steps}")


class NotSupportStepNameQueryException(BaseClusteringException):
    ERROR_CODE = "003"
    MESSAGE = _("不支持的step_name状态获取: {step_name}")


class EvaluationStatusResponseException(BaseClusteringException):
    ERROR_CODE = "004"
    MESSAGE = _("evaluation_status返回异常: {evaluation_status}")


class ClusteringConfigNotExistException(BaseClusteringException):
    ERROR_CODE = "005"
    MESSAGE = _("聚类配置不存在")


class ClusteringConfigStrategyException(BaseClusteringException):
    ERROR_CODE = "006"
    MESSAGE = _("聚类配置对应告警策略错误: {index_set_id}")


class ClusteringIndexSetNotExistException(BaseClusteringException):
    ERROR_CODE = "007"
    MESSAGE = _("聚类配置对应索引集不存在: {index_set_id}")


class BkdataStorageNotExistException(BaseClusteringException):
    ERROR_CODE = "009"
    MESSAGE = _("计算平台落地存储不存在: {index_set_id}")


class BkdataFlowException(BaseClusteringException):
    ERROR_CODE = "010"
    MESSAGE = _("计算平台flow返回异常: {flow_id}")


class BkdataRegexException(BaseClusteringException):
    ERROR_CODE = "011"
    MESSAGE = _("正则表达式字段名: {field_name}不符合计算平台标准[a-zA-Z][a-zA-Z0-9]*")


class BkdataFieldsException(BaseClusteringException):
    ERROR_CODE = "012"
    MESSAGE = _("不允许删除参与日志聚类字段: {field}")


class ModelReleaseNotFoundException(BaseClusteringException):
    ERROR_CODE = "013"
    MESSAGE = _("模型找不到对应的发布版本: {model_id}")


class LogSearchUrlNotFoundException(BaseClusteringException):
    ERROR_CODE = "014"
    MESSAGE = _("聚类配置log_search_url配置不存在")
