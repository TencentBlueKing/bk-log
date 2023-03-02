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
# 采集配置
# =================================================


class BaseCollectorConfigException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_COLLECTOR_CONFIG
    MESSAGE = _("采集配置模块异常")


class BaseCollectorPluginException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_COLLECTOR_PLUGIN
    MESSAGE = _("采集插件模块异常")


class CollectorConfigNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "001"
    MESSAGE = _("采集配置不存在")


class DataLinkConfigNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "002"
    MESSAGE = _("链路配置不存在")


class CollectorPluginNotExistException(BaseCollectorPluginException):
    ERROR_CODE = "003"
    MESSAGE = _("采集插件不存在")


class CollectorIdNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "101"
    MESSAGE = _("参数校验异常：采集项ID不存在")


class CollectorTaskIdNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "102"
    MESSAGE = _("参数校验异常：采集任务ID不存在")


class CollectorTaskInstanceIdNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "103"
    MESSAGE = _("参数校验异常：采集实例ID不存在")


class CollectorConfigNameDuplicateException(BaseCollectorConfigException):
    ERROR_CODE = "104"
    MESSAGE = _("采集项名称已存在")


class CollectorConfigDataIdNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "105"
    MESSAGE = _("数据链路ID不存在")


class SubscriptionInfoNotFoundException(BaseCollectorConfigException):
    ERROR_CODE = "106"
    MESSAGE = _("无法查询到该订阅配置信息")


class CollectorActiveException(BaseCollectorConfigException):
    ERROR_CODE = "107"
    MESSAGE = _("采集项在停止状态下不能编辑")


class CollectorTaskRunningStatusException(BaseCollectorConfigException):
    ERROR_CODE = "108"
    MESSAGE = _("采集项已存在正在部署中的任务，请不要重复部署")


class CollectorCreateOrUpdateSubscriptionException(BaseCollectorConfigException):
    ERROR_CODE = "109"
    MESSAGE = _("创建或更新节点管理订阅配置异常{err}")


class CollectorCreateBkdataIdException(BaseCollectorConfigException):
    ERROR_CODE = "110"
    MESSAGE = _("创建数据平台异常{err}")


class CollectorIllegalIPException(BaseCollectorConfigException):
    ERROR_CODE = "111"
    MESSAGE = _("采集项包含非该业务【{bk_biz_id}】IP，异常IP列表为: {illegal_ips}")


class CollectorConfigNameENDuplicateException(BaseCollectorConfigException):
    ERROR_CODE = "112"
    MESSAGE = _("采集项{collector_config_name_en}英文名重复")


class CollectorBkDataNameDuplicateException(BaseCollectorConfigException):
    ERROR_CODE = "113"
    MESSAGE = _("采集项{bk_data_name}采集链路data_name重复")


class CollectorResultTableIDDuplicateException(BaseCollectorConfigException):
    ERROR_CODE = "114"
    MESSAGE = _("采集项{result_table_id}结果表ID重复")


class CollectorPluginNameDuplicateException(BaseCollectorPluginException):
    ERROR_CODE = "115"
    MESSAGE = _("采集插件名称已存在")


class CollectorPluginNotMatchException(BaseCollectorPluginException):
    ERROR_CODE = "116"
    MESSAGE = _("参数异常：采集插件不匹配")


class ContainerCollectConfigValidateYamlException(BaseCollectorConfigException):
    ERROR_CODE = "117"
    MESSAGE = _("容器采集配置 yaml 格式不合法")


class ModifyCollectorConfigException(BaseCollectorConfigException):
    ERROR_CODE = "118"
    MESSAGE = _("更新采集项配置异常: {e}")


class ResultTableNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "119"
    MESSAGE = _("采集项{result_table_id}结果表ID不存在")


class CollectorPluginNotImplemented(BaseCollectorPluginException):
    ERROR_CODE = "120"
    MESSAGE = _("采集插件无采集项实例")


class StorageNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "201"
    MESSAGE = _("集群不存在")


class StorageCreateException(BaseCollectorConfigException):
    ERROR_CODE = "202"
    MESSAGE = _("bk_biz_id为必填字段，且为整数")


class StorageNotPermissionException(BaseCollectorConfigException):
    ERROR_CODE = "203"
    MESSAGE = _("权限异常")


class StorageConnectException(BaseCollectorConfigException):
    ERROR_CODE = "204"
    MESSAGE = _("集群连接异常")


class StorageConnectInfoException(BaseCollectorConfigException):
    ERROR_CODE = "205"
    MESSAGE = _("集群连接异常, 异常信息{info}")


class StorageUnKnowEsVersionException(BaseCollectorConfigException):
    ERROR_CODE = "206"
    MESSAGE = _('未知的ES服务端版本类型"{ip}":"{port}"')


class StorageVersionCheckerException(BaseCollectorConfigException):
    ERROR_CODE = "207"
    MESSAGE = _('http探测ES版本错误, "{msg}"')


class HotColdCheckException(BaseCollectorConfigException):
    ERROR_CODE = "208"
    MESSAGE = _("集群不支持冷热数据功能")


class StorageHaveResource(BaseCollectorConfigException):
    ERROR_CODE = "209"
    MESSAGE = _("集群还有未删除的采集项、第三方集群索引集")


class BKBASEStorageNotExistException(BaseCollectorPluginException):
    ERROR_CODE = "210"
    MESSAGE = _("集群未同步到数据平台")


class BKBaseStorageSyncFailed(BaseCollectorConfigException):
    ERROR_CODE = "211"
    MESSAGE = _("集群同步到数据平台失败")


class PublicESClusterNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "212"
    MESSAGE = _("不存在公共ES集群")


class EtlNotSupportedException(BaseCollectorConfigException):
    ERROR_CODE = "301"
    MESSAGE = _("暫不支持{separator_node_action}类清洗")


class EtlDelimiterParseException(BaseCollectorConfigException):
    ERROR_CODE = "302"
    MESSAGE = _("分隔符配置解析异常")


class EtlPreviewException(BaseCollectorConfigException):
    ERROR_CODE = "303"
    MESSAGE = _("字段提取预览失败，请检查提取规则与数据是否匹配")


class EtlParseTimeFieldException(BaseCollectorConfigException):
    ERROR_CODE = "304"
    MESSAGE = _("解析数据时间字段异常")


class EtlParseTimeFormatException(BaseCollectorConfigException):
    ERROR_CODE = "305"
    MESSAGE = _("解析时间格式异常")


class EtlDelimiterFieldsException(BaseCollectorConfigException):
    ERROR_CODE = "306"
    MESSAGE = _("字段名总长度超过256，暂不支持")


class EtlStorageUsedException(BaseCollectorConfigException):
    ERROR_CODE = "307"
    MESSAGE = _("该业务已超出公共集群容量限制")


class SameLinkNameException(BaseCollectorConfigException):
    ERROR_CODE = "308"
    MESSAGE = _("该数据链路名已被使用")


class EditLinkException(BaseCollectorConfigException):
    ERROR_CODE = "309"
    MESSAGE = _("数据链路kafka、transfer集群不可修改，es集群不可删除")


class RegexMatchException(BaseCollectorConfigException):
    ERROR_CODE = "310"
    MESSAGE = _("无法匹配到行首，请确认")


class RegexInvalidException(BaseCollectorConfigException):
    ERROR_CODE = "311"
    MESSAGE = _('正则表达式不合法: "{error}" 请确认')


class KafkaConnectException(BaseCollectorConfigException):
    ERROR_CODE = "401"
    MESSAGE = _('kafka连接失败"{error}"')


class KafkaPartitionException(BaseCollectorConfigException):
    ERROR_CODE = "402"
    MESSAGE = _("最新数据获取失败, 可刷新重试一下")


