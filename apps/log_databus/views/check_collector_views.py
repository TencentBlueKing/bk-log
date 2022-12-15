# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.generic import APIViewSet
from apps.utils.drf import detail_route


class CheckCollectorViewSet(APIViewSet):
    lookup_field = "collector_id"
    serializer_class = serializers.Serializer

    @detail_route(methods=["GET"], url_path="run_check_collector")
    def get_check_collector_status(self, request, collector_id, *args, **kwargs):
        pass

    @detail_route(methods=["GET"], url_path="run_check_collector")
    def run_check_collector(self, request, collector_id, *args, **kwargs):
        pass

    @detail_route(methods=["GET"], url_path="get_check_collector")
    def get_check_collector(self, request, collector_id, *args, **kwargs):
        pass
