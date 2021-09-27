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
import copy
from django.utils.translation import ugettext_lazy as _

from django.utils.module_loading import import_string
from django.conf import settings

from apps.utils import is_match_variate
from apps.api import TransferApi
from apps.exceptions import ValidationError
from apps.log_search.constants import FieldBuiltInEnum, FieldDataTypeEnum
from apps.log_databus.constants import EtlConfig, FIELD_TEMPLATE
from apps.log_databus.models import CollectorConfig
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.exceptions import EtlParseTimeFieldException, HotColdCheckException


class EtlStorage(object):
    """
    清洗入库
    """

    # 子类需重载
    etl_config = None
    separator_node_name = "bk_separator_object"

    @classmethod
    def get_instance(cls, etl_config=None):
        mapping = {
            EtlConfig.BK_LOG_TEXT: "BkLogTextEtlStorage",
            EtlConfig.BK_LOG_JSON: "BkLogJsonEtlStorage",
            EtlConfig.BK_LOG_DELIMITER: "BkLogDelimiterEtlStorage",
            EtlConfig.BK_LOG_REGEXP: "BkLogRegexpEtlStorage",
        }
        try:
            etl_storage = import_string(
                "apps.log_databus.handlers.etl_storage.{}.{}".format(etl_config, mapping.get(etl_config))
            )
            return etl_storage()
        except ImportError as error:
            raise NotImplementedError(f"{etl_config} not implement, error: {error}")

    @classmethod
    def get_etl_config(cls, result_table_config):
        """
        根据RT表配置返回etl_config类型
        """
        separator_node_action = result_table_config.get("option", {}).get("separator_node_action")
        return {
            "regexp": "bk_log_regexp",
            "delimiter": "bk_log_delimiter",
            "json": "bk_log_json",
        }.get(separator_node_action, "bk_log_text")

    def etl_preview(self, data, etl_params) -> list:
        """
        字段提取预览
        :param data: 日志原文
        :param etl_params: 字段提取参数
        :return: 字段列表 list
        """
        raise NotImplementedError("功能暂未实现")

    def get_result_table_config(self, fields, etl_params, built_in_config, es_version="5.X"):
        """
        配置清洗入库策略，需兼容新增、编辑
        """
        raise NotImplementedError("功能暂未实现")

    def get_result_table_fields(self, fields, etl_params, built_in_config, es_version="5.X"):
        """
        META
        """
        # field_list
        field_list = built_in_config.get("fields", [])

        # 是否保留原文
        if etl_params.get("retain_original_text"):
            field_list.append(
                {
                    "field_name": "log",
                    "field_type": "string",
                    "tag": "metric",
                    "alias_name": "data",
                    "description": "original_text",
                    "option": {"es_type": "text", "es_include_in_all": True}
                    if es_version.startswith("5.")
                    else {"es_type": "text"},
                }
            )

        # 默认使用上报时间做为数据时间
        time_field = built_in_config["time_field"]
        built_in_keys = FieldBuiltInEnum.get_choices()

        etl_field_index = 1
        for field in fields:
            # 过滤掉删除的字段
            if field["is_delete"]:
                continue

            # 设置字段的来源与目标存储
            source_field = field["field_name"]
            target_field = field["field_name"]
            if field.get("alias_name") and self.etl_config in [EtlConfig.BK_LOG_JSON]:
                target_field = field["alias_name"]

            if target_field.lower() in built_in_keys:
                raise ValidationError(_("字段不能与标准字段重复") + f":{target_field}")

            if not is_match_variate(target_field):
                raise ValidationError(_("字段名不符合变量规则"))

            # option
            field_option = dict()
            field_option["field_index"] = etl_field_index
            etl_field_index += 1

            # ES_TYPE
            field_option["es_type"] = FieldDataTypeEnum.get_es_field_type(
                field["field_type"], is_analyzed=field["is_analyzed"]
            )

            # ES_INCLUDE_IN_ALL
            if field["is_analyzed"] and es_version.startswith("5."):
                field_option["es_include_in_all"] = True

            # ES_DOC_VALUES
            field_option["es_doc_values"] = field["is_dimension"]

            # REAL_PATH
            field_option["real_path"] = f"{self.separator_node_name}.{source_field}"

            # 时间字段处理
            if field["is_time"]:
                time_field["alias_name"] = source_field
                time_field["option"]["real_path"] = field_option["real_path"]
                time_field["option"]["time_zone"] = field["option"]["time_zone"]
                time_field["option"]["time_format"] = field["option"]["time_format"]
                time_field["option"]["field_index"] = field_option["field_index"]
                # 删除原时间字段配置
                field_option["es_doc_values"] = False

            # 加入字段列表
            field_list.append(
                {
                    "field_name": target_field,
                    "field_type": FieldDataTypeEnum.get_meta_field_type(field_option["es_type"]),
                    "tag": "dimension" if field_option.get("es_doc_values", True) else "metric",
                    "description": field.get("description"),
                    "option": field_option,
                }
            )

        field_list.append(time_field)
        return {"fields": field_list, "time_field": time_field}

    def update_or_create_result_table(
        self,
        collector_config: CollectorConfig,
        table_id: str,
        storage_cluster_id: int,
        retention: int,
        allocation_min_days: int,
        storage_replies: int,
        fields: list = None,
        etl_params: dict = None,
        es_version: str = "5.X",
        hot_warm_config: dict = None,
    ):
        """
        创建或更新结果表
        :param collector_config: 采集项配置
        :param table_id: 结果表ID
        :param storage_cluster_id: 存储集群id
        :param retention: 数据保留时间
        :param allocation_min_days: 执行分配的等待天数
        :param fields: 字段列表
        :param etl_params: 清洗配置
        :param es_version: es
        :param hot_warm_config: 冷热数据配置
        """

        # 时间格式
        date_format = settings.ES_DATE_FORMAT
        # ES-分片数
        if not collector_config.storage_shards_nums:
            collector_config.storage_shards_nums = settings.ES_SHARDS

        # ES-副本数
        collector_config.storage_replies = storage_replies

        # 需要切分的大小阈值，单位（GB）
        if not collector_config.storage_shards_size:
            collector_config.storage_shards_size = settings.ES_SHARDS_SIZE

        slice_size = collector_config.storage_shards_nums * collector_config.storage_shards_size
        # index分片时间间隔，单位（分钟）
        slice_gap = settings.ES_SLICE_GAP

        # ES兼容—mapping设置
        param_mapping = {
            "dynamic_templates": [
                {
                    "strings_as_keywords": {
                        "match_mapping_type": "string",
                        "mapping": {"norms": "false", "type": "keyword"},
                    }
                }
            ],
        }
        if es_version.startswith("5."):
            param_mapping["_all"] = {"enabled": True}
            param_mapping["include_in_all"] = False

        params = {
            "bk_data_id": collector_config.bk_data_id,
            # 必须为 库名.表名
            "table_id": f"{collector_config.bk_biz_id}_{settings.TABLE_ID_PREFIX}.{table_id}",
            "is_enable": True,
            "table_name_zh": collector_config.collector_config_name,
            "is_custom_table": True,
            "schema_type": "free",
            "default_storage": "elasticsearch",
            "default_storage_config": {
                "cluster_id": storage_cluster_id,
                "retention": retention,
                "date_format": date_format,
                "slice_size": slice_size,
                "slice_gap": slice_gap,
                "mapping_settings": param_mapping,
                "index_settings": {
                    "number_of_shards": collector_config.storage_shards_nums,
                    "number_of_replicas": collector_config.storage_replies,
                },
            },
            "is_time_field_only": True,
            "bk_biz_id": collector_config.bk_biz_id,
            "label": collector_config.category_id,
            "option": {},
            "field_list": [],
            "warm_phase_days": 0,
            "warm_phase_settings": {},
        }

        # 是否启用冷热集群
        if allocation_min_days:
            if not hot_warm_config or not hot_warm_config.get("is_enabled"):
                # 检查集群是否支持冷热数据功能
                raise HotColdCheckException()

            # 对于新数据，路由到热节点
            params["default_storage_config"]["index_settings"].update(
                {
                    f"index.routing.allocation.include.{hot_warm_config['hot_attr_name']}": hot_warm_config[
                        "hot_attr_value"
                    ],
                }
            )
            # n天后的数据，路由到冷节点
            params["default_storage_config"].update(
                {
                    "warm_phase_days": allocation_min_days,
                    "warm_phase_settings": {
                        "allocation_attr_name": hot_warm_config["warm_attr_name"],
                        "allocation_attr_value": hot_warm_config["warm_attr_value"],
                        "allocation_type": "include",
                    },
                }
            )

        # 获取清洗配置
        collector_scenario = CollectorScenario.get_instance(
            collector_scenario_id=collector_config.collector_scenario_id
        )
        built_in_config = collector_scenario.get_built_in_config(es_version)
        result_table_config = self.get_result_table_config(fields, etl_params, built_in_config, es_version=es_version)
        params.update(result_table_config)

        # 字段mapping优化
        for field in params["field_list"]:
            # 如果datetype不支持doc_values，则不设置doc_values，避免meta判断类型不一致创建新的index
            if "es_doc_values" in field["option"]:
                if field["option"]["es_doc_values"] or field["option"]["es_type"] in ["date", "text"]:
                    del field["option"]["es_doc_values"]
            # 移除计分
            if "es_type" in field["option"] and field["option"]["es_type"] in ["text"]:
                field["option"]["es_norms"] = False

        # 时间默认为维度
        if "time_option" in params and "es_doc_values" in params["time_option"]:
            del params["time_option"]["es_doc_values"]

        if not collector_config.table_id:
            # 创建结果表
            collector_config.table_id = TransferApi.create_result_table(params)["table_id"]
            collector_config.save()
        else:
            # 更新结果表
            params["table_id"] = collector_config.table_id
            TransferApi.modify_result_table(params)

        return {"table_id": collector_config.table_id, "params": params}

    @classmethod
    def switch_result_table(cls, collector_config: CollectorConfig, is_enable=True):
        """
        起停result_table
        :param collector_config: 采集项
        :param is_enable: 是否有效
        :return:
        """
        params = {
            "bk_data_id": collector_config.bk_data_id,
            # 必须为 库名.表名
            "table_id": f"{collector_config.table_id}",
            "is_enable": is_enable,
        }
        TransferApi.switch_result_table(params)
        return True

    @classmethod
    def parse_result_table_config(cls, result_table_config, result_table_storage=None):
        """
        根据meta配置返回前端格式
        :param result_table_config metadata_get_result_table
        :param result_table_storage metadata_get_result_table_storage
        """

        # 存储配置 && 清洗配置
        collector_config = {"etl_params": result_table_config.get("option", {})}
        if result_table_storage:
            collector_config["storage_cluster_id"] = result_table_storage["cluster_config"]["cluster_id"]
            collector_config["storage_cluster_name"] = result_table_storage["cluster_config"]["cluster_name"]
            collector_config["retention"] = result_table_storage["storage_config"].get("retention")
            collector_config["allocation_min_days"] = result_table_storage["storage_config"].get("warm_phase_days")

        # 字段
        built_in_fields = FieldBuiltInEnum.get_choices()
        field_list = []
        time_fields = [item for item in result_table_config["field_list"] if item["field_name"] == "dtEventTimeStamp"]
        if not time_fields:
            raise EtlParseTimeFieldException()
        time_field = copy.deepcopy(time_fields[0])

        for field in result_table_config["field_list"]:
            # 判断是不是标准字段
            field["is_built_in"] = True if field["field_name"].lower() in built_in_fields else False

            # 如果有指定别名，则需要调转位置(field_name：ES入库的字段名称；alias_name：数据源的字段名称)
            field_option = field.get("option", {})
            if field_option.get("real_path"):
                field["alias_name"] = field_option["real_path"].replace(f"{cls.separator_node_name}.", "")

            if field.get("alias_name"):
                field["field_name"], field["alias_name"] = field["alias_name"], field["field_name"]

            # 如果别名与field_name相同，则不返回
            if field["field_name"] == field["alias_name"]:
                field["alias_name"] = ""

            # 时间字段处理
            field["is_time"] = False
            if field["field_name"] == time_field["alias_name"]:
                field["is_time"] = True
                field["is_dimension"] = True
                # option
                field_es_type = field["option"]["es_type"]
                field["option"] = time_field["option"]
                field["option"]["time_zone"] = int(time_field["option"]["time_zone"])
                field["option"]["es_type"] = field_es_type

            es_type = field_option.get("es_type", "keyword")

            # 字段类型
            field["field_type"] = FieldDataTypeEnum.get_field_type(es_type)

            # 分词字段设置
            field["is_analyzed"] = False
            if es_type == "text":
                field["is_analyzed"] = True
                field["is_dimension"] = False
            field["is_delete"] = field.get("is_delete", False)

            # 如果未设置维度，则获取es_doc_values的值
            if "is_dimension" not in field:
                field["is_dimension"] = field_option.get("es_doc_values", True)
                if field_option.get("es_type") == "text":
                    field["is_dimension"] = False

            field_list.append(field)

        # 添加删除字段
        if result_table_config["option"].get("separator_fields_remove"):
            fields_remove = result_table_config["option"]["separator_fields_remove"].split(",")
            for field_name in fields_remove:
                field_name = field_name.strip()
                if field_name == "":
                    continue

                field_info = copy.deepcopy(FIELD_TEMPLATE)
                field_info["field_name"] = field_name
                field_list.append(field_info)

        collector_config["fields"] = sorted(field_list, key=lambda x: x.get("option", {}).get("field_index", 0))
        return collector_config
