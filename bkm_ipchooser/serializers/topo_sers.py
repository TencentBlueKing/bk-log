# -*- coding: utf-8 -*-
from rest_framework import serializers

from bkm_ipchooser import mock_data
from bkm_ipchooser.serializers import base


class TreesRequestSer(base.ScopeSelectorBaseSer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_TREES_REQUEST}


class TreesResponseSer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_TREES_RESPONSE}


class QueryPathRequestSer(base.ScopeSelectorBaseSer):
    node_list = serializers.ListField(child=base.TreeNodeSer())

    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_PATH_REQUEST}


class QueryPathResponseSer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_PATH_RESPONSE}


class QueryHostsRequestSer(base.QueryHostsBaseSer):
    node_list = serializers.ListField(child=base.TreeNodeSer())

    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_HOSTS_REQUEST}


class QueryHostsResponseSer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_HOSTS_RESPONSE}


class QueryHostIdInfosRequestSer(QueryHostsRequestSer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_HOST_ID_INFOS_REQUEST}


class QueryHostIdInfosResponseSer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_HOST_ID_INFOS_RESPONSE}


class AgentStatisticsRequestSer(QueryHostsRequestSer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.API_TOPO_QUERY_HOST_ID_INFOS_REQUEST}
