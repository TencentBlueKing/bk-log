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
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
import copy
import json
from typing import Union

from django.conf import settings

from apps.api import BkDataDatabusApi
from apps.log_databus.constants import BKDATA_ES_TYPE_MAP
from apps.log_databus.exceptions import BKBASEStorageNotExistException
from apps.log_databus.handlers.collector import build_result_table_id
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.etl.base import EtlHandler
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.models import CollectorConfig, CollectorPlugin
from apps.utils.local import get_request_username


class BKBaseEtlHandler(EtlHandler):
    """
    数据平台
    """

    @staticmethod
    def stop_bkdata_clean(bkdata_result_table_id: str) -> None:
        """停止清洗任务"""

        BkDataDatabusApi.delete_tasks(
            params={"result_table_id": bkdata_result_table_id, "bk_username": get_request_username()}
        )

    @staticmethod
    def start_bkdata_clean(bkdata_result_table_id: str) -> None:
        """
        启动清洗任务
        """

        BkDataDatabusApi.post_tasks(
            params={
                "result_table_id": bkdata_result_table_id,
                "storages": ["kafka"],
                "bk_username": get_request_username(),
            }
        )

    @staticmethod
    def restart_bkdata_clean(bkdata_result_table_id: str) -> None:
        """
        重启清洗任务
        """

        BKBaseEtlHandler.stop_bkdata_clean(bkdata_result_table_id)
        BKBaseEtlHandler.start_bkdata_clean(bkdata_result_table_id)

    def update_or_create(self, instance: Union[CollectorConfig, CollectorPlugin], params=None):
        """
        创建或更新清洗入库
        """

        if params is None:
            params = {}

        # 参数
        fields = params.get("fields", [])
        etl_params = params.get("etl_params", {})

        # 获取清洗入库
        collector_scenario = CollectorScenario.get_instance(collector_scenario_id=instance.collector_scenario_id)
        built_in_config = collector_scenario.get_built_in_config()
        etl_storage: EtlStorage = EtlStorage.get_instance(instance.etl_config)
        fields_config = etl_storage.get_result_table_config(fields, etl_params, copy.deepcopy(built_in_config)).get(
            "field_list", []
        )
        bkdata_json_config = etl_storage.get_bkdata_etl_config(fields, etl_params, built_in_config)
        fields_config.append({"alias_name": "time", "field_name": "time", "option": {"es_type": "long"}})

        bkdata_params = {
            "raw_data_id": instance.bk_data_id,
            "result_table_name": f"{settings.TABLE_ID_PREFIX}_{instance.get_en_name()}",
            "result_table_name_alias": instance.get_en_name(),
            "clean_config_name": instance.get_name(),
            "description": instance.description,
            "bk_biz_id": instance.get_bk_biz_id(),
            "bk_username": get_request_username(),
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

        # 创建清洗
        if not instance.bkbase_table_id:
            result = BkDataDatabusApi.databus_cleans_post(bkdata_params)
            self.start_bkdata_clean(result["result_table_id"])
            instance.processing_id = result["processing_id"]
            instance.bkbase_table_id = result["result_table_id"]
            instance.save()

        # 更新清洗
        else:
            bkdata_params.update({"processing_id": instance.processing_id})
            BkDataDatabusApi.databus_cleans_put(bkdata_params, request_cookies=False)
            self.restart_bkdata_clean(instance.bkbase_table_id)

        # 入库参数
        cluster_info = StorageHandler(params.get("storage_cluster_id")).get_cluster_info_by_id()
        bkbase_cluster_id = cluster_info["cluster_config"].get("custom_option", {}).get("bkbase_cluster_id")
        if bkbase_cluster_id is None:
            raise BKBASEStorageNotExistException

        for field in bkdata_params["fields"]:
            field["physical_field"] = field["field_name"]

        storage_params = {
            "bk_biz_id": instance.get_bk_biz_id(),
            "raw_data_id": instance.bk_data_id,
            "data_type": "clean",
            "result_table_name": f"{settings.TABLE_ID_PREFIX}_{instance.get_en_name()}",
            "result_table_name_alias": instance.get_en_name(),
            "storage_type": "es",
            "storage_cluster": bkbase_cluster_id,
            "expires": f"{params.get('retention', 1)}d",
            "fields": bkdata_params["fields"],
        }

        # 合流入库
        if not params.get("is_allow_alone_storage", True):
            timestamp_format = "{%s}" % params.get("rt_timestamp_format", "yyyyMMdd")
            if isinstance(instance, CollectorConfig) and instance.collector_plugin_id:
                collector_plugin = CollectorPlugin.objects.get(collector_plugin_id=instance.collector_plugin_id)
                table_name = collector_plugin.get_en_name()
            else:
                table_name = instance.get_en_name()
            table_id = build_result_table_id(instance.get_bk_biz_id(), table_name)
            storage_params["physical_table_name"] = f"write_{timestamp_format}_{table_id}"

        has_storage = BkDataDatabusApi.get_config_db_list({"raw_data_id": instance.bk_data_id})
        # 创建入库
        if not has_storage:
            BkDataDatabusApi.databus_data_storages_post(storage_params)
            return

        # 更新入库
        storage_params.update({"result_table_id": instance.bkbase_table_id})
        BkDataDatabusApi.databus_data_storages_put(storage_params)
