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
import datetime
import time
import arrow

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import ValidationError
from apps.log_search.handlers.search.aggs_handlers import AggsHandlers
from apps.log_trace.constants import TIME_DIMENSION_VALUE, MetricTypeEnum
from apps.utils.local import get_local_param
from bkm_space.serializers import SpaceUIDField


class TraceIndexSetScopeSerializer(serializers.Serializer):
    """
    获取索引集所属项目
    """

    space_uid = SpaceUIDField(label=_("空间唯一标识"), required=True)


class TraceSearchAttrSerializer(serializers.Serializer):
    # business
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False, default=None)

    # filter条件，span选择器等
    addition = serializers.ListField(allow_empty=True, required=False, default="")
    host_scopes = serializers.DictField(default={}, required=False)

    # 时间选择器字段
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    time_range = serializers.CharField(required=False, default=None)

    # 关键字填充条
    keyword = serializers.CharField(allow_null=True, allow_blank=True)

    # 分页
    begin = serializers.IntegerField(required=False, default=0)
    size = serializers.IntegerField(required=False, default=30)

    # 支持用户自定义排序，后续优化再考虑加入
    # sort_list = serializers.ListField(required=False, allow_null=True, allow_empty=True)


class TraceSearchTraceIdAttrSerializer(serializers.Serializer):
    startTime = serializers.CharField(allow_null=False, allow_blank=False)
    traceID = serializers.CharField(allow_null=False, allow_blank=False)


class AggsTermsSerializer(serializers.Serializer):
    # 时间选择器字段
    start_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    time_range = serializers.CharField(required=False, default=None)

    addition = serializers.ListField(allow_empty=True, required=False, default="")
    host_scopes = serializers.DictField(default={}, required=False)
    # 关键字填充条
    keyword = serializers.CharField(required=False, default=None)

    time_dimension = serializers.IntegerField(required=False, default=TIME_DIMENSION_VALUE)
    fields = serializers.ListField(child=serializers.CharField(), required=True)
    size = serializers.IntegerField(required=False, default=AggsHandlers.AGGS_BUCKET_SIZE)
    order = serializers.DictField(required=False, default=AggsHandlers.DEFAULT_ORDER)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # 查询全量数据
        if attrs["time_dimension"] == -1:
            attrs["end_time"] = None
            attrs["start_time"] = None
            return attrs

        # 查询最近N天时间维度数据
        if not attrs.get("start_time") or not attrs.get("end_time"):
            time_zone = get_local_param("time_zone")
            attrs["end_time"] = arrow.get(int(time.time())).to(time_zone).strftime("%Y-%m-%d %H:%M:%S%z")
            attrs["start_time"] = (
                datetime.datetime.strptime(attrs["end_time"], "%Y-%m-%d %H:%M:%S%z")
                - datetime.timedelta(days=attrs["time_dimension"])
            ).strftime("%Y-%m-%d %H:%M:%S%z")
        return attrs


class DateHistogramSerializer(TraceSearchAttrSerializer):
    class DateHistogramFieldSerializer(serializers.Serializer):
        term_filed = serializers.CharField(required=True)
        metric_type = serializers.ChoiceField(required=False, choices=MetricTypeEnum.get_choices())
        metric_field = serializers.CharField(required=False)

        def validate(self, attrs):
            attrs = super().validate(attrs)

            metric_type = attrs.get("metric_type")
            metric_field = attrs.get("metric_field")
            if metric_type and not metric_field:
                raise ValidationError(_("metric_field字段不能为空"))
            return attrs

    fields = serializers.ListField(child=DateHistogramFieldSerializer(), required=False, default=[])
    interval = serializers.CharField(required=False, default="auto", max_length=16)
