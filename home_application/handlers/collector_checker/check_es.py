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
import logging

from apps.api import TransferApi
from apps.log_databus.handlers.storage import StorageHandler
from home_application.constants import (
    CHECK_STORY_5,
)
from home_application.handlers.collector_checker.base import BaseStory

logger = logging.getLogger()


class CheckESStory(BaseStory):
    name = CHECK_STORY_5

    def __init__(self, table_id, bk_data_name):
        super().__init__()
        self.table_id = table_id
        self.bk_data_name = bk_data_name
        self.result_table = {}
        self.cluster_id = 0
        self.indices = []
        try:
            result = TransferApi.get_result_table_storage(
                {"result_table_list": self.table_id, "storage_type": "elasticsearch"}
            )
            self.result_table = result.get(self.table_id, {})
            self.cluster_id = self.result_table.get("cluster_config", {}).get("cluster_id", 0)
        except Exception as e:
            self.report.add_error(f"[TransferApi] [get_result_table_storage] 失败, err: {e}")

    def check(self):
        self.get_indices()

    def get_indices(self):
        indices = StorageHandler(self.cluster_id).indices()
        for i in indices:
            if i["index_pattern"] == self.bk_data_name:
                self.indices = i["indices"]
        if not self.indices:
            self.report.add_error("获取索引为空")
            return
        for i in self.indices:
            self.report.add_info("索引: {}, 健康: {}, 状态: {}".format(i["index"], i["health"], i["status"]))
