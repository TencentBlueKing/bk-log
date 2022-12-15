# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from apps.log_databus.handlers.check_collector.base import CheckCollectorHandler


class Checker(ABC):
    CHECKER_NAME = ""

    def __init__(self, check_collector_handler: CheckCollectorHandler):
        self.handler = check_collector_handler

    @abstractmethod
    def run(self):
        raise NotImplemented
