# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.log_databus.handlers.check_collector.base import CheckCollectorRecord
from apps.log_databus.handlers.check_collector.handler import CheckCollectorHandler, async_run_check
from apps.log_databus.serializers import CheckCollectorSerializer, GetCollectorCheckResultSerializer
from apps.utils.drf import list_route


class CheckCollectorViewSet(APIViewSet):
    serializer_class = serializers.Serializer

    @list_route(methods=["POST"], url_path="get_check_collector_infos")
    def get_check_collector_infos(self, request, *args, **kwargs):
        data = self.params_valid(GetCollectorCheckResultSerializer)
        result = {"infos": CheckCollectorHandler(**data).get_record_infos()}
        return Response(result)

    @list_route(methods=["POST"], url_path="run_check_collector")
    def run_check_collector(self, request, *args, **kwargs):
        data = self.params_valid(CheckCollectorSerializer)
        key = CheckCollectorRecord.generate_check_result_cache_key(**data)
        async_run_check.delay(**data)
        return Response({"task_id": key})
