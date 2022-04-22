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

from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.models import CollectorConfig


class TransferCollectorPluginHandler(CollectorPluginHandler):
    def _get_mock_collector_config(self):
        return CollectorConfig(
            bk_biz_id=self.collector_plugin.bk_biz_id,
            bk_data_id=self.collector_plugin.bk_data_id,
            collector_config_name=self.collector_plugin.collector_plugin_name,
            storage_shards_nums=self.collector_plugin.storage_shards_nums,
            storage_replies=self.collector_plugin.storage_replies,
            storage_shards_size=self.collector_plugin.storage_shards_size,
            category_id=self.collector_plugin.category_id,
            collector_scenario_id=self.collector_plugin.collector_scenario_id,
        )

    def _create_etl_storage(self, instance, params: dict) -> str:
        # 集群信息
        cluster_info = StorageHandler(params["storage_cluster_id"]).get_cluster_info_by_id()
        # 创建清洗
        etl_storage: EtlStorage = EtlStorage.get_instance(params["etl_config"])
        table_id = etl_storage.update_or_create_result_table(
            self._get_mock_collector_config(),
            instance.collector_plugin_name_en,
            instance.storage_cluster_id,
            instance.retention,
            instance.allocation_min_days,
            instance.storage_replies,
            params.get("fields", []),
            params.get("etl_params", {}),
            cluster_info["cluster_config"]["version"],
            cluster_info["cluster_config"].get("custom_option", {}).get("hot_warm_config"),
        )["table_id"]
        return table_id

    def _create_instance_etl_storage(self, params: dict) -> None:
        etl_config = {
            "etl_config": params.get("etl_config"),
            "table_id": params.get("table_id"),
            "etl_params": params.get("etl_params"),
            "fields": params.get("fields"),
            "storage_cluster_id": params.get("storage_cluster_id"),
            "retention": params.get("retention"),
            "allocation_min_days": params.get("allocation_min_days"),
            "storage_replies": params.get("storage_replies"),
        }
        EtlHandler(self.collector_config_id).update_or_create(**etl_config)
