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
from rest_framework import serializers

from apps.generic import DataModelSerializer
from apps.log_audit.models import UserOperationRecord


class UserSearchHistorySerializer(serializers.Serializer):
    start_time = serializers.CharField(required=True)
    end_time = serializers.CharField(required=True)
    page = serializers.IntegerField(required=True)
    pagesize = serializers.IntegerField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["start_time"] = attrs["start_time"].replace("&nbsp;", " ")
        attrs["end_time"] = attrs["end_time"].replace("&nbsp;", " ")
        return attrs


class CustomReportConfSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    data_id = serializers.IntegerField(required=False)
    result_table_id = serializers.CharField(required=False)


class CustomReportSettingSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    conf = CustomReportConfSerializer(required=True)


class UserSearchHistoryOperationStatisticSerializer(serializers.Serializer):
    start_time = serializers.CharField(required=True)
    end_time = serializers.CharField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["start_time"] = attrs["start_time"].replace("&nbsp;", " ")
        attrs["end_time"] = attrs["end_time"].replace("&nbsp;", " ")
        return attrs


class AuditRecordSerializer(DataModelSerializer):
    operate_type = serializers.CharField(required=False)
    operate_id = serializers.IntegerField(required=False)
    bk_biz_id = serializers.IntegerField(required=False)

    class Meta:
        model = UserOperationRecord
        fields = "__all__"
