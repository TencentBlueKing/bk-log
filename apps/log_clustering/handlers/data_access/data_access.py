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

from apps.api import BkDataDatabusApi, BkDataMetaApi
from apps.log_clustering.handlers.aiops.base import BaseAiopsHandler
from apps.log_clustering.models import ClusteringConfig
from apps.log_databus.constants import BKDATA_ES_TYPE_MAP
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import CollectorConfig


class DataAccessHandler(BaseAiopsHandler):
    def __init__(self, raw_data_id: int):
        super(DataAccessHandler, self).__init__()
        self.raw_data_id = raw_data_id

    def get_deploy_plan(self):
        return BkDataDatabusApi.get_config_db_list(params={"raw_data_id": self.raw_data_id})

    @classmethod
    def get_fields(cls, result_table_id: str):
        return BkDataMetaApi.result_tables.fields({"result_table_id": result_table_id})

    def sync_bkdata_etl(self, collector_config_id):
        collector_config = CollectorConfig.objects.get(collector_config_id=collector_config_id)
        etl_config = collector_config.get_etl_config()
        self._create_or_update_bkdata_etl(etl_config["fields"], etl_config["etl_params"])

    def _create_or_update_bkdata_etl(self, collector_config_id, fields, etl_params):
        clustering_config = ClusteringConfig.objects.get(collector_config_id=collector_config_id)
        collector_config = CollectorConfig.objects.get(collector_config_id=clustering_config.collector_config_id)
        _, table_id = collector_config.table_id.split(".")
        etl_storage = EtlStorage.get_instance(etl_config=collector_config.etl_config)

        # 获取清洗配置
        collector_scenario = CollectorScenario.get_instance(
            collector_scenario_id=collector_config.collector_scenario_id
        )
        built_in_config = collector_scenario.get_built_in_config()
        fields_config = etl_storage.get_result_table_config(fields, etl_params, copy.deepcopy(built_in_config)).get(
            "field_list", []
        )
        bkdata_json_config = etl_storage.get_bkdata_etl_config(fields, etl_params, built_in_config)
        params = {
            "raw_data_id": clustering_config.bkdata_data_id,
            "result_table_name": collector_config.collector_config_name_en,
            "result_table_name_alias": collector_config.collector_config_name_en,
            "clean_config_name": collector_config.collector_config_name,
            "description": collector_config.description,
            "bk_biz_id": collector_config.bk_biz_id,
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
        }

        params = self._set_username(params)
        if not clustering_config.bkdata_etl_processing_id:
            result = BkDataDatabusApi.databus_cleans_post(params)
            clustering_config.bkdata_etl_processing_id = result["processing_id"]
            clustering_config.bkdata_etl_result_table_id = result["result_table_id"]
            clustering_config.save()
            return

        params.update({"processing_id": clustering_config.bkdata_etl_processing_id})
        BkDataDatabusApi.databus_cleans_put(params)
