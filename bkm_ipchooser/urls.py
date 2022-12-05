# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter

from bkm_ipchooser.views import IpChooserHostViewSet, IpChooserTopoViewSet

routers = DefaultRouter(trailing_slash=True)

routers.register("topo", IpChooserTopoViewSet, basename="ipchooser_topo")
routers.register("host", IpChooserHostViewSet, basename="ipchooser_host")

urlpatterns = routers.urls
