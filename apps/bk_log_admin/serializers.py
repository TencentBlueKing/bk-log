# -*- coding: utf-8 -*-

from rest_framework import serializers

from apps.generic import DataModelSerializer
from apps.log_audit.models import UserOperationRecord


class UserSearchHistorySerializer(serializers.Serializer):
    start_time = serializers.CharField(required=True)
    end_time = serializers.CharField(required=True)
    page = serializers.IntegerField(required=True)
    pagesize = serializers.IntegerField(required=True)

    def validate(self, attrs):
        super().validate(attrs)
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
        super().validate(attrs)
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
