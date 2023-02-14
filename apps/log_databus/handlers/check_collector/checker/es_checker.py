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
import datetime

from apps.api import TransferApi
from apps.log_databus.constants import RETRY_TIMES, INDEX_WRITE_PREFIX, INDEX_READ_SUFFIX
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_esquery.utils.es_client import get_es_client
from apps.log_measure.exceptions import EsConnectFailException
from apps.utils.time_handler import strftime_local


class EsChecker(Checker):
    CHECKER_NAME = "es checker"

    def __init__(self, table_id, bk_data_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_id = table_id
        self.bk_data_name = bk_data_name
        self.result_table = {}
        self.cluster_config = {}
        self.cluster_id = 0
        # 物理索引列表
        self.indices = []
        self.es_client = None
        self.index_pattern = ""

    def pre_run(self):
        try:
            result = TransferApi.get_result_table_storage(
                {"result_table_list": self.table_id, "storage_type": "elasticsearch"}
            )
            self.result_table = result.get(self.table_id, {})
            self.cluster_config = self.result_table.get("cluster_config", {})
            self.cluster_id = self.cluster_config.get("cluster_id", 0)
        except Exception as e:
            self.append_error_info(f"[TransferApi] [get_result_table_storage] 失败, err: {e}")

    def _run(self):
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
                self.append_warning_info(f"获取物理索引失败第{i + 1}次, err: {e}")
        if not indices:
            self.append_error_info("获取物理索引为空")
            return
        for i in indices:
            if i["index_pattern"] == self.bk_data_name or i["index_pattern"] == self.table_id.replace(".", "_"):
                self.index_pattern = i["index_pattern"]
                self.indices = i["indices"]
                break
        if not self.indices:
            self.append_error_info("获取物理索引为空")
            return

        for i in self.indices:
            self.append_normal_info("物理索引: {}, 健康: {}, 状态: {}".format(i["index"], i["health"], i["status"]))

        hot_node_count = 0

        for node in StorageHandler(self.cluster_id).cluster_nodes():
            if node.get("tag") == "hot":
                hot_node_count += 1

        latest_indices = self.indices[0]
        query_body = {"size": 1}
        query_data = self.es_client.search(index=latest_indices["index"], body=query_body)
        latest_data = query_data.get("hits", {}).get("hits", [])
        latest_data = latest_data[0] if latest_data else None
        self.append_normal_info("最近物理索引:{} 最新一条数据为:{}".format(latest_indices["index"], latest_data))

        if latest_indices["pri"] < hot_node_count:
            self.append_warning_info(
                "最近物理索引分片数量小于热节点分片数量, 可能会造成性能问题, 当前索引分片数{}, 热节点分片数{}".format(latest_indices["pri"], hot_node_count)
            )

    def get_es_client(self):
        es_client = None
        auth_info = self.result_table.get("auth_info", {})
        username = auth_info.get("username")
        password = auth_info.get("password")
        for i in range(RETRY_TIMES):
            try:
                es_client = get_es_client(
                    version=self.cluster_config["version"],
                    hosts=[self.cluster_config["domain_name"]],
                    username=username,
                    password=password,
                    scheme=self.cluster_config["schema"],
                    port=self.cluster_config["port"],
                    sniffer_timeout=600,
                    verify_certs=False,
                )
                if es_client is not None:
                    break
            except Exception as e:
                self.append_warning_info(f"创建es_client失败第{i + 1}次, err: {e}")

        if es_client and not es_client.ping(params={"request_timeout": 10}):
            self.append_error_info(EsConnectFailException().message)
            return

        self.es_client = es_client

    def get_index_alias(self):
        """获取物理索引的alias情况"""
        if not self.es_client:
            self.append_error_info("es_client不存在, 跳过检查index_alias")
            return
        index_alias_info_dict = self.es_client.indices.get_alias(index=[i["index"] for i in self.indices])

        now_datetime = strftime_local(datetime.datetime.now(), "%Y%m%d")

        now_read_index_alias = "{}_{}{}".format(self.index_pattern, now_datetime, INDEX_READ_SUFFIX)
        now_write_index_alias = "{}{}_{}".format(INDEX_WRITE_PREFIX, now_datetime, self.index_pattern)

        now_read_index_alias_exist = False
        now_write_index_alias_exist = False

        for i in self.indices:
            # index 物理索引名
            physical_index = i["index"]
            aliases = index_alias_info_dict.get(physical_index)
            if not aliases:
                self.append_error_info(f"物理索引: {physical_index} 不存在alias别名")
                continue

            if physical_index.startswith(INDEX_WRITE_PREFIX):
                self.append_warning_info(f"集群存在 write_ 开头的索引: \n{physical_index}")
                return

            if aliases.get(now_read_index_alias):
                now_read_index_alias_exist = True
            if aliases.get(now_write_index_alias):
                now_write_index_alias_exist = True

            if now_read_index_alias_exist and now_write_index_alias_exist:
                self.append_normal_info(f"索引: [{self.index_pattern}] 当天[{now_datetime}]读写别名已成功创建")
                return

        if self.index_pattern:
            self.append_error_info(f"索引: [{self.index_pattern}] 当天[{now_datetime}]读写别名未成功创建")
