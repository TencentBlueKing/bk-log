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
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.log_search.constants import InstanceTypeEnum


class GetVariableFieldSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    type = serializers.ChoiceField(label=_("查询类型"), choices=["host", "module", "set"])


class GetVariableValueSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    type = serializers.ChoiceField(label=_("查询类型"), choices=["dimension", "host", "module", "set"])
    params = serializers.DictField(label=_("查询参数"))


class GetMetricListSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    result_table_label = serializers.CharField(label=_("分类ID"), default="", allow_blank=True)


class TargetTreeSerializer(serializers.Serializer):
    """
    获取拓扑序列化
    """

    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    instance_type = serializers.ChoiceField(label=_("实例类型"), choices=InstanceTypeEnum.get_choices(), required=False)
    remove_empty_nodes = serializers.BooleanField(label=_("是否删除空节点"), required=False)


class QuerySerializer(serializers.Serializer):
    dashboard_id = serializers.CharField(label=_("仪表盘ID"), default="", allow_blank=True)
    panel_id = serializers.IntegerField(label=_("面板ID"), default=0)

    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    metric_field = serializers.CharField(label=_("监控指标"), allow_blank=True, default="")
    result_table_id = serializers.CharField(label=_("结果表ID"))
    where = serializers.ListField(label=_("过滤条件"))
    group_by = serializers.ListField(label=_("聚合字段"))
    query_string = serializers.CharField(label=_("查询字符串"), allow_blank=True, default="")

    method = serializers.CharField(label=_("聚合方法"))
    interval = serializers.IntegerField(default=60, label=_("时间间隔"))
    target = serializers.ListField(default=[], label=_("监控目标"))

    start_time = serializers.IntegerField(required=False, label=_("开始时间"))
    end_time = serializers.IntegerField(required=False, label=_("结束时间"))


class QueryLogSerializer(serializers.Serializer):
    dashboard_id = serializers.CharField(label=_("仪表盘ID"), default="", allow_blank=True)
    panel_id = serializers.IntegerField(label=_("面板ID"), default=0)

    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    result_table_id = serializers.CharField(label=_("结果表ID"))
    where = serializers.ListField(label=_("过滤条件"))
    query_string = serializers.CharField(label=_("查询字符串"), allow_blank=True, default="")
    target = serializers.ListField(default=[], label=_("监控目标"))
    size = serializers.IntegerField(default=10, label=_("日志条数"), max_value=10000)
    start_time = serializers.IntegerField(required=False, label=_("开始时间"))
    end_time = serializers.IntegerField(required=False, label=_("结束时间"))


class DimensionSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    result_table_id = serializers.CharField(label=_("结果表ID"))
    field = serializers.CharField(label=_("查询字段"))
    start_time = serializers.IntegerField(label=_("开始时间"))
    end_time = serializers.IntegerField(label=_("结束时间"))
    query_string = serializers.CharField(label=_("查询字符串"), allow_blank=True, default="")


class TracesSerializer(serializers.Serializer):
    operation = serializers.CharField(label=_("operation"), required=False)
    service = serializers.CharField(label=_("service"), required=False)
    tags = serializers.CharField(label=_("tags"), required=False)
    minDuration = serializers.IntegerField(label=_("minDuration"), required=False)
    maxDuration = serializers.IntegerField(label=_("maxDuration"), required=False)
    limit = serializers.IntegerField(label=_("limit"), default=20)
    start = serializers.IntegerField(label=_("开始时间"), required=False)
    end = serializers.IntegerField(label=_("结束时间"), required=False)
