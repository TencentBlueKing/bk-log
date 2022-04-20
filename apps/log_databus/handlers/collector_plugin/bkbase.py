import copy
import json

from apps.api import BkDataDatabusApi
from apps.log_databus.constants import BKDATA_ES_TYPE_MAP
from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.utils.function import ignored
from apps.utils.local import get_request_username


class BKBaseCollectorPluginHandler(CollectorPluginHandler):
    def _build_plugin_etl_template(self, params: dict) -> dict:
        return {
            "raw_data_id": self.collector_plugin.bk_data_id,
            "bk_biz_id": self.collector_plugin.bk_biz_id,
            "result_table_name": self.collector_plugin.collector_plugin_name_en,
            "result_table_name_alias": self.collector_plugin.collector_plugin_name_en,
            "description": self.collector_plugin.description,
            "clean_config_name": self.collector_plugin.collector_plugin_name_en,
        }

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

    def _create_instance_etl_storage(self, params: dict) -> None:
        if not self.collector_plugin.is_allow_alone_etl_config:
            params.update(**self.collector_plugin.etl_template)

        # 获取基础参数
        fields = params.get("fields", [])
        etl_params = params.get("etl_params", {})

        # 获取 table_id
        with ignored(Exception):
            _, table_id = self.collector_config.table_id.split(".")

        # 获取清洗入库处理器
        etl_storage = EtlStorage.get_instance(etl_config=self.collector_config.etl_config)

        # 获取清洗配置
        collector_scenario = CollectorScenario.get_instance(
            collector_scenario_id=self.collector_config.collector_scenario_id
        )
        built_in_config = collector_scenario.get_built_in_config()
        fields_config = etl_storage.get_result_table_config(fields, etl_params, copy.deepcopy(built_in_config)).get(
            "field_list", []
        )
        bkdata_json_config = etl_storage.get_bkdata_etl_config(fields, etl_params, built_in_config)
        # 固定有time字段
        fields_config.append({"alias_name": "time", "field_name": "time", "option": {"es_type": "long"}})
        params = {
            "raw_data_id": self.collector_config.bk_data_id,
            "result_table_name": self.collector_config.collector_config_name_en,
            "result_table_name_alias": self.collector_config.collector_config_name_en,
            "clean_config_name": self.collector_config.collector_config_name,
            "description": self.collector_config.description,
            "bk_biz_id": self.collector_config.bkdata_biz_id
            if self.collector_config.bkdata_biz_id
            else self.collector_config.bk_biz_id,
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
        result = BkDataDatabusApi.databus_cleans_post(params)
        self.collector_config.bkdata_etl_processing_id = result["processing_id"]
        self.collector_config.bkdata_etl_result_table_id = result["result_table_id"]
        self._start_bkdata_clean(result["result_table_id"])
