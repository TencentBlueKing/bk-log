# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

from bkm_space.utils import inject_space_field


class ParamInjectMiddleware(MiddlewareMixin):
    """
    空间参数注入器
    """

    def __init__(self, *args, **kwargs):
        super(ParamInjectMiddleware, self).__init__(*args, **kwargs)
        self.inject_request_enabled = getattr(settings, "BKM_SPACE_INJECT_REQUEST_ENABLED", True)
        self.inject_response_enabled = getattr(settings, "BKM_SPACE_INJECT_RESPONSE_ENABLED", False)

    def process_request(self, request, **kwargs):
        if not self.inject_request_enabled:
            return

        request.GET = inject_space_field(request.GET.copy())
        request.POST = inject_space_field(request.POST.copy())

        if request.content_type == "application/json":
            try:
                body = json.loads(request.body)
                request._body = json.dumps(inject_space_field(body)).encode("utf-8")
            except TypeError:
                pass

    def process_response(self, request, response):
        if not self.inject_response_enabled:
            return response

        if isinstance(response, Response):
            try:
                content = json.loads(request.content)
                request.content = json.dumps(inject_space_field(content)).encode("utf-8")
            except TypeError:
                pass
        return response
