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
from rest_framework import serializers
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.log_databus.handlers.check_collector.base import CheckCollectorRecord
from apps.log_databus.handlers.check_collector.handler import async_run_check
from apps.log_databus.serializers import CheckCollectorSerializer, GetCollectorCheckResultSerializer
from apps.utils.drf import list_route


class CheckCollectorViewSet(APIViewSet):
    serializer_class = serializers.Serializer

    @list_route(methods=["POST"], url_path="get_check_collector_infos")
    def get_check_collector_infos(self, request, *args, **kwargs):
        data = self.params_valid(GetCollectorCheckResultSerializer)
        record = CheckCollectorRecord(**data)
        result = {"infos": record.get_infos(), "finished": record.finished}
        return Response(result)

    @list_route(methods=["POST"], url_path="run_check_collector")
    def run_check_collector(self, request, *args, **kwargs):
        data = self.params_valid(CheckCollectorSerializer)
        key = CheckCollectorRecord.generate_check_record_id(**data)
        bk_token = request.COOKIES.get("bk_token")
        data.update({"bk_token": bk_token})
        async_run_check.delay(**data)
        return Response({"check_record_id": key})
