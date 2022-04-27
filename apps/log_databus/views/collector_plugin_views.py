from django.conf import settings
from rest_framework.response import Response

from apps.generic import ModelViewSet
from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.collector_plugin.base import get_collector_plugin_handler
from apps.log_databus.models import CollectorPlugin
from apps.log_databus.serializers import (
    CollectorPluginCreateSerializer,
    CollectorPluginInitSerializer,
    CollectorPluginSerializer,
    CollectorPluginUpdateSerializer,
)
from apps.log_search.permission import Permission
from apps.utils.drf import detail_route
from apps.utils.function import ignored


class CollectorPluginViewSet(ModelViewSet):
    """
    采集插件
    """

    model = CollectorPlugin
    queryset = CollectorPlugin.objects.all()
    filter_backends = []

    def get_permissions(self):
        with ignored(Exception, log_exception=True):
            auth_info = Permission.get_auth_info(self.request)
            # ESQUERY白名单不需要鉴权
            if auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
                return []
        return []

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["create"]:
            return CollectorPluginCreateSerializer
        if self.action in ["instances"]:
            return CollectorPluginInitSerializer
        if self.action in ["update", "partial_update"]:
            return CollectorPluginUpdateSerializer
        return CollectorPluginSerializer

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/collector_plugins/ 1_创建采集插件
        @apiName create_collector_plugin
        @apiDescription 创建采集插件
        @apiGroup 12_CollectorPlugin
        @apiParam {Bool} is_create_public_data_id 是否创建公共DATAID
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Int} bkdata_biz_id 数据归属业务ID
        @apiParam {String} collector_plugin_name 采集插件名称
        @apiParam {String} collector_plugin_name_en 采集插件英文名
        @apiParam {String} collector_scenario_id 采集场景
        @apiParam {String} description 采集插件描述
        @apiParam {String} category_id 类别
        @apiParam {String} data_encoding 日志字符集
        @apiParam {Bool} is_enabled_display_collector 是否显示采集项
        @apiParam {Bool} is_allow_alone_data_id 是否允许独立DATAID
        @apiParam {Bool} is_allow_alone_etl_config 是否允许独立清洗配置
        @apiParam {String} etl_processor 数据处理器
        @apiParam {String} [etl_template] 清洗模板
        @apiParam {String} [etl_config] 清洗配置
        @apiParam {String} [etl_params] 清洗配置
        @apiParam {String} [fields] 清洗配置
        @apiParam {Array} [params] 清洗字段
        @apiParam {Bool} is_allow_alone_storage 是否允许独立存储配置
        @apiParam {Int} [storage_cluster_id] 存储集群ID
        @apiParam {Int} [retention] 保留时间
        @apiParam {Int} [allocation_min_days] 冷热数据时间
        @apiParam {Int} [storage_replies] 副本数量
        @apiParam {Int} [storage_shards_size] 单shards分片大小
        @apiParam {Int} [storage_shards_nums] 单shards分片数量
        @apiParamExample {json} 请求样例:
        {
            "is_create_public_data_id": true,
            "bk_biz_id": 0,
            "bkdata_biz_id": 0,
            "collector_plugin_name": "采集插件名称",
            "collector_plugin_name_en": "collector_plugin_name",
            "collector_scenario_id": "custom",
            "description": "采集插件描述",
            "category_id": "application_check",
            "data_encoding": "UTF-8"
            "is_enabled_display_collector": false,
            "is_allow_alone_data_id": false,
            "is_allow_alone_etl_config": false,
            "etl_processor": "bkbase",
            "etl_config": "custom",
            "fields": [
                {
                    "id": 12159347,
                    "field_name": "ip",
                    "field_type": "string",
                    "field_alias": "IP地址",
                    "is_dimension": false,
                    "field_index": 5
                },
                {
                    "id": 12159348,
                    "field_name": "datetime",
                    "field_type": "string",
                    "field_alias": "日志时间",
                    "is_dimension": false,
                    "field_index": 7
                }
            ],
            "etl_params": {
                "retain_original_text": false,
                "separator_regexp": "",
                "json_config": "……"
            },
            "is_allow_alone_storage": false,
            "storage_cluster_id": 2,
            "retention": 7,
            "allocation_min_days": 0,
            "storage_replies": 1,
            "storage_shards_nums": 1,
            "storage_shards_size": 10,
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collector_plugin_id": 1,
                "collector_plugin_name": "采集插件"
            },
            "result": true
        }
        """
        data = self.validated_data
        collector_plugin_handler: CollectorPluginHandler = get_collector_plugin_handler(data["etl_processor"])
        return Response(collector_plugin_handler.update_or_create(data))

    def update(self, request, *args, **kwargs):
        """
        @api {post} /databus/collector_plugins/$collector_plugin_id/ 2_更新采集插件
        @apiName update_collector_plugin
        @apiDescription 更新采集插件
        @apiGroup 12_CollectorPlugin
        @apiParam {String} collector_plugin_name 采集插件名称
        @apiParam {String} description 采集插件描述
        @apiParam {String} data_encoding 日志字符集
        @apiParam {Bool} is_enabled_display_collector 是否显示采集项
        @apiParam {Bool} is_allow_alone_data_id 是否允许独立DATAID
        @apiParam {Bool} is_allow_alone_etl_config 是否允许独立清洗配置
        @apiParam {String} [etl_params] 清洗模板
        @apiParam {String} [etl_config] 清洗配置
        @apiParam {Array} [fields] 清洗字段
        @apiParam {Array} [params] 模板参数
        @apiParam {Bool} is_allow_alone_storage 是否允许独立存储配置
        @apiParam {Int} [storage_cluster_id] 存储集群ID
        @apiParam {Int} [retention] 保留时间
        @apiParam {Int} [allocation_min_days] 冷热数据时间
        @apiParam {Int} [storage_replies] 副本数量
        @apiParam {Int} [storage_shards_size] 单shards分片大小
        @apiParam {Int} [storage_shards_nums] 单shards分片数量
        @apiParamExample {json} 请求样例:
        {
            "collector_plugin_name": "采集插件名称",
            "description": "采集插件描述",
            "data_encoding": "UTF-8"
            "is_enabled_display_collector": false,
            "is_allow_alone_data_id": false,
            "is_allow_alone_etl_config": false,
            "etl_config": "custom",
            "fields": [
                {
                    "id": 12159347,
                    "field_name": "ip",
                    "field_type": "string",
                    "field_alias": "IP地址",
                    "is_dimension": false,
                    "field_index": 5
                },
                {
                    "id": 12159348,
                    "field_name": "datetime",
                    "field_type": "string",
                    "field_alias": "日志时间",
                    "is_dimension": false,
                    "field_index": 7
                }
            ],
            "etl_params": {
                "retain_original_text": false,
                "separator_regexp": "",
                "json_config": "……"
            },
            "is_allow_alone_storage": false,
            "storage_cluster_id": 2,
            "retention": 7,
            "allocation_min_days": 0,
            "storage_replies": 1,
            "storage_shards_nums": 1,
            "storage_shards_size": 10,
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collector_plugin_id": 1,
                "collector_plugin_name": "采集插件"
            },
            "result": true
        }
        """
        data = self.validated_data
        collector_plugin: CollectorPlugin = self.get_object()
        collector_plugin_handler: CollectorPluginHandler = get_collector_plugin_handler(
            collector_plugin.etl_processor, collector_plugin.collector_plugin_id
        )
        return Response(collector_plugin_handler.update_or_create(data))

    @detail_route(methods=["POST"])
    def instances(self, request, *args, **kwargs):
        """
        @api {post} /databus/collector_plugins/$collector_plugin_id/instances/ 3_实例化采集插件
        @apiName create_collector_plugin_instance
        @apiDescription 实例化采集插件
        @apiGroup 12_CollectorPlugin
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collector_plugin_id": 1,
                "collector_plugin_name": "采集插件"
            },
            "result": true
        }
        """
        pass
