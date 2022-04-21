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
import json
from typing import Union

from apps.api import BkDataDatabusApi
from apps.log_databus.constants import BKDATA_ES_TYPE_MAP
from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import CollectorConfig, CollectorPlugin
from apps.utils.local import get_request_username


class BKBaseCollectorPluginHandler(CollectorPluginHandler, EtlStorage):
    def _stop_bkdata_clean(self, bkdata_result_table_id: str) -> None:
        BkDataDatabusApi.delete_tasks(
            params={
                "result_table_id": bkdata_result_table_id,
                "bk_username": get_request_username(),
            }
        )

    def _start_bkdata_clean(self, bkdata_result_table_id: str) -> None:
        BkDataDatabusApi.post_tasks(
            params={
                "result_table_id": bkdata_result_table_id,
                "storages": ["kafka"],
                "bk_username": get_request_username(),
            }
        )

    def _get_bkdata_etl_config(self, fields, etl_params, built_in_config):
        built_in_fields = built_in_config.get("fields", [])
        result_table_fields = self.get_result_table_fields(fields, etl_params, copy.deepcopy(built_in_config))
        time_field = result_table_fields.get("time_field")

        return {
            "extract": {
                "method": "from_json",
                "next": {
                    "next": [
                        {
                            "default_type": "null",
                            "default_value": "",
                            "next": {
                                "method": "iterate",
                                "next": {
                                    "next": None,
                                    "subtype": "assign_obj",
                                    "label": "labelb140f1",
                                    "assign": [
                                        {"key": "data", "assign_to": "data", "type": "text"},
                                    ]
                                    + [
                                        self._to_bkdata_assign(built_in_field)
                                        for built_in_field in built_in_fields
                                        if built_in_field.get("flat_field", False)
                                    ],
                                    "type": "assign",
                                },
                                "label": "label21ca91",
                                "result": "iter_item",
                                "args": [],
                                "type": "fun",
                            },
                            "label": "label36c8ad",
                            "key": "items",
                            "result": "item_data",
                            "subtype": "access_obj",
                            "type": "access",
                        },
                        {
                            "next": None,
                            "subtype": "assign_obj",
                            "label": "labelf676c9",
                            "assign": self._get_bkdata_default_fields(built_in_fields, time_field),
                            "type": "assign",
                        },
                    ],
                    "name": "",
                    "label": None,
                    "type": "branch",
                },
                "result": "json_data",
                "label": "label04a222",
                "args": [],
                "type": "fun",
            },
            "conf": self._to_bkdata_conf(time_field),
        }

    def _get_result_table_config(self, fields, etl_params, built_in_config, es_version="5.X"):
        """
        配置清洗入库策略，需兼容新增、编辑
        """
        built_in_fields = built_in_config.get("fields", [])
        return {
            "option": built_in_config.get("option", {}),
            "field_list": built_in_fields
            + (fields or [])
            + [built_in_config["time_field"]]
            + [
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
            ],
            "time_alias_name": built_in_config["time_field"]["alias_name"],
            "time_option": built_in_config["time_field"]["option"],
        }

    def _create_instance_etl_storage(self, params: dict) -> None:
        self.collector_config.table_id = self._create_etl_storage(self.collector_config, params)

    def _create_etl_storage(self, instance: Union[CollectorPlugin, CollectorConfig], params: dict) -> str:
        is_collector_plugin = True if isinstance(instance, CollectorPlugin) else False
        # 获取基础参数
        fields = params.get("params", {}).get("fields", [])
        etl_params = params.get("params", {}).get("etl_params", {})

        # 获取清洗配置
        collector_scenario = CollectorScenario.get_instance(collector_scenario_id=instance.collector_scenario_id)
        built_in_config = collector_scenario.get_built_in_config()
        fields_config = self._get_result_table_config(fields, etl_params, copy.deepcopy(built_in_config)).get(
            "field_list", []
        )
        bkdata_json_config = self._get_bkdata_etl_config(fields, etl_params, built_in_config)
        # 固定有time字段
        fields_config.append({"alias_name": "time", "field_name": "time", "option": {"es_type": "long"}})
        # 构造请求参数
        table_name = instance.collector_plugin_name_en if is_collector_plugin else instance.collector_config_name_en
        clean_config_name = instance.collector_plugin_name if is_collector_plugin else instance.collector_config_name
        if is_collector_plugin:
            bk_biz_id = instance.bk_biz_id
        else:
            bk_biz_id = instance.bkdata_biz_id if instance.bkdata_biz_id else instance.bk_biz_id
        params = {
            "raw_data_id": instance.bk_data_id,
            "result_table_name": table_name,
            "result_table_name_alias": table_name,
            "clean_config_name": clean_config_name,
            "description": instance.description,
            "bk_biz_id": bk_biz_id,
            "fields": [
                {
                    "field_name": field.get("alias_name") if field.get("alias_name") else field.get("field_name"),
                    "field_type": BKDATA_ES_TYPE_MAP.get(field.get("option").get("es_type"), "string"),
                    "field_alias": field.get("description") if field.get("description") else field.get("field_name"),
                    "is_dimension": field.get("tag", "dimension") == "dimension",
                    "field_index": index,
                }
                for index, field in enumerate(fields_config, 1)
            ],
            "json_config": json.dumps(bkdata_json_config),
            "bk_username": get_request_username(),
        }
        # 创建并启动清洗
        result = BkDataDatabusApi.databus_cleans_post(params)
        self._start_bkdata_clean(result["result_table_id"])
        return result["result_table_id"]
