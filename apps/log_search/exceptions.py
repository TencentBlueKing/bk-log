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
# PERM
# =================================================
class BasePermException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_PERM
    MESSAGE = _("权限异常")


class ProjectIdDoesNotExists(BasePermException):
    ERROR_CODE = "001"
    MESSAGE = _("参数校验异常：项目ID不存在")


# =================================================
# 管理
# =================================================
class BaseAdminException(BaseException):
    ERROR_CODE = "100"
    MESSAGE = _("管理模块异常")


# =================================================
# 管理-接入场景
# =================================================


class ScenarioException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SCENARIO
    MESSAGE = _("接入场景异常")


class ScenarioNotSupportedException(ScenarioException):
    ERROR_CODE = "601"
    MESSAGE = _('暂不支持"{scenario_id}"场景的操作')


class ScenarioConnectEsFailException(ScenarioException):
    ERROR_CODE = "602"
    MESSAGE = _('探测ES连通性失败,失败原因："{es_fail_reason}"')


class ScenarioEsClientConnectException(ScenarioException):
    ERROR_CODE = "603"
    MESSAGE = _("EsClient链接失败")


class ScenarioQueryIndexFailException(ScenarioException):
    ERROR_CODE = "604"
    MESSAGE = _('EsClient查询index失败,失败原因:"{es_fail_reason}"')


# =================================================
# 管理-数据源
# =================================================
class BaseSourceException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SOURCE
    MESSAGE = _("数据源模块异常")


class SourceDuplicateException(BaseSourceException):
    ERROR_CODE = "201"
    MESSAGE = _('该项目下已存在名称为"{source_name}"的数据源')


class SourceDoseNotExistException(BaseSourceException):
    ERROR_CODE = "202"
    MESSAGE = _("数据源不存在")


class SourceNotAllowEditableException(BaseSourceException):
    ERROR_CODE = "203"
    MESSAGE = _("此数据源不允许编辑")


class SourceConnectException(BaseSourceException):
    ERROR_CODE = "204"
    MESSAGE = _("ES服务器连接异常")


class SourceNotAllowDeleteException(BaseSourceException):
    ERROR_CODE = "205"
    MESSAGE = _("此数据源已有关联的索引集，无法直接删除")


# =================================================
# 管理-索引集
# =================================================


class BaseIndexSetException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_INDEX_SET
    MESSAGE = _("索引集模块异常")


class IndexSetDoseNotExistException(BaseIndexSetException):
    ERROR_CODE = "301"
    MESSAGE = _("索引集不存在")


class IndexDoseNotExistInBkDataException(BaseIndexSetException):
    ERROR_CODE = "302"
    MESSAGE = _('索引"{result_table_id}"在数据平台中不存在')


class IndexSetNameDuplicateException(BaseIndexSetException):
    ERROR_CODE = "305"
    MESSAGE = _('该项目下已存在名称为"{index_set_name}"的数据集')


class IndexDoseNotExistInEsException(BaseIndexSetException):
    ERROR_CODE = "306"
    MESSAGE = _('索引"{result_table_id}"在此ES中不存在')


class ResultTableIdDuplicateException(BaseIndexSetException):
    ERROR_CODE = "307"
    MESSAGE = _('该索引集下已存在"{result_table_id}"结果表')


class FieldsConsistencyException(BaseIndexSetException):
    ERROR_CODE = "308"
    MESSAGE = _("索引字段不一致，无法添加索引到同一个索引集中")


class IndexDuplicateException(BaseIndexSetException):
    ERROR_CODE = "309"
    MESSAGE = _("索引已存在，请勿添加相同索引")


class IndexCrossBusinessException(BaseIndexSetException):
    ERROR_CODE = "310"
    MESSAGE = _("索引集不支持跨业务")


class IndexResultTableApiException(BaseIndexSetException):
    ERROR_CODE = "311"
    MESSAGE = _("获取结果表信息失败")


class IndexCrossClusterException(BaseIndexSetException):
    ERROR_CODE = "312"
    MESSAGE = _("索引集不支持跨集群")


class IndexListDataException(BaseIndexSetException):
    ERROR_CODE = "313"
    MESSAGE = _("索引列表数据异常")


