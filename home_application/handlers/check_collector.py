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
from apps.log_databus.constants import TargetNodeTypeEnum
from apps.log_databus.models import CollectorConfig
from home_application.constants import CHECK_STORY_0
from home_application.handlers.collector_checker import (
    CheckAgentStory,
    CheckESStory,
    CheckKafkaStory,
    CheckRouteStory,
    CheckTransferStory,
    Report,
)


class CollectorCheckHandler(object):
    def __init__(self, collector_config_id, hosts=None, debug=False):
        self.collector_config_id = collector_config_id
        self.hosts = hosts
        self.debug = debug
        # 先定义字段
        self.subscription_id = None
        self.table_id = None
        self.bk_data_name = None
        self.bk_data_id = None
        self.bk_biz_id = None
        self.target_server = None
        self.collector_config = None

        self.story_report = []
        self.kafka = []
        self.latest_log = []

    def pre_run(self):
        init_check_report = Report(CHECK_STORY_0)
        # 检查采集项ID是否存在
        try:
            self.collector_config = CollectorConfig.objects.get(collector_config_id=self.collector_config_id)
        except CollectorConfig.DoesNotExist:
            init_check_report.add_error(f"不存在的采集项ID: {self.collector_config_id}")
            self.story_report.append(init_check_report)
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
                hosts = self.hosts.split("=")[1].split(",")
                for host in hosts:
                    ip_list.append({"bk_cloud_id": int(host.split(":")[0]), "ip": host.split(":")[1]})
                self.target_server = {"ip_list": ip_list}
            except Exception as e:  # pylint: disable=broad-except
                init_check_report.add_error(f"输入合法的hosts, err: {e}, 参考: 0:ip1,0:ip2,1:ip3")
                self.story_report.append(init_check_report)
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
                init_check_report.add_error(f"暂不支持该target_node_type: {target_node_type}")
                self.story_report.append(init_check_report)
        if not self.story_report:
            init_check_report.add_info("初始化检查成功")
            self.story_report.append(init_check_report)

    def run(self):
        self.pre_run()
        if self.story_report[0].has_problem():
            return

        check_agent_report = self.check_agent()
        self.story_report.append(check_agent_report)

        check_route_report = self.check_route()
        self.story_report.append(check_route_report)

        check_kafka_report = self.check_kafka()
        self.story_report.append(check_kafka_report)

        check_transfer_report = self.check_transfer()
        self.story_report.append(check_transfer_report)

        check_es_report = self.check_es()
        self.story_report.append(check_es_report)

    def command_format(self):
        is_success = "失败"
        if not any([i.has_problem() for i in self.story_report]):
            is_success = "成功"
        print(f"\n采集项检查{is_success}\n\n\n")
        for story_m in self.story_report:
            print("-" * 100)
            if story_m.has_problem():
                self.error(story_m.name, "存在问题, 查看详细报错")
            else:
                self.info(story_m.name, "正常")
            if self.debug:
                for story_info in story_m.info:
                    self.info(story_m.name, story_info)
            for story_warning in story_m.warning:
                self.warning(story_m.name, story_warning)
            for story_error in story_m.error:
                self.error(story_m.name, story_error)
            print("\n")

    def api_format(self):
        is_success = "失败"
        outputs = []
        if not any([i.has_problem() for i in self.story_report]):
            is_success = "成功"
        outputs.append(f"\n采集项检查{is_success}\n\n\n")
        for story_m in self.story_report:
            outputs.append("-" * 100 + "\n")
            if story_m.has_problem():
                outputs.append(f"[ERROR] [{story_m.name}] 存在问题, 查看详细报错\n")
            else:
                outputs.append(f"[INFO] [{story_m.name}] 正常\n")
            if self.debug:
                for story_info in story_m.info:
                    outputs.append(f"[INFO] [{story_m.name}] {story_info}\n")
            for story_warning in story_m.warning:
                outputs.append(f"[WARNING] [{story_m.name}] {story_warning}\n")
            for story_error in story_m.error:
                outputs.append(f"[ERROR] [{story_m.name}] {story_error}\n")
            outputs.append("\n")

        return "".join(outputs).encode("utf-8")

    @staticmethod
    def info(story_name, message):
        print(f"\033[32m[INFO] [{story_name}]: \033[0m{message}")

    @staticmethod
    def warning(story_name, message):
        print(f"\033[33m[WARNING] [{story_name}]: \033[0m{message}")

    @staticmethod
    def error(story_name, message):
        print(f"\033[31m[ERROR] [{story_name}]: \033[0m{message}")

    def check_agent(self):
        story = CheckAgentStory(
            bk_biz_id=self.bk_biz_id,
            target_server=self.target_server,
            subscription_id=self.subscription_id,
        )
        story.check()
        return story.get_report()

    def check_route(self):
        """
        检查步骤第二步, 会把获得的kafka信息放到类实例里供第三步使用
        """
        story = CheckRouteStory(self.bk_data_id)
        story.check()
        self.kafka = story.kafka
        return story.get_report()

    def check_kafka(self):
        """
        检查步骤第三步, 通过第二步获取到的kafka信息, 以及测试消费组查看是否有数据
        """
        story = CheckKafkaStory(self.kafka)
        story.check()
        self.latest_log = story.latest_log
        return story.get_report()

    def check_transfer(self):
        """
        检查步骤第四步, 包含以下两个检查项目
        - 通过第三步获取到的数据, 进行清洗, 看清洗是不是成功
        - 获取transfer
        """
        story = CheckTransferStory(collector_config=self.collector_config, latest_log=self.latest_log)
        story.check()
        return story.get_report()

    def check_es(self):
        story = CheckESStory(self.table_id, self.bk_data_name)
        story.check()
        return story.get_report()
