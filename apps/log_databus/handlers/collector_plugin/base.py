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
    CollectorConfigNotExistException,
    CollectorPluginNameDuplicateException,
    CollectorPluginNotExistException,
)
from apps.log_databus.handlers.collector import CollectorHandler
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
    """
    采集插件
    """

    def __init__(self, collector_plugin_id=None):
        """
        初始化
        """

        if collector_plugin_id:
            self.collector_plugin_id = collector_plugin_id
            try:
                self.collector_plugin: CollectorPlugin = CollectorPlugin.objects.get(
                    collector_plugin_id=collector_plugin_id
                )
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

    def _post_operation(self, params: dict) -> None:
        """
        额外的自定义操作，在采集插件创建完成后执行
        """

        pass

    def _update_or_create_etl_storage(self, params: dict, is_create: bool) -> None:
        """
        创建或更新采集插件清洗入库
        """

        raise NotImplementedError

    def _update_or_create_instance_etl(self, collect_config: CollectorConfig, params: dict) -> None:
        """
        创建或更新实例清洗入库
        """

        raise NotImplementedError

    @transaction.atomic()
    def _update_or_create(self, params: dict) -> bool:
        """
        创建或更新插件
        """

        # 通用参数，允许更新
        collector_plugin_name = params["collector_plugin_name"]
        description = params.get("description")
        data_encoding = params.get("data_encoding")
        is_display_collector = params["is_display_collector"]
        is_allow_alone_data_id = params["is_allow_alone_data_id"]
        is_allow_alone_etl_config = params["is_allow_alone_etl_config"]
        is_allow_alone_storage = params["is_allow_alone_storage"]
        model_fields = {
            "collector_plugin_name": collector_plugin_name,
            "description": description,
            "data_encoding": data_encoding,
            "is_display_collector": is_display_collector,
            "is_allow_alone_data_id": is_allow_alone_data_id,
            "is_allow_alone_etl_config": is_allow_alone_etl_config,
            "is_allow_alone_storage": is_allow_alone_storage,
            "storage_cluster_id": params.get("storage_cluster_id"),
            "retention": params.get("retention", 1),
            "allocation_min_days": params.get("allocation_min_days", 0),
            "storage_replies": params.get("storage_replies", 1),
            "storage_shards_nums": params.get("storage_shards_nums", 1),
            "etl_config": params.get("etl_config"),
            "etl_params": params.get("etl_params", {}),
            "fields": params.get("fields", []),
            "params": params.get("params", []),
        }

        is_create_public_data_id = params.get("create_public_data_id", False)

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
                self.collector_plugin: CollectorPlugin = CollectorPlugin.objects.create(**model_fields)
            except IntegrityError:
                logger.warning(f"collector plugin name duplicate => [{collector_plugin_name}]")
                raise CollectorPluginNameDuplicateException()

            # DATA_ID
            if not is_allow_alone_data_id or is_create_public_data_id:
                # 绑定采集链路
                if not data_link_id:
                    data_links = DataLinkConfig.objects.filter(bk_biz_id__in=[0, bk_biz_id]).order_by("data_link_id")
                    if data_links.exists():
                        self.collector_plugin.data_link_id = data_links.first().data_link_id
                # 创建 DATA ID
                self.collector_plugin.bk_data_id = CollectorHandler.update_or_create_data_id(self.collector_plugin)

            is_create = True

        # 更新插件
        else:

            # 更新字段
            for key, val in model_fields.items():
                setattr(self.collector_plugin, key, val)

            # 更新可见性
            self.collector_plugin.change_collector_display_status(is_display_collector)

            # DATA_ID
            if not is_allow_alone_data_id or is_create_public_data_id:
                self.collector_plugin.bk_data_id = CollectorHandler.update_or_create_data_id(self.collector_plugin)

            is_create = False

        # 清洗
        if not is_allow_alone_etl_config or self.collector_plugin.bk_data_id:
            self._update_or_create_etl_storage(params, is_create)

        # 额外操作
        self._post_operation(params)

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
            "etl_processor": self.collector_plugin.etl_processor,
            "collector_scenario_id": self.collector_plugin.collector_scenario_id,
            "category_id": self.collector_plugin.category_id,
            "data_encoding": self.collector_plugin.data_encoding,
            "is_display": self.collector_plugin.is_display_collector,
            "is_allow_alone_data_id": self.collector_plugin.is_allow_alone_data_id,
            "is_allow_alone_etl_config": self.collector_plugin.is_allow_alone_etl_config,
            "is_allow_alone_storage": self.collector_plugin.is_allow_alone_storage,
        }

        # 不独立DATAID
        if not self.collector_plugin.is_allow_alone_data_id:
            build_in_params.update(
                {
                    "bk_data_id": self.collector_plugin.bk_data_id,
                    "data_link_id": self.collector_plugin.data_link_id,
                }
            )
        # 允许独立DATAID，指定数据归属业务
        else:
            bkdata_biz_id = self.collector_plugin.bkdata_biz_id
            if bkdata_biz_id:
                build_in_params.update({"bkdata_biz_id": bkdata_biz_id})

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
                    "table_id": self.collector_plugin.table_id,
                    "bkbase_table_id": self.collector_plugin.bkbase_table_id,
                }
            )

        # 独立清洗入库
        if not self.collector_plugin.is_allow_alone_etl_config:
            build_in_params.update(
                {
                    "etl_config": self.collector_plugin.etl_config,
                    "etl_params": self.collector_plugin.etl_params,
                    "fields": self.collector_plugin.fields,
                }
            )

        return build_in_params

    def replenish_params(self, params: dict) -> dict:
        """
        补全不足的参数
        """

        all_param_keys = [
            "storage_cluster_id",
            "retention",
            "allocation_min_days",
            "storage_replies",
            "storage_shards_nums",
            "storage_shards_size",
            "etl_params",
            "fields",
            "etl_config",
        ]
        for key in all_param_keys:
            if key not in params.keys():
                params[key] = getattr(self.collector_plugin, key)
        return params

    def create_instance(self, params: dict) -> dict:
        """
        采集插件实例化
        """

        # 构造参数
        build_in_params = self.build_instance_params()
        params.update(build_in_params)

        # 补全不足的参数
        params = self.replenish_params(params)

        # 创建采集项
        result = CollectorHandler().update_or_create(params)
        collector_config_id = result["collector_config_id"]
        try:
            collector_config: CollectorConfig = CollectorConfig.objects.get(collector_config_id=collector_config_id)
        except CollectorConfig.DoesNotExist:
            raise CollectorConfigNotExistException()

        # 清洗入库
        if self.collector_plugin.is_allow_alone_etl_config:
            self._update_or_create_instance_etl(collector_config, params)

        return {
            "collector_config_id": collector_config.collector_config_id,
            "collector_config_name": collector_config.collector_config_name,
        }
