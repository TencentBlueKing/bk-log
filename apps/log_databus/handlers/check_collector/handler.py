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

from celery.task import task

from apps.log_databus.constants import GSE_PATH, IPC_PATH, CheckStatusEnum, TargetNodeTypeEnum
from apps.log_databus.handlers.check_collector.base import CheckCollectorRecord
from apps.log_databus.handlers.check_collector.checker.agent_checker import AgentChecker
from apps.log_databus.handlers.check_collector.checker.es_checker import EsChecker
from apps.log_databus.handlers.check_collector.checker.kafka_checker import KafkaChecker
from apps.log_databus.handlers.check_collector.checker.route_checker import RouteChecker
from apps.log_databus.handlers.check_collector.checker.transfer_checker import TransferChecker
from apps.log_databus.models import CollectorConfig


class CheckCollectorHandler:
    HANDLER_NAME = "启动入口"

    def __init__(self, collector_config_id: int, hosts: str = None, gse_path=None, ipc_path=None):
        self.collector_config_id = collector_config_id
        self.hosts = hosts

        # 先定义字段
        self.subscription_id = None
        self.table_id = None
        self.bk_data_name = None
        self.bk_data_id = None
        self.bk_biz_id = None
        self.target_server = None
        self.collector_config = None
        self.gse_path = gse_path or os.environ.get("GSE_ROOT_PATH", GSE_PATH)
        self.ipc_path = ipc_path or os.environ.get("GSE_IPC_PATH", IPC_PATH)

        self.story_report = []
        self.kafka = []
        self.latest_log = []
        cache_key = CheckCollectorRecord.generate_check_record_id(collector_config_id, hosts)

        self.record = CheckCollectorRecord(cache_key)

        if not self.record.is_exist() or self.record.get_check_status() == CheckStatusEnum.FINISH.value:
            self.record.new_record()

    def pre_run(self):
        try:
            self.collector_config = CollectorConfig.objects.get(collector_config_id=self.collector_config_id)
        except CollectorConfig.DoesNotExist:
            self.record.append_error_info("采集项ID查找失败", "pre-run")
            return

        # 快速脚本执行的参数target_server
        self.target_server = {}
        self.bk_biz_id = self.collector_config.bk_biz_id
        self.bk_data_id = self.collector_config.bk_data_id
        self.bk_data_name = self.collector_config.bk_data_name
        self.table_id = self.collector_config.table_id
        self.subscription_id = self.collector_config.subscription_id

        # 如果有输入host, 则覆盖, 否则使用collector_config.target_nodes
        if self.hosts:
            try:
                # "0:ip1,0:ip2,1:ip3"
                ip_list = []
                hosts = self.hosts.split(",")
                for host in hosts:
                    ip_list.append({"bk_cloud_id": int(host.split(":")[0]), "ip": host.split(":")[1]})
                self.target_server = {"ip_list": ip_list}
            except Exception as e:  # pylint: disable=broad-except
                self.record.append_error_info(f"输入合法的hosts, err: {e}, 参考: 0:ip1,0:ip2,1:ip3", self.HANDLER_NAME)
                return
        else:
            # 不同的target_node_type
            target_node_type = self.collector_config.target_node_type
            if target_node_type == TargetNodeTypeEnum.TOPO.value:
                self.target_server = {
                    "topo_node_list": [
                        {"id": i["bk_inst_id"], "node_type": i["bk_obj_id"]} for i in self.collector_config.target_nodes
                    ]
                }
            elif target_node_type == TargetNodeTypeEnum.INSTANCE.value:
                self.target_server = {"ip_list": self.collector_config.target_nodes}
            elif target_node_type == TargetNodeTypeEnum.DYNAMIC_GROUP.value:
                self.target_server = {"dynamic_group_list": self.collector_config.target_nodes}
            else:
                self.record.append_error_info(f"暂不支持该target_node_type: {target_node_type}", self.HANDLER_NAME)
        if not self.story_report:
            self.record.append_normal_info("初始化检查成功", self.HANDLER_NAME)

    def run(self):
        self.pre_run()
        if not self.record.have_error:
            self.execute_check()

    def execute_check(self):
        agent_checker = AgentChecker(
            bk_biz_id=self.bk_biz_id,
            target_server=self.target_server,
            subscription_id=self.subscription_id,
            gse_path=self.gse_path,
            ipc_path=self.ipc_path,
            check_collector_record=self.record,
        )

        agent_checker.run()

        router_checker = RouteChecker(self.bk_data_id, check_collector_record=self.record)
        router_checker.run()
        self.kafka = router_checker.kafka

        kafka_checker = KafkaChecker(self.kafka, check_collector_record=self.record)
        kafka_checker.run()
        self.latest_log = kafka_checker.latest_log

        transfer_checker = TransferChecker(
            collector_config=self.collector_config, latest_log=self.latest_log, check_collector_record=self.record
        )
        transfer_checker.run()

        es_checker = EsChecker(self.table_id, self.bk_data_name, check_collector_record=self.record)
        es_checker.run()

    def get_record_infos(self) -> str:
        return self.record.get_infos()


@task(ignore_result=True)
def async_run_check(collector_config_id: int, hosts: str = None):
    handler = CheckCollectorHandler(collector_config_id, hosts)
    handler.record.append_normal_info("check start", handler.HANDLER_NAME)
    handler.record.change_status(CheckStatusEnum.STARTED.value)
    handler.run()
    handler.record.append_normal_info("check finish", handler.HANDLER_NAME)
    handler.record.change_status(CheckStatusEnum.FINISH.value)
