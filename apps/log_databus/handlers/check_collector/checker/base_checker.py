# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from apps.log_databus.constants import CheckStatusEnum
from apps.log_databus.handlers.check_collector.base import CheckCollectorRecord


class Checker(ABC):
    CHECKER_NAME = ""

    def __init__(self, check_collector_record: CheckCollectorRecord):
        self.record = check_collector_record

    @abstractmethod
    def _run(self):
        raise NotImplementedError

    def run(self):
        if self.record.get_check_status() != CheckStatusEnum.STARTED.value:
            return

        self._run()

    def append_normal_info(self, info: str):
        self.record.append_normal_info(info=info, prefix=self.CHECKER_NAME)

    def append_warning_info(self, info: str):
        self.record.append_warning_info(info=info, prefix=self.CHECKER_NAME)

    def append_error_info(self, info: str):
        self.record.append_error_info(info=info, prefix=self.CHECKER_NAME)
