# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from bkm_ipchooser.serializers import base
from rest_framework import serializers


ListDynamicGroupSer = base.ScopeSelectorBaseSer


class ExecuteDynamicGroupSer(base.ScopeSelectorBaseSer, base.PaginationSer):
    dynamic_group_id = serializers.CharField(label=_("动态分组ID"), required=True)
