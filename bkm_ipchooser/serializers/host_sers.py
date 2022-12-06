# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bkm_ipchooser import mock_data
from bkm_ipchooser.serializers import base


class HostCheckRequestSer(base.ScopeSelectorBaseSer):
    ip_list = serializers.ListField(
        help_text=_("IPv4 列表"),
        child=serializers.CharField(help_text=_("IPv4，支持的输入格式：`cloud_id:ip` / `ip`"), min_length=1),
        default=[],
        required=False,
    )
    ipv6_list = serializers.ListField(
        help_text=_("IPv6 列表"),
        child=serializers.CharField(help_text=_("IPv6，支持的输入格式：`cloud_id:ipv6` / `ipv6`"), min_length=1),
        default=[],
        required=False,
    )
    key_list = serializers.ListField(
        help_text=_("关键字列表"),
        child=serializers.CharField(help_text=_("关键字，解析出的`主机名`、`host_id` 等关键字信息"), min_length=1),
        default=[],
        required=False,
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.API_HOST_CHECK_REQUEST}


class HostCheckResponseSer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_HOST_CHECK_RESPONSE}


class HostDetailsRequestSer(base.ScopeSelectorBaseSer):
    host_list = serializers.ListField(child=base.HostInfoWithMetaSer(), default=[])

    class Meta:
        swagger_schema_fields = {"example": mock_data.API_HOST_DETAILS_REQUEST}


class HostDetailsResponseSer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_HOST_DETAILS_RESPONSE}
