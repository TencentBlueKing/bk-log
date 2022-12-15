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
from django.conf.urls import include, url
from rest_framework import routers

from apps.log_databus.views import (
    archive_views,
    clean_views,
    collector_plugin_views,
    collector_views,
    itsm_views,
    restore_views,
    check_collector_views,
)
from apps.log_databus.views import link_views
from apps.log_databus.views import storage_views

router = routers.DefaultRouter(trailing_slash=True)

router.register(r"archive", archive_views.ArchiveViewSet, basename="archive")
router.register(r"restore", restore_views.RestoreViewSet, basename="restore")
router.register(r"storage", storage_views.StorageViewSet, basename="databus_storage")
router.register(r"collectors", collector_views.CollectorViewSet, basename="collectors")
router.register(r"collector_plugins", collector_plugin_views.CollectorPluginViewSet, basename="collector_plugins")
router.register(r"data_link", link_views.DataLinkViewSet, basename="data_link")
router.register(r"collect_itsm", itsm_views.ItsmViewSet, basename="collect_itsm")
router.register(r"collect_itsm_cb", itsm_views.ItsmCallbackViewSet, basename="collect_itsm_cb")
router.register(r"clean_template", clean_views.CleanTemplateViewSet, basename="clean_template")
router.register(r"clean", clean_views.CleanViewSet, basename="clean")
router.register(r"check_collector", check_collector_views.CheckCollectorViewSet, basename="check_collector")


urlpatterns = [
    url(r"^", include(router.urls)),
]
