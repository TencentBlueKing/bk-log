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
from rest_framework.response import Response
from django.urls import Resolver404
from django.urls import resolve
from django.conf import settings

from apps.generic import APIViewSet
from apps.esb import exceptions
from apps.api import BkLogApi


class LogESBViewSet(APIViewSet):
    dst_call = ""
    dst_kwargs = {}

    def check_permissions(self, request):
        """
        重写rest_framework.views.APIView，目的是为了resolve对应path的view以获得对应的view的get_permissions以及has_permission方法
        """
        dst_url = "".join(self.request.path.split("esb/", 1))
        dst_url = f"/api/{dst_url.split('/api/', 1)[1]}"
        try:
            view, args, kwargs = resolve(dst_url)
        except Resolver404:
            raise exceptions.UrlNotExistError()
        dst_views_objects = view.cls(request=self.request)

        try:
            action = view.actions[self.request.method.lower()]
        except KeyError:
            raise exceptions.MethodNotAllowedError()

        dst_views_objects.action = action
        dst_views_objects.kwargs = kwargs
        dst_views_objects.args = args
        for permission in dst_views_objects.get_permissions():
            if not permission.has_permission(request, dst_views_objects):
                self.permission_denied(request, message=getattr(permission, "message", None))

        module_name = dst_views_objects.__module__
        if (
            module_name not in settings.ALLOWED_MODULES_FUNCS.keys()
            or action not in settings.ALLOWED_MODULES_FUNCS[module_name].keys()
        ):
            raise exceptions.UrlNotImplementError()

        self.dst_kwargs = kwargs
        self.dst_call = settings.ALLOWED_MODULES_FUNCS[module_name][action]

    def call(self, request):
        """
        访问esb接口
        """
        if request.method in ["GET"]:
            params = request.query_params
        else:
            params = request.data
        dst_params = self.request_params_regroup(dict(params), request.method in ["GET"])

        try:
            call_func = getattr(BkLogApi, self.dst_call)
        except AttributeError:
            raise exceptions.UrlNotImplementError

        return Response(call_func(dst_params))

    def request_params_regroup(self, query_params, method_get=True):
        """
        request_param 和 kwargs 重组
        @param {dict} query_params request请求中query_params的data转换的dict
        @param  {Boolean} method_get 是否为get请求
        @return {dict} dst_params 返回重组之后的dict
        """
        dst_params = {}
        if not method_get:
            dst_params.update(query_params)
        else:
            for tmp_key, tmp_val in query_params.items():
                dst_params[tmp_key], *_ = tmp_val

        dst_params.update(self.dst_kwargs)

        return dst_params
