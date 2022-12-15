# -*- coding: utf-8 -*-
import os
from enum import Enum
from typing import Union

from dataclasses import dataclass, asdict, fields
from django.core.cache import cache

from apps.log_databus.constants import CHECK_COLLECTOR_CACHE_KEY_PREFIX, CHECK_COLLECTOR_ITEM_CACHE_TIMEOUT, GSE_PATH, \
    IPC_PATH, CheckStatusEnum
from apps.log_databus.models import CollectorConfig


@dataclass
class CheckResult:
    status: str
    info: list

    to_dict = asdict

    @classmethod
    def from_dict(cls, data: dict):
        init_fields = {f.name for f in fields(cls) if f.init}
        filtered_data = {k: data.pop(k, None) for k in init_fields}
        instance = cls(**filtered_data)
        return instance


class CheckCollectorRecord:
    @staticmethod
    def generate_check_result_cache_key(collector_config_id: int, hosts: str) -> str:
        """
        生成检查结果的缓存key
        :param collector_config_id: 采集项ID
        :param hosts: host字符串 example "{bk_cloud_id}:{ip},{bk_cloud_id}:{ip},{bk_cloud_id}:{ip}"
        :return: 检查结果的缓存key
        """
        return f"{CHECK_COLLECTOR_CACHE_KEY_PREFIX}_{collector_config_id}_{hosts}"

    @classmethod
    def get_check_result(cls, cache_key: str) -> Union[CheckResult, None]:
        cache_result = cache.get(cache_key, None)

        if cache_result:
            return CheckResult.from_dict(cache_result)
        else:
            None

    def __init__(self, collector_config_id: int, hosts: str):
        self.collector_config_id = collector_config_id
        self.hosts = hosts

        self.check_result_cache_key = self.generate_check_result_cache_key(collector_config_id=self.collector_config_id,
                                                                           hosts=self.hosts)

        self.check_record = self.get_check_result(self.check_result_cache_key)

    def is_exist(self):
        return self.check_record is None

    def new_record(self):
        record = CheckResult(status=CheckStatusEnum.WAIT.value, info=[])
        self.check_record = record
        self.save_check_record()

    def save_check_record(self):
        if not self.is_exist():
            return

        cache.set(self.check_result_cache_key, self.check_record.to_dict(), CHECK_COLLECTOR_ITEM_CACHE_TIMEOUT)

    def append_info(self, info: str):
        if not self.is_exist():
            return

        self.check_record.info.append(info)
        self.save_check_record()

    def append_normal_info(self, info: str, prefix: str):
        info = f"[normal][{prefix}]{info}"
        self.append_info(info)

    def append_warning_info(self, info: str, prefix: str):
        info = f"[warning][{prefix}]{info}"
        self.append_info(info)

    def append_error_info(self, info: str, prefix: str):
        info = f"[error][{prefix}]{info}"
        self.append_info(info)

    def change_status(self, status):
        self.check_record.status = status
        self.save_check_record()


class CheckCollectorHandler:
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
            self.record.append_error_info("采集项ID查找失败")
            self.record.change_status(CheckStatusEnum.FINISH.value)
            return

        # 快速脚本执行的参数target_server
        self.target_server = {}
        self.bk_biz_id = self.collector_config.bk_biz_id
        self.bk_data_id = self.collector_config.bk_data_id
        self.bk_data_name = self.collector_config.bk_data_name
        self.table_id = self.collector_config.table_id
        self.subscription_id = self.collector_config.subscription_id
