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
# since each thread has its own greenlet we can just use those as identifiers
# for the context.  If greenlets are not available we fall back to the
# current thread ident depending on where it is.
import json
import os
import traceback

from blueapps.core.exceptions.base import BlueException

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from _thread import get_ident
    except ImportError:
        from _thread import get_ident

from django.utils.deprecation import MiddlewareMixin
from django.dispatch import Signal
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from apps.exceptions import BaseException
from apps.utils.log import logger


class AccessorSignal(Signal):
    """
    与 RequestProvider 中间件搭配使用
    """

    allowed_receiver = "apps.middlewares.RequestProvider"

    def __init__(self, providing_args=None):
        Signal.__init__(self, providing_args)
        self.bind_times = 0

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        # 一般情况下中间件只会被初始化一次，在不明情况下，中间件会在用户请求后，再初始化一次
        # 目前先姑且认定这种情况的初始化属于异常情况不进行信号绑定
        if self.bind_times >= 1:
            return

        receiver_name = ".".join([receiver.__class__.__module__, receiver.__class__.__name__])
        if receiver_name != self.allowed_receiver:
            raise BaseException("%s is not allowed to connect" % receiver_name)
        Signal.connect(self, receiver, sender, weak, dispatch_uid)
        self.bind_times += 1


request_accessor = AccessorSignal()


class RequestProvider(MiddlewareMixin):
    """
    与 AccessorSignal 搭建使用，request 事件接收者
    """

    def __init__(self, get_response=None):
        super(RequestProvider, self).__init__(get_response=get_response)
        self._request_pool = {}
        request_accessor.connect(self)

    def process_request(self, request, **kwargs):
        self._request_pool[get_ident()] = request
        return None

    def process_response(self, request, response):
        assert request is self._request_pool.pop(get_ident())
        return response

    def __call__(self, *args, **kwargs):
        from_signal = kwargs.get("from_signal", False)
        if from_signal:
            return self.get_request(**kwargs)
        else:
            return super(RequestProvider, self).__call__(args[0])

    def get_request(self, **kwargs):
        sender = kwargs.get("sender")
        if sender is None:
            sender = get_ident()
        if sender not in self._request_pool:
            raise BaseException("get_request can't be called in a new thread.")
        return self._request_pool[sender]


def get_x_request_id():
    x_request_id = ""
    http_request = get_request()
    if hasattr(http_request, "META"):
        meta = http_request.META
        x_request_id = meta.get("HTTP_X_REQUEST_ID", "") if isinstance(meta, dict) else ""
    return x_request_id


def get_request():
    return request_accessor.send(get_ident(), from_signal=True)[0][1]


class CommonMid(MiddlewareMixin):
    """
    公共中间件，统一处理逻辑
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # SAAS 部署包必须部署正式环境
        if settings.RUN_MODE == "TEST":
            test_switch = os.environ.get("BKAPP_ALLOW_TEST", False)
            if not test_switch:
                return HttpResponse(_("S-mart应用仅支持正式环境部署！"))

        return None

    def process_exception(self, request, exception):
        """
        app后台错误统一处理
        """

        # 处理 Data APP 自定义异常
        if isinstance(exception, BaseException):
            _msg = _("【APP 自定义异常】{message}, code={code}, args={args}").format(
                message=exception.message, code=exception.code, args=exception.args, data=exception.data
            )
            logger.warning(_msg)
            return JsonResponse(
                {"code": exception.code, "message": exception.message, "data": exception.data, "result": False}
            )

        # 用户自我感知的异常抛出
        if isinstance(exception, BlueException):

            logger.warning(
                ("""捕获主动抛出异常, 具体异常堆栈->[%s] status_code->[%s] & """ """client_message->[%s] & args->[%s] """)
                % (traceback.format_exc(), exception.error_code, exception.message, exception.args)
            )

            response = JsonResponse(
                {"code": exception.error_code, "message": exception.message, "data": "", "result": False}
            )

            response.status_code = exception.error_code / 100
            return response

        # 用户未主动捕获的异常
        logger.error(
            ("""捕获未处理异常,异常具体堆栈->[%s], 请求URL->[%s], """ """请求方法->[%s] 请求参数->[%s]""")
            % (traceback.format_exc(), request.path, request.method, json.dumps(getattr(request, request.method, None)))
        )

        # 判断是否在debug模式中,
        # 在这里判断是防止阻止了用户原本主动抛出的异常
        if settings.DEBUG:
            return None

        response = JsonResponse({"code": 50000, "message": _("系统异常,请联系管理员处理"), "data": "", "result": False})
        response.status_code = 500

        return response


class HttpResponseIndexRedirect(HttpResponseRedirect):
    def __init__(self, redirect_to, *args, **kwargs):
        super(HttpResponseIndexRedirect, self).__init__(redirect_to, *args, **kwargs)
        self["Location"] = os.path.join(settings.DEFAULT_HTTPS_HOST, redirect_to.lstrip("/"))


class HttpsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.BKAPP_IS_BKLOG_API:
            return None
        if not request.is_secure() and settings.DEFAULT_HTTPS_HOST:
            return HttpResponseIndexRedirect(request.path)
