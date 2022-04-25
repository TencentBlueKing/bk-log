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
        if self.action in ["update"]:
            return CollectorPluginUpdateSerializer
        return CollectorPluginSerializer

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/collector_plugins/ 1_创建采集插件
        @apiName create_collector_plugin
        @apiDescription 创建采集插件
        @apiGroup 12_CollectorPlugin
        @apiParam {Bool} create_public_data_id 是否创建公共DATAID
        @apiParam {String} collector_plugin_name 采集插件名称
        @apiParam {String} collector_plugin_name_en 采集插件英文名
        @apiParam {String} description 采集插件描述
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Bool} is_enabled_display_collector 是否显示采集项
        @apiParam {String} collector_scenario_id 采集场景
        @apiParam {String} category_id 类别
        @apiParam {Bool} is_allow_alone_data_id 是否允许独立DATAID
        @apiParam {Bool} is_allow_alone_etl_config 是否允许独立清洗配置
        @apiParam {Bool} is_allow_alone_storage 是否允许独立存储配置
        @apiParam {Int} [storage_cluster_id] 存储集群ID
        @apiParam {String} etl_processor 数据处理器
        @apiParam {String} [etl_config] 清洗配置
        @apiParam {Int} [retention] 保留时间
        @apiParam {Int} [allocation_min_days] 冷热数据时间
        @apiParam {Int} [storage_replies] 副本数量
        @apiParam {Int} [storage_shards_size] 单shards分片大小
        @apiParam {Int} [storage_shards_nums] 单shards分片数量
        @apiParam {Object} params 采集插件参数
        @apiParam {Objects} params.fields 清洗字段
        @apiParam {Objects} params.etl_params 清洗入库参数
        @apiParam {String} data_encoding 日志字符集
        @apiParamExample {json} 请求样例:
        {
            "create_public_data_id": true,
            "collector_plugin_name": "采集插件名称",
            "collector_plugin_name_en": "collector_plugin_name",
            "description": "采集插件描述",
            "bk_biz_id": 2,
            "is_enabled_display_collector": false,
            "is_allow_alone_data_id": false,
            "is_allow_alone_etl_config": false,
            "is_allow_alone_storage": false,
            "collector_scenario_id": "custom",
            "category_id": "application_check",
            "storage_cluster_id": 2,
            "etl_processor": "transfer",
            "etl_config": "bk_log_text",
            "etl_template": {},
            "retention": 7,
            "allocation_min_days": 7,
            "storage_replies": 1,
            "params": {},
            "data_encoding": "UTF-8"
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
        @apiParam {String} [collector_plugin_name] 采集插件名称
        @apiParam {String} [description] 采集插件描述
        @apiParam {Bool} [is_enabled_display_collector] 是否显示采集项
        @apiParam {Bool} [is_allow_alone_data_id] 是否允许独立DATAID
        @apiParam {Bool} [is_allow_alone_etl_config] 是否允许独立清洗配置
        @apiParam {Bool} [is_allow_alone_storage] 是否允许独立存储配置
        @apiParam {Int} [storage_cluster_id] 存储集群ID
        @apiParam {String} [etl_config] 清洗配置
        @apiParam {Int} [retention] 保留时间
        @apiParam {Int} [allocation_min_days] 冷热数据时间
        @apiParam {Int} [storage_replies] 副本数量
        @apiParam {Int} [storage_shards_size] 单shards分片大小
        @apiParam {Int} [storage_shards_nums] 单shards分片数量
        @apiParam {Object} [params] 采集插件参数
        @apiParam {Objects} params.fields 清洗字段
        @apiParam {Objects} params.etl_params 清洗入库参数
        @apiParam {String} data_encoding 日志字符集
        @apiParamExample {json} 请求样例:
        {
            "collector_plugin_name": "采集插件名称",
            "description": "采集插件描述",
            "is_enabled_display_collector": false,
            "is_allow_alone_data_id": false,
            "is_allow_alone_etl_config": false,
            "is_allow_alone_storage": false,
            "storage_cluster_id": 2,
            "etl_config": "bk_log_text",
            "retention": 7,
            "allocation_min_days": 7,
            "storage_replies": 1,
            "params": {}
            "data_encoding": "UTF-8"
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
            data["etl_processor"], collector_plugin_id=collector_plugin.collector_plugin_id
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
        @apiParam {Int} [bkdata_biz_id] 数据所属业务
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {String} collector_config_name_en 采集项英文名
        @apiParam {Int} [data_link_id] 数据链路id
        @apiParam {String} category_id 数据分类 GlobalsConfig.category读取
        @apiParam {String} target_object_type 对象类型，目前固定为 HOST
        @apiParam {String} target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array[Dict]} target 已选目标
        @apiParam {Array(json)} target_nodes 采集目标
        @apiParam {Int} target_nodes.id 服务实例id （暂时没用到）
        @apiParam {Int} target_nodes.bk_inst_id 节点实例id (动态)
        @apiParam {String} target_nodes.bk_obj_id 节点对象id （动态）
        @apiParam {String} target_nodes.ip 主机实例ip （静态）
        @apiParam {Int} target_nodes.bk_cloud_id 蓝鲸云区域id （静态）
        @apiParam {Int} target_nodes.bk_supplier_id 供应商id （静态）
        @apiParam {String} data_encoding 日志字符集 可选字段`UTF-8, GBK`
        @apiParam {String} bk_data_name 存储索引名
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
        @apiParam {String} etl_config 清洗类型（格式化方式）
        @apiParam {String} table_id 结果表名（不需要传前辍）
        @apiParam {Object} etl_params 清洗配置，不同的清洗类型的参数有所不同
        @apiParam {String} etl_params.separator 分隔符，当etl_config=="bk_log_delimiter"时需要传递
        @apiParam {String} etl_params.separator_regexp 正则表达式，当etl_config=="bk_log_regexp"时需要传递
        @apiParam {Bool} etl_params.retain_original_text 是否保留原文
        @apiParam {list} fields 字段列表
        @apiParam {String} fields.field_name 字段名称
        @apiParam {String} [fields.alias_name] 别名
        @apiParam {String} fields.field_type 字段类型
        @apiParam {String} fields.description 字段说明
        @apiParam {Bool} fields.is_analyzed 是否分词
        @apiParam {Bool} fields.is_dimension 是否维度
        @apiParam {Bool} fields.is_time 是否时间字段
        @apiParam {Bool} fields.is_delete 是否删除
        @apiParam {Json} [fields.option] 字段配置
        @apiParam {Int} fields.option.time_zone 时间
        @apiParam {String} fields.option.time_format 时间格式
        @apiParam {Int} storage_cluster_id 存储集群ID
        @apiParam {Int} retention 保留时间
        @apiParam {Int} [storage_replies] 副本数量
        @apiParamExample {json} 请求样例:
        {
            "bk_biz_id": 706,
            "collector_config_name": "采集项名称",
            "collector_config_name_en": "采集项英文名",
            "data_link_id": 1
            "collector_scenario_id": "line",
            "category_id": "application",
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
            "table_id": "xxx",
            "etl_config": "bk_log_text | bk_log_json | bk_log_regexp | bk_log_delimiter",
            "etl_params": {
                "separator_regexp": "[a-z][0-9]",
                "separator": "|",
                "retain_original_text": true
            },
            "fields": [
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
            "storage_cluster_id": 3,
            "retention": 1,
        }
        @apiSuccess {Int} collector_config_id 采集配置ID
        @apiSuccess {Int} collector_config_name 采集配置名称
        @apiSuccess {Int} bk_data_id 采集链路data_id
        @apiSuccess {Int} subscription_id 节点管理订阅ID
        @apiSuccess {List} task_id_list 最后部署ID
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
                "collector_config_id": 1,
                "collector_config_name": "采集项名称",
                "bk_data_id": 2001,
                "subscription_id": "订阅ID",
                "task_id_list": [1]
            },
            "result": true
        }
        """
        data = self.validated_data
        collector_plugin: CollectorPlugin = self.get_object()
        data["collector_plugin_id"] = collector_plugin.pk
        if not collector_plugin.is_allow_alone_etl_config:
            data["etl_processor"] = collector_plugin.etl_processor
        collector_plugin_handler: CollectorPluginHandler = get_collector_plugin_handler(
            data["etl_processor"], collector_plugin_id=collector_plugin.pk
        )
        return Response(collector_plugin_handler.create_instance(data))
