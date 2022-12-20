# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from bkm_ipchooser.serializers import base
from rest_framework import serializers


class ExecuteDynamicGroupSer(base.ScopeSelectorBaseSer, base.PaginationSer):
    id = serializers.CharField(label=_("动态分组ID"), required=True)


class DynamicGroupSer(serializers.Serializer):
    meta = base.ScopeSer()
    id = serializers.CharField(label=_("动态分组ID"), required=True)


class ListDynamicGroupSer(base.ScopeSelectorBaseSer):
    dynamic_group_list = serializers.ListField(child=DynamicGroupSer(), required=False, default=[])


class AgentStatistiscSer(base.ScopeSelectorBaseSer):
    dynamic_group_list = serializers.ListField(child=DynamicGroupSer(), required=True)
