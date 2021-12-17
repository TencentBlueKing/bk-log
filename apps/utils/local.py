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

"""
记录线程变量
"""
import uuid  # noqa
import sys  # noqa
from threading import local  # noqa

from django.conf import settings  # noqa

from apps.exceptions import BaseException  # noqa


_local = local()


def activate_request(request, request_id=None):
    """
    激活request线程变量
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    request.request_id = request_id
    _local.request = request
    return request


def get_request():
    """
    获取线程请求request
    """
    try:
        return _local.request
    except AttributeError:
        raise BaseException(u"request thread error!")


def get_request_id():
    """
    获取request_id
    """
    try:
        return get_request().request_id
    except BaseException:
        return str(uuid.uuid4())


def get_request_username():
    """
    获取请求的用户名
    """
    from apps.utils.function import ignored

    username = ""
    with ignored(Exception):
        username = get_request().user.username
    if not username and "celery" in sys.argv:
        username = "admin"
    return username


def set_request_username(username):
    set_local_param("request.username", username)


def get_request_app_code():
    """
    获取线程请求中的 APP_CODE
    """
    try:
        return get_request().META.get("HTTP_BK_APP_CODE", settings.APP_CODE)
    except Exception:  # pylint: disable=broad-except
        return settings.APP_CODE


def set_local_param(key, value):
    """
    设置自定义线程变量
    """
    setattr(_local, key, value)


def del_local_param(key):
    """
    删除自定义线程变量
    """
    if hasattr(_local, key):
        delattr(_local, key)


def get_local_param(key, default=None):
    """
    获取线程变量
    """
    return getattr(_local, key, default)


def get_request_language_code():
    """
    获取线程请求中的language_code
    """
    try:
        return get_request().LANGUAGE_CODE
    except Exception:  # pylint: disable=broad-except
        return settings.LANGUAGE_CODE
