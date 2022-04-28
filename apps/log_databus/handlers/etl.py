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
import json
from typing import Union

import arrow
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from apps.api import BkDataDatabusApi, TransferApi
from apps.constants import UserOperationActionEnum, UserOperationTypeEnum
from apps.decorators import user_operation_record
from apps.log_clustering.handlers.clustering_config import ClusteringConfigHandler
from apps.log_clustering.handlers.data_access.data_access import DataAccessHandler
from apps.log_clustering.tasks.flow import update_clustering_clean
from apps.log_databus.constants import ETL_PARAMS, EtlConfig, REGISTERED_SYSTEM_DEFAULT
from apps.log_databus.exceptions import (
    BKBASEStorageNotExistException,
    CollectorActiveException,
    CollectorConfigNotExistException,
    CollectorResultTableIDDuplicateException,
    EtlParseTimeFormatException,
    EtlStorageUsedException,
)
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.collector_scenario.custom_define import get_custom
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.models import CleanStash, CollectorConfig, CollectorPlugin, StorageCapacity, StorageUsed
from apps.log_search.constants import CollectorScenarioEnum, FieldDateFormatEnum, ISO_8601_TIME_FORMAT_NAME
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import ProjectInfo, Scenario
from apps.models import model_to_dict
from apps.utils.db import array_group
from apps.utils.local import get_request_username
from apps.utils.log import logger


