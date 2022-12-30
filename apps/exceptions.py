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
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class ErrorCode(object):
    BKLOG_PLAT_CODE = "36"
    BKLOG_WEB_CODE = "00"
    BKLOG_AUTH = "11"
    BKLOG_PERM = "12"
    BKLOG_SCENARIO = "21"
    BKLOG_SOURCE = "22"
    BKLOG_INDEX_SET = "23"
    BKLOG_SEARCH = "24"
    BKLOG_TRACE = "25"
    BKLOG_EXTRACT = "26"
    BKLOG_COMMONS = "30"
    BKLOG_COLLECTOR_CONFIG = "31"
    BKLOG_ESQUERY = "32"
    BKLOG_COLLECTOR_PLUGIN = "33"
    BKLOG_TENCENT_AUTH = "41"
    BKLOG_UPGRADE = "51"
    BKLOG_MEASURE = "61"
    BKLOG_GRAFANA = "71"
    BKLOG_IAM = "99"
    BKLOG_ESB = "100"
    BKLOG_ADMIN = "101"
    BKLOG_CLUSTERING = "102"
    BKLOG_BCS = "103"


class BaseException(Exception):
    MODULE_CODE = "00"
    ERROR_CODE = "500"
    MESSAGE = _("系统异常")

    def __init__(self, *args, data=None, **kwargs):
        """
        @param {String} code 自动设置异常状态码
        """
        super(BaseException, self).__init__(*args)

        self.code = f"{ErrorCode.BKLOG_PLAT_CODE}{self.MODULE_CODE}{self.ERROR_CODE}"
        self.errors = kwargs.get("errors")

        # 优先使用第三方系统的错误编码
        if kwargs.get("code"):
            self.code = kwargs["code"]

        # 位置参数0是异常MESSAGE
        self.message = force_text(self.MESSAGE) if len(args) == 0 else force_text(args[0])

        # 当异常有进一步处理时，需返回data
        self.data = data

    def __str__(self):
        return "[{}] {}".format(self.code, self.message)


class ApiError(BaseException):
    pass


class ValidationError(BaseException):
    MESSAGE = _("参数验证失败")
    ERROR_CODE = "001"


class ApiResultError(ApiError):
    MESSAGE = _("远程服务请求结果异常")
    ERROR_CODE = "002"


class ComponentCallError(BaseException):
    MESSAGE = _("组件调用异常")
    ERROR_CODE = "003"


class BizNotExistError(BaseException):
    MESSAGE = _("业务不存在: {bk_biz_id}")
    ERROR_CODE = "004"


class LanguageDoseNotSupported(BaseException):
    MESSAGE = _("语言不支持")
    ERROR_CODE = "005"


class LockError(BaseException):
    MESSAGE = _("获取锁失败")
    ERROR_CODE = "006"


class PermissionError(BaseException):
    MESSAGE = _("权限不足")
    ERROR_CODE = "403"


class ApiRequestError(ApiError):
    # 属于严重的场景，一般为第三方服务挂了，ESB调用超时
    MESSAGE = _("服务不稳定，请检查组件健康状况")
    ERROR_CODE = "015"


class UnknownLuceneOperatorException(BaseException):
    """非法的lucene语法异常"""

    ERROR_CODE = "500"
    MESSAGE = _("非法的lucene语法")
