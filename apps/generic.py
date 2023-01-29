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
from typing import List

from django.conf import settings
from django.http import JsonResponse, Http404
from django.utils.translation import ugettext as _
from opentelemetry import trace
from opentelemetry.trace import format_trace_id
from rest_framework import exceptions, filters
from rest_framework import serializers
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet as _ModelViewSet
from django_filters import rest_framework as django_filters

from apps.log_measure.events import NOTIFY_EVENT
from apps.utils.function import ignored
from apps.utils.log import logger
from apps.exceptions import BaseException, ValidationError, ErrorCode
from apps.iam import ActionEnum, ResourceEnum, Permission
from apps.iam.exceptions import PermissionDeniedError
from apps.iam.handlers.actions import ActionMeta
from apps.log_esquery.exceptions import EsTimeoutException
from apps.log_esquery.qos import esquery_qos
from apps.utils.drf import DataPageNumberPagination, GeneralSerializer, custom_params_valid
from iam import Resource


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # To not perform the csrf check previously happening
        return


class FlowMixin(object):
    """
    封装 APIViewSet 修改 ModelViewSet 默认返回内容，固定格式为
        {result: True, data: {}, code: 00, message: ''}
    """

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def finalize_response(self, request, response, *args, **kwargs):

        # 目前仅对 Restful Response 进行处理
        if isinstance(response, Response):
            response.data = {"result": True, "data": response.data, "code": 0, "message": ""}
            response.status_code = status.HTTP_200_OK

        # 返回响应头禁用浏览器的类型猜测行为
        response.headers["x-content-type-options"] = ("X-Content-Type-Options", "nosniff")
        return super(FlowMixin, self).finalize_response(request, response, *args, **kwargs)

    def valid(self, form_class, filter_blank=False, filter_none=False):
        """
        校验参数是否满足组 form_class 的校验
        @param {django.form.Form} form_class 验证表单
        @param {Boolean} filter_blank 是否过滤空字符的参数
        @param {Boolean} filter_none 是否过滤 None 的参数

        @raise FormError 表单验证不通过时抛出
        """
        if self.request.method == "GET":
            _form = form_class(self.request.query_params)
        else:
            _form = form_class(self.request.data)

        if not _form.is_valid():
            raise ValidationError(_form.format_errmsg())
        _data = _form.cleaned_data
        if filter_blank:
            _data = {_k: _v for _k, _v in list(_data.items()) if _v != ""}
        if filter_none:
            _data = {_k: _v for _k, _v in list(_data.items()) if _v is not None}

        return _data

    def valid_serializer(self, serializer):
        """
        校验参数是否满足组 serializer 的校验
        @param {serializer} serializer 验证表单
        @return {serializer} _serializer 序列器（已进行校验清洗）
        """
        _request = self.request
        if _request.method == "GET":
            _serializer = serializer(data=_request.query_params)
        else:
            _serializer = serializer(data=_request.data)
        _serializer.is_valid(raise_exception=True)
        return _serializer

    def is_pagination(self, request):
        page = request.query_params.get("page", "")
        page_size = request.query_params.get("page_size", "")
        return page != "" and page_size != ""

    def do_paging(self, request, data):
        # 处理分页
        if self.is_pagination(request):
            page = int(request.query_params["page"])
            page_size = int(request.query_params["page_size"])

            count = len(data)
            total_page = (count + page_size - 1) / page_size
            data = data[page_size * (page - 1) : page_size * page]

            return {"total_page": total_page, "count": count, "results": data}
        else:
            # 无分页请求时返回全部
            return {"total_page": 1, "count": len(data), "results": data}


class ValidationMixin(object):
    def params_valid(self, serializer, params=None):
        """
        校验参数是否满足 serializer 规定的格式
        """
        # 获得Django的request对象
        _request = self.request

        # 校验request中的参数
        if not params:
            if _request.method in ["GET"]:
                params = _request.query_params
            else:
                params = _request.data

        return custom_params_valid(serializer=serializer, params=params)


class IAMPermissionMixin:

    ActionEnum = ActionEnum
    ResourceEnum = ResourceEnum

    @property
    def iam_permission(self) -> Permission:
        if not hasattr(self, "_iam_permission"):
            setattr(self, "_iam_permission", Permission())
        return getattr(self, "_iam_permission")

    def assert_allowed(self, action: ActionMeta, resources: List[Resource] = None):
        """
        权限校验
        """
        self.iam_permission.is_allowed(action, resources, raise_exception=True)

    def assert_business_action_allowed(self, action: ActionMeta):
        bk_biz_id = self.request.data.get("bk_biz_id", 0) or self.request.query_params.get("bk_biz_id", 0)

        self.assert_allowed(action, [self.ResourceEnum.BUSINESS.create_instance(bk_biz_id)])

    def assert_view_business_allowed(self):
        self.assert_business_action_allowed(self.ActionEnum.VIEW_BUSINESS)


class APIViewSet(FlowMixin, ValidationMixin, IAMPermissionMixin, GenericViewSet):
    pass


class Meta(object):
    pass


