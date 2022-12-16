"""
记录线程变量
"""
import logging
import uuid
import sys
import traceback
from contextlib import contextmanager
from threading import local

from django.conf import settings

from bkm_ipchooser.exceptions import IpChooserBaseException

logger = logging.getLogger("bkm_ipchooser")

_local = local()


@contextmanager
def ignored(*exceptions, **kwargs):
    try:
        yield
    except exceptions:
        if kwargs.get("log_exception", True):
            logger.warning(traceback.format_exc())
        pass


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
        raise IpChooserBaseException()


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
    username = ""
    with ignored(IpChooserBaseException):
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
