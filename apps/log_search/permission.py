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
from django.conf import settings
from rest_framework.permissions import BasePermission

from apps.log_search.exceptions import (
    BkJwtClientException,
    BkJwtVerifyException,
    BkJwtVerifyFailException,
)
from apps.utils.local import get_request_username
from apps.utils.log import logger


bk_jwt_backend = True
try:
    from blueapps.account.components.bk_jwt.backends import BkJwtBackend
except ImportError:
    bk_jwt_backend = False


class Permission(BasePermission):
    @classmethod
    def is_superuser(cls, request):
        username = get_request_username()
        if not request.user.is_superuser and username not in settings.INIT_SUPERUSER:
            return False
        return True

    """
    ESQUEYR鉴权
    1. esquery_search 查询需要指定index_set_id 或 数据平台的索引
    2. dsl、mapping只有日志平台可以使用，第三方应用暂时不能使用（或只能用数据平台）
    """

    @classmethod
    def get_auth_info(cls, request, raise_exception=True):
        if not bk_jwt_backend:
            if raise_exception:
                raise BkJwtClientException()
            return False

        try:
            verify_data = BkJwtBackend.verify_bk_jwt_request(request)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("[BK_JWT]校验异常: %s" % e)
            if raise_exception:
                raise BkJwtVerifyException()
            return False

        if not verify_data["result"] or not verify_data["data"]:
            logger.exception("BK_JWT 验证失败： %s" % (verify_data))
            if raise_exception:
                raise BkJwtVerifyFailException()
            return False

        return {
            "bk_app_code": verify_data["data"]["app"]["bk_app_code"],
            "bk_username": verify_data["data"]["user"]["bk_username"],
        }
