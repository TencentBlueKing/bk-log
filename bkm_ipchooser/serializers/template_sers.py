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
    meta = base.ScopeSer(help_text=_("Meta元数据"), required=False)


class ListTemplateRequestSer(serializers.Serializer):
    """模板列表请求"""

    id = serializers.IntegerField(help_text=_("模板ID"), required=True)
    meta = base.ScopeSer(help_text=_("Meta元数据"), required=False)


class ListTemplateSer(BaseTemplateSer):
    """模板列表"""

    service_template_list = serializers.ListField(child=ListTemplateRequestSer(), required=False, default=[])
    set_template_list = serializers.ListField(child=ListTemplateRequestSer(), required=False, default=[])
    template_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])

    def validate(self, attrs):
        super().validate(attrs)
        if attrs["template_type"] == constants.TemplateType.SERVICE_TEMPLATE.value:
            attrs["template_id_list"] = [a["id"] for a in attrs["service_template_list"]]
        if attrs["template_type"] == constants.TemplateType.SET_TEMPLATE.value:
            attrs["template_id_list"] = [a["id"] for a in attrs["set_template_list"]]
        return attrs


class ListTemplateResponseSer(serializers.ListSerializer):
    """模板列表返回"""

    child = TemplateSer()


class ListNodeSer(BaseTemplateSer, base.PaginationSer):
    """获取模板节点列表"""

    meta = base.ScopeSer(help_text=_("Meta元数据"), required=False)
    id = serializers.IntegerField(help_text=_("模板ID"), required=True)


class ListHostSer(BaseTemplateSer, base.PaginationSer):
    """获取模板主机列表"""

    meta = base.ScopeSer(help_text=_("Meta元数据"), required=False)
    id = serializers.IntegerField(help_text=_("模板ID"), required=True)


class AgentStatisticsSer(BaseTemplateSer):
    """模板Agent状态统计"""

    service_template_list = serializers.ListField(child=ListTemplateRequestSer(), required=False, default=[])
    set_template_list = serializers.ListField(child=ListTemplateRequestSer(), required=False, default=[])
    template_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])

    def validate(self, attrs):
        super().validate(attrs)
        if attrs["template_type"] == constants.TemplateType.SERVICE_TEMPLATE.value:
            attrs["template_id_list"] = [a["id"] for a in attrs["service_template_list"]]
        if attrs["template_type"] == constants.TemplateType.SET_TEMPLATE.value:
            attrs["template_id_list"] = [a["id"] for a in attrs["set_template_list"]]
        if not attrs["template_id_list"]:
            raise serializers.ValidationError(_("模板列表不能为空"))
        return attrs