class IndexTraceNotAcceptException(BaseIndexSetException):
    ERROR_CODE = "314"
    MESSAGE = _("索引列表不满足Trace要求")


class IndexTraceProjectIDException(BaseIndexSetException):
    ERROR_CODE = "315"
    MESSAGE = _("项目ID不存在无法搜索TRACE类型索引集")


class FieldsTypeConsistencyException(BaseIndexSetException):
    ERROR_CODE = "316"
    MESSAGE = _("索引字段{field_type}类型不一致，无法添加索引到同一个索引集中")


class FieldsDateNotExistException(BaseIndexSetException):
    ERROR_CODE = "317"
    MESSAGE = _("索引缺少时间字段，无法添加索引到同一个索引集中")


class FieldsDateNotSameException(BaseIndexSetException):
    ERROR_CODE = "318"
    MESSAGE = _("索引时间字段不同，无法添加索引到同一个索引集中")


class FieldsDateTypeNotSameException(BaseIndexSetException):
    ERROR_CODE = "319"
    MESSAGE = _("索引时间字段类型不同，无法添加索引到同一个索引集中")


class MappingEmptyException(BaseIndexSetException):
    ERROR_CODE = "320"
    MESSAGE = _("索引{result_table_id} mapping信息查询结果为空")


class IndexSetSourceException(BaseIndexSetException):
    ERROR_CODE = "321"
    MESSAGE = _("您没有此索引集的编辑权限")


class IndexSetNotEmptyException(BaseIndexSetException):
    ERROR_CODE = "322"
    MESSAGE = _("索引集不能为空集")


class IndexSetNotHaveConflictIndex(BaseIndexSetException):
    ERROR_CODE = "323"
    MESSAGE = _("索引集中的索引字段不能有冲突")


# =================================================
# 管理-检索
# =================================================


class BaseSearchException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_SEARCH
    MESSAGE = _("检索模块异常")


class BaseSearchIndexSetException(BaseException):
    ERROR_CODE = "401"
    MESSAGE = _('找不到索引集"{index_set_id}"的相关信息')


class BaseSearchIndexSetTimeFieldException(BaseException):
    ERROR_CODE = "402"
    MESSAGE = _('找不到索引集"{index_set_id}"的时间字段信息，无法进行检索')


class BaseSearchTimeTranslateException(BaseException):
    ERROR_CODE = "403"
    MESSAGE = _("将时间字段转换成handler接口可用格式失败")


class BaseSearchKeyWordException(BaseException):
    ERROR_CODE = "404"
    MESSAGE = _("参数中没有keyword")


class BaseSearchStartPointException(BaseException):
    ERROR_CODE = "405"
    MESSAGE = _("参数中没有开始指针")


class BaseSearchScenarioException(BaseException):
    ERROR_CODE = "406"
    MESSAGE = _("场景选择错误")


class BaseSearchGseIndexNoneException(BaseException):
    ERROR_CODE = "407"
    MESSAGE = _("查询上下文需要gseindex相关信息")


class BaseSearchConnectFailException(BaseSearchException):
    ERROR_CODE = "408"
    MESSAGE = _("链接到ES数据源失败")


class BaseSearchParamNotExistException(BaseSearchException):
    ERROR_CODE = "409"
    MESSAGE = _("添加用户index字段时缺少相关参数")


class BaseSearchFieldsFailException(BaseSearchException):
    ERROR_CODE = "410"
    MESSAGE = _("查询ES中索引下的fields字段失败,失败原因{fail_reason}")


class BaseSearchIndexSetDataDoseNotExists(BaseSearchException):
    ERROR_CODE = "411"
    MESSAGE = _("索引集【{index_set_id}】没有已审批通过的索引信息")


class BaseSearchQueryBuilderException(BaseSearchException):
    ERROR_CODE = "412"
    MESSAGE = _("构建查询参数失败")


class BaseSearchResultAnalyzeException(BaseException):
    ERROR_CODE = "413"
    MESSAGE = _("不需要输出")


class BaseSearchDictException(BaseException):
    ERROR_CODE = "414"
    MESSAGE = _("search dict empty错误{search_dict}")


class BaseSearchSortListException(BaseException):
    ERROR_CODE = "415"
    MESSAGE = _("该字段{sort_item}不支持排序")


