# -*- coding: utf-8 -*-
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker


class AgentChecker(Checker):
    CHECKER_NAME = "agent"

    def run(self):
        pass
