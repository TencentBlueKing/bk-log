# -*- coding: utf-8 -*-
import os

from celery.task import task

from apps.log_databus.constants import GSE_PATH, IPC_PATH
from apps.log_databus.handlers.check_collector.base import CheckCollectorRecord
from apps.log_databus.handlers.check_collector.checker.agent_checker import AgentChecker
from apps.log_databus.models import CollectorConfig


class CheckCollectorHandler:
    HANDLER_NAME = "启动入口"

    def __init__(self, collector_config_id: int, hosts: str, gse_path=None, ipc_path=None):
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

        self.record = CheckCollectorRecord(collector_config_id=self.collector_config_id, hosts=self.hosts)

        if not self.record.is_exist():
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

    def run(self):
        self.pre_run()
        self.execute_check()

    @task
    def execute_check(self):
        AgentChecker(
            bk_biz_id=self.bk_biz_id,
            target_server=self.target_server,
            subscription_id=self.subscription_id,
            gse_path=self.gse_path,
            ipc_path=self.ipc_path,
            check_collector_record=self.record,
        ).run()

    def get_record_infos(self) -> str:
        return self.record.get_infos()