class ModelViewSet(FlowMixin, ValidationMixin, IAMPermissionMixin, _ModelViewSet):
    model = None
    filter_fields_exclude = []
    pagination_class = DataPageNumberPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, django_filters.DjangoFilterBackend)
    serializer_meta = type("Meta", (Meta,), {"model": None, "fields": "__all__"})

    def __init__(self, *args, **kwargs):
        super(ModelViewSet, self).__init__(**kwargs)
        self.filter_fields = [f.name for f in self.model._meta.get_fields() if f.name not in self.filter_fields_exclude]
        self.view_set_name = self.get_view_object_name(*args, **kwargs)

    def get_view_name(self, *args, **kwargs):
        return self.model._meta.db_table

    def get_view_description(self, *args, **kwargs):
        return self.model._meta.verbose_name

    def get_view_module(self, *args, **kwargs):
        return getattr(self.model._meta, "module", None)

    def get_view_object_name(self, *args, **kwargs):
        return getattr(self.model._meta, "object_name", None)

    def get_queryset(self):
        return self.model.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        self.serializer_meta.model = self.model
        return type("GeneralSerializer", (GeneralSerializer,), {"Meta": self.serializer_meta})

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class DataSerializerMixin(object):
    """
    该 Mixin 类主要用于重载部分 Serializer 方法
    """

    def is_valid(self, raise_exception=False):
        if not raise_exception:
            return super(DataSerializerMixin, self).is_valid()

        try:
            return super(DataSerializerMixin, self).is_valid(raise_exception=True)
        except exceptions.ValidationError as exc:
            # 对于DRF默认返回的校验异常，需要额外补充 message 字段
            # 由于 ValidationError 需要返回给前端，需要把错误信息处理一下
            # @todo 多层serializer的报错需递归生成
            exc.message = self.format_errmsg()
            raise exc

    def format_errmsg(self):
        """
        格式化 DRF serializer 序列化器返回错误信息，简化为字符串提示，错误信息形如：
            {
                "result_tables": {
                    "non_field_errors": [
                        "结果表不可为空"
                    ]
                },
                "app_code": [
                    "该字段是必填项。"
                ]
            }
        @return {String} 简化后的提示信息
        @returnExample
            结果表，结果表不可为空
        """
        errors = self.errors
        declared_fields = self.fields

        _key, _val = list(errors.items())[0]
        _whole_key = _key

        while type(_val) is dict:
            _key, _val = list(_val.items())[0]
            _whole_key += "." + _key

        _key_display = ""
        for _key in _whole_key.split("."):
            # 特殊KEY，表示全局字段
            if _key == "non_field_errors":
                break

            _field = declared_fields[_key]
            if hasattr(_field, "child"):
                declared_fields = _field.child

            _key_display = _field.label if _field.label else _key

        format_msg = "{}，{}".format(_key_display, _val[0])
        return format_msg


class DataSerializer(DataSerializerMixin, serializers.Serializer):
    pass


class DataModelSerializer(DataSerializerMixin, serializers.ModelSerializer):
    pass


def custom_exception_handler(exc, context):
    """
    自定义错误处理方式
    """
    # 专门处理 404 异常，直接返回前端，前端处理
    if isinstance(exc, Http404):
        return JsonResponse(_error("404", str(exc)))

    # 处理EsQuery超时报错
    if isinstance(exc, EsTimeoutException):
        esquery_qos(context["request"])

    # 专门处理无权限异常，直接返回前端，前端处理
    if isinstance(exc, PermissionDeniedError):
        result = {
            "result": False,
            "code": exc.code,
            "message": exc.message,
            "data": {"apply_url": exc.data["apply_url"]},
            "permission": exc.data["permission"],
        }
        response = JsonResponse(result, status=status.HTTP_200_OK)
        return response

    # 特殊处理 rest_framework ValidationError
    if isinstance(exc, exceptions.ValidationError):
        message = str(exc)
        return JsonResponse(_error("{}".format(exc.status_code), message))

    # 处理 rest_framework 的异常
    if isinstance(exc, exceptions.APIException):
        return JsonResponse(_error("{}".format(exc.status_code), exc.detail))

    # 处理 Data APP 自定义异常
    if isinstance(exc, BaseException):
        _msg = _("【APP 自定义异常】{message}, code={code}, args={args}").format(
            message=exc.message, code=exc.code, args=exc.args, data=exc.data, errors=exc.errors
        )
        logger.exception(_msg)
        _notify(context["request"], _msg)
        return JsonResponse(_error(exc.code, exc.message, exc.data, exc.errors))

    # 处理校验异常
    if isinstance(exc, ValueError):
        logger.exception(str(exc))
        return JsonResponse(_error("500001", str(exc)))

    # 判断是否在debug模式中,
    # 在这里判断是防止阻止了用户原本主动抛出的异常
    if settings.DEBUG:
        return None

    # 非预期异常
    logger.exception(getattr(exc, "message", exc))
    _notify(context["request"], getattr(exc, "message", exc))
    return JsonResponse(_error("500", _("系统错误，请联系管理员"), errors=str(exc)))


def _notify(request, msg):
    # 旁路告警
    with ignored(Exception):
        username = ""
        with ignored(Exception):
            username = request.user.username
        NOTIFY_EVENT(
            content=str(msg),
            dimensions={
                "trace_id": format_trace_id(trace.get_current_span().get_span_context().trace_id),
                "username": username,
            },
        )


def _error(code=None, message="", data=None, errors=None):
    if len(str(code)) == 3:
        code = f"{ErrorCode.BKLOG_PLAT_CODE}{ErrorCode.BKLOG_WEB_CODE}{code}"
    message = f"{message}（{code}）"
    if errors:
        message += f"（detail => {errors}）"
    return {"result": False, "code": code, "data": data, "message": message, "errors": errors}
