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
import json
import threading
from typing import Collection

import MySQLdb
from celery.signals import worker_process_init
from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation import dbapi
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, Status, StatusCode
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF, DEFAULT_OFF, ALWAYS_ON

from apps.feature_toggle.handlers.toggle import FeatureToggleObject


def requests_callback(span: Span, response):
    """处理蓝鲸格式返回码"""
    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except
        return
    if not isinstance(json_result, dict):
        return

    # NOTE: esb got a result, but apigateway  /iam backend / search-engine got not result
    code = json_result.get("code", 0)
    span.set_attribute("result_code", code)
    span.set_attribute("result_message", json_result.get("message", ""))
    span.set_attribute("result_errors", str(json_result.get("errors", "")))
    try:
        request_id = (
            # new esb and apigateway
            response.headers.get("x-bkapi-request-id")
            # iam backend
            or response.headers.get("x-request-id")
            # old esb
            or json_result.get("request_id", "")
        )
        if request_id:
            span.set_attribute("bk.request_id", request_id)
    except Exception:  # pylint: disable=broad-except
        pass

    if code in [0, "0", "00"]:
        span.set_status(Status(StatusCode.OK))
    else:
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


class LazyBatchSpanProcessor(BatchSpanProcessor):
    def __init__(self, *args, **kwargs):
        super(LazyBatchSpanProcessor, self).__init__(*args, **kwargs)
        # 停止默认线程
        self.done = True
        with self.condition:
            self.condition.notify_all()
        self.worker_thread.join()
        self.done = False
        self.worker_thread = None

    def on_end(self, span: ReadableSpan) -> None:
        if self.worker_thread is None:
            self.worker_thread = threading.Thread(target=self.worker, daemon=True)
            self.worker_thread.start()
        super(LazyBatchSpanProcessor, self).on_end(span)

    def shutdown(self) -> None:
        # signal the worker thread to finish and then wait for it
        self.done = True
        with self.condition:
            self.condition.notify_all()
        if self.worker_thread:
            self.worker_thread.join()
        self.span_exporter.shutdown()


class BluekingInstrumentor(BaseInstrumentor):
    has_instrument = False
    GRPC_HOST = "otlp_grpc_host"
    BK_DATA_ID = "otlp_bk_data_id"
    BK_DATA_TOKEN = "otlp_bk_data_token"
    SAMPLE_ALL = "sample_all"

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
        otlp_bk_data_token = ""
        sample_all = False
        if feature_config:
            otlp_grpc_host = feature_config.get(self.GRPC_HOST, otlp_grpc_host)
            otlp_bk_data_id = feature_config.get(self.BK_DATA_ID, otlp_bk_data_id)
            otlp_bk_data_token = feature_config.get(self.BK_DATA_TOKEN, otlp_bk_data_token)
            sample_all = feature_config.get(self.SAMPLE_ALL, sample_all)
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_grpc_host)
        span_processor = LazyBatchSpanProcessor(otlp_exporter)


        # periord task not sampler
        sampler = DEFAULT_OFF
        if settings.IS_CELERY_BEAT:
            sampler = ALWAYS_OFF

        if sample_all:
            sampler = ALWAYS_ON

        tracer_provider = TracerProvider(
            resource=Resource.create(
                {
                    "service.name": settings.SERVICE_NAME,
                    "service.version": settings.VERSION,
                    "bk_data_id": otlp_bk_data_id,
                    "bk.data.token": otlp_bk_data_token,
                }
            ),
            sampler=sampler,
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
