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

import arrow
from django.conf import settings
from django.db import transaction
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from apps.api import TransferApi
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import FEATURE_COLLECTOR_ITSM
from apps.log_databus.constants import ETLProcessorChoices, ETL_PARAMS, EtlConfig, REGISTERED_SYSTEM_DEFAULT
from apps.log_databus.exceptions import (
    CollectorConfigNotExistException,
    EtlParseTimeFormatException,
    EtlStorageUsedException,
)
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import (
    CollectorConfig,
    ItsmEtlConfig,
    StorageCapacity,
    StorageUsed,
)
from apps.log_search.constants import FieldDateFormatEnum, ISO_8601_TIME_FORMAT_NAME
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import ProjectInfo, Scenario
from apps.models import model_to_dict
from apps.utils.db import array_group


class EtlHandler(object):
    def __init__(self, collector_config_id=None, etl_processor=ETLProcessorChoices.TRANSFER.value):
        super().__init__()
        self.collector_config_id = collector_config_id
        self.data = None
        self.etl_processor = etl_processor
        if collector_config_id:
            self.data = self._get_collect_config(collector_config_id)
            self.etl_processor = self.data.etl_processor

    @staticmethod
    def _get_collect_config(collector_config_id):
        try:
            collect_config: CollectorConfig = CollectorConfig.objects.get(collector_config_id=collector_config_id)
            return collect_config
        except CollectorConfig.DoesNotExist:
            raise CollectorConfigNotExistException()

    def __new__(cls, *args, **kwargs):
        # 获取处理器信息
        etl_processor = kwargs.get("etl_processor", ETLProcessorChoices.TRANSFER.value)
        collector_config_id = kwargs.get("collector_config_id")
        if collector_config_id:
            collect_config = cls._get_collect_config(collector_config_id)
            etl_processor = collect_config.etl_processor
        # 处理器映射关系
        mapping = {
            ETLProcessorChoices.BKBASE.value: "BKBaseEtlHandler",
            ETLProcessorChoices.TRANSFER.value: "TransferEtlHandler",
        }
        # 获取处理器
        try:
            etl_handler = import_string(
                "apps.log_databus.handlers.etl.{}.{}".format(etl_processor, mapping.get(etl_processor))
            )
            return object.__new__(etl_handler)
        except ImportError as error:
            raise NotImplementedError(f"EtlHandler of {etl_processor} not implement, error: {error}")

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

    def itsm_pre_hook(self, data, collect_config_id):
        if not FeatureToggleObject.switch(name=FEATURE_COLLECTOR_ITSM):
            return data, True

        collect_config = CollectorConfig.objects.get(collector_config_id=collect_config_id)
        if data["need_assessment"]:
            from apps.log_databus.handlers.itsm import ItsmHandler

            itsm_handler = ItsmHandler()
            sn = itsm_handler.create_ticket(
                {
                    "title": collect_config.generate_itsm_title(),
                    "bk_biz_id": collect_config.bk_biz_id,
                    "approvals": ",".join(data["assessment_config"]["approvals"]),
                    "log_assessment": data["assessment_config"]["log_assessment"],
                    "collector_detail": itsm_handler.generate_collector_detail_itsm_form(collect_config),
                }
            )
            collect_config.set_itsm_applying(sn)
            if data["assessment_config"]["need_approval"]:
                ItsmEtlConfig.objects.create(ticket_sn=sn, request_param=data)
                return itsm_handler.collect_itsm_status(collect_config_id), False
            collect_config.set_itsm_success()
        return data, True

    def update_or_create(self, *args, **kwargs):
        raise NotImplementedError

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