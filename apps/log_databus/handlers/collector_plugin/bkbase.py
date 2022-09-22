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
from typing import Union

from apps.log_databus.constants import ETLProcessorChoices
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.models import CollectorConfig, CollectorPlugin


class BKBaseCollectorPluginHandler(CollectorPluginHandler):
    """
    数据平台
    """

    def _create_data_id(self, instance: Union[CollectorConfig, CollectorPlugin]) -> int:
        """
        创建metadata后赋值给数据平台
        """

        metadata_bk_data_id = CollectorHandler.update_or_create_data_id(
            self.collector_plugin, etl_processor=ETLProcessorChoices.TRANSFER.value
        )
        return CollectorHandler.update_or_create_data_id(self.collector_plugin, bk_data_id=metadata_bk_data_id)

    def _create_metadata_result_table(self) -> None:
        """
        若不允许独立存储，则需要同时创建 metadata 的结果表
        """

        if not self.collector_plugin.is_allow_alone_storage:
            # 集群信息
            cluster_info = StorageHandler(self.collector_plugin.storage_cluster_id).get_cluster_info_by_id()

            # 创建结果表
            etl_storage: EtlStorage = EtlStorage.get_instance(self.collector_plugin.etl_config)
            etl_storage.update_or_create_result_table(
                instance=self.collector_plugin,
                table_id=self.collector_plugin.collector_plugin_name_en,
                storage_cluster_id=self.collector_plugin.storage_cluster_id,
                retention=self.collector_plugin.retention,
                allocation_min_days=self.collector_plugin.allocation_min_days,
                storage_replies=self.collector_plugin.storage_replies,
                fields=self.collector_plugin.fields,
                etl_params=self.collector_plugin.etl_params,
                es_version=cluster_info["cluster_config"]["version"],
                hot_warm_config=cluster_info["cluster_config"].get("custom_option", {}).get("hot_warm_config"),
                es_shards=self.collector_plugin.storage_shards_nums,
                index_settings=self.collector_plugin.index_settings,
            )

    def _update_or_create_etl_storage(self, params: dict, is_create: bool) -> None:
        """
        创建或更新清洗入库
        """

        etl_handler = EtlHandler.get_instance(etl_processor=self.collector_plugin.etl_processor)
        etl_handler.update_or_create(instance=self.collector_plugin, is_create=is_create, params=params)

    def _update_or_create_instance_etl(self, collect_config: CollectorConfig, params: dict) -> None:
        """
        创建或更新实例清洗入库
        """

        # 使用对应的配置创建清洗与入库
        etl_handler = EtlHandler.get_instance(
            etl_processor=self.collector_plugin.etl_processor, collector_config_id=collect_config.collector_config_id
        )
        etl_handler.update_or_create(instance=collect_config, params=params)
