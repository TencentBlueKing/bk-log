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
from django.utils.translation import ugettext_lazy as _lazy
from django.utils.translation import ugettext as _

from apps.exceptions import ErrorCode, BaseException


class BaseIAMError(BaseException):
    MODULE_CODE = ErrorCode.BKLOG_IAM
    MESSAGE = _lazy("权限中心异常")


class ActionNotExistError(BaseIAMError):
    ERROR_CODE = "001"
    MESSAGE = _lazy("动作ID不存在")


class ResourceNotExistError(BaseIAMError):
    ERROR_CODE = "002"
    MESSAGE = _lazy("资源ID不存在")


class GetSystemInfoError(BaseIAMError):
    ERROR_CODE = "003"
    MESSAGE = _lazy("获取系统信息错误")


class NotHaveInstanceIdError(BaseIAMError):
    ERROR_CODE = "004"
    MESSAGE = _lazy("没有传入鉴权实例id")


class PermissionDeniedError(BaseIAMError):
    ERROR_CODE = "403"
    MESSAGE = _lazy("权限校验不通过")

    def __init__(self, action_name, permission, apply_url=settings.BK_IAM_SAAS_HOST):
        message = _("当前用户无 [{action_name}] 权限").format(action_name=action_name)
        data = {
            "permission": permission,
            "apply_url": apply_url,
        }
        super(PermissionDeniedError, self).__init__(message, data=data, code="9900403")
