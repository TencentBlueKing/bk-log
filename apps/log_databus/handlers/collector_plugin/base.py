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

import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils.module_loading import import_string

from apps.api import BkDataAccessApi
from apps.constants import UserOperationActionEnum, UserOperationTypeEnum
from apps.decorators import user_operation_record
from apps.log_databus.constants import (
    ADMIN_REQUEST_USER,
    BKDATA_DATA_REGION,
    BKDATA_DATA_SCENARIO,
    BKDATA_DATA_SCENARIO_ID,
    BKDATA_DATA_SENSITIVITY,
    BKDATA_DATA_SOURCE,
    BKDATA_DATA_SOURCE_TAGS,
    BKDATA_PERMISSION,
    BKDATA_TAGS,
    ETLProcessorChoices,
    META_DATA_ENCODING,
)
from apps.log_databus.exceptions import (
    CollectorConfigNotExistException,
    CollectorPluginNameDuplicateException,
    CollectorPluginNotExistException,
)
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.models import CollectorConfig, CollectorPlugin, DataLinkConfig
from apps.log_search.constants import CollectorScenarioEnum
from apps.models import model_to_dict
from apps.utils.local import get_request_username

logger = logging.getLogger("app")


def get_collector_plugin_handler(etl_processor, collector_plugin_id=None, collector_config_id=None):
    mapping = {
        ETLProcessorChoices.BKBASE.value: "BKBaseCollectorPluginHandler",
        ETLProcessorChoices.TRANSFER.value: "TransferCollectorPluginHandler",
    }
    try:
        collector_plugin_handler = import_string(
            "apps.log_databus.handlers.collector_plugin.{}.{}".format(etl_processor, mapping.get(etl_processor))
        )
        return collector_plugin_handler(collector_plugin_id, collector_config_id)
    except ImportError as error:
        raise NotImplementedError(f"CollectorPluginHandler of {etl_processor} not implement, error: {error}")


