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

import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from apps.api import TransferApi
from apps.log_databus.constants import (
    TargetObjectTypeEnum,
    TargetNodeTypeEnum,
    BUILT_IN_MIN_DATAID,
    BUILT_IN_MAX_DATAID,
)
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.models import CollectorConfig, DataLinkConfig
from apps.log_databus.serializers import CollectorEtlStorageSerializer
from apps.log_search.constants import EncodingsEnum, CollectorScenarioEnum


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--data_link_id", type=int, help="data link id(default:0)")

    def handle(self, **options):
        """
        [
            {
                "data_id": 1110001,
                "module_name": "bklog",
            },
            {
                "data_id": 1110002,
                "module_name": "bkmonitor"
            },
        ]
        """
        build_in_platform_data_id = os.environ.get("platBuiltInCollect", [])

        data_link = DataLinkConfig.objects.filter(bk_biz_id=0, is_active=True).first()
        if not data_link:
            raise ValueError("default data link not exists.")

        for built_in_info in build_in_platform_data_id:
            try:
                if not (BUILT_IN_MIN_DATAID <= int(built_in_info["data_id"]) <= BUILT_IN_MAX_DATAID):
                    print("data id (%s) not valid, do nothing" % built_in_info["data_id"])
                    continue

                # 1. 创建采集配置
                collect_config = self.create_or_update_build_in_collect(built_in_info, data_link)

                # 2. 申请内置dataid
                # collector_scenario.update_or_create_data_id
                self.create_data_id(collect_config, data_link)

                # 3. 创建存储相关结果表 & 创建索引集
                self.create_etl_handle_and_index_set(collect_config)

            except Exception as e:  # noqa
                print(f"create build in collect error({e}), ")

    @classmethod
    def create_or_update_build_in_collect(cls, built_in_info, default_data_link):
        data_id = built_in_info["data_id"]
        module_name = built_in_info["module_name"]

        try:
            collect_config = CollectorConfig.objects.get(bk_data_id=data_id)
        except CollectorConfig.DoesNotExist:
            collect_config = CollectorConfig.objects.create(
                **{
                    "bk_app_code": settings.APP_CODE,
                    "bk_data_id": data_id,
                    "collector_config_name": module_name,
                    "collector_config_name_en": module_name,
                    "target_object_type": TargetObjectTypeEnum.HOST.value,
                    "target_node_type": TargetNodeTypeEnum.INSTANCE.value,
                    "target_nodes": [],
                    "description": _("平台内置采集项 ") + module_name,
                    "data_encoding": EncodingsEnum.UTF.value,
                    "params": {
                        "conditions": {
                            "match_content": "",
                            "match_type": "include",
                            "separator": "",
                            "separator_filters": [],
                            "type": "match",
                        },
                        "encoding": "UTF-8",
                        "paths": ["/built_in/collector/ignore/me"],
                    },
                    "is_active": True,
                    "category_id": "custom",
                    "bk_biz_id": settings.BLUEKING_BK_BIZ_ID,
                    "data_link_id": default_data_link.data_link_id,
                    "collector_scenario_id": CollectorScenarioEnum.ROW.value,
                    "created_by": settings.SYSTEM_USE_API_ACCOUNT,
                    "updated_by": settings.SYSTEM_USE_API_ACCOUNT,
                }
            )
        collect_config.save()
        return collect_config

    @classmethod
    def create_data_id(cls, collect_config, data_link):
        data_name = f"{collect_config.bk_biz_id}_{settings.TABLE_ID_PREFIX}_{collect_config.collector_config_name}"
        params = {
            "data_name": data_name,
            "etl_config": "bk_flat_batch",
            "data_description": collect_config.description,
            "source_label": "bk_monitor",
            "type_label": "log",
            "option": {"encoding": EncodingsEnum.UTF.value, "is_log_data": True, "allow_metrics_missing": True},
            "transfer_cluster_id": data_link.transfer_cluster_id,
            "mq_cluster": data_link.kafka_cluster_id,
            "bk_username": settings.SYSTEM_USE_API_ACCOUNT,
            "operator": settings.SYSTEM_USE_API_ACCOUNT,
            "bk_data_id": collect_config.bk_data_id,
        }
        return TransferApi.create_data_id(params)

    @classmethod
    def create_etl_handle_and_index_set(cls, collect_config):
        etl_storage = CollectorEtlStorageSerializer(
            data={
                "etl_config": "bk_log_text",
                "table_id": collect_config.collector_config_name,
                "storage_cluster_id": 3,
                "retention": settings.ES_STORAGE_DEFAULT_DURATION,
                "allocation_min_days": 0,
                "etl_params": {"retain_original_text": True, "separator_regexp": "", "separator": ""},
                "fields": [],
            }
        )
        etl_storage.is_valid()
        params = etl_storage.data
        params["username"] = settings.SYSTEM_USE_API_ACCOUNT
        EtlHandler(collect_config.collector_config_id).update_or_create(**params)