class DataLinkConfigPartitionException(BaseCollectorConfigException):
    ERROR_CODE = "403"
    MESSAGE = _("数据链路配置获取失败")


class CollectItsmTokenIllega(BaseCollectorConfigException):
    ERROR_CODE = "501"
    MESSAGE = _("采集接入ITSM-TOKEN非法")


class CollectItsmHasApply(BaseCollectorConfigException):
    ERROR_CODE = "502"
    MESSAGE = _("已经提交采集接入申请")


class CollectItsmNotExists(BaseCollectorConfigException):
    ERROR_CODE = "503"
    MESSAGE = _("采集接入ITSM流程服务不存在")


class CollectNotSuccessNotCanStart(BaseCollectorConfigException):
    ERROR_CODE = "504"
    MESSAGE = _("采集接入流程未完成，无法启动采集")


class CollectNotSuccess(BaseCollectorConfigException):
    ERROR_CODE = "504"
    MESSAGE = _("采集接入未完成")


class BkdataIdFeatureNotExist(BaseCollectorConfigException):
    ERROR_CODE = "601"
    MESSAGE = _("后台bkdata_id_feature不存在")


class CleanTemplateNotExistException(BaseCollectorConfigException):
    ERROR_CODE = "701"
    MESSAGE = _("清洗模板{clean_template_id}不存在")


class CleanTemplateRepeatException(BaseCollectorConfigException):
    ERROR_CODE = "702"
    MESSAGE = _("该业务 {bk_biz} 已存在该模板{name}")


class ProjectNoteExistException(BaseCollectorConfigException):
    ERROR_CODE = "703"
    MESSAGE = _("该业务{bk_biz_id}未找到对应project")


class CleanTemplateVisibleException(BaseCollectorConfigException):
    ERROR_CODE = "704"
    MESSAGE = _("该业务{bk_biz} 不可编辑或删除该模板{name}")


class ArchiveNotFound(BaseCollectorConfigException):
    ERROR_CODE = "800"
    MESSAGE = _("归档配置不存在")


class RestoreNotFound(BaseCollectorConfigException):
    ERROR_CODE = "801"
    MESSAGE = _("归档回溯不存在")


class RestoreExpired(BaseCollectorConfigException):
    ERROR_CODE = "802"
    MESSAGE = _("归档回溯已经过期")


class MissedNamespaceException(BaseCollectorConfigException):
    ERROR_CODE = "901"
    MESSAGE = _("缺少namespace参数")


class BCSApiException(BaseCollectorConfigException):
    ERROR_CODE = "902"
    MESSAGE = _("bcs api错误: {error}")


class RuleCollectorException(BaseCollectorConfigException):
    ERROR_CODE = "903"
    MESSAGE = _("rule: {rule_id}异常")


class NeedBcsClusterIdException(BaseCollectorConfigException):
    ERROR_CODE = "904"
    MESSAGE = _("请求无bcs_cluster_id参数，请检查")


class BcsClusterIdNotValidException(BaseCollectorConfigException):
    ERROR_CODE = "905"
    MESSAGE = _("bcs_cluster_id不合法，请检查")


class NamespaceNotValidException(BaseCollectorConfigException):
    ERROR_CODE = "906"
    MESSAGE = _("namespace({namespaces})不合法，请检查")


class AllNamespaceNotAllowedException(BaseCollectorConfigException):
    ERROR_CODE = "907"
    MESSAGE = _("共享集群下namespace不允许为空，或设置为all，请检查")


class NodeNotAllowedException(BaseCollectorConfigException):
    ERROR_CODE = "908"
    MESSAGE = _("共享集群下不允许采集node的日志，请检查")


class VclusterNodeNotAllowedException(BaseCollectorConfigException):
    ERROR_CODE = "909"
    MESSAGE = _("虚拟集群下不允许采集node的日志，请检查")
