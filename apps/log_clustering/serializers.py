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
from rest_framework import serializers

from apps.log_clustering.constants import PatternEnum


class PatternSearchSerlaizer(serializers.Serializer):
    host_scopes = serializers.DictField(default={}, required=False)
    addition = serializers.ListField(allow_empty=True, required=False, default=[])
    start_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    time_range = serializers.CharField(required=False, default="customized")
    keyword = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    size = serializers.IntegerField(required=False, default=10000)
    pattern_level = serializers.ChoiceField(required=True, choices=PatternEnum.get_choices())
    show_new_pattern = serializers.BooleanField(required=True)
    year_on_year_hour = serializers.IntegerField(required=False, default=0, min_value=0)
    group_by = serializers.ListField(required=False, default=[])


class FilerRuleSerializer(serializers.Serializer):
    fields_name = serializers.CharField(required=False)
    op = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    logic_operator = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ClusteringConfigSerializer(serializers.Serializer):
    collector_config_id = serializers.IntegerField(required=False, allow_null=True, default=0)
    collector_config_name_en = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    index_set_id = serializers.IntegerField()
    min_members = serializers.IntegerField(required=False, default=1, allow_null=True)
    max_dist_list = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)
    predefined_varibles = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    delimeter = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    max_log_length = serializers.IntegerField(required=False, allow_null=True, default=100)
    is_case_sensitive = serializers.IntegerField(required=False, allow_null=True, default=1)
    clustering_fields = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    bk_biz_id = serializers.IntegerField()
    filter_rules = serializers.ListField(child=FilerRuleSerializer(), required=False, default=[])
    signature_enable = serializers.BooleanField(default=False)


class InputDataSerializer(serializers.Serializer):
    dtEventTimeStamp = serializers.IntegerField()
    log = serializers.CharField()
    uuid = serializers.CharField()


class ClusteringPreviewSerializer(serializers.Serializer):
    input_data = serializers.ListField(child=InputDataSerializer())
    min_members = serializers.IntegerField()
    max_dist_list = serializers.CharField()
    predefined_varibles = serializers.CharField()
    delimeter = serializers.CharField()
    max_log_length = serializers.IntegerField()
    is_case_sensitive = serializers.IntegerField()
