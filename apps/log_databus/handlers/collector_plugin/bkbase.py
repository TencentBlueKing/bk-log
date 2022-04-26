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

from apps.api import BkDataAccessApi, BkDataDatabusApi
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
    META_DATA_ENCODING,
)
from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.utils.local import get_request_username


class BKBaseCollectorPluginHandler(CollectorPluginHandler):
    """
    数据平台
    """

    def _update_or_create_data_id(self) -> None:
        """
        更新或创建DATAID
        """

        maintainers = {self.collector_plugin.updated_by, self.collector_plugin.created_by}
        maintainers.discard(ADMIN_REQUEST_USER)
        if not maintainers:
            raise Exception(f"dont have enough maintainer only {ADMIN_REQUEST_USER}")

        bkdata_params = {
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
                "data_encoding": (
                    self.collector_plugin.data_encoding if self.collector_plugin.data_encoding else META_DATA_ENCODING
                ),
                "sensitivity": BKDATA_DATA_SENSITIVITY,
                "description": self.collector_plugin.description,
                "preassigned_data_id": self.collector_plugin.bk_data_id,
            },
        }

        # 更新
        if self.collector_plugin.bk_data_id:
            bkdata_params.update({"raw_data_id": self.collector_plugin.bk_data_id})
            BkDataAccessApi.deploy_plan_put(bkdata_params)
            return

        # 创建
        result = BkDataAccessApi.deploy_plan_post(bkdata_params)
        self.collector_plugin.bk_data_id = result["raw_data_id"]
        self.collector_plugin.save()

    def _stop_bkdata_clean(self, bkdata_result_table_id: str) -> None:
        """停止清洗任务"""

        BkDataDatabusApi.delete_tasks(
            params={
                "result_table_id": bkdata_result_table_id,
                "bk_username": get_request_username(),
            }
        )

    def _start_bkdata_clean(self, bkdata_result_table_id: str) -> None:
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

    def _restart_bkdata_clean(self, bkdata_result_table_id: str) -> None:
        """
        重启清洗任务
        """

        self._stop_bkdata_clean(bkdata_result_table_id)
        self._start_bkdata_clean(bkdata_result_table_id)

    def _update_or_create_etl_storage(self, params: dict) -> None:
        """
        创建或更新清洗入库
        """

        bkdata_params = {
            "raw_data_id": self.collector_plugin.bk_data_id,
            "result_table_name": self.collector_plugin.collector_plugin_name_en,
            "result_table_name_alias": self.collector_plugin.collector_plugin_name_en,
            "clean_config_name": self.collector_plugin.collector_plugin_name,
            "description": self.collector_plugin.description,
            "bk_biz_id": self.collector_plugin.bk_biz_id,
            "bk_username": get_request_username(),
            "fields": [],
            "json_config": "",
        }
        bkdata_params.update(self.collector_plugin.etl_template)

        # 如参数不完整则不创建
        template_params = params.get("params", {}).get("template_params", [])
        if len(template_params):
            return

        # 创建清洗
        if self.collector_plugin.processing_id:
            result = BkDataDatabusApi.databus_cleans_post(bkdata_params)
            self._start_bkdata_clean(result["result_table_id"])
            self.collector_plugin.processing_id = result["processing_id"]
            self.collector_plugin.table_id = result["result_table_id"]
            self.collector_plugin.save()
            return

        # 更新清洗
        bkdata_params.update({"processing_id": self.collector_plugin.processing_id})
        BkDataDatabusApi.databus_cleans_put(bkdata_params, request_cookies=False)
        # 更新rt之后需要重启清洗任务
        self._stop_bkdata_clean(self.collector_plugin.table_id)
        self._start_bkdata_clean(self.collector_plugin.table_id)

        # 入库参数
        storage_params = {
            "bk_biz_id": self.collector_plugin.bk_biz_id,
            "raw_data_id": self.collector_plugin.bk_data_id,
            "data_type": "clean",
            "result_table_name": self.collector_plugin.collector_plugin_name_en,
            "result_table_name_alias": self.collector_plugin.collector_plugin_name_en,
            "storage_type": "es",
            "storage_cluster": self.collector_plugin.storage_cluster_id,
            "expires": f"{self.collector_plugin.retention}d",
            "fields": self.collector_plugin.etl_template.get("fields", []),
        }

        # 更新入库
        if self.collector_plugin.storage_table_id:
            storage_params.update({"result_table_id": self.collector_plugin.storage_table_id})
            BkDataDatabusApi.databus_data_storages_put(storage_params)
            return

        # 创建入库
        BkDataDatabusApi.databus_data_storages_post(storage_params)
        db_list = BkDataDatabusApi.get_config_db_list({"raw_data_id": self.collector_plugin.bk_data_id})
        if len(db_list):
            self.collector_plugin.storage_table_id = db_list[0]["result_table_id"]
            self.collector_plugin.save()