class CollectorPluginHandler:
    collector_plugin: CollectorPlugin = None
    collector_config: CollectorConfig = None

    def __init__(self, collector_plugin_id=None, collector_config_id=None):
        if collector_plugin_id:
            self._get_collector_plugin(collector_plugin_id)
        if collector_config_id:
            self._get_collector_config(collector_config_id)

    def _get_collector_plugin(self, collector_plugin_id: int) -> None:
        """绑定采集插件Model"""
        self.collector_plugin_id = collector_plugin_id
        try:
            self.collector_plugin: CollectorPlugin = CollectorPlugin.objects.get(
                collector_plugin_id=collector_plugin_id
            )
        except CollectorPlugin.DoesNotExist:
            raise CollectorPluginNotExistException()

    def _get_collector_config(self, collector_config_id: int) -> None:
        """绑定采集项Model"""
        self.collector_config_id = collector_config_id
        try:
            self.collector_config: CollectorConfig = CollectorConfig.objects.get(
                collector_config_id=collector_config_id
            )
        except CollectorConfig.DoesNotExist:
            raise CollectorConfigNotExistException()

    def _create_bkdata_data_id(self):
        """创建数据平台DATAID"""
        maintainers = {self.collector_plugin.updated_by, self.collector_plugin.created_by}
        maintainers.discard(ADMIN_REQUEST_USER)
        if not maintainers:
            raise Exception(f"dont have enough maintainer only {ADMIN_REQUEST_USER}")
        BkDataAccessApi.deploy_plan_post(
            params={
                "bk_username": self.collector_plugin.get_updated_by(),
                "data_scenario": BKDATA_DATA_SCENARIO,
                "data_scenario_id": BKDATA_DATA_SCENARIO_ID,
                "permission": BKDATA_PERMISSION,
                "bk_biz_id": self.collector_plugin.bk_biz_id,
                "description": self.collector_plugin.description,
                "access_raw_data": {
                    "tags": BKDATA_TAGS,
                    "raw_data_name": self.collector_plugin.collector_plugin_name_en,
                    "maintainer": ",".join(maintainers),
                    "raw_data_alias": self.collector_plugin.collector_plugin_name,
                    "data_source_tags": BKDATA_DATA_SOURCE_TAGS,
                    "data_region": BKDATA_DATA_REGION,
                    "data_source": BKDATA_DATA_SOURCE,
                    "data_encoding": self.collector_plugin.data_encoding
                    if self.collector_plugin.data_encoding
                    else META_DATA_ENCODING,
                    "sensitivity": BKDATA_DATA_SENSITIVITY,
                    "description": self.collector_plugin.description,
                    "preassigned_data_id": self.collector_plugin.bk_data_id,
                },
            }
        )

    def _update_or_create_data_id(self) -> int:
        """创建DATAID"""
        collector_scenario = CollectorScenario.get_instance(CollectorScenarioEnum.CUSTOM.value)
        bk_data_id = collector_scenario.update_or_create_data_id(
            bk_data_id=self.collector_plugin.bk_data_id,
            data_link_id=self.collector_plugin.data_link_id,
            data_name="{bk_biz_id}_{table_id_prefix}_{name}".format(
                bk_biz_id=self.collector_plugin.bk_biz_id,
                table_id_prefix=settings.TABLE_ID_PREFIX,
                name=self.collector_plugin.collector_plugin_name,
            ),
            description=self.collector_plugin.description,
            encoding=META_DATA_ENCODING,
        )
        # self._create_bkdata_data_id()
        return bk_data_id

    def _pre_check_en_name(self, en_name: str) -> None:
        """校验英文名称，不能与插件或实例的名字重复"""
        config_name_duplicate = CollectorConfig.objects.filter(collector_config_name_en=en_name).exists()
        plugin_name_duplicate = CollectorPlugin.objects.filter(collector_plugin_name_en=en_name).exists()
        if config_name_duplicate or plugin_name_duplicate:
            raise CollectorPluginNameDuplicateException()

    def _update_or_create_etl(self, instance, params: dict, is_create: bool) -> str:
        raise NotImplementedError

    @transaction.atomic()
    def _update_or_create(self, params: dict) -> bool:
        # 创建插件
        if not self.collector_plugin:
            model_fields = {
                "bk_biz_id": params["bk_biz_id"],
                "collector_plugin_name": params["collector_plugin_name"],
                "collector_plugin_name_en": params["collector_plugin_name_en"],
                "description": params["description"] if params.get("description") else params["collector_plugin_name"],
                "category_id": params["category_id"],
                "data_encoding": params.get("data_encoding"),
                "params": params.get("params", {}),
                "data_link_id": params.get("data_link_id"),
                "is_enabled_display_collector": params["is_enabled_display_collector"],
                "is_allow_alone_data_id": params["is_allow_alone_data_id"],
                "is_allow_alone_etl_config": params["is_allow_alone_etl_config"],
                "is_allow_alone_storage": params["is_allow_alone_storage"],
                "collector_scenario_id": params["collector_scenario_id"],
                "etl_processor": params["etl_processor"],
            }

            # 校验英文名
            self._pre_check_en_name(params["collector_plugin_name_en"])

            # 创建采集插件
            try:
                self.collector_plugin = CollectorPlugin.objects.create(**model_fields)
            except IntegrityError:
                logger.warning(f"collector plugin name duplicate => [{params.get('collector_plugin_name')}]")
                raise CollectorPluginNameDuplicateException()

            # DATA_ID
            if not params["is_allow_alone_data_id"] or params.get("create_public_data_id", False):
                # 绑定链路
                if not self.collector_plugin.data_link_id:
                    data_links = DataLinkConfig.objects.filter(
                        bk_biz_id__in=[0, self.collector_plugin.bk_biz_id]
                    ).order_by("data_link_id")
                    if data_links.exists():
                        self.collector_plugin.data_link_id = data_links.first().data_link_id
                # 创建 DATA ID
                self.collector_plugin.bk_data_id = self._update_or_create_data_id()

            is_create = True
        # 更新插件
        else:
            model_fields = self._build_model_fields(
                params,
                "collector_plugin_name",
                "description",
                "data_encoding",
                "params",
                "is_enabled_display_collector",
                "is_allow_alone_data_id",
                "is_allow_alone_etl_config",
                "is_allow_alone_storage",
                "storage_cluster_id",
                "retention",
                "allocation_min_days",
                "storage_replies",
                "storage_shards_nums",
                "etl_config",
            )
            params.update(model_fields)
            for key, val in model_fields.items():
                setattr(self.collector_plugin, key, val)

            # 更新可见性
            self.collector_plugin.change_collector_display_status(params["is_enabled_display_collector"])

            # DATA_ID
            if not params["is_allow_alone_data_id"] or params.get("create_public_data_id", False):
                self.collector_plugin.bk_data_id = self._update_or_create_data_id()

            is_create = False

        # 存储
        if not params["is_allow_alone_storage"] or self.collector_plugin.bk_data_id:
            self.collector_plugin.storage_cluster_id = params["storage_cluster_id"]
            self.collector_plugin.retention = params["retention"]
            self.collector_plugin.allocation_min_days = params["allocation_min_days"]
            self.collector_plugin.storage_replies = params["storage_replies"]
            self.collector_plugin.storage_shards_nums = params["storage_shards_nums"]

        # 清洗
        if not params["is_allow_alone_etl_config"] or self.collector_plugin.bk_data_id:
            self.collector_plugin.etl_config = params["etl_config"]
            self._update_or_create_etl(self.collector_plugin, params, is_create)

        self.collector_plugin.save()

        return is_create

    def update_or_create(self, params: dict) -> dict:
        """
        创建采集插件
        1. 创建采集插件
        2. 根据需要初始化 data id & 数据链路
        3. 根据需要创建清洗规则
        4. 根据需要创建存储集群
        """

        is_create = self._update_or_create(params)

        # add user_operation_record
        user_operation_record.delay(
            {
                "username": get_request_username(),
                "biz_id": self.collector_plugin.bk_biz_id,
                "record_type": UserOperationTypeEnum.COLLECTOR_PLUGIN,
                "record_object_id": self.collector_plugin.collector_plugin_id,
                "action": UserOperationActionEnum.CREATE.value if is_create else UserOperationActionEnum.UPDATE.value,
                "params": model_to_dict(self.collector_plugin, exclude=["deleted_at", "created_at", "updated_at"]),
            }
        )

        return {
            "collector_plugin_id": self.collector_plugin.collector_plugin_id,
            "collector_plugin_name": self.collector_plugin.collector_plugin_name,
        }

    def _build_model_fields(self, params: dict, *args):
        model_fields = {}
        for key in args:
            if key in params.keys():
                model_fields[key] = params[key]
            else:
                model_fields[key] = getattr(self.collector_plugin, key)
        return model_fields
