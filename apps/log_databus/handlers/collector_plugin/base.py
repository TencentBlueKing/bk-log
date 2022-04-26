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

from django.db import IntegrityError, transaction
from django.utils.module_loading import import_string

from apps.constants import UserOperationActionEnum, UserOperationTypeEnum
from apps.decorators import user_operation_record
from apps.log_databus.constants import (
    ETLProcessorChoices,
)
from apps.log_databus.exceptions import (
    CollectorPluginNameDuplicateException,
    CollectorPluginNotExistException,
)
from apps.log_databus.models import CollectorConfig, CollectorPlugin, DataLinkConfig
from apps.models import model_to_dict
from apps.utils.local import get_request_username

logger = logging.getLogger("app")


def get_collector_plugin_handler(etl_processor, collector_plugin_id=None):
    mapping = {
        ETLProcessorChoices.BKBASE.value: "BKBaseCollectorPluginHandler",
    }
    try:
        collector_plugin_handler = import_string(
            "apps.log_databus.handlers.collector_plugin.{}.{}".format(etl_processor, mapping.get(etl_processor))
        )
        return collector_plugin_handler(collector_plugin_id)
    except ImportError as error:
        raise NotImplementedError(f"CollectorPluginHandler of {etl_processor} not implement, error: {error}")


