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

from elasticsearch import Elasticsearch

from apps.api import TransferApi
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_measure.exceptions import EsConnectFailException
from home_application.constants import CHECK_STORY_5, INDEX_WRITE_PREFIX, RETRY_TIMES
from home_application.handlers.collector_checker.base import BaseStory

logger = logging.getLogger()


class CheckESStory(BaseStory):
    name = CHECK_STORY_5

    def __init__(self, table_id, bk_data_name):
        super().__init__()
        self.table_id = table_id
        self.bk_data_name = bk_data_name
        self.result_table = {}
        self.cluster_config = {}
        self.cluster_id = 0
        # 物理索引列表
        self.indices = []
        self.es_client = None

    def pre_run(self):
        try:
            result = TransferApi.get_result_table_storage(
                {"result_table_list": self.table_id, "storage_type": "elasticsearch"}
            )
            self.result_table = result.get(self.table_id, {})
            self.cluster_config = self.result_table.get("cluster_config", {})
            self.cluster_id = self.cluster_config.get("cluster_id", 0)
        except Exception as e:
            self.report.add_error(f"[TransferApi] [get_result_table_storage] 失败, err: {e}")

    def check(self):
        self.pre_run()
        self.get_es_client()
        self.get_indices()
        self.get_index_alias()

    def get_indices(self):
        """
        获取物理索引的名称
        """
        indices = None
        # 可能会请求失败, 重试几次
        for i in range(RETRY_TIMES):
            try:
                indices = StorageHandler(self.cluster_id).indices()
                if indices is not None:
                    break
            except Exception as e:  # disable
                self.report.add_warning(f"获取物理索引失败第{i+1}次, err: {e}")

        for i in indices:
            if i["index_pattern"] == self.bk_data_name:
                self.indices = i["indices"]
        if not self.indices:
            self.report.add_error("获取物理索引为空")
            return
        for i in self.indices:
            self.report.add_info("物理索引: {}, 健康: {}, 状态: {}".format(i["index"], i["health"], i["status"]))

    def get_es_client(self):
        es_client = None
        domain_name = self.cluster_config["domain_name"]
        port = self.cluster_config["port"]
        auth_info = self.result_table.get("auth_info", {})
        username = auth_info.get("username")
        password = auth_info.get("password")
        http_auth = (username, password) if username and password else None
        for i in range(RETRY_TIMES):
            try:
                es_client = Elasticsearch(
                    hosts=[domain_name],
                    http_auth=http_auth,
                    scheme="http",
                    port=port,
                    verify_certs=False,
                    timeout=10,
                )
                if es_client is not None:
                    break
            except Exception as e:
                self.report.add_warning(f"创建es_client失败第{i + 1}次, err: {e}")

        if not es_client.ping(params={"request_timeout": 10}):
            self.report.add_error(EsConnectFailException().message)
            return

        self.es_client = es_client

    def get_index_alias(self):
        """获取物理索引的alias情况"""
        if not self.es_client:
            self.report.add_error("es_client不存在, 跳过检查index_alias")
            return
        index_alias_info_dict = self.es_client.indices.get_alias(index=[i["index"] for i in self.indices])
        for i in self.indices:
            # index 物理索引名
            physical_index = i["index"]
            if not index_alias_info_dict.get(physical_index):
                self.report.add_error(f"物理索引: {physical_index} 不存在alias别名")
                continue
            index_alias_list = list(index_alias_info_dict[physical_index]["aliases"].keys())
            write_prefix_index_list = []
            for index_alias in index_alias_list:
                if index_alias.startswith(INDEX_WRITE_PREFIX):
                    write_prefix_index_list.append(index_alias)
            if write_prefix_index_list:
                self.report.add_warning(
                    "物理索引: {} 存在 write_ 开头的alias别名: \n{}".format(physical_index, "\n".join(write_prefix_index_list))
                )
            else:
                self.report.add_info(f"物理索引: {physical_index} alias别名正常")
