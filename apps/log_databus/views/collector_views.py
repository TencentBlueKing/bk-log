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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django.db.models import Q

from rest_framework.response import Response

from apps.exceptions import ValidationError
from apps.log_databus.constants import EtlConfig
from apps.log_search.constants import HAVE_DATA_ID, BKDATA_OPEN
from apps.log_search.permission import Permission
from apps.utils.drf import detail_route, list_route
from apps.generic import ModelViewSet
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import (
    InstanceActionPermission,
    ViewBusinessPermission,
    BusinessActionPermission,
    insert_permission_field,
)
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.handlers.link import DataLinkHandler
from apps.log_databus.models import CollectorConfig
from apps.log_databus.serializers import (
    RunSubscriptionSerializer,
    BatchSubscriptionStatusSerializer,
    TaskStatusSerializer,
    TaskDetailSerializer,
    CollectorListSerializer,
    RetrySerializer,
    CollectorEtlSerializer,
    CollectorEtlStorageSerializer,
    CollectorCreateSerializer,
    CollectorUpdateSerializer,
    CollectorEtlTimeSerializer,
    CollectorDataLinkListSerializer,
    CollectorRegexDebugSerializer,
    ListCollectorsByHostSerializer,
    CleanStashSerializer,
)
from apps.utils.function import ignored


