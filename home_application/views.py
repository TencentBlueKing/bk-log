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
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from blueapps.account.decorators import login_exempt

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from apps.utils.db import get_toggle_data
from home_application.constants import API_FORMAT_CONTENT_TYPE
from home_application.handlers.healthz import HealthzHandler


def home(request):
    """
    首页
    """
    return render(request, settings.VUE_INDEX, get_toggle_data())


def bkdata_auth(request):
    """
    鉴权页面
    """
    return render(request, "auth.html")


@login_exempt
def contact(request):
    """
    联系我们
    """
    return JsonResponse({"data": "login_exempt"})


@login_exempt
def readiness(request):
    """就绪探测接口"""
    return JsonResponse({"server_up": 1})


@login_exempt
def healthz(request):
    """
    format_type: 格式化类型, 支持 json, 默认为k8s
    include: 包含的namespace, include不为空时, exclude失效
    exclude: 去除的namespace
    """
    format_type = request.GET.get("format_type")
    include = request.GET.get("include", [])
    if include:
        include = include.split(",")
    exclude = request.GET.get("exclude", [])
    if exclude:
        exclude = exclude.split(",")
    response = HttpResponse(
        content=HealthzHandler().get_data(
            format_type=format_type, include_namespaces=include, exclude_namespaces=exclude
        )
    )

    if format_type == "json":
        response["Content-Type"] = "application/json"
    else:
        response["Content-Type"] = API_FORMAT_CONTENT_TYPE

    return response


@login_exempt
def metrics(request):
    from django_prometheus import exports
    from settings import PROMETHEUS_METRICS_TOKEN

    token = request.GET.get("token")
    if PROMETHEUS_METRICS_TOKEN:
        if token is None:
            return HttpResponse(_("缺少参数token"))
        if token != PROMETHEUS_METRICS_TOKEN:
            return HttpResponse(_("token验证失败"))
    return exports.ExportToDjangoView(request)
