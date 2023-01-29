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

import os

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from apps.api import TransferApi
from apps.exceptions import ApiResultError
from apps.log_databus.constants import (
    BUILT_IN_MAX_DATAID,
    BUILT_IN_MIN_DATAID,
    STORAGE_CLUSTER_TYPE,
    TargetNodeTypeEnum,
    TargetObjectTypeEnum,
)
from apps.log_databus.handlers.collector import build_bk_data_name
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.models import CollectorConfig
from apps.log_databus.serializers import CollectorEtlStorageSerializer
from apps.log_search.constants import CollectorScenarioEnum, EncodingsEnum


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--es_cluster_id", type=int, help="es storage cluster id(default:0)")

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
        default_es_cluster_id = options.get("es_cluster_id")

        builtin_collect_file_path = os.environ.get("BK_LOG_BUILTIN_COLLECT_CONFIG_PATH", "")
        if not builtin_collect_file_path:
            print("config file not exists. do nothing")
            return

        # Yaml Format:
        # builtin_collect:
        #    - dataid: 11000001
        #      name: bk-log-search-saas
        #    - dataid: 11000002
        #      name: bk-log-search-api
        with open(builtin_collect_file_path, encoding="utf-8") as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        config = config or {}

        for built_in_info in config.get("builtin_collect") or []:
            try:
                if not (BUILT_IN_MIN_DATAID <= int(built_in_info["dataId"]) <= BUILT_IN_MAX_DATAID):
                    print("data id (%s) not valid, do nothing" % built_in_info["dataId"])
                    continue

                # 1. 创建采集配置
                collect_config = self.create_or_update_build_in_collect(built_in_info)

                # 2. 申请内置dataid
                # collector_scenario.update_or_create_data_id
                self.create_data_id(collect_config)

                # 3. 创建存储相关结果表 & 创建索引集
                self.create_etl_handle_and_index_set(collect_config, default_es_cluster_id)

            except Exception as e:  # pylint: disable=broad-except
                print(f"create build in collect error({e}), ")

    @classmethod
    def create_or_update_build_in_collect(cls, built_in_info):
        data_id = built_in_info["dataId"]
        module_name = built_in_info["moduleName"]

        try:
            collect_config = CollectorConfig.objects.get(bk_data_id=data_id)
        except CollectorConfig.DoesNotExist:
            collect_config = CollectorConfig.objects.create(
                **{
                    "bk_app_code": settings.APP_CODE,
                    "bk_data_id": data_id,
                    "collector_config_name": module_name,
                    "collector_config_name_en": str(module_name).replace("-", "_"),
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
                    "custom_type": "log",
                    "category_id": "other_rt",
                    "bk_biz_id": settings.BLUEKING_BK_BIZ_ID,
                    "collector_scenario_id": CollectorScenarioEnum.CUSTOM.value,
                    "created_by": settings.SYSTEM_USE_API_ACCOUNT,
                    "updated_by": settings.SYSTEM_USE_API_ACCOUNT,
                }
            )
        collect_config.save()
        return collect_config

    @classmethod
    def create_data_id(cls, collect_config):
        data_name = build_bk_data_name(collect_config.bk_biz_id, collect_config.collector_config_name_en)
        params = {
            "data_name": data_name,
            "etl_config": "bk_flat_batch",
            "data_description": collect_config.description,
            "source_label": "bk_monitor",
            "type_label": "log",
            "option": {"encoding": EncodingsEnum.UTF.value, "is_log_data": True, "allow_metrics_missing": True},
            "bk_username": settings.SYSTEM_USE_API_ACCOUNT,
            "operator": settings.SYSTEM_USE_API_ACCOUNT,
            "bk_data_id": collect_config.bk_data_id,
        }
        try:
            return TransferApi.create_data_id(params)
        except ApiResultError:
            params["data_id"] = params["bk_data_id"]
            return TransferApi.modify_data_id(params)

    @classmethod
    def create_etl_handle_and_index_set(cls, collect_config, storage_cluster_id):
        if not storage_cluster_id:
            es_clusters = TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True})
            for es in es_clusters:
                if es["cluster_config"]["is_default_cluster"]:
                    storage_cluster_id = es["cluster_config"]["cluster_id"]

        if not storage_cluster_id:
            raise ValueError("default es cluster not exists.")

        etl_storage = CollectorEtlStorageSerializer(
            data={
                "etl_config": "bk_log_text",
                "table_id": collect_config.collector_config_name_en,
                "storage_cluster_id": storage_cluster_id,
                "retention": settings.ES_STORAGE_DEFAULT_DURATION,
                "allocation_min_days": 0,
                "etl_params": {"retain_original_text": True, "separator_regexp": "", "separator": ""},
                "fields": [],
            }
        )
        etl_storage.is_valid()
        params = etl_storage.data
        params["username"] = settings.SYSTEM_USE_API_ACCOUNT
        etl_handler = EtlHandler.get_instance(collect_config.collector_config_id)
        etl_handler.update_or_create(**params)
