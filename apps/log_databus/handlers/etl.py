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
import arrow

from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.conf import settings

from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.log_databus.exceptions import (
    CollectorConfigNotExistException,
    EtlParseTimeFormatException,
    EtlStorageUsedException,
    CollectorActiveException,
)
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import CollectorConfig, StorageCapacity, StorageUsed
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import Scenario, ProjectInfo
from apps.log_search.constants import FieldDateFormatEnum
from apps.models import model_to_dict
from apps.utils.db import array_group
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_databus.constants import REGISTERED_SYSTEM_DEFAULT
from apps.decorators import user_operation_record
from apps.utils.local import get_request_username


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

    def update_or_create(
        self,
        etl_config,
        table_id,
        storage_cluster_id,
        retention,
        allocation_min_days,
        storage_replies,
        view_roles,
        etl_params=None,
        fields=None,
    ):
        # 停止状态下不能编辑
        if self.data and not self.data.is_active:
            raise CollectorActiveException()

        # 存储集群信息
        cluster_info = StorageHandler(storage_cluster_id).get_cluster_info_by_id()
        self.check_es_storage_capacity(cluster_info, storage_cluster_id)
        is_add = False if self.data.table_id else True

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

        # 2. 创建索引集
        index_set = self._update_or_create_index_set(etl_config, storage_cluster_id, view_roles)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
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
        if len(data) != len(fmt["description"]):
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
    def _update_or_create_index_set(self, etl_config, storage_cluster_id, view_roles=None):
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
                index_set_name=index_set_name, view_roles=view_roles, category_id=self.data.category_id, indexes=indexes
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
            )
            self.data.index_set_id = index_set.index_set_id
        self.data.etl_config = etl_config
        self.data.save()

        return model_to_dict(index_set)