class EtlHandler(object):
    def __init__(self, collector_config_id=None):
        super().__init__()
        self.collector_config_id = collector_config_id
        self.data = None
        if collector_config_id:
            try:
                self.data = CollectorConfig.objects.get(collector_config_id=self.collector_config_id)
            except CollectorConfig.DoesNotExist:
                raise CollectorConfigNotExistException()

    def check_es_storage_capacity(self, cluster_info, storage_cluster_id):
        if self.data.table_id:
            return
        es_storage_capacity = int(settings.ES_STORAGE_CAPACITY)
        register_system = cluster_info["cluster_config"].get("registered_system")
        if es_storage_capacity > 0 and register_system == REGISTERED_SYSTEM_DEFAULT:
            biz_storage = StorageCapacity.objects.filter(bk_biz_id=self.data.bk_biz_id).first()
            biz_storage_used = StorageUsed.objects.filter(
                bk_biz_id=self.data.bk_biz_id, storage_cluster_id=storage_cluster_id
            ).first()

            if biz_storage and biz_storage_used:
                storage = biz_storage.storage_capacity
                storage_used = biz_storage_used.storage_used
                if storage > 0:
                    if storage_used >= storage:
                        raise EtlStorageUsedException()

    @classmethod
    def stop_bkdata_clean(cls, bkdata_result_table_id: str) -> None:
        """停止清洗任务"""

        BkDataDatabusApi.delete_tasks(
            params={
                "result_table_id": bkdata_result_table_id,
                "bk_username": get_request_username(),
            }
        )

    @classmethod
    def start_bkdata_clean(cls, bkdata_result_table_id: str) -> None:
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

    @classmethod
    def restart_bkdata_clean(cls, bkdata_result_table_id: str) -> None:
        """
        重启清洗任务
        """

        cls.stop_bkdata_clean(bkdata_result_table_id)
        cls.start_bkdata_clean(bkdata_result_table_id)

    @classmethod
    def update_or_create_bkbase_etl_storage(
        cls,
        instance: Union[CollectorConfig, CollectorPlugin],
        fields: list,
        json_config: Union[str, dict],
        is_create: bool,
        params: dict = None,
    ) -> None:
        """
        创建或更新清洗入库
        """

        # 类型适配
        if params is None:
            params = {}

        json_config = json_config if isinstance(json_config, dict) else json.loads(json_config)

        # TODO 指定 result_table

        bkdata_params = {
            "raw_data_id": instance.bk_data_id,
            "result_table_name": f"{settings.TABLE_ID_PREFIX}_{instance.get_en_name()}",
            "result_table_name_alias": instance.get_en_name(),
            "clean_config_name": instance.get_name(),
            "description": instance.description,
            "bk_biz_id": instance.get_bk_biz_id(),
            "bk_username": get_request_username(),
            "fields": fields,
            "json_config": json.dumps(json_config),
        }

        # 创建清洗
        if is_create:
            result = BkDataDatabusApi.databus_cleans_post(bkdata_params)
            cls.start_bkdata_clean(result["result_table_id"])
            instance.processing_id = result["processing_id"]
            instance.bkbase_table_id = result["result_table_id"]
            instance.save()

        # 更新清洗
        else:
            bkdata_params.update({"processing_id": instance.processing_id})
            BkDataDatabusApi.databus_cleans_put(bkdata_params, request_cookies=False)
            cls.restart_bkdata_clean(instance.bkbase_table_id)

        # 入库参数
        # TODO 同步集群信息到 BKBASE
        cluster_info = StorageHandler(instance.storage_cluster_id).get_cluster_info_by_id()
        bkbase_cluster_id = cluster_info["cluster_config"].get("custom_option", {}).get("bkbase_cluster_id")
        if bkbase_cluster_id is None:
            raise BKBASEStorageNotExistException

        storage_params = {
            "bk_biz_id": instance.get_bk_biz_id(),
            "raw_data_id": instance.bk_data_id,
            "data_type": "clean",
            "result_table_name": f"{settings.TABLE_ID_PREFIX}_{instance.get_en_name()}",
            "result_table_name_alias": instance.get_en_name(),
            "storage_type": "es",
            "storage_cluster": bkbase_cluster_id,
            "expires": f"{instance.retention}d",
            "fields": fields,
        }

        # 创建入库
        if is_create:
            BkDataDatabusApi.databus_data_storages_post(storage_params)
            return

        # 更新入库
        storage_params.update({"result_table_id": instance.bkbase_table_id})
        BkDataDatabusApi.databus_data_storages_put(storage_params)

    def update_or_create(
        self,
        etl_config,
        table_id,
        storage_cluster_id,
        retention,
        allocation_min_days,
        storage_replies,
        view_roles=None,
        etl_params=None,
        fields=None,
        username="",
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
            log_clustering_fields = CollectorScenario.log_clustering_fields(cluster_info["cluster_config"]["version"])
            fields = CollectorScenario.fields_insert_field_index(source_fields=fields, dst_fields=log_clustering_fields)
            update_clustering_clean.delay(index_set_id=clustering_handler.data.index_set_id)

        # 判断是否已存在同result_table_id
        if CollectorConfig(table_id=table_id).get_result_table_by_id():
            logger.error(f"result_table_id {table_id} already exists")
            raise CollectorResultTableIDDuplicateException(
                CollectorResultTableIDDuplicateException.MESSAGE.format(result_table_id=table_id)
            )

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
        }

    @staticmethod
    def etl_preview(etl_config, etl_params, data):

        etl_storage = EtlStorage.get_instance(etl_config=etl_config)
        fields = etl_storage.etl_preview(data, etl_params)
        return {"fields": fields}

    def etl_time(self, time_format, time_zone, data):
        """
        时间解析
        """
        fmts = array_group(FieldDateFormatEnum.get_choices_list_dict(), "id", True)
        fmt = fmts.get(time_format)
        if fmt["name"] == ISO_8601_TIME_FORMAT_NAME:
            try:
                epoch_second = arrow.get(data, tzinfo=f"GMT{time_zone}").timestamp
            except Exception:  # pylint: disable=broad-except
                raise EtlParseTimeFormatException()
        else:
            if len(data) != len(fmt["description"]) and len(data) != len(fmt["name"]):
                raise EtlParseTimeFormatException()

            if time_format in ["epoch_second", "epoch_millis", "epoch_micros"]:
                epoch_second = str(data)[0:10]
            else:
                try:
                    epoch_second = arrow.get(data, fmt["name"], tzinfo=f"GMT{time_zone}").timestamp
                except Exception:  # pylint: disable=broad-except
                    raise EtlParseTimeFormatException()
        return {"epoch_millis": f"{epoch_second}000"}

    @transaction.atomic()
    def _update_or_create_index_set(self, etl_config, storage_cluster_id, view_roles=None, username=""):
        """
        创建索引集
        """
        # view_roles的来源
        indexes = [
            {
                "bk_biz_id": self.data.bk_biz_id,
                "result_table_id": self.data.table_id,
                "result_table_name": self.data.collector_config_name,
                "time_field": "dtEventTimeStamp",
            }
        ]
        index_set_name = _("[采集项]") + self.data.collector_config_name

        if self.data.index_set_id:
            index_set_handler = IndexSetHandler(index_set_id=self.data.index_set_id)
            if not view_roles:
                view_roles = index_set_handler.data.view_roles
            index_set = index_set_handler.update(
                index_set_name=index_set_name,
                view_roles=view_roles,
                category_id=self.data.category_id,
                indexes=indexes,
                username=username,
            )
        else:
            project_id = ProjectInfo.objects.filter(bk_biz_id=self.data.bk_biz_id).first().project_id
            if not view_roles:
                view_roles = []
            index_set = IndexSetHandler.create(
                index_set_name=index_set_name,
                project_id=project_id,
                storage_cluster_id=storage_cluster_id,
                scenario_id=Scenario.LOG,
                view_roles=view_roles,
                indexes=indexes,
                category_id=self.data.category_id,
                collector_config_id=self.collector_config_id,
                username=username,
            )
            self.data.index_set_id = index_set.index_set_id
        self.data.etl_config = etl_config
        self.data.save()

        return model_to_dict(index_set)

    def close_clean(self):
        storage = TransferApi.get_result_table_storage(
            params={"result_table_list": self.data.table_id, "storage_type": "elasticsearch"}
        )[self.data.table_id]
        storage_cluster_id = storage["cluster_config"]["cluster_id"]
        retention = storage["storage_config"].get("retention")
        allocation_min_days = storage["storage_config"].get("warm_phase_days")
        storage_replies = storage["storage_config"]["index_settings"]["number_of_replicas"]
        _, table_id = self.data.table_id.split(".")
        self.update_or_create(
            etl_config=EtlConfig.BK_LOG_TEXT,
            table_id=table_id,
            storage_cluster_id=storage_cluster_id,
            retention=retention,
            allocation_min_days=allocation_min_days,
            storage_replies=storage_replies,
            etl_params=ETL_PARAMS,
            fields=[],
        )
        return {"collector_config_id": self.collector_config_id}
