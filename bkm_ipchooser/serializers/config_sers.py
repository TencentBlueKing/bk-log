# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class BatchGetSer(serializers.Serializer):
    module_list = serializers.ListField(label=_("配置列表"), default=[], child=serializers.CharField())


class UpdateSer(serializers.Serializer):
    settings_map = serializers.JSONField(label=_("配置"))


class BatchDeleteSer(serializers.Serializer):
    module_list = serializers.ListField(label=_("配置列表"), default=[], child=serializers.CharField())
