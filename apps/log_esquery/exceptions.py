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
from django.conf import settings
from apps.exceptions import BaseException, ErrorCode

# =================================================
# PERM
# =================================================


class BasePermException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_ESQUERY
    MESSAGE = _("权限异常")


class AccessControlTypeException(BasePermException):
    ERROR_CODE = "911"
    MESSAGE = _('查询的接入类型"{scenario_id}"不在接入范围%s' % settings.ES_QUERY_ACCESS_LIST)


class EsqueryIndexSetIdNotExistsException(BasePermException):
    ERROR_CODE = "915"
    MESSAGE = _("请输入索引集ID")


class EsqueryAccessDenyException(BasePermException):
    ERROR_CODE = "916"
    MESSAGE = _("此接口暂未对外，请确认")


# =================================================
# 场景问题
# =================================================


class ScenarioBaseException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SCENARIO
    MESSAGE = _("场景类型异常")


class ScenarioNotExistException(ScenarioBaseException):
    ERROR_CODE = "921"
    MESSAGE = _('该索引"{result_table_id}"不存在，所在的scenario_id不存在"{scenario_id}"')


class ScenarioMoreThenOneException(ScenarioBaseException):
    ERROR_CODE = "922"
    MESSAGE = _('该索引所在的scenario_id不唯一"{scenario_id_list}"')


class ScenarioEmptyException(ScenarioBaseException):
    ERROR_CODE = "923"
    MESSAGE = _("scenario空异常")


class SourceMoreThenOneException(ScenarioBaseException):
    ERROR_CODE = "924"
    MESSAGE = _('该索引所在的source_id不唯一"{source_id_list}"')


class SourceEmptyException(ScenarioBaseException):
    ERROR_CODE = "925"
    MESSAGE = _("存储集群ID(storage_cluster_id)信息空异常，当查询场景（scenario_id）不是bkdata时候需要传入正确的storage_cluster_id")


class SourceNotExistException(ScenarioBaseException):
    ERROR_CODE = "926"
    MESSAGE = _('该索引"{result_table_id}"不存在，所在的Source_id不存在"{source_id}"')


class ResultTableIdScenarioNotMatchException(ScenarioBaseException):
    ERROR_CODE = "927"
    MESSAGE = _('该索引"{result_table_id}"所在查询场景"{scenario_id}"与查询连接信息所需场景不匹配')


# =================================================
# 时间问题
# =================================================


class TimeBaseException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SEARCH
    MESSAGE = _("时间异常")


class TimeFieldEmptyException(TimeBaseException):
    ERROR_CODE = "931"
    MESSAGE = _("时间字段空异常")


# =================================================
# 版本问题
# =================================================


class VersionBaseException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SEARCH
    MESSAGE = _("客户端版本异常")


class UnKnowEsVersionException(VersionBaseException):
    ERROR_CODE = "941"
    MESSAGE = _('未知的ES服务端版本类型"{ip}":"{port}"')


# =================================================
# EsClient
# =================================================


class EsClientBaseException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SEARCH
    MESSAGE = _("客户端版本异常")


class EsClientAuthenticatorException(EsClientBaseException):
    ERROR_CODE = "950"
    MESSAGE = _("EsClient认证错误, 请检查连接ES的账号密码")


class EsClientConnectInfoException(EsClientBaseException):
    ERROR_CODE = "951"
    MESSAGE = _("缺少连接ES的账号密码")


class EsClientSocketException(EsClientBaseException):
    ERROR_CODE = "952"
    MESSAGE = _('连接ES错误"{error}"')


class EsClientLoaderException(EsClientBaseException):
    ERROR_CODE = "953"
    MESSAGE = _('加载EsClient客户端失败，场景"{scenario_id}"，版本"{version}')


class EsClientSearchException(EsClientBaseException):
    ERROR_CODE = "954"
    MESSAGE = _('EsClient查询错误"{error}"')


class EsClientHostPortException(EsClientBaseException):
    ERROR_CODE = "955"
    MESSAGE = _('原生ES主机"{host}"和端口"{port}错误"')


class EsClientMetaInfoException(EsClientBaseException):
    ERROR_CODE = "956"
    MESSAGE = _("从meta获取连接信息失败{message}")


class EsClientScrollException(EsClientBaseException):
    ERROR_CODE = "957"
    MESSAGE = _('EsClient scroll查询错误"{error}"')


class EsClientAliasException(EsClientBaseException):
    ERROR_CODE = "958"
    MESSAGE = _('EsClient Alias查询错误"{error}"')


class EsClientCatIndicesException(EsClientBaseException):
    ERROR_CODE = "959"
    MESSAGE = _('EsClient cat indices查询错误"{error}"')


class EsException(EsClientBaseException):
    ERROR_CODE = "960"
    MESSAGE = _("EsClient 查询错误")


class EsTimeoutException(EsClientBaseException):
    ERROR_CODE = "961"
    MESSAGE = _("Es 查询超时")


# =================================================
# Search
# =================================================


class BaseSearchException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SEARCH
    MESSAGE = _("查询异常")


class BaseSearchQueryBuilderException(BaseSearchException):
    ERROR_CODE = "961"
    MESSAGE = _("构建查询参数失败")


class BaseSearchFieldsException(BaseSearchException):
    ERROR_CODE = "962"
    MESSAGE = _('拉取ES字段失败, ERROR: "{error}"')


class BaseSearchContextTailScenarioException(BaseSearchException):
    ERROR_CODE = "963"
    MESSAGE = _('查询上下文场景错误, ERROR Scenario_id is : "{scenario_id}"')


class BaseSearchDslException(BaseSearchException):
    ERROR_CODE = "963"
    MESSAGE = _('查询DSL错误, ERROR DSL is : "{dsl}"')


class BaseSearchIndexSetDataDoseNotExists(BaseSearchException):
    ERROR_CODE = "964"
    MESSAGE = _("索引集【{index_set_id}】没有已审批通过的索引信息")


class BaseSearchIndexSetException(BaseException):
    ERROR_CODE = "965"
    MESSAGE = _('找不到索引集"{index_set_id}"的相关信息')


class BaseSearchIndexSetIdTimeFieldException(BaseException):
    ERROR_CODE = "966"
    MESSAGE = _('找不到索引集"{index_set_id}"的相关信息time_field信息')
