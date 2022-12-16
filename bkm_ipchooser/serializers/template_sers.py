# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bkm_ipchooser import constants
from bkm_ipchooser.serializers import base


class BaseTemplateSer(base.ScopeSelectorBaseSer):
    """模板基类"""

    template_type = serializers.ChoiceField(
        help_text=_("模板类型"), required=True, choices=constants.TemplateType.list_choices()
    )


class TemplateSer(serializers.Serializer):
    """模板基类"""

    id = serializers.IntegerField(help_text=_("模板ID"))
    name = serializers.CharField(help_text=_("模板名称"))
    template_type = serializers.ChoiceField(
        help_text=_("模板类型"), required=True, choices=constants.TemplateType.list_choices()
    )
    meta = base.ScopeSer(help_text=_("模板元数据"))


ListTemplateSer = BaseTemplateSer


class ListTemplateResponseSer(serializers.ListSerializer):
    """模板列表返回"""

    child = TemplateSer()


class ListNodeSer(BaseTemplateSer):
    """
    获取模板节点列表
    """

    template_ids = serializers.ListField(
        help_text=_("模板ID列表"), required=False, default=[], child=serializers.IntegerField()
    )


class ListAgentStatusSer(BaseTemplateSer):
    """
    获取模板Agent状态
    """

    template_ids = serializers.ListField(
        help_text=_("模板ID列表"), required=False, default=[], child=serializers.IntegerField()
    )
