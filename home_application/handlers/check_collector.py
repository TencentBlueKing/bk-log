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
import sys

from apps.log_databus.models import CollectorConfig
from home_application.constants import (
    SELF_CHECK_STEPS,
)
from home_application.handlers.collector_checker.check_collector_config import CheckCollectorConfig


class CollectorCheckHandler(object):
    status = False
    data = []
    steps = dict()

    def __init__(self, collector_config_id, hosts):
        try:
            self.collector_config = CollectorConfig.objects.get(collector_config_id=collector_config_id)
        except CollectorConfig.DoesNotExist:
            print(f"不存在的采集项ID: {collector_config_id}")
            sys.exit(1)
        self.hosts = hosts
        self.init_hosts()

    def get_collector_config_hosts(self):
        collector_hosts = self.collector_config.target_nodes
        # TODO: 将target_nodes里的节点转成对应的HOST信息
        return collector_hosts

    def init_hosts(self):
        """判断入参hosts是否在采集项的target_nodes里, 如果在则返回存在的列表"""
        collector_hosts = self.get_collector_config_hosts()
        need_check_hosts = []
        if self.hosts:
            for host in self.hosts:
                if host in collector_hosts:
                    need_check_hosts.append(host)
                else:
                    print(f"host: {host}不在该采集项的目标节点里")
            self.hosts = need_check_hosts
        else:
            self.hosts = collector_hosts

    def register_step(self, step, *args):
        self.steps[step.step_name] = step(*args)

    def command_format(self):
        if self.status:
            icon = "[+]"
            message = "检查采集项成功"
            print(f"{icon} {message}\n")
            for di in self.data:
                for ri in di.data:
                    print(f"{ri.data} {ri.message}\n")
        else:
            icon = "[-]"
            error_step = len(self.data)
            message = f"检查采集项失败, 报错在第{error_step}步: {SELF_CHECK_STEPS[error_step-1]}"
            print(f"{icon} {message}\n")
            for ri in self.data[-1].data:
                print(f"{ri.message}\n")

    def pre_run(self):
        self.register_step(CheckCollectorConfig, self.collector_config, self.hosts)

    def run(self):
        self.pre_run()
        for i in range(len(SELF_CHECK_STEPS)):
            step_name = SELF_CHECK_STEPS[i]
            step = self.steps[step_name]
            step_result = step.run()
            self.data.append(step_result)
            if not step_result.status:
                break

        if len(SELF_CHECK_STEPS) == [i.status for i in self.data].count(True):
            self.status = True
