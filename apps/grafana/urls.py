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
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework import routers
from apps.grafana.views import GrafanaProxyView
from bk_dataview.grafana.views import SwitchOrgView, StaticView
from apps.grafana import views

router = routers.DefaultRouter(trailing_slash=True)
router.register(r"grafana", views.GrafanaViewSet, basename="grafana_api")

proxy_router = routers.DefaultRouter(trailing_slash=False)

proxy_router.register(r"trace", views.GrafanaTraceViewSet, basename="trace_api")

urlpatterns = [
    url(r"^api/v1/", include(router.urls)),
    # iframe访问地址 org_name 可以是项目id/业务id 需要保证唯一
    url(r"^bk-dataview/orgs/(?P<org_name>[a-zA-Z0-9\-_]+)/grafana/", SwitchOrgView.as_view()),
    # grafana访问地址, 需要和grafana前缀保持一致
    url(r"^grafana/$", SwitchOrgView.as_view()),
    url(r"^grafana/explore$", SwitchOrgView.as_view()),
    url(r"^grafana/proxy/", include(proxy_router.urls)),
    url(r"^grafana/public/", StaticView.as_view()),
    url(r"^grafana/", GrafanaProxyView.as_view()),
]
