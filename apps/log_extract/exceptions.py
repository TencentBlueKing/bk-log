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


class BaseExtractException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_EXTRACT
    MESSAGE = _("日志提取模块异常")


class CstoneConfigNotExists(BaseExtractException):
    ERROR_CODE = "001"
    MESSAGE = _("请配置云石账密信息")


class TransitServerConfigNotExists(BaseExtractException):
    ERROR_CODE = "002"
    MESSAGE = _("请配置中转服务器信息")


class TaskIDDoesNotExist(BaseExtractException):
    ERROR_CODE = "101"
    MESSAGE = _("该Task ID 不存在")


class TaskPullTopoError(BaseExtractException):
    ERROR_CODE = "102"
    MESSAGE = _("拉取topo结构失败：{error}, 请求参数：{params} ")


class TaskPullTopoNotExist(BaseExtractException):
    ERROR_CODE = "103"
    MESSAGE = _("获取全部topo为空,请求参数：{params} ")


class TasksRetrieveFailed(BaseExtractException):
    ErrorCode = "104"
    MESSAGE = _("获取任务详情失败，您不是该任务的创建者")


class TaskCreateFailed(BaseExtractException):
    ErrorCode = "105"
    MESSAGE = _("选择文件不可下载，请确认所配置策略，不可下载文件：{failed_download_file_list}")


class TasksRecreateFailed(BaseExtractException):
    ErrorCode = "106"
    MESSAGE = _("重新创建任务失败，您不是原任务的创建者")


class TaskDeleteNotAllowed(BaseExtractException):
    ErrorCode = "107"
    MESSAGE = _("禁止删除任务！")


class TaskFilterError(BaseExtractException):
    ErrorCode = "108"
    MESSAGE = _("{message}")


class TaskDownloadExpired(BaseExtractException):
    ErrorCode = "109"
    MESSAGE = _("当前任务已过期")


class TaskOverDownloadCount(BaseExtractException):
    ErrorCode = "110"
    MESSAGE = _("当前任务已达最大下载次数")


class TaskRunPipelineError(BaseExtractException):
    ErrorCode = "111"
    MESSAGE = _("创建任务异常")


class TaskDownloadNotAvailable(BaseExtractException):
    ErrorCode = "112"
    MESSAGE = _("当前任务不可下载")


class TaskDownloadDenied(BaseExtractException):
    ErrorCode = "113"
    MESSAGE = _("下载任务失败，您没有此任务的下载权限")


class TaskUpdateFailed(BaseExtractException):
    ErrorCode = "114"
    MESSAGE = _("更新任务信息失败，你不是此任务的创建者")


class TaskQcloudCosNotConfig(BaseExtractException):
    ErrorCode = "115"
    MESSAGE = _("{message}")


class TaskNotHaveExtractLink(BaseExtractException):
    ErrorCode = "116"
    MESSAGE = _("请管理员配置提取链路")


class TaskExtractLinkNotExist(BaseExtractException):
    ErrorCode = "117"
    MESSAGE = _("提取链路不存在，请管理员检查")


class TaskFileLinkNotExist(BaseExtractException):
    ErrorCode = "118"
    MESSAGE = _("下载目标文件不存在")


class TaskCannotCreateByCommonLink(BaseExtractException):
    ErrorCode = "119"
    MESSAGE = _("当前容器化部署方式, 不支持内网链路")


class ExplorerDirFailed(BaseExtractException):
    ErrorCode = "201"
    MESSAGE = _("访问{request_dir}目录错误，请检查是否已授权")


class ExplorerStrategiesFailed(BaseExtractException):
    ErrorCode = "202"
    MESSAGE = _("用户获取可访问目录失败，请重新选择服务器")


class ExplorerModuleNotAllowed(BaseExtractException):
    ErrorCode = "203"
    MESSAGE = _("未对用户授权模块{request_module}")


class ExplorerFileOrDirDoesNotExist(BaseExtractException):
    ErrorCode = "204"
    MESSAGE = _("文件或目录不存在")


