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

from apps.exceptions import BaseException, ErrorCode


class BaseAdminException(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_ADMIN
    MESSAGE = _("管理端模块异常")


class UserIndexSetSearchHistoryDoesNotExistException(BaseAdminException):
    ERROR_CODE = "001"
    MESSAGE = _("检索历史不存在")


class ValidationError(BaseAdminException):
    ERROR_CODE = "002"
    MESSAGE = _("参数验证失败")


class GetCustomReportTokenError(BaseAdminException):
    ERROR_CODE = "101"
    MESSAGE = _("获取自定义上报token异常")


class GetCustomReportSettingError(BaseAdminException):
    ERROR_CODE = "201"
    MESSAGE = _("获取globalConfig中custom_report_setting 异常")


class IndexSetIdError(BaseAdminException):
    ERROR_CODE = "301"
    MESSAGE = _("index_set_id不应该为空")


class EmptyAuditRecordRequestError(BaseAdminException):
    ERROR_CODE = "401"
    MESSAGE = _("biz_id or operate_type and operate_id 两组参数必填其中一组")


class InitDataSourceErrorException(BaseAdminException):
    ERROR_CODE = "501"
    MESSAGE = _("数据源初始化异常, 请联系管理员")
