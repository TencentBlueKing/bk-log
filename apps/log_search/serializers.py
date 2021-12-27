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
import re
import time
import datetime
import arrow

from dateutil.parser import parse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.exceptions import ValidationError
from apps.log_search.constants import InstanceTypeEnum, TemplateType
from apps.log_search.handlers.meta import MetaHandler
from apps.log_search.models import ProjectInfo, Scenario, UserIndexSetConfig
from apps.utils.local import get_local_param

HISTORY_MAX_DAYS = 7


class PageSerializer(serializers.Serializer):
    """
    分页序列化器
    """

    page = serializers.IntegerField(label=_("页码"), default=1)
    pagesize = serializers.IntegerField(label=_("分页大小"), default=10)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInfo
        fields = ["project_id", "project_name", "bk_biz_id", "bk_app_code", "time_zone", "description"]


class ResultTableListSerializer(serializers.Serializer):
    scenario_id = serializers.CharField(label=_("接入场景"))
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)
    storage_cluster_id = serializers.IntegerField(label=_("集群ID"), required=False)
    result_table_id = serializers.CharField(label=_("索引"), required=False, allow_blank=True)

    def validate(self, attrs):
        super().validate(attrs)

        scenario_id = attrs["scenario_id"]
        if scenario_id in [Scenario.BKDATA, Scenario.LOG] and not attrs.get("bk_biz_id"):
            raise ValidationError(_("业务ID不能为空"))

        if scenario_id == Scenario.ES and not attrs.get("storage_cluster_id"):
            raise ValidationError(_("数据源ID不能为空"))

        return attrs


class ResultTableTraceMatchSerializer(serializers.Serializer):
    indices = serializers.ListField(label=_("索引列表"))
    scenario_id = serializers.CharField(label=_("接入场景"))
    storage_cluster_id = serializers.IntegerField(label=_("数据源ID"), required=False)

    def validate(self, attrs):
        super().validate(attrs)

        scenario_id = attrs["scenario_id"]
        indices = attrs.get("indices")
        if scenario_id == Scenario.ES and not attrs.get("storage_cluster_id"):
            raise ValidationError(_("数据源ID不能为空"))
        if scenario_id not in [Scenario.ES] and not indices:
            raise ValidationError(_("indices不能为空"))
        return attrs


class ResultTableDetailSerializer(serializers.Serializer):
    scenario_id = serializers.CharField(label=_("接入场景"))
    storage_cluster_id = serializers.IntegerField(label=_("数据源ID"), required=False)

    def validate(self, attrs):
        super().validate(attrs)

        scenario_id = attrs["scenario_id"]
        if scenario_id == Scenario.ES and not attrs.get("storage_cluster_id"):
            raise ValidationError(_("数据源ID不能为空"))

        return attrs


class ResultTableAdaptSerializer(serializers.Serializer):
    class IndexSerializer(serializers.Serializer):
        index = serializers.CharField(required=True)
        time_field = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        time_field_type = serializers.ChoiceField(
            choices=["date", "long"], required=False, allow_null=True, allow_blank=True
        )

    scenario_id = serializers.CharField(label=_("接入场景"))
    storage_cluster_id = serializers.CharField(label=_("存储集群ID"), required=False, allow_blank=True, allow_null=True)
    basic_index = IndexSerializer(label=_("源索引"), required=False)
    basic_indices = serializers.ListField(label=_("源索引"), child=IndexSerializer(), required=False)
    append_index = IndexSerializer(label=_("待追加的索引"))

    def validate(self, attrs):
        super().validate(attrs)

        scenario_id = attrs["scenario_id"]
        if scenario_id == Scenario.ES and not attrs.get("storage_cluster_id"):
            raise ValidationError(_("数据源ID不能为空"))

        # 第三方ES必须传入时间字段和类型
        basic_indices = attrs.get("basic_indices", [])
        if scenario_id == Scenario.ES and basic_indices:
            for basic_index in basic_indices:
                if not basic_index.get("time_field"):
                    raise ValidationError(_("源索引时间字段不能为空"))
                if not basic_index.get("time_field_type"):
                    raise ValidationError(_("源索引时间字段类型不能为空"))
        append_index = attrs.get("append_index")
        if scenario_id == Scenario.ES:
            if not append_index.get("time_field"):
                raise ValidationError(_("待追加索引时间字段不能为空"))
            if not append_index.get("time_field_type"):
                raise ValidationError(_("待追加索引时间字段类型不能为空"))

        return attrs


class SearchAttrSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False, default=None)
    # 从host scope 转换成ip
    host_scopes = serializers.DictField(default={}, required=False)
    addition = serializers.ListField(allow_empty=True, required=False, default="")

    start_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    time_range = serializers.CharField(required=False, default=None)

    keyword = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    begin = serializers.IntegerField(required=False, default=0)
    size = serializers.IntegerField(required=False, default=10)

    # 支持用户自定义排序
    sort_list = serializers.ListField(required=False, allow_null=True, allow_empty=True)

    def validate(self, attrs):
        super().validate(attrs)
        return attrs


class UserSearchHistorySerializer(serializers.Serializer):
    start_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")

    def validate(self, attrs):
        super().validate(attrs)

        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        # 最多查询7天数据,如果开始时间或者结束时间为空，查询最近7天数据
        if start_time and end_time:
            days = (end_time - start_time).days
            if days > HISTORY_MAX_DAYS:
                raise ValidationError(_("最大只支持查询7天数据"))
        else:
            time_zone = get_local_param("time_zone")
            attrs["end_time"] = arrow.get(int(time.time())).to(time_zone).strftime("%Y-%m-%d %H:%M:%S%z")
            attrs["start_time"] = (
                datetime.datetime.strptime(attrs["end_time"], "%Y-%m-%d %H:%M:%S%z")
                - datetime.timedelta(days=HISTORY_MAX_DAYS)
            ).strftime("%Y-%m-%d %H:%M:%S%z")
        return attrs


class SearchIndexSetScopeSerializer(serializers.Serializer):
    """
    获取索引集所属项目
    如果用户传的是bk_biz_id，直接转成对应的project_id
    """

    project_id = serializers.IntegerField(label=_("项目ID"), required=False)
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)

    def validate(self, attrs):
        if attrs.get("project_id"):
            return attrs
        if not attrs.get("bk_biz_id"):
            raise ValidationError(_("请输入业务ID"))

        return MetaHandler.get_project_info(attrs["bk_biz_id"])


class SearchUserIndexSetConfigSerializer(serializers.Serializer):
    display_fields = serializers.ListField(allow_empty=False)
    sort_list = serializers.ListField(label=_("排序规则"), allow_empty=True, child=serializers.ListField())

    def validate_sort_list(self, value):
        for _item in value:
            if len(_item) != 2:
                raise ValidationError(_("sort_list参数格式有误"))

            if _item[1].lower() not in ["desc", "asc"]:
                raise ValidationError(_("排序规则只支持升序asc或降序desc"))
        return value

    class Meta:
        model = UserIndexSetConfig
        fields = ["display_fields"]


class SearchExportSerializer(serializers.Serializer):
    export_dict = serializers.CharField(required=False, allow_blank=False, allow_null=False)

    def validate(self, attrs):
        super().validate(attrs)
        export_dict_str = attrs["export_dict"]
        export_dict: dict = json.loads(export_dict_str)

        # deal time
        start_time = export_dict.get("start_time")
        start_time = parse(start_time)
        end_time = export_dict.get("end_time")
        end_time = parse(end_time)
        export_dict.update(
            {"start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"), "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")}
        )

        attrs["export_dict"] = json.dumps(export_dict)
        return attrs


class SearchAsyncExportSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"), required=True)
    keyword = serializers.CharField(label=_("搜索关键字"), required=True)
    time_range = serializers.CharField(label=_("时间范围"), required=False)
    start_time = serializers.CharField(label=_("起始时间"), required=True)
    end_time = serializers.CharField(label=_("结束时间"), required=True)
    host_scopes = serializers.DictField(label=_("检索模块ip等信息"), required=True)
    addition = serializers.ListField(label=_("搜索条件"), required=False)
    begin = serializers.IntegerField(label=_("检索开始 offset"), required=True)
    size = serializers.IntegerField(label=_("检索结果大小"), required=True)
    interval = serializers.CharField(label=_("匹配规则"), required=False)

    def validate(self, attrs):
        super().validate(attrs)

        # deal time
        start_time = attrs.get("start_time")
        start_time = parse(start_time)
        end_time = attrs.get("end_time")
        end_time = parse(end_time)
        attrs["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        attrs["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        return attrs


class SourceDetectSerializer(serializers.Serializer):
    es_host = serializers.CharField(label=_("ES HOST"))
    es_port = serializers.IntegerField(label=_("ES 端口"))
    es_user = serializers.CharField(label=_("ES 用户"), allow_blank=True, required=False)
    es_password = serializers.CharField(label=_("ES 密码"), allow_blank=True, required=False)


class HostIpListSerializer(serializers.Serializer):
    """
    主机ip序列化
    """

    ip = serializers.CharField(label=_("主机IP"), max_length=15)
    bk_cloud_id = serializers.IntegerField(label=_("云区域ID"), required=False, default=0)


class HostInstanceByIpListSerializer(serializers.Serializer):
    """
    根据ip列表获取主机实例序列化
    """

    ip_list = HostIpListSerializer(many=True)


class TopoSerializer(serializers.Serializer):
    """
    获取拓扑序列化
    """

    instance_type = serializers.ChoiceField(label=_("实例类型"), choices=InstanceTypeEnum.get_choices(), required=False)
    remove_empty_nodes = serializers.BooleanField(label=_("是否删除空节点"), required=False)


class NodeListParamSerializer(serializers.Serializer):
    """
    节点列表参数序列化
    """

    bk_inst_id = serializers.IntegerField(label=_("实例id"))
    bk_inst_name = serializers.CharField(label=_("实例名称"), max_length=64)
    bk_obj_id = serializers.CharField(label=_("类型id"), max_length=64)
    bk_biz_id = serializers.IntegerField(label=_("业务id"))


class NodeListSerializer(serializers.Serializer):
    """
    节点列表序列化
    """

    node_list = NodeListParamSerializer(many=True)


class FavoriteSearchSerializer(serializers.Serializer):
    """
    检索收藏序列化
    """

    project_id = serializers.IntegerField(label=_("项目ID"), required=False)
    index_set_id = serializers.IntegerField(label=_("索引集ID"), required=False)
    description = serializers.CharField(label=_("收藏描述"), max_length=50)
    host_scopes = serializers.DictField(default={}, required=False)
    addition = serializers.ListField(allow_empty=True, required=False, default="")
    keyword = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get("index_set_id"):
            raise ValidationError(_("索引集ID不能为空"))
        if not attrs.get("project_id"):
            raise ValidationError(_("项目id不能为空"))
        return attrs


class FavoriteSearchListSerializer(serializers.Serializer):
    """
    获取收藏所属项目
    如果用户传的是bk_biz_id，直接转成对应的project_id
    """

    project_id = serializers.IntegerField(label=_("项目ID"), required=False)
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)

    def validate(self, attrs):
        if attrs.get("project_id"):
            return attrs
        if not attrs.get("bk_biz_id"):
            raise ValidationError(_("请输入业务ID"))

        return MetaHandler.get_project_info(attrs["bk_biz_id"])


class BcsWebConsoleSerializer(serializers.Serializer):
    """
    获取bcs容器管理页面url序列化
    """

    cluster_id = serializers.CharField(label=_("集群id"), required=True)
    container_id = serializers.CharField(label=_("容器id"), required=True)


class TemplateTopoSerializer(serializers.Serializer):
    template_type = serializers.ChoiceField(label=_("模版类型"), choices=TemplateType.get_choices())


class TemplateSerializer(serializers.Serializer):
    bk_inst_ids = serializers.CharField(label=_("下载任务ID列表"))
    template_type = serializers.ChoiceField(label=_("模版类型"), choices=TemplateType.get_choices())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # 数据库中字段名为 task_id
        task_list = attrs["bk_inst_ids"].split(",")
        for task_id in task_list:
            if not re.findall(r"^\d+", task_id):
                raise serializers.ValidationError(_("类型错误,请输入正确的整型数组"))
        return attrs


class DynamicGroupSerializer(serializers.Serializer):
    dynamic_group_id = serializers.CharField(label=_("动态分组ID"))