class SearchGetSchemaException(BaseSearchException):
    ERROR_CODE = "416"
    MESSAGE = _("拉取schema错误{index}")


class SearchIndexNoTimeFieldException(BaseException):
    ERROR_CODE = "417"
    MESSAGE = _("Trace查询time field不存在")


class SearchExceedMaxSizeException(BaseException):
    ERROR_CODE = "418"
    MESSAGE = _("超出最大查询数量：{size}")


class SearchUnKnowTimeFieldType(BaseException):
    ERROR_CODE = "419"
    MESSAGE = _("未知的时间字段类型")


class SearchUnKnowTimeField(BaseException):
    ERROR_CODE = "420"
    MESSAGE = _("未知的时间字段/时间字段类型/时间字段单位")


class UnauthorizedResultTableException(BaseSearchException):
    ERROR_CODE = "421"
    MESSAGE = _("用户无结果表 {result_tables} 的管理权限，无法添加到索引集中")


class SearchNotTimeFieldType(BaseException):
    ERROR_CODE = "422"
    MESSAGE = _("此索引没有找到时间字段类型")


class FavoriteSearchNotExists(BaseException):
    ERROR_CODE = "423"
    MESSAGE = _("收藏查询不存在")


class DateHistogramException(BaseException):
    ERROR_CODE = "424"
    MESSAGE = _("索引集【{index_set_id}】聚合查询异常：{err}")


class FavoriteNotExistException(BaseException):
    ERROR_CODE = "425"
    MESSAGE = _("收藏不存在")


class FavoriteAlreadyExistException(BaseException):
    ERROR_CODE = "426"
    MESSAGE = _("收藏名已存在")


class FavoriteVisibleTypeNotAllowedModifyException(BaseException):
    ERROR_CODE = "426"
    MESSAGE = _("收藏可见类型不允许修改")


class FavoriteGroupNotExistException(BaseException):
    ERROR_CODE = "430"
    MESSAGE = _("收藏组不存在")


class FavoriteGroupAlreadyExistException(BaseException):
    ERROR_CODE = "431"
    MESSAGE = _("收藏组已存在")


class FavoriteGroupNotAllowedModifyException(BaseException):
    ERROR_CODE = "432"
    MESSAGE = _("个人收藏组不允许修改")


class FavoriteGroupNotAllowedDeleteException(BaseException):
    ERROR_CODE = "433"
    MESSAGE = _("只有公开收藏组可以删除")


class IndexSetFieldsConfigNotExistException(BaseException):
    ERROR_CODE = "434"
    MESSAGE = _("索引集字段配置不存在")


class DefaultConfigNotAllowedDelete(BaseException):
    ERROR_CODE = "435"
    MESSAGE = _("默认索引集字段配置不允许删除")


class IndexSetFieldsConfigAlreadyExistException(BaseException):
    ERROR_CODE = "436"
    MESSAGE = _("索引集字段配置名称已存在")


# =================================================
# 导出
# =================================================


class MissAsyncExportException(BaseException):
    ERROR_CODE = "501"
    MESSAGE = _("对应索引集缺少异步导出必备fields{}")


class OverAsyncExportMaxCount(BaseException):
    ERROR_CODE = "502"
    MESSAGE = _("超过异步导出最大条数限制{max_async_export_count}")


class CouldNotFindTemplateException(BaseException):
    ERROR_CODE = "503"
    MESSAGE = _("无法找到{template_name}{language}相关模板")


class PreCheckAsyncExportException(BaseException):
    ERROR_CODE = "504"
    MESSAGE = _("创建异步导出任务前置检查失败,请检查索引集字段配置")


# =================================================
# JWT
# =================================================


class BkJwtClientException(BasePermException):
    ERROR_CODE = "901"
    MESSAGE = _("请升级blueapps至最新版本")


class BkJwtVerifyException(BasePermException):
    ERROR_CODE = "902"
    MESSAGE = _("获取JWT信息异常")


class BkJwtVerifyFailException(BasePermException):
    ERROR_CODE = "903"
    MESSAGE = _("JWT校验失败")


class SettingMenuException(BasePermException):
    ERROR_CODE = "1001"
    MESSAGE = _("配置中menu对象异常")


class FunctionGuideException(BaseException):
    ERROR_CODE = "1002"
    MESSAGE = _("不存在该功能引导")
