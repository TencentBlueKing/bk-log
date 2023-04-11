from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from apps.generic import ModelViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import insert_permission_field
from apps.log_databus.exceptions import CollectorConfigNotExistException, CollectorPluginNotImplemented
from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.collector_plugin.base import get_collector_plugin_handler
from apps.log_databus.models import CollectorConfig, CollectorPlugin
from apps.log_databus.serializers import (
    CollectorPluginCreateSerializer,
    CollectorPluginSerializer,
    CollectorPluginUpdateSerializer,
    CreateColelctorConfigEtlSerializer,
    CreateCollectorPluginInstanceSerializer,
    UpdateCollectorPluginInstanceSerializer,
)
from apps.log_search.permission import Permission
from apps.utils.drf import detail_route, list_route
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
            return CreateCollectorPluginInstanceSerializer
        if self.action in ["update_instance"]:
            return UpdateCollectorPluginInstanceSerializer
        if self.action in ["instance_etl"]:
            return CreateColelctorConfigEtlSerializer
        if self.action in ["update", "partial_update"]:
            return CollectorPluginUpdateSerializer
        return CollectorPluginSerializer

    @insert_permission_field(
        id_field=lambda d: d["_collector_config_id"],
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        for plugin in response.data:
            try:
                plugin["_collector_config_id"] = CollectorPlugin.get_collector_config_id(plugin["collector_plugin_id"])
            except CollectorPluginNotImplemented:
                plugin["_collector_config_id"] = -1
        return response

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
        @apiParam {Bool} is_display_collector 是否显示采集项
        @apiParam {Bool} is_allow_alone_data_id 是否允许独立DATAID
        @apiParam {Bool} is_allow_alone_etl_config 是否允许独立清洗配置
        @apiParam {String} etl_processor 数据处理器
        @apiParam {String} [etl_config] 清洗配置
        @apiParam {Object} [etl_params] 清洗参数
        @apiParam {Array} [fields] 清洗字段
        @apiParam {Array} [params] 插件参数
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
            "is_display_collector": false,
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
        @apiParam {Bool} is_display_collector 是否显示采集项
        @apiParam {Bool} is_allow_alone_data_id 是否允许独立DATAID
        @apiParam {Bool} is_allow_alone_etl_config 是否允许独立清洗配置
        @apiParam {Object} [etl_params] 清洗模板
        @apiParam {String} [etl_config] 清洗配置
        @apiParam {Array} [fields] 清洗字段
        @apiParam {Array} [params] 插件参数
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
            "is_display_collector": false,
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
        @apiParam {Int} bk_biz_id 所属业务
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {String} collector_config_name_en 采集项英文名称
        @apiParam {Int} data_link_id 数据链路id
        @apiParam {String} target_object_type 对象类型，目前固定为 HOST
        @apiParam {String} target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array[Dict]} target 已选目标
        @apiParam {Array(json)}  target_nodes 采集目标
        @apiParam {Int} target_nodes.id 服务实例id （暂时没用到）
        @apiParam {Int} target_nodes.bk_inst_id 节点实例id (动态)
        @apiParam {String} target_nodes.bk_obj_id 节点对象id （动态）
        @apiParam {String} target_nodes.ip 主机实例ip （静态）
        @apiParam {Int} target_nodes.bk_cloud_id 蓝鲸云区域id （静态）
        @apiParam {Int} target_nodes.bk_supplier_id 供应商id （静态）
        @apiParam {Int} target_nodes.bk_host_id 主机ID （静态）
        @apiParam {String} data_encoding 日志字符集 可选字段`UTF-8, GBK`
        @apiParam {String} description 备注说明
        @apiParam {json} params 插件参数（日志路径、过滤方式等）
        @apiParam {Array} params.paths 日志路径
        @apiParam {json} params.conditions 过滤方式
        @apiParam {String} params.conditions.type 过滤方式类型 可选字段 `match, separator`
        @apiParam {String} params.conditions.match_type 过滤方式 可选字段 `include, exclude`
        @apiParam {String} params.conditions.match_content 过滤内容
        @apiParam {String} params.conditions.separator 分隔符
        @apiParam {String} params.conditions.separator_filters 分隔符过滤条件
        @apiParam {Array} params.winlog_name windows事件名称
        @apiParam {Array} params.winlog_level windows事件等级
        @apiParam {Array} params.winlog_event_id windows事件id
        @apiParamExample {json} 请求样例:
        {
            "bk_biz_id": 706,
            "collector_config_name": "采集项名称",
            "collector_config_name_en": "采集项英文名",
            "data_link_id": 1
            "target_object_type": "HOST",
            "target_node_type": "TOPO",
            "target_nodes": [
                {
                   "id": 12
                },
                {
                    "bk_inst_id": 33,   // 节点实例ID
                    "bk_obj_id": "module",  // 节点对象ID
                },
                {
                    "ip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_supplier_id": 0,
                }
            ],
            "data_encoding": "UTF-8",
            "description": "这是一个描述",
            "params": {
                "paths": ["/log/abc"],
                "conditions": {
                    "type": "match",
                    "match_type": "include",
                    "match_content": "delete",
                    "separator": "|",
                    "separator_filters": [
                        {
                            "fieldindex": 1,
                            "word": "",
                            "op": "=",
                            "logic_op": "and"
                        }
                    ]
                },
                "multiline_pattern": "",
                "multiline_max_lines": 10,
                "multiline_timeout": 60,
                "winlog_name": ["Application", "Security"],
                "winlog_level": ["info", "error"],
                "winlog_event_id": ["-200", "123-1234", "123"]
            },
        }
        @apiSuccess {Int} collector_config_id 采集配置ID
        @apiSuccess {Int} collector_config_name 采集配置名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collector_config_id": 1,
                "collector_config_name": "采集插件"
            },
            "result": true
        }
        """
        collector_plugin: CollectorPlugin = self.get_object()
        data = self.validated_data
        data.update({"collector_plugin_id": collector_plugin.collector_plugin_id})
        collector_plugin_handler: CollectorPluginHandler = get_collector_plugin_handler(
            collector_plugin.etl_processor, collector_plugin.collector_plugin_id
        )
        return Response(collector_plugin_handler.create_instance(data))

    @list_route(methods=["PUT"])
    def update_instance(self, request, *args, **kwargs):
        """
        @api {post} /databus/collector_plugins/update_instance/ 4_实例化采集插件
        @apiName update_collector_plugin_instance
        @apiDescription 更新采集插件实例
        @apiGroup 13_CollectorPlugin
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {String} collector_config_name_en 采集项英文名称
        @apiParam {String} target_object_type 对象类型，目前固定为 HOST
        @apiParam {String} target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array[Dict]} target 已选目标
        @apiParam {Array(json)}  target_nodes 采集目标
        @apiParam {Int} target_nodes.id 服务实例id （暂时没用到）
        @apiParam {Int} target_nodes.bk_inst_id 节点实例id (动态)
        @apiParam {String} target_nodes.bk_obj_id 节点对象id （动态）
        @apiParam {String} target_nodes.ip 主机实例ip （静态）
        @apiParam {Int} target_nodes.bk_cloud_id 蓝鲸云区域id （静态）
        @apiParam {Int} target_nodes.bk_supplier_id 供应商id （静态）
        @apiParam {Int} target_nodes.bk_host_id 主机ID （静态）
        @apiParam {String} data_encoding 日志字符集 可选字段`UTF-8, GBK`
        @apiParam {String} description 备注说明
        @apiParam {json} params 插件参数（日志路径、过滤方式等）
        @apiParam {Array} params.paths 日志路径
        @apiParam {json} params.conditions 过滤方式
        @apiParam {String} params.conditions.type 过滤方式类型 可选字段 `match, separator`
        @apiParam {String} params.conditions.match_type 过滤方式 可选字段 `include, exclude`
        @apiParam {String} params.conditions.match_content 过滤内容
        @apiParam {String} params.conditions.separator 分隔符
        @apiParam {String} params.conditions.separator_filters 分隔符过滤条件
        @apiParam {Array} params.winlog_name windows事件名称
        @apiParam {Array} params.winlog_level windows事件等级
        @apiParam {Array} params.winlog_event_id windows事件id
        @apiParamExample {json} 请求样例:
        {
            "collector_config_name": "采集项名称",
            "collector_config_name_en": "采集项英文名",
            "target_object_type": "HOST",
            "target_node_type": "TOPO",
            "target_nodes": [
                {
                   "id": 12
                },
                {
                    "bk_inst_id": 33,   // 节点实例ID
                    "bk_obj_id": "module",  // 节点对象ID
                },
                {
                    "ip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_supplier_id": 0,
                }
            ],
            "data_encoding": "UTF-8",
            "description": "这是一个描述",
            "params": {
                "paths": ["/log/abc"],
                "conditions": {
                    "type": "match",
                    "match_type": "include",
                    "match_content": "delete",
                    "separator": "|",
                    "separator_filters": [
                        {
                            "fieldindex": 1,
                            "word": "",
                            "op": "=",
                            "logic_op": "and"
                        }
                    ]
                },
                "multiline_pattern": "",
                "multiline_max_lines": 10,
                "multiline_timeout": 60,
                "winlog_name": ["Application", "Security"],
                "winlog_level": ["info", "error"],
                "winlog_event_id": ["-200", "123-1234", "123"]
            },
        }
        @apiSuccess {Int} collector_config_id 采集配置ID
        @apiSuccess {Int} collector_config_name 采集配置名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collector_config_id": 1,
                "collector_config_name": "采集插件"
            },
            "result": true
        }
        """
        data = self.validated_data
        collector_config = get_object_or_404(CollectorConfig, collector_config_id=data["collector_config_id"])
        collector_plugin_handler: CollectorPluginHandler = get_collector_plugin_handler(
            collector_config.etl_processor, collector_config.collector_plugin_id
        )
        return Response(collector_plugin_handler.update_instance(data))

    @list_route(methods=["POST"])
    def instance_etl(self, request, *args, **kwargs):
        """
        @api {post} /databus/collector_plugins/$collector_plugin_id/instance_etl/ 5_采集插件清洗入库
        @apiName create_collector_plugin_instance_etl
        @apiDescription 采集插件清洗入库
        @apiGroup 14_CollectorPlugin
        @apiParam {String} collector_config_id 采集项ID
        @apiParam {String} etl_config 清洗配置
        @apiParam {Object} etl_params 清洗参数
        @apiParam {Array} fields 清洗字段
        @apiParam {Int} [storage_cluster_id] 存储集群ID
        @apiParam {Int} [retention] 保留时间
        @apiParam {Int} [allocation_min_days] 冷热数据时间
        @apiParam {Int} [storage_replies] 副本数量
        @apiParam {Int} [storage_shards_size] 单shards分片大小
        @apiParam {Int} [storage_shards_nums] 单shards分片数量
        @apiParamExample {json} 请求样例:
        {
            "collector_config_id": 1,
            "etl_config": "bk_log_text | bk_log_json | bk_log_regexp | bk_log_delimiter | custom",
            "etl_params": {
                "separator_regexp": "[a-z][0-9]",
                "separator": "|",
                "retain_original_text": true
            },
            "fields": [
                {
                    "field_name": "user",
                    "alias_name": "",
                    "field_type": "long",
                    "description": "字段描述",
                    "is_analyzed": true,
                    "is_dimension": false,
                    "is_time": false,
                    "is_delete": false,
                },
                {
                    "field_name": "report_time",
                    "alias_name": "",
                    "field_type": "string",
                    "description": "字段描述",
                    "tag": "metric",
                    "is_analyzed": false,
                    "is_dimension": false,
                    "is_time": true,
                    "is_delete": false,
                    "option": {
                        "time_zone": 8,
                        "time_format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            ],
            "storage_cluster_id": 2,
            "retention": 7,
            "allocation_min_days": 0,
            "storage_replies": 1,
            "storage_shards_nums": 1,
            "storage_shards_size": 10,
        }
        @apiSuccess {Int} collector_config_id 采集配置ID
        @apiSuccess {Int} collector_config_name 采集配置名称
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "collector_config_id": 1,
                "collector_config_name": "采集插件"
            },
            "result": true
        }
        """
        data = self.validated_data
        try:
            collector_config: CollectorConfig = CollectorConfig.objects.get(
                collector_config_id=data["collector_config_id"]
            )
        except CollectorConfig.DoesNotExist:
            raise CollectorConfigNotExistException()
        collector_plugin_handler: CollectorPluginHandler = get_collector_plugin_handler(
            collector_config.etl_processor, collector_config.collector_plugin_id
        )
        return Response(collector_plugin_handler.create_instance_etl(collector_config, data))
