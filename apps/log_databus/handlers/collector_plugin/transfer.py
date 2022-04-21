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

from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.serializers import CollectorEtlStorageSerializer


class TransferCollectorPluginHandler(CollectorPluginHandler):
    def _build_plugin_etl_template(self, params: dict) -> dict:
        params["etl_template"].update(
            {
                "retention": self.collector_plugin.retention,
                "table_id": self.collector_plugin.collector_plugin_name_en,
                "etl_config": self.collector_plugin.etl_config,
                "storage_cluster_id": self.collector_plugin.storage_cluster_id,
                "allocation_min_days": self.collector_plugin.allocation_min_days,
                "storage_replies": self.collector_plugin.storage_replies,
            }
        )
        serializer = CollectorEtlStorageSerializer(data=params["etl_template"])
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def _create_instance_etl_storage(self, params: dict) -> None:
        etl_config = {
            "etl_config": params.get("etl_config"),
            "table_id": params.get("table_id"),
            "etl_params": params.get("etl_params"),
            "fields": params.get("fields"),
            "storage_cluster_id": params.get("storage_cluster_id"),
            "retention": params.get("retention"),
            "allocation_min_days": params.get("allocation_min_days"),
            "storage_replies": params.get("storage_replies"),
        }
        EtlHandler(self.collector_config_id).update_or_create(**etl_config)
