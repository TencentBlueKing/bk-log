# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter

from bkm_ipchooser.views import (
    IpChooserHostViewSet,
    IpChooserTopoViewSet,
    IpChooserTemplateViewSet,
    IpChooserConfigViewSet,
)

routers = DefaultRouter(trailing_slash=True)

routers.register("topo", IpChooserTopoViewSet, basename="ipchooser_topo")
routers.register("host", IpChooserHostViewSet, basename="ipchooser_host")
routers.register("template", IpChooserTemplateViewSet, basename="ipchooser_template")
routers.register("config", IpChooserConfigViewSet, basename="ipchooser_config")

urlpatterns = routers.urls