class ExplorerOsTypeMismatch(BaseExtractException):
    ErrorCode = "205"
    MESSAGE = _("所选服务器器中同时包含windows与linux，请重新选择服务器")


class ExplorerMatchTopoFailed(BaseExtractException):
    ErrorCode = "206"
    MESSAGE = _("存在{mismatch_number}个服务器无对应TOPO，请重新选择服务器")


class ExplorerDoesNotIntersection(BaseExtractException):
    ErrorCode = "207"
    MESSAGE = _("所选择的服务器授权目录或文件后缀无交集，请重新选择服务器")


class ExplorerPullTopoError(BaseExtractException):
    ERROR_CODE = "208"
    MESSAGE = _("拉取topo结构失败：{error}, 请求参数：{params} ")


class ExplorerPullTopoNotExist(BaseExtractException):
    ERROR_CODE = "209"
    MESSAGE = _("获取topo为空,请求参数：{params} ")


class DoesNotPermission(BaseExtractException):
    ERROR_CODE = "210"
    MESSAGE = _("暂无权限访问此页面,请联系管理员")


class ExplorerFilterTopoNotExist(BaseExtractException):
    ERROR_CODE = "211"
    MESSAGE = _("过滤topo为空,请检查策略配置")


class ExplorerFilesTimeout(BaseExtractException):
    ErrorCode = "212"
    MESSAGE = _("预览文件超时，请重试")


class ExplorerException(BaseExtractException):
    ErrorCode = "213"
    MESSAGE = _("文件预览异常")


class StrategyDoesNotExist(BaseExtractException):
    ErrorCode = "301"
    MESSAGE = _("ID为{strategy_id}的策略不存在!")


class StrategyIDDoesNotExists(BaseExtractException):
    ERROR_CODE = "302"
    MESSAGE = _("参数异常：策略ID不存在")


class StrategyNameExisted(BaseExtractException):
    ErrorCode = "303"
    MESSAGE = _("该业务下已存在相同的策略名")


class StrategiesNoExistsForGeneral(BaseExtractException):
    ErrorCode = "304"
    MESSAGE = _("您在该业务下尚未拥有下载策略，联系业务运维进行下载策略授权")


class StrategiesNoExistsForOperator(BaseExtractException):
    ErrorCode = "305"
    MESSAGE = _("您在该业务下尚未拥有下载策略，请先通过'管理-日志提取配置'添加策略")


class StrategyOperatorNotAllow(BaseExtractException):
    ErrorCode = "306"
    MESSAGE = _("策略执行人配置不合法")


class StrategyGroupDoesNotExist(BaseExtractException):
    ErrorCode = "307"
    MESSAGE = _("该用户组不存在")


class FileServerExecuteFailed(BaseExtractException):
    ErrorCode = "401"
    MESSAGE = _("搜索文件失败,失败原因: {message}")


class PipelineApiFailed(BaseExtractException):
    ErrorCode = "402"
    MESSAGE = _("{message}")


class PipelineRevoked(BaseExtractException):
    ErrorCode = "501"
    MESSAGE = _(
        "[periodic_clear_timeout_pipeline_task]撤销超时pipeline任务失败：{exceptions} "
        "task_id=>{task_id}, pipeline_id=>{pipeline_id}"
    )


class ExtractLinkDoesNotExistException(BaseExtractException):
    ErrorCode = "601"
    MESSAGE = _("查找的日志提取链路不存在")


class ExtractLinkTypeNotImplementException(BaseExtractException):
    ErrorCode = "602"
    MESSAGE = _("查找的日志提取链路type不支持")


class ExtractLinkCannotModifyException(BaseExtractException):
    ErrorCode = "603"
    MESSAGE = _("不能修改或者删除还在进行中任务的链路")


class ExtractLinkExistedException(BaseExtractException):
    ErrorCode = "604"
    MESSAGE = _("同名日志提取链路已存在")