class CollectorPluginHandler:
    collector_plugin_id: int = None
    collector_plugin: CollectorPlugin = None

    def __init__(self, collector_plugin_id=None):
        if collector_plugin_id:
            self._get_collector_plugin(collector_plugin_id)

    def _get_collector_plugin(self, collector_plugin_id: int) -> None:
        """
        绑定采集插件Model
        """

        try:
            self.collector_plugin = CollectorPlugin.objects.get(collector_plugin_id=collector_plugin_id)
            self.collector_plugin_id = collector_plugin_id
        except CollectorPlugin.DoesNotExist:
            raise CollectorPluginNotExistException()

    def _pre_check_en_name(self, en_name: str) -> None:
        """
        校验英文名称，不能与插件或实例的名字重复
        """

        config_name_duplicate = CollectorConfig.objects.filter(collector_config_name_en=en_name).exists()
        plugin_name_duplicate = CollectorPlugin.objects.filter(collector_plugin_name_en=en_name).exists()
        if config_name_duplicate or plugin_name_duplicate:
            raise CollectorPluginNameDuplicateException()

    def _update_or_create_data_id(self) -> None:
        """
        创建或更新DATAID
        """

        raise NotImplementedError

    def _update_or_create_etl_storage(self, params: dict) -> None:
        """
        创建或更新清洗入库
        """

        raise NotImplementedError

    @transaction.atomic()
    def _update_or_create(self, params: dict) -> bool:
        """
        创建或更新插件
        """

        # 通用参数，允许更新
        collector_plugin_name = params["collector_plugin_name"]
        description = params["description"] if params.get("description") else params["collector_plugin_name"]
        data_encoding = params.get("data_encoding")
        is_enabled_display_collector = params["is_enabled_display_collector"]
        is_allow_alone_data_id = params["is_allow_alone_data_id"]
        is_allow_alone_etl_config = params["is_allow_alone_etl_config"]
        is_allow_alone_storage = params["is_allow_alone_storage"]
        model_fields = {
            "collector_plugin_name": collector_plugin_name,
            "description": description,
            "data_encoding": data_encoding,
            "is_enabled_display_collector": is_enabled_display_collector,
            "is_allow_alone_data_id": is_allow_alone_data_id,
            "is_allow_alone_etl_config": is_allow_alone_etl_config,
            "is_allow_alone_storage": is_allow_alone_storage,
        }

        # 创建插件
        if not self.collector_plugin:

            # 创建后不允许更新的参数
            bk_biz_id = params["bk_biz_id"]
            collector_plugin_name_en = params["collector_plugin_name_en"]
            collector_scenario_id = params["collector_scenario_id"]
            category_id = params["category_id"]
            data_link_id = params.get("data_link_id")
            bkdata_biz_id = params.get("bkdata_biz_id")
            etl_processor = params["etl_processor"]
            model_fields.update(
                {
                    "bk_biz_id": bk_biz_id,
                    "collector_plugin_name_en": collector_plugin_name_en,
                    "collector_scenario_id": collector_scenario_id,
                    "category_id": category_id,
                    "data_link_id": data_link_id,
                    "bkdata_biz_id": bkdata_biz_id,
                    "etl_processor": etl_processor,
                }
            )

            # 校验英文名
            self._pre_check_en_name(collector_plugin_name_en)

            # 创建采集插件
            try:
                self.collector_plugin = CollectorPlugin.objects.create(**model_fields)
            except IntegrityError:
                logger.warning(f"collector plugin name duplicate => [{collector_plugin_name}]")
                raise CollectorPluginNameDuplicateException()

            # DATA_ID
            is_create_public_data_id = params.get("create_public_data_id", False)
            if not is_allow_alone_data_id or is_create_public_data_id:
                # 绑定链路
                if not data_link_id:
                    data_links = DataLinkConfig.objects.filter(bk_biz_id__in=[0, bk_biz_id]).order_by("data_link_id")
                    if data_links.exists():
                        self.collector_plugin.data_link_id = data_links.first().data_link_id
                # 创建 DATA ID
                self._update_or_create_data_id()

            is_create = True

        # 更新插件
        else:

            # 更新字段
            for key, val in model_fields.items():
                setattr(self.collector_plugin, key, val)

            # 更新可见性
            self.collector_plugin.change_collector_display_status(params["is_enabled_display_collector"])

            # DATA_ID
            is_create_public_data_id = params.get("create_public_data_id", False)
            if not is_allow_alone_data_id or is_create_public_data_id:
                self._update_or_create_data_id()

            is_create = False

        # 存储
        if not is_allow_alone_storage or self.collector_plugin.bk_data_id:
            self.collector_plugin.storage_cluster_id = params["storage_cluster_id"]
            self.collector_plugin.retention = params["retention"]
            self.collector_plugin.allocation_min_days = params["allocation_min_days"]
            self.collector_plugin.storage_replies = params["storage_replies"]
            self.collector_plugin.storage_shards_nums = params["storage_shards_nums"]

        # 清洗
        if not is_allow_alone_etl_config or self.collector_plugin.bk_data_id:
            self.collector_plugin.etl_config = params["etl_config"]
            self.collector_plugin.etl_template = params["etl_template"]
            self.collector_plugin.params = params["params"]
            self._update_or_create_etl_storage(params)

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

    def build_instance_params(self) -> dict:
        """
        构造插件实例更新字段
        """

        build_in_params = {
            "collector_scenario_id": self.collector_plugin.collector_scenario_id,
            "category_id": self.collector_plugin.category_id,
            "data_encoding": self.collector_plugin.data_encoding,
            "is_display": self.collector_plugin.is_enabled_display_collector,
            "is_allow_alone_data_id": self.collector_plugin.is_allow_alone_data_id,
            "is_allow_alone_etl_config": self.collector_plugin.is_allow_alone_etl_config,
            "is_allow_alone_storage": self.collector_plugin.is_allow_alone_storage,
        }

        # 数据归属Biz
        bkdata_biz_id = self.collector_plugin.bkdata_biz_id
        if bkdata_biz_id:
            build_in_params.update({"bkdata_biz_id": bkdata_biz_id})

        # 独立DATAID
        if not self.collector_plugin.is_allow_alone_data_id:
            build_in_params.update(
                {
                    "bk_data_id": self.collector_plugin.bk_data_id,
                    "data_link_id": self.collector_plugin.data_link_id,
                }
            )

        # 独立存储
        if not self.collector_plugin.is_allow_alone_storage:
            build_in_params.update(
                {
                    "storage_cluster_id": self.collector_plugin.storage_cluster_id,
                    "retention": self.collector_plugin.retention,
                    "allocation_min_days": self.collector_plugin.allocation_min_days,
                    "storage_replies": self.collector_plugin.storage_replies,
                    "storage_shards_nums": self.collector_plugin.storage_shards_nums,
                    "storage_shards_size": self.collector_plugin.storage_shards_size,
                }
            )

        # 独立清洗入库
        if not self.collector_plugin.is_allow_alone_etl_config:
            build_in_params.update(
                {
                    "etl_processor": self.collector_plugin.etl_processor,
                    "etl_config": self.collector_plugin.etl_config,
                }
            )

        return build_in_params
