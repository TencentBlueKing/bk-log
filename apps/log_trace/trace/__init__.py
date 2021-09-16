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
import json
from typing import Collection

import MySQLdb
from celery.signals import worker_process_init
from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation import dbapi
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, Status, StatusCode

from apps.feature_toggle.handlers.toggle import FeatureToggleObject


def requests_callback(span: Span, response):
    """处理蓝鲸格式返回码"""
    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except
        return
    if not isinstance(json_result, dict):
        return
    result = json_result.get("result")
    if result is None:
        return
    span.set_attribute("result_code", json_result.get("code", 0))
    span.set_attribute("blueking_esb_request_id", json_result.get("request_id", ""))
    span.set_attribute("result_message", json_result.get("message", ""))
    span.set_attribute("result_errors", str(json_result.get("errors", "")))
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


def django_response_hook(span, request, response):
    if hasattr(response, "data"):
        result = response.data
    else:
        try:
            result = json.loads(response.content)
        except Exception:  # pylint: disable=broad-except
            return
    if not isinstance(result, dict):
        return
    span.set_attribute("result_code", result.get("code", 0))
    span.set_attribute("result_message", result.get("message", ""))
    span.set_attribute("result_errors", result.get("errors", ""))
    result = result.get("result", True)
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


class BluekingInstrumentor(BaseInstrumentor):
    has_instrument = False
    GRPC_HOST = "otlp_grpc_host"
    BK_DATA_ID = "otlp_bk_data_id"

    def _uninstrument(self, **kwargs):
        pass

    def _instrument(self, **kwargs):
        """Instrument the library"""
        if self.has_instrument:
            return
        toggle = FeatureToggleObject.toggle("bk_log_trace")
        feature_config = toggle.feature_config
        otlp_grpc_host = settings.OTLP_GRPC_HOST
        otlp_bk_data_id = settings.OTLP_BK_DATA_ID
        if feature_config:
            otlp_grpc_host = feature_config.get(self.GRPC_HOST, otlp_grpc_host)
            otlp_bk_data_id = feature_config.get(self.BK_DATA_ID, otlp_bk_data_id)
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_grpc_host)
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider = TracerProvider(
            resource=Resource.create(
                {
                    "service.name": settings.APP_CODE,
                    "bk_data_id": otlp_bk_data_id,
                }
            ),
        )
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        DjangoInstrumentor().instrument(response_hook=django_response_hook)
        RedisInstrumentor().instrument()
        ElasticsearchInstrumentor().instrument()
        RequestsInstrumentor().instrument(tracer_provider=tracer_provider, span_callback=requests_callback)
        CeleryInstrumentor().instrument(tracer_provider=tracer_provider)
        LoggingInstrumentor().instrument()
        dbapi.wrap_connect(
            __name__,
            MySQLdb,
            "connect",
            "mysql",
            {
                "database": "db",
                "port": "port",
                "host": "host",
                "user": "user",
            },
            tracer_provider=tracer_provider,
        )
        self.has_instrument = True

    def instrumentation_dependencies(self) -> Collection[str]:
        return []


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    from apps.feature_toggle.handlers.toggle import FeatureToggleObject

    if FeatureToggleObject.switch("bk_log_trace"):
        BluekingInstrumentor().instrument()
