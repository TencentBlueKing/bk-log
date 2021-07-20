# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework import routers

from apps.bk_log_admin.views import (
    index_set,
    audit_record_views,
)

router = routers.DefaultRouter(trailing_slash=True)

router.register(
    r"admin/index_set",
    index_set.IndexSetViewSet,
    basename="index_set",
)

router.register(r"admin/audit", audit_record_views.AuditRecordViewSet, basename="audit_record")

urlpatterns = [url(r"^", include(router.urls))]
