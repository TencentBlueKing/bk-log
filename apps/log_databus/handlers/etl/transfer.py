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
from django.conf import settings

from apps.constants import UserOperationActionEnum, UserOperationTypeEnum
from apps.decorators import user_operation_record
from apps.log_clustering.handlers.clustering_config import ClusteringConfigHandler
from apps.log_clustering.handlers.data_access.data_access import DataAccessHandler
from apps.log_clustering.tasks.flow import update_clustering_clean
from apps.log_databus.constants import EtlConfig
from apps.log_databus.exceptions import CollectorActiveException
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.collector_scenario.custom_define import get_custom
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.models import CleanStash
from apps.log_search.constants import CollectorScenarioEnum
from apps.utils.local import get_request_username


class TransferEtlHandler(EtlHandler):
    def update_or_create(
        self,
        etl_config,
        table_id,
        storage_cluster_id,
        retention,
        allocation_min_days,
        storage_replies,
        es_shards=settings.ES_SHARDS,
        view_roles=None,
        etl_params=None,
        fields=None,
        username="",
        *args,
        **kwargs,
    ):
        # 停止状态下不能编辑
        if self.data and not self.data.is_active:
            raise CollectorActiveException()

        # 当清洗为直接入库时，直接清理对应采集项清洗配置stash
        if etl_config == EtlConfig.BK_LOG_TEXT:
            CleanStash.objects.filter(collector_config_id=self.collector_config_id).delete()

        # 存储集群信息
        cluster_info = StorageHandler(storage_cluster_id).get_cluster_info_by_id()
        self.check_es_storage_capacity(cluster_info, storage_cluster_id)
        is_add = False if self.data.table_id else True

        if self.data.is_clustering:
            clustering_handler = ClusteringConfigHandler(collector_config_id=self.data.collector_config_id)
            ClusteringConfigHandler.pre_check_fields(
                fields=fields, etl_config=etl_config, clustering_fields=clustering_handler.data.clustering_fields
            )
            if clustering_handler.data.bkdata_etl_processing_id:
                DataAccessHandler().create_or_update_bkdata_etl(self.data.collector_config_id, fields, etl_params)
            etl_params["etl_flat"] = True
            etl_params["separator_node_action"] = ""
            log_clustering_fields = CollectorScenario.log_clustering_fields(cluster_info["cluster_config"]["version"])
            fields = CollectorScenario.fields_insert_field_index(source_fields=fields, dst_fields=log_clustering_fields)
            update_clustering_clean.delay(index_set_id=clustering_handler.data.index_set_id)

        # 暂时去掉这个效验逻辑，底下的逻辑都是幂等的，可以继续也必须继续往下走
        # # 判断是否已存在同result_table_id
        # if is_add and CollectorConfig(table_id=table_id).get_result_table_by_id():
        #     logger.error(f"result_table_id {table_id} already exists")
        #     raise CollectorResultTableIDDuplicateException(
        #         CollectorResultTableIDDuplicateException.MESSAGE.format(result_table_id=table_id)
        #     )

        # 1. meta-创建/修改结果表
        etl_storage = EtlStorage.get_instance(etl_config=etl_config)
        etl_storage.update_or_create_result_table(
            self.data,
            table_id=table_id,
            storage_cluster_id=storage_cluster_id,
            retention=retention,
            allocation_min_days=allocation_min_days,
            storage_replies=storage_replies,
            fields=fields,
            etl_params=etl_params,
            es_version=cluster_info["cluster_config"]["version"],
            hot_warm_config=cluster_info["cluster_config"].get("custom_option", {}).get("hot_warm_config"),
            es_shards=es_shards,
        )

        if not view_roles:
            view_roles = []

        # 2. 创建索引集
        index_set = self._update_or_create_index_set(etl_config, storage_cluster_id, view_roles, username=username)

        # add user_operation_record
        operation_record = {
            "username": username or get_request_username(),
            "biz_id": self.data.bk_biz_id,
            "record_type": UserOperationTypeEnum.ETL,
            "record_object_id": self.data.collector_config_id,
            "action": UserOperationActionEnum.CREATE if is_add else UserOperationActionEnum.UPDATE,
            "params": {
                "etl_config": etl_config,
                "table_id": table_id,
                "storage_cluster_id": storage_cluster_id,
                "retention": retention,
                "allocation_min_days": allocation_min_days,
                "view_roles": view_roles,
                "etl_params": etl_params,
                "fields": fields,
                "es_shards": es_shards,
            },
        }
        user_operation_record.delay(operation_record)
        if self.data.collector_scenario_id == CollectorScenarioEnum.CUSTOM.value:
            custom_config = get_custom(self.data.custom_type)
            custom_config.after_etl_hook(self.data)

        return {
            "collector_config_id": self.data.collector_config_id,
            "collector_config_name": self.data.collector_config_name,
            "etl_config": etl_config,
            "index_set_id": index_set["index_set_id"],
            "scenario_id": index_set["scenario_id"],
            "storage_cluster_id": storage_cluster_id,
            "retention": retention,
            "es_shards": es_shards,
        }
