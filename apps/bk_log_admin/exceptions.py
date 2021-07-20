# -*- coding: utf-8 -*-
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