class CollectorViewSet(ModelViewSet):
    """
    采集项
    """

    lookup_field = "collector_config_id"
    filter_fields_exclude = ["collector_config_overlay"]
    model = CollectorConfig
    search_fields = ("collector_config_name", "table_id", "bk_biz_id")
    ordering_fields = ("updated_at", "updated_by")

    def get_permissions(self):
        with ignored(Exception, log_exception=True):
            auth_info = Permission.get_auth_info(self.request)
            # ESQUERY白名单不需要鉴权
            if auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
                return []

        if self.action in ["list_scenarios", "batch_subscription_status"]:
            return []
        if self.action in ["create", "only_create"]:
            return [BusinessActionPermission([ActionEnum.CREATE_COLLECTION])]
        if self.action in [
            "indices_info",
            "retrieve",
            "task_status",
            "task_detail",
            "subscription_status",
            "get_data_link_list",
        ]:
            return [InstanceActionPermission([ActionEnum.VIEW_COLLECTION], ResourceEnum.COLLECTION)]
        if self.action in [
            "update",
            "only_update",
            "destroy",
            "retry",
            "tail",
            "start",
            "stop",
            "etl_preview",
            "etl_time",
            "update_or_create_clean_config",
        ]:
            return [InstanceActionPermission([ActionEnum.MANAGE_COLLECTION], ResourceEnum.COLLECTION)]
        return [ViewBusinessPermission()]

    def get_queryset(self):
        qs = self.model.objects
        if self.request.query_params.get(HAVE_DATA_ID):
            qs = qs.filter(bk_data_id__isnull=False)
        if self.request.query_params.get(BKDATA_OPEN) and settings.FEATURE_TOGGLE["scenario_bkdata"] == "off":
            qs = qs.filter(Q(etl_config=EtlConfig.BK_LOG_TEXT) | Q(etl_config__isnull=True))
        return qs.all()

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "subscription_run": RunSubscriptionSerializer,
            "batch_subscription_status": BatchSubscriptionStatusSerializer,
            "task_status": TaskStatusSerializer,
            "task_detail": TaskDetailSerializer,
            "list": CollectorListSerializer,
            "retry": RetrySerializer,
            "list_collectors": CollectorListSerializer,
        }
        return action_serializer_map.get(self.action, serializers.Serializer)

    @list_route(methods=["GET"], url_path="scenarios")
    def list_scenarios(self, request, *args, **kwargs):
        """
        @api {get} /databus/collector/scenarios/ 01_采集类型
        @apiName list_collector_scenarios
        @apiGroup 10_Collector
        @apiDescription 显示采集类型及支持的个定义配置
        @apiSuccess {Int} collector_scenario_id 采集类型ID
        @apiSuccess {String} collector_scenario_name 采集类型名称
        @apiSuccess {Bool} is_active 是否可用（如果不可用，则在前端只可以显示，但不能选择）
        @apiSuccess {Json} config 采集类型配置（与创建采集项的params对应）
        @apiSuccess {String} config.field_type 字段类型
        @apiSuccess {String} config.field_name 字段名称
        @apiSuccess {String} config.field_alias 别名
        @apiSuccess {Bool} config.required 是否必填
        @apiSuccess {Json} config.option 字段特殊配置
        @apiSuccess {List} config.conditions.option.choices 支持的选项
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "collector_scenario_id": "row",
                    "collector_scenario_name": "行日志",
                    "is_active": true,
                    "config": {
                        "paths": {
                            "field_type": "list",
                            "field_name": "paths",
                            "field_alias": "日志路径",
                            "required": true,
                            "option": {}
                        },
                        "conditions": {
                            "field_type": "dict",
                            "field_name": "conditions",
                            "field_alias": "过滤方式",
                            "required": false,
                            "option": {
                                "choices": ["match", "separator"]
                            }
                        }
                    }
                }
            ],
            "result": true
        }
        """
        scenarios = [
            {
                "collector_scenario_id": "row",
                "collector_scenario_name": _("行日志"),
                "is_active": True,
                "config": {
                    "paths": {
                        "field_type": "list",
                        "field_name": "paths",
                        "field_alias": _("日志路径"),
                        "required": True,
                        "option": {},
                    },
                    "conditions": {
                        "field_type": "dict",
                        "field_name": "conditions",
                        "field_alias": _("过滤方式"),
                        "required": False,
                        "option": {"choices": ["match", "separator"]},
                    },
                },
            },
            {
                "collector_scenario_id": "section",
                "collector_scenario_name": _("段日志"),
                "is_active": False,
                "config": {
                    "paths": {
                        "field_type": "list",
                        "field_name": "paths",
                        "field_alias": _("日志路径"),
                        "required": True,
                        "option": {},
                    },
                    "conditions": {
                        "field_type": "dict",
                        "field_name": "conditions",
                        "field_alias": _("过滤方式"),
                        "required": False,
                        "option": {"choices": ["match"]},
                    },
                },
            },
        ]
        return Response(scenarios)

    @insert_permission_field(
        id_field=lambda d: d["collector_config_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    @insert_permission_field(
        id_field=lambda d: d["index_set_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.SEARCH_LOG],
        resource_meta=ResourceEnum.INDICES,
    )
    def list(self, request, *args, **kwargs):
        """
        @api {get} /databus/collectors/?page=$page&pagesize=$pagesize&keyword=$keyword&bk_biz_id=$bk_biz_id 11_采集项-列表
        @apiName list_collector
        @apiGroup 10_Collector
        @apiDescription 采集项列表，运行状态通过异步接口获取，
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {Int} page 页数
        @apiParam {Int} pagesize 每页数量
        @apiParam {String} keyword 搜索关键字
        @apiSuccess {Int} count 总数
        @apiSuccess {Int} total_page 总共页数
        @apiSuccess {Array} results 返回结果
        @apiSuccess {Int} results.collector_config_id 采集项ID
        @apiSuccess {Int} results.collector_config_name 采集项名称
        @apiSuccess {String} results.collector_scenario_id 类型id
        @apiSuccess {String} results.collector_scenario_name 类型名称
        @apiSuccess {String} results.category_id 分类ID
        @apiSuccess {String} results.category_name 分类名称
        @apiSuccess {Bool} results.is_active 是否可用
        @apiSuccess {String} results.description 描述
        @apiSuccess {String} results.created_by 创建人
        @apiSuccess {String} results.created_at 创建时间
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": {
                "count": 10,
                "total_page": 1,
                "results": [{
                    "collector_config_id": 1,
                    "collector_config_name": "采集项名称",
                    "collector_scenario_id": "line",
                    "collector_scenario_name": "行日志",
                    "category_id": "host_os",
                    "category_name": "主机-操作系统",
                    "is_active": true,
                    "created_by": "小星星"
                    "created_at": "2019-06-12 12:00:00"
                }]
            },
            "result": true
        }
        """
        # 强制前端必须传分页参数

        if not request.GET.get("page") or not request.GET.get("pagesize"):
            raise ValidationError(_("分页参数不能为空"))
        response = super().list(request, *args, **kwargs)
        response.data["list"] = CollectorHandler.add_cluster_info(response.data["list"])

        return response

    def retrieve(self, request, *args, collector_config_id=None, **kwargs):
        """
        @api {get} /databus/collectors/$collector_config_id/ 12_采集项-详情
        @apiName retrieve_collector
        @apiGroup 10_Collector
        @apiParam {Int} collector_config_id 采集项ID
        @apiSuccess {String} collector_scenario_id 日志类型 可选字段`row, section, win_event`
        @apiSuccess {String} collector_scenario_name 日志类型名称
        @apiSuccess {String} collector_config_name 采集项名称
        @apiSuccess {String} category_id 数据分类
        @apiSuccess {String} category_name 数据分类显示名称
        @apiSuccess {Array[Dict]} target 已选目标
        @apiSuccess {Array(json)}  target_nodes 采集目标
        @apiSuccess {Int} target_nodes.id 服务实例id
        @apiSuccess {Int} target_nodes.bk_inst_id 节点实例id
        @apiSuccess {String} target_nodes.bk_obj_id 节点对象id
        @apiSuccess {String} target_nodes.ip 主机实例ip
        @apiSuccess {Int} target_nodes.bk_cloud_id 蓝鲸云主机id
        @apiSuccess {Int} target_nodes.bk_supplier_id 支撑id
        @apiSuccess {String} data_encoding 日志字符集
        @apiSuccess {String} bk_data_id META-采集项ID
        @apiSuccess {String} bk_data_name META-采集项名称
        @apiSuccess {String} description 备注说明
        @apiSuccess {json} params 日志信息
        @apiSuccess {Array} params.paths 日志路径
        @apiSuccess {json} params.conditions 过滤方式
        @apiSuccess {String} params.conditions.type 过滤方式类型 可选字段 `match, separator`
        @apiSuccess {String} params.conditions.match_type 过滤方式 可选字段 `include, exclude`
        @apiSuccess {String} params.conditions.match_content 过滤内容
        @apiSuccess {String} params.conditions.separator 分隔符
        @apiSuccess {Json} params.conditions.separator_filters 分隔符过滤条件
        @apiSuccess {String} etl_config 字段提取方式
        @apiSuccess {Object} etl_params 字段提取参数
        @apiSuccess {String} etl_params.separator 分隔符
        @apiSuccess {String} etl_params.separator_regexp 正则-字段提取正则
        @apiSuccess {Bool} etl_params.retain_original_text 是否保留原文
        @apiSuccess {list} fields 字段列表
        @apiSuccess {Int} fields.field_index 字段顺序（分隔符显示）
        @apiSuccess {String} fields.field_name 字段名称
        @apiSuccess {String} [fields.alias_name] 别名
        @apiSuccess {String} fields.field_type 字段类型
        @apiSuccess {String} fields.description 字段说明
        @apiSuccess {Bool} fields.is_analyzed 是否分词
        @apiSuccess {Bool} fields.is_dimension 是否维度
        @apiSuccess {Bool} fields.is_time 是否时间字段
        @apiSuccess {Bool} fields.is_built_in 是否标准字段
        @apiSuccess {Bool} fields.is_delete 是否删除
        @apiSuccess {Json} [fields.option] 字段配置
        @apiSuccess {Int} fields.option.time_zone 时间
        @apiSuccess {String} fields.option.time_format 时间格式
        @apiSuccess {Int} storage_cluster_id 存储集群ID
        @apiSuccess {String} storage_cluster_name 存储集群名称
        @apiSuccess {Int} retention 过期天数
        @apiSuccess {String} table_id_prefix 存储索引名前辍
        @apiSuccess {String} table_id 存储索引名
        @apiSuccess {String} created_at 创建时间
        @apiSuccess {String} created_by 创建人
        @apiSuccess {String} updated_at 更新时间
        @apiSuccess {String} updated_by 更新人
        @apiSuccess {String} itsm_ticket_status 采集ITSM状态
        @apiSuccess {String} itsm_ticket_status_display 采集ITSM状态显示名称
        @apiSuccess {String} ticket_url 采集ITSM流程地址
        @apiSuccess {String} index_split_rule 分裂规则
        @apiSuccessExample {json} 成功返回:
        {
            "collector_scenario_id": "row",
            "collector_scenario_name": "行日志",
            "collector_config_name": "我叫access的",
            "category_id": "os",
            "category_name": "主机-操作系统",
            "target_nodes": [
                {
                   "id": 12
                },
                {
                    "bk_inst_id": 33,
                    "bk_obj_id": "module",
                },
                {
                    "ip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_supplier_id": 0,
                }
            ],
            "data_encoding": "utf-8",
            "bk_data_name": "存储索引名",
            "description": "这是一个描述",
            "params": {
                "paths": ["/tmp/health_check.log"],
                "conditions": {
                    "type": "match",
                    "match_type": "include",
                    "match_content": "delete",
                    "separator": "|",
                    "separator_filters": [
                        {
                            "fieldindex": 2,
                            "word": "32",
                            "op": "="
                        }
                    ]
                }
            },
            "etl_config": "bk_log_text",
            "etl_params": {
                "separator_regexp": "[a-z][0-9]",
                "separator": "|",
                "retain_original_text": true
            },
            "fields": [
              {
                "field_index": 1,
                "field_name": "user",
                "alias_name": "",
                "field_type": "string",
                "description": "字段描述",
                "is_analyzed": true,
                "is_dimension": false,
                "is_time": false,
                "is_built_in": false,
                "is_delete": false,
              },
              {
                "field_index": 2,
                "field_name": "",
                "alias_name": "",
                "field_type": "string",
                "description": "",
                "is_analyzed": true,
                "is_dimension": false,
                "is_time": false,
                "is_built_in": false,
                "is_delete": true,
              },
              {
                "field_index": 3,
                "field_name": "report_time",
                "alias_name": "",
                "field_type": "string",
                "description": "字段描述",
                "is_analyzed": false,
                "is_dimension": true,
                "is_time": true,
                "is_built_in": false,
                "is_delete": false,
                "option": {
                  "time_zone": 8,
                  "time_format": "yyyy-MM-dd HH:mm:ss"
                }
            ],
            "table_id_prefix": "2_bklog_",
            "table_id": "search",
            "storage_cluster_id": 3,
            "storage_cluster_name": "存储集群名称",
            "retention": 1,
            "itsm_ticket_status": "success_apply",
            "itsm_ticket_status_display": "采集接入完成",
            "ticket_url": "",
            "index_split_rule": ""
        }
        """
        return Response(CollectorHandler(collector_config_id=collector_config_id).retrieve())

    def create(self, request, *args, **kwargs):
        """
        @api {post} /databus/collectors/ 13_采集项-创建
        @apiName create_collector
        @apiDescription 创建采集项
        @apiGroup 10_Collector
        @apiParam {Int} bk_biz_id 所属业务
        @apiParam {String} collector_scenario_id 日志类型 可选字段`row, section, win_event`
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {Int} data_link_id 数据链路id
        @apiParam {String} category_id 数据分类 GlobalsConfig.category读取
        @apiParam {String}  target_object_type 对象类型，目前固定为 HOST
        @apiParam {String}  target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array[Dict]} target 已选目标
        @apiParam {Array(json)}  target_nodes 采集目标
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
                multiline_pattern: ""
                multiline_max_lines: 10
                multiline_timeout: 60
            },
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
        data = self.params_valid(CollectorCreateSerializer)
        return Response(CollectorHandler().update_or_create(data))

    def update(self, request, *args, collector_config_id=None, **kwargs):
        """
        @api {put} /databus/collectors/$collector_config_id/ 14_采集项-更新
        @apiName update_collector
        @apiGroup 10_Collector
        @apiDescription 更新采集项
        @apiParam {Int} collector_config_id 采集项ID
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {String}  target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array(json)}  target_nodes 采集目标
        @apiParam {Int} target_nodes.id 服务实例id
        @apiParam {Int} target_nodes.bk_inst_id 节点实例id
        @apiParam {String} target_nodes.bk_obj_id 节点对象id
        @apiParam {String} target_nodes.ip 主机实例ip
        @apiParam {Int} target_nodes.bk_cloud_id 蓝鲸云主机id
        @apiParam {Int} target_nodes.bk_supplier_id 支撑id
        @apiParam {String} data_encoding 日志字符集 可选字段`UTF-8, GBK`
        @apiParam {String} description 备注说明
        @apiParam {json} params 日志信息
        @apiParam {Array} params.paths 日志路径
        @apiParam {json} params.conditions 过滤方式
        @apiParam {String} params.conditions.type 过滤方式类型 可选字段 `match, separator`
        @apiParam {String} params.conditions.match_type 过滤方式 可选字段 `include, exclude`
        @apiParam {String} params.conditions.match_content 过滤内容
        @apiParam {String} params.conditions.separator 分隔符
        @apiParam {String} params.conditions.separator_filters 分隔符过滤条件
        @apiParamExample {json} 请求样例:
        {
            "collector_config_name": "采集项名称",
            "collector_config_name_en": "采集项英文名",
            "data_link_id": 1
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
                            "op": "="
                        }
                    ]
                }
            },
        }
        @apiSuccess {Int} collector_config_id 采集配置ID
        @apiSuccess {Int} collector_config_name 采集配置名称
        @apiSuccess {Int} bk_data_id 采集链路data_id
        @apiSuccess {Int} subscription_id 节点管理订阅ID
        @apiSuccess {String} task_id_list 最后部署任务
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
                "collector_config_id": 1,
                "collector_config_name": "采集项名称",
                "bk_data_id": 2001,
                "subscription_id": "订阅ID",
                "task_id_list": "1,2,3"
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorUpdateSerializer)
        return Response(CollectorHandler(collector_config_id=collector_config_id).update_or_create(data))

    def destroy(self, request, *args, collector_config_id=None, **kwargs):
        """
        @api {delete} /databus/collectors/$collector_config_id/ 23_采集项-删除
        @apiName delete_collector
        @apiGroup 10_Collector
        @apiDescription 删除采集项
        @apiParam {Int} collector_config_id 采集项ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "success",
            "result": true
        }
        """
        return Response(CollectorHandler(collector_config_id=collector_config_id).destroy())

    @list_route(methods=["GET"], url_path="batch_subscription_status")
    def batch_subscription_status(self, request):
        """
        @api {get} /databus/collectors/batch_subscription_status/ 15_采集项-批量获取采集项订阅状态
        @apiName collector_batch_subscription_status
        @apiGroup 10_Collector
        @apiParam {String} collector_id_list 采集项ID列表（用半角,分隔）
        @apiSuccess {Int} collector_id 采集项ID
        @apiSuccess {Int} subscription_id 订阅ID
        @apiSuccess {String} status 订阅状态
        @apiSuccess {String} status_name 订阅状态名称
        @apiSuccess {String} total 主机总数
        @apiSuccess {String} success 成功数
        @apiSuccess {String} failed 失败数
        @apiSuccess {String} pending 执行中
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data":[
                {
                    "collector_id": 1,
                    "subscription_id": 1,
                    "status": "FAILED",
                    "status_name": "部分失败",
                    "total": 11,
                    "success": 11,
                    "failed": 0,
                    "pending": 0
                }
            ]
        }
        """
        data = self.validated_data
        collector_id_list = data.get("collector_id_list").split(",")
        return Response(CollectorHandler().get_subscription_status_by_list(collector_id_list, multi_flag=True))

    @detail_route(methods=["GET"], url_path="task_status")
    def task_status(self, request, collector_config_id=None):
        """
        @api {get} /databus/collectors/$collector_id/task_status/?task_id_list=$task_id_list 16_任务执行情况
        @apiName collector_task_status
        @apiGroup 10_Collector
        @apiParam {String} task_id_list 最后部署任务的ID，用半角,分隔（重试时获取的task_id）
        @apiSuccess {Json} contents 订阅内容
        @apiSuccess {String} contents.is_label 是否显示标签
        @apiSuccess {String} contents.label_name 标签内容
        @apiSuccess {String} contents.bk_obj_name 集群名称
        @apiSuccess {List} contents.child 主机实例列表
        @apiSuccess {String} contents.child.status 实例订阅状态 (FAILED:失败； SUCCESS：成功； PENDING：执行中)
        @apiSuccess {String} contents.child.ip 实例IP
        @apiSuccess {String} contents.child.bk_cloud_id 云区域ID
        @apiSuccess {String} contents.child.instance_name 实例名称
        @apiSuccess {String} contents.child.instance_id 实例ID
        @apiSuccess {String} contents.child.bk_supplier_id 供应商ID
        @apiSuccess {String} contents.child.create_time 最新更新时间
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data":{
                "contents":[
                    {
                        "is_label":false,
                        "label_name":"",
                        "bk_obj_name":"集群",
                        "node_path":"蓝鲸/test1/PaaS平台",
                        "bk_obj_id":"set",
                        "child":[
                            {
                                "status":"FAILED",
                                "ip":"127.0.0.1",
                                "bk_cloud_id":0,
                                "log":"[bkmonitorbeat] 下发插件配置-重载插件进程",
                                "instance_name":"127.0.0.1",
                                "task_id":24456,
                                "instance_id":"host|instance|host|127.0.0.1-0-0",
                                "steps":{
                                    "bkmonitorbeat":"INSTALL",
                                    "sunzhiyu_label4":"INSTALL"
                                },
                                "bk_supplier_id":0,
                                "create_time": "2019-08-24T18:47:27",
                            },
                            {
                                "status":"FAILED",
                                "ip":"127.0.0.1",
                                "bk_cloud_id":0,
                                "log":"[bkmonitorbeat] 下发插件配置-重载插件进程",
                                "instance_name":"127.0.0.1",
                                "task_id":24456,
                                "instance_id":"host|instance|host|127.0.0.1-0-0",
                                "steps":{
                                    "bkmonitorbeat":"INSTALL",
                                    "sunzhiyu_label4":"INSTALL"
                                },
                                "bk_supplier_id":0,
                                "create_time": "2019-08-24T18:47:27",
                            }
                        ],
                        "bk_inst_id":6,
                        "bk_inst_name":"PaaS平台"
                    }
                ]
            },
            "result":true
        }
        """
        data = self.validated_data
        task_id_list = data.get("task_id_list").split(",")
        return Response(CollectorHandler(collector_config_id).get_subscription_task_status(task_id_list))

    @detail_route(methods=["GET"], url_path="task_detail")
    def task_detail(self, request, collector_config_id=None):
        """
        @api {get} /databus/collectors/$collector_id/task_detail/?xx 17_任务执行详情【前端在失败时点击"更多"调用】
        @apiName collector_task_detail
        @apiGroup 10_Collector
        @apiParam {String} collector_id 采集项ID
        @apiParam {String} instance_id 实例ID
        @apiParam {String} [task_id] 任务id, 如果不传task_id，则取最近一次任务的执行情况
        @apiSuccess {String} log_detail 内容详情，用于前端展示
        @apiSuccess {Json} log_result 原始日志, 仅用于调试
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data":{
                "log_detail": "错误的详细内容，根据log_result拼装而成",
                "log_result": {
                    "instance_id": "service|instance|service|1",
                    "pipeline_id": "f89825d5fa8c324bb1da5cd80e6c8704",
                    "create_time": "2019-08-24T18:47:27.848888",
                    "status": "FINISHED",
                    "task_id": 2827,
                    "finish_time": "2019-08-24 18:47:58",
                    "steps": []
                }
            },
            "result":true
        }
        """
        data = self.validated_data
        return Response(
            CollectorHandler(collector_config_id).get_subscription_task_detail(
                data["instance_id"], task_id=data.get("task_id")
            )
        )

    @detail_route(methods=["POST"], url_path="retry")
    def retry(self, request, collector_config_id=None):
        """
        @api {post} /databus/collectors/$collector_config_id/retry/ 18_任务重试
        @apiName collector_subscription_run
        @apiGroup 10_Collector
        @apiDescription 订阅触发
        @apiParam {Array(json)} target_nodes 采集目标
        @apiParam {String} target_nodes.ip 主机实例ip
        @apiParam {int} target_nodes.bk_cloud_id 蓝鲸云区域id
        @apiParam {int} target_nodes.bk_supplier_id 供应商id
        @apiSuccess {int} task_id 任务ID（在采集下发界面，需要将task_id合并到）
        @apiParamExample {json} 请求样例:
        {
            "target_nodes": [
                {
                    "ip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_supplier_id":0,
                },
                {
                    "ip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_supplier_id":0,
                }
            ],
        }
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [ "24484", "24702"],
            "result": true
        }
        """
        data = self.validated_data
        return Response(
            CollectorHandler(collector_config_id=collector_config_id).retry_target_nodes(data["target_nodes"])
        )

    @detail_route(methods=["GET"], url_path="subscription_status")
    def subscription_status(self, request, collector_config_id=None):
        """
        @api {get} /databus/collectors/$collector_config_id/subscription_status/ 19_采集详情-订阅状态
        @apiName collector_subscription_status
        @apiGroup 10_Collector
        @apiParam {Int} collector_id 采集项ID
        @apiSuccess {Json} contents 订阅内容
        @apiSuccess {String} contents.is_label 是否显示标签
        @apiSuccess {String} contents.label_name 标签内容
        @apiSuccess {String} contents.bk_obj_name 集群名称
        @apiSuccess {List} contents.child 主机实例列表
        @apiSuccess {String} contents.child.status 实例订阅状态 (FAILED:失败； SUCCESS：成功； PENDING：执行中)
        @apiSuccess {String} contents.child.ip 实例IP
        @apiSuccess {String} contents.child.bk_cloud_id 云区域ID
        @apiSuccess {String} contents.child.instance_name 实例名称
        @apiSuccess {String} contents.child.instance_id 实例ID
        @apiSuccess {String} contents.child.bk_supplier_id 供应商ID
        @apiSuccess {String} contents.child.create_time 最新更新时间
        @apiSuccessExample {json} 成功返回:
        {
            "message":"",
            "code":0,
            "data":{
                "contents":[
                    {
                        "is_label":false,
                        "label_name":"",
                        "bk_obj_name":"集群",
                        "node_path":"蓝鲸/test1/PaaS平台",
                        "bk_obj_id":"set",
                        "child":[
                            {
                                "status":"FAILED",
                                "ip":"127.0.0.1",
                                "bk_cloud_id":0,
                                "instance_name":"127.0.0.1",
                                "plugin_version":"1.1",
                                "instance_id":"host|instance|host|127.0.0.1-0-0",
                                "bk_supplier_id":0,
                                "create_time": "2019-08-24T18:47:27",
                            },
                            {
                                "status":"FAILED",
                                "ip":"127.0.0.1",
                                "bk_cloud_id":0,
                                "instance_name":"127.0.0.1",
                                "plugin_version":"1.1",
                                "instance_id":"host|instance|host|127.0.0.1-0-0",
                                "bk_supplier_id":0,
                                "create_time": "2019-08-24T18:47:27",
                            }
                        ],
                        "bk_inst_id":6,
                        "bk_inst_name":"PaaS平台"
                    }
                ]
            },
            "result":true
        }
        """
        return Response(CollectorHandler(collector_config_id).get_subscription_status())

    @detail_route(methods=["GET"], url_path="tail")
    def tail(self, request, collector_config_id=None):
        """
        @api {get} /databus/collectors/$collector_config_id/tail/ 20_采集项-数据采样
        @apiName Collector_tail
        @apiGroup 10_Collector
        @apiSuccess {String} data 采集器上报原始日志内容（批量上报显示最新采集的内容）
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [
                 {
                    "_bizid_": 0,
                    "_cloudid_": 0,
                    "_dstdataid_": 2012,
                    "_errorcode_": 0,
                    "_gseindex_": 2069,
                    "_path_": "/tmp/bkc.log",
                    "_private_": {},
                    "_server_": "127.0.0.1",
                    "_srcdataid_": 2012,
                    "_time_": "2019-08-07 10:15:03",
                    "_type_": 0,
                    "_utctime_": "2019-08-07 02:15:03",
                    "_value_": [
                        "[127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch",
                        "这是mock数据这是mock数据这是mock数据这是mock数据这是mock数据这是mock数据这是mock数据这是mock数据"
                    ],
                    "data": "127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch",
                    "_worldid_": -1
                },
                {
                    "_bizid_": 0,
                    "_cloudid_": 0,
                    "_dstdataid_": 2012,
                    "_errorcode_": 0,
                    "_gseindex_": 2069,
                    "_path_": "/tmp/bkc.log",
                    "_private_": {},
                    "_server_": "127.0.0.1",
                    "_srcdataid_": 2012,
                    "_time_": "2019-08-07 10:15:03",
                    "_type_": 0,
                    "_utctime_": "2019-08-07 02:15:03",
                    "_value_": [
                        "[127.0.0.1]20190807-101502 INFO|38|ok-_watch-watch_tsdbproxy-main tsdbproxy is running",
                        "这是测试数据这是测试数据这是测试数据这是测试数据这是测试数据这是测试数据这是测试数据这是测试数据"
                    ],
                    "data": "127.0.0.1]20190807-101502 INFO|14|log-main /data/bkee/bin/process_watch",
                    "_worldid_": -1
               }
            ],
            "result": true
        }
        """
        return Response(CollectorHandler(collector_config_id=collector_config_id).tail())

    @detail_route(methods=["POST"], url_path="start")
    def start(self, request, collector_config_id=None):
        """
        @api {post} /databus/collectors/$collector_config_id/start/ 21_采集项-启动
        @apiName start_collector
        @apiGroup 10_Collector
        @apiDescription 启动采集项
        @apiParam {Int} collector_config_id 采集项ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        return Response(CollectorHandler(collector_config_id=collector_config_id).start())

    @detail_route(methods=["POST"], url_path="stop")
    def stop(self, request, collector_config_id=None):
        """
        @api {post} /databus/collectors/$collector_config_id/stop/ 22_采集项-停止
        @apiName stop_collector
        @apiGroup 10_Collector
        @apiDescription 停止采集项
        @apiParam {Int} collector_config_id 采集项ID
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": "",
            "result": true
        }
        """
        return Response(CollectorHandler(collector_config_id=collector_config_id).stop())

    @detail_route(methods=["POST"])
    def etl_preview(self, request, collector_config_id=None):
        """
        @api {post} /databus/collectors/${collector_config_id}/etl_preview/ 31_字段提取-预览提取结果
        @apiName collector_etl_preview
        @apiDescription 字段提取-预览提取结果
        @apiGroup 10_Collector
        @apiParam {String} etl_config 清洗类型（格式化方式）
        @apiParam {Object} etl_params 清洗配置，不同的清洗类型的参数有所不同
        @apiParam {String} etl_params.separator 分隔符，当etl_config=="bk_log_delimiter"时需要传递
        @apiParam {String} etl_params.separator_regexp 正则表达式，当etl_config=="bk_log_regexp"时需要传递
        @apiParam {String} data 日志内容

        @apiSuccess {list} fields 字段列表
        @apiSuccess {Int} fields.field_index 字段顺序
        @apiSuccess {String} fields.field_name 字段名称 (分隔符默认为空)
        @apiSuccess {String} fields.value 值
        @apiParamExample {json} 请求样例:
        {
            "etl_config": "bk_log_text | bk_log_json | bk_log_regexp | bk_log_delimiter",
            "etl_params": {
                "separator": "|"
            },
            "data": "a|b|c"
        }
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
                "fields": [
                    {
                        "field_index": 1,
                        "field_name": "",
                        "value": "a"
                    },
                    {
                        "field_index": 2,
                        "field_name": "",
                        "value": "b"
                    },
                    {
                        "field_index": 3,
                        "field_name": "",
                        "value": "c"
                    }
                ]
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorEtlSerializer)
        return Response(EtlHandler.etl_preview(**data))

    @detail_route(methods=["POST"])
    def etl_time(self, request, collector_config_id=None):
        """
        @api {post} /databus/collectors/${collector_config_id}/etl_time/ 32_字段提取-时间格式解析
        @apiName collector_etl_time
        @apiDescription 字段提取-时间格式解析
        @apiGroup 10_Collector
        @apiParam {String} time_format 时间格式
        @apiParam {String} data 用户时间字段

        @apiSuccess {String} epoch_millis 转换成ES存储格式
        @apiParamExample {json} 请求样例:
        {
            "time_format": "yyyy-MM-dd HH:mm:ss",
            "time_zone": 8,
            "data": "2006-01-0 15:04:05"
        }
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
                "epoch_millis": 1136185445000,
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorEtlTimeSerializer)
        return Response(EtlHandler(collector_config_id=collector_config_id).etl_time(**data))

    @detail_route(methods=["POST"])
    def update_or_create_clean_config(self, request, collector_config_id=None):
        """
        @api {post} /databus/collectors/${collector_config_id}/update_or_create_clean_config/ 33_字段提取-更新或创建清洗配置
        @apiName create_collector_clean_config
        @apiDescription 更新或创建清洗配置
        @apiGroup 10_Collector
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
        @apiParam {list} view_roles 查看权限
        @apiParamExample {json} 请求样例:
        {
            "table_id": "xxx",
            "etl_config": "bk_log_text | bk_log_json | bk_log_regexp | bk_log_delimiter",
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
            ],
            "storage_cluster_id": 3,
            "retention": 1,
            "view_roles": [1,2]
        }
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorEtlStorageSerializer)
        return Response(EtlHandler(collector_config_id=collector_config_id).update_or_create(**data))

    @detail_route(methods=["GET"], url_path="get_data_link_list")
    def get_data_link_list(self, request):
        """
        @api {get} /databus/collectors/get_data_link_list/ 获取数据链路列表
        @apiName get_data_link_list
        @apiGroup 10_Collector
        @apiSuccess {Int} data.data_link_id 数据链路id
        @apiSuccess {Int} data.link_group_name 链路集群名称
        @apiSuccess {Int} data.bk_biz_id 链路允许的业务id
        @apiSuccess {Int} data.kafka_cluster_id kafka集群id
        @apiSuccess {Int} data.transfer_cluster_id transfer集群id
        @apiSuccess {list} data.es_cluster_ids es集群id
        @apiSuccess {Bool} data.is_active 是否启用
        @apiSuccess {String} data.description 描述
        @apiSuccessExample {json} 成功返回:
        {
            "message": "",
            "code": 0,
            "data": [{
                "data_link_id": 1,
                "link_group_name": "默认",
                "bk_biz_id": 0,
                "kafka_cluster_id": "kafka_01",
                "transfer_cluster_id": "transfer_01",
                "es_cluster_id": ["es_01", "es_02"],
                "is_active": true,
                "description": ""
            }],
            "result": true
        }
        """
        data = self.params_valid(CollectorDataLinkListSerializer)
        return Response(DataLinkHandler().list(data))

    @detail_route(methods=["POST"], url_path="regex_debug")
    def regex_debug(self, request, collector_config_id=None):
        """
        @api {get} /databus/collectors/${collector_config_id}/regex_debug/ 采集配置-行首正则调试
        @apiName collector_regex_debug
        @apiDescription 采集配置-行首正则调试
        @apiGroup 10_Collector
        @apiParam {String} log_sample 日志样例
        @apiParam {String} multiline_pattern 行首正则表达式
        @apiParamExample {json} 请求样例:
        {
            "log_sample": "xxx",
            "multiline_pattern": "xxx"
        }
        @apiSuccessExample {json} 成功返回:
        {

            "message": "",
            "code": 0,
            "data": {
                "log_sample": "xxx",
                "multiline_pattern": "xxx",
                "match_lines": 3
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorRegexDebugSerializer)
        return Response(CollectorHandler().regex_debug(data))

    @list_route(methods=["post"])
    def only_create(self, request):
        """
        @api {post} /databus/collectors/only_create 采集项-只创建配置
        @apiName only_create_collector_model
        @apiDescription 创建采集项
        @apiGroup 10_Collector
        @apiParam {Int} bk_biz_id 所属业务
        @apiParam {String} collector_scenario_id 日志类型 可选字段`row, section, win_event`
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {Int} data_link_id 数据链路id
        @apiParam {String} category_id 数据分类 GlobalsConfig.category读取
        @apiParam {String}  target_object_type 对象类型，目前固定为 HOST
        @apiParam {String}  target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array[Dict]} target 已选目标
        @apiParam {Array(json)}  target_nodes 采集目标
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
                multiline_pattern: ""
                multiline_max_lines: 10
                multiline_timeout: 60
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
                "collector_config_name": "采集项名称",
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorCreateSerializer)
        return Response(CollectorHandler().only_create_or_update_model(data))

    @detail_route(methods=["post"])
    def only_update(self, request, *args, collector_config_id=None, **kwargs):
        """
        @api {post} /databus/collectors/$collector_config_id/only_update 采集项-只更新配置
        @apiName only_update_collector_model
        @apiDescription 更新采集项
        @apiGroup 10_Collector
        @apiParam {Int} bk_biz_id 所属业务
        @apiParam {String} collector_scenario_id 日志类型 可选字段`row, section, win_event`
        @apiParam {String} collector_config_name 采集项名称
        @apiParam {Int} data_link_id 数据链路id
        @apiParam {String} category_id 数据分类 GlobalsConfig.category读取
        @apiParam {String}  target_object_type 对象类型，目前固定为 HOST
        @apiParam {String}  target_node_type 节点类型 动态：TOPO  静态：INSTANCE
        @apiParam {Array[Dict]} target 已选目标
        @apiParam {Array(json)}  target_nodes 采集目标
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
                multiline_pattern: ""
                multiline_max_lines: 10
                multiline_timeout: 60
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
                "collector_config_name": "采集项名称",
            },
            "result": true
        }
        """
        data = self.params_valid(CollectorUpdateSerializer)
        return Response(CollectorHandler(collector_config_id=collector_config_id).only_create_or_update_model(data))

    @detail_route(methods=["GET"], url_path="indices_info")
    def indices_info(self, request, *args, collector_config_id, **kwargs):
        """
        @api {post} /databus/collectors/$collector_config_id/indices_info 采集项-物理索引
        @apiName indices_info
        @apiDescription 采集项物理索引信息
        @apiGroup 10_Collector
        @apiSuccess {String} health 索引健康状态 red green yellow
        @apiSuccess {String} status 索引状态
        @apiSuccess {String} pri 主分片数量
        @apiSuccess {String} rep 副本数量
        @apiSuccess {String} docs.count 文档数量
        @apiSuccess {String} docs.deleted 删除文档数量
        @apiSuccess {String} store.size 储存大小 Byte
        @apiSuccess {String} pri.store.size 主分片储存大小 Byte
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                "health": "green",
                "status": "open",
                "index": "215_bklog_local_test_2020",
                "uuid": "MdsmaswLQeOfo_ql1LLQdg",
                "pri": "5",
                "rep": "1",
                "docs.count": "0",
                "docs.deleted": "0",
                "store.size": "2610",
                "pri.store.size": "1305"
            }
            ],
            "code": 0,
            "message": ""
        }
        """
        return Response(CollectorHandler(collector_config_id).indices_info())

    @list_route(methods=["GET"])
    def list_collectors_by_host(self, request):
        """
        @api {GET} /databus/collectors/list_collectors_by_host/ 获取主机采集项列表
        @apiName databus_collectors_list_collectors_by_host
        @apiGroup 10_Collector
        @apiParam {String} [bk_host_innerip] 内网IP
        @apiParam {Number} [bk_cloud_id] 云区域ID
        @apiParam {Number} [bk_host_id] CMDB主机ID
        @apiParam {Number} [bk_biz_id] 业务ID
        @apiSuccessExample {json} 成功返回:
        [
            {
                collector_config_id: 817,
                collector_config_name: "采集项名称",
                collector_scenario_id: 接入场景，
                index_set_id: 索引集ID，
                description： 描述
            }
        ]
        """
        data = self.params_valid(ListCollectorsByHostSerializer)
        return Response(CollectorHandler().list_collectors_by_host(data))

    @detail_route(methods=["GET"])
    def clean_stash(self, request, *args, collector_config_id=None, **kwarg):
        """
        @api {GET} /databus/collectors/$collector_config_id/clean_stash 获取采集项清洗缓存
        @apiName databus_collectors_clean_stash
        @apiGroup 10_Collector
        @apiSuccessExample {json} 成功返回(有数据)
        {
            "result":true,
            "data":{
                "collector_config_id":1,
                "clean_type":"bk_log_text",
                "bk_biz_id": 0,
                "etl_params":{
                    "retain_original_text":true,
                    "separator":" "
                },
                "etl_fields":[
                    {
                        "field_name":"user",
                        "alias_name":"",
                        "field_type":"long",
                        "description":"字段描述",
                        "is_analyzed":true,
                        "is_dimension":false,
                        "is_time":false,
                        "is_delete":false
                    },
                    {
                        "field_name":"report_time",
                        "alias_name":"",
                        "field_type":"string",
                        "description":"字段描述",
                        "tag":"metric",
                        "is_analyzed":false,
                        "is_dimension":false,
                        "is_time":true,
                        "is_delete":false,
                        "option":{
                            "time_zone":8,
                            "time_format":"yyyy-MM-dd HH:mm:ss"
                        }
                    }
                ]
            },
            "code":0,
            "message":""
        }
        @apiSuccessExample {json} 成功返回(空)
        {
            "result": true,
            "data": null,
            "code": 0,
            "message": ""
        }
        """
        return Response(CollectorHandler(collector_config_id=collector_config_id).get_clean_stash())

    @detail_route(methods=["POST"])
    def create_clean_stash(self, request, *args, collector_config_id=None, **kwarg):
        """
        @api {POST} /databus/collectors/$collector_config_id/create_clean_stash 更新采集项清洗缓存
        @apiName databus_collectors_create_clean_stash
        @apiGroup 10_Collector
        @apiParamExample {json} 成功请求
        {
            "bk_biz_id": 0,
            "clean_type":"bk_log_text",
            "etl_params":{
                "retain_original_text":true,
                "separator":" "
            },
            "etl_fields":[
                {
                    "field_name":"user",
                    "alias_name":"",
                    "field_type":"long",
                    "description":"字段描述",
                    "is_analyzed":true,
                    "is_dimension":false,
                    "is_time":false,
                    "is_delete":false
                },
                {
                    "field_name":"report_time",
                    "alias_name":"",
                    "field_type":"string",
                    "description":"字段描述",
                    "tag":"metric",
                    "is_analyzed":false,
                    "is_dimension":false,
                    "is_time":true,
                    "is_delete":false,
                    "option":{
                        "time_zone":8,
                        "time_format":"yyyy-MM-dd HH:mm:ss"
                    }
                }
            ]
        }
        @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "code": 0,
            "data": {
                "clean_stash_id": 1
            },
            "result": true
        }
        """
        data = self.params_valid(CleanStashSerializer)
        return Response(CollectorHandler(collector_config_id=collector_config_id).create_clean_stash(params=data))

    @insert_permission_field(
        id_field=lambda d: d["collector_config_id"],
        data_field=lambda d: d,
        actions=[ActionEnum.VIEW_COLLECTION, ActionEnum.MANAGE_COLLECTION],
        resource_meta=ResourceEnum.COLLECTION,
    )
    @insert_permission_field(
        id_field=lambda d: d["index_set_id"],
        data_field=lambda d: d,
        actions=[ActionEnum.SEARCH_LOG],
        resource_meta=ResourceEnum.INDICES,
    )
    @list_route(methods=["GET"])
    def list_collectors(self, request, *args, **kwargs):
        """
        @api {get} /databus/collectors/list_collectors/ 34_采集项-获取列表(可不带分页参数)
        @apiName dababus_list_collector
        @apiGroup 10_Collector
        @apiDescription 采集项列表，运行状态通过异步接口获取，可不带分页参数
        @apiParam {Int} bk_biz_id 业务ID
        @apiParam {String} keyword 搜索关键字
        @apiSuccess {Array} results 返回结果
        @apiSuccess {Int} results.collector_config_id 采集项ID
        @apiSuccess {Int} results.collector_config_name 采集项名称
        @apiSuccess {String} results.collector_scenario_id 类型id
        @apiSuccess {String} results.collector_scenario_name 类型名称
        @apiSuccess {String} results.category_id 分类ID
        @apiSuccess {String} results.category_name 分类名称
        @apiSuccess {Bool} results.is_active 是否可用
        @apiSuccess {String} results.description 描述
        @apiSuccess {String} results.created_by 创建人
        @apiSuccess {String} results.created_at 创建时间
        @apiSuccess {Boolean} results.create_clean_able 是否可创建基础清洗
        @apiSuccess {List} results.bkdata_index_set_ids 采集对应的高级清洗索引集id列表
        @apiSuccessExample {json} 成功返回:
        {
        "result": true,
        "data": [
            {
                "collector_config_id": 1,
                "collector_scenario_name": "行日志文件",
                "category_name": "操作系统",
                "target_nodes": [
                    {
                        "bk_inst_id": 2000000992,
                        "bk_obj_id": "module"
                    }
                ],
                "task_id_list": [
                    "3469542"
                ],
                "target_subscription_diff": [],
                "create_clean_able": true,
                "bkdata_index_set_ids": [],
                "created_at": "2021-07-20 12:07:25",
                "created_by": "test",
                "updated_at": "2021-08-02 16:38:26",
                "updated_by": "test",
                "is_deleted": false,
                "deleted_at": null,
                "deleted_by": null,
                "collector_config_name": "test",
                "bk_app_code": "bk_log_search",
                "collector_scenario_id": "row",
                "bk_biz_id": 215,
                "category_id": "os",
                "target_object_type": "HOST",
                "target_node_type": "TOPO",
                "description": "test",
                "is_active": true,
                "data_link_id": 0,
                "bk_data_id": 525452,
                "bk_data_name": null,
                "table_id": "215_bklog.test",
                "etl_config": "bk_log_text",
                "subscription_id": 3420,
                "bkdata_data_id": null,
                "index_set_id": 1,
                "data_encoding": "UTF-8",
                "params": "{}",
                "itsm_ticket_sn": null,
                "itsm_ticket_status": "not_apply",
                "can_use_independent_es_cluster": true,
                "collector_package_count": 10,
                "collector_output_format": null,
                "collector_config_overlay": null,
                "storage_shards_nums": 3,
                "storage_shards_size": 30,
                "storage_replies": 1,
                "bkdata_data_id_sync_times": 0,
                "collector_config_name_en": "test"
            }
        ],
        "code": 0,
        "message": ""
        }
        """
        response = super().list(request, *args, **kwargs)
        response.data = CollectorHandler.add_cluster_info(response.data)
        return response
