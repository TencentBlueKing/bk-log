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
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.contrib import admin
from django.views import static
from django.conf import settings
from version_log import config

urlpatterns = [
    url(r"^bklog_manage/", admin.site.urls),
    url(r"^account/", include("blueapps.account.urls")),
    # 通用
    url(r"^api/v1/", include("apps.log_commons.urls")),
    # 接口
    url(r"^api/v1/iam/", include("apps.iam.urls")),
    url(r"^api/v1/databus/", include("apps.log_databus.urls")),
    # trace
    url(r"^api/v1/trace/", include("apps.log_trace.urls")),
    url(r"^api/v1/", include("apps.log_search.urls")),
    url(r"^api/v1/", include("apps.log_esquery.urls")),
    url(r"^api/v1/", include("apps.esb.urls")),
    url(r"^api/v1/", include("apps.bk_log_admin.urls")),
    url(r"^api/v1/", include("apps.log_bcs.urls")),
    url(r"^api/v1/", include("apps.log_clustering.urls")),
    url(r"^", include("apps.grafana.urls")),
    # 前端页面
    url(r"^", include("home_application.urls")),
    # celery flower
    url(r"^flower/", include("flower_proxy.urls")),
    url(r"^{}".format(config.ENTRANCE_URL), include("version_log.urls")),
    url(r"^api/v1/log_extract/", include("apps.log_extract.urls")),
    url(r"^api/v1/", include("apps.log_measure.urls")),
    url(r"^api/v1/ipchooser/", include("bkm_ipchooser.urls")),
]


if settings.IS_K8S_DEPLOY_MODE:
    urlpatterns.extend(
        [url(r"^static/(?P<path>.*)$", static.serve, {"document_root": settings.STATIC_ROOT}, name="static")]
    )
