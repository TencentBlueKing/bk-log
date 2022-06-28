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
import json

from apps.log_databus.models import CollectorConfig
from home_application.constants import CHECK_STORIES, CHECK_STORY_1, CHECK_STORY_2, CHECK_STORY_3
from home_application.handlers.collector_checker.base import Report
from home_application.handlers.collector_checker.check_agent import (
    fast_execute_script,
    get_job_instance_log,
    dict_to_str,
)
from home_application.handlers.collector_checker.check_kafka import get_kafka_test_group_latest_log
from home_application.handlers.collector_checker.check_route import get_route


class CollectorCheckHandler(object):
    def __init__(self, collector_config_id, hosts, debug):
        try:
            self.collector_config = CollectorConfig.objects.get(collector_config_id=collector_config_id)
        except CollectorConfig.DoesNotExist:
            print(f"不存在的采集项ID: {collector_config_id}")
            sys.exit(1)
        self.hosts = hosts
        self.debug = debug

        self.story_report = []
        self.kafka = []
        self.latest_log = []

    def run(self):
        check_agent_report = self.check_agent()
        self.story_report.append(check_agent_report)
        if check_agent_report.has_problem():
            return

        check_route_report = self.check_route()
        self.story_report.append(check_route_report)
        if check_route_report.has_problem():
            return

        check_kafka_report = self.check_kafka()
        self.story_report.append(check_kafka_report)
        if check_kafka_report.has_problem():
            return

    def command_format(self):
        is_success = "失败"
        if len(self.story_report) == len(CHECK_STORIES):
            is_success = "成功"
        print(f"\n采集项检查{is_success}\n\n")
        for story_m in self.story_report:
            print("-" * 100)
            if story_m.has_problem:
                self.error(f"{story_m.name} 存在问题, 查看详细报错")
            else:
                self.info(f"{story_m.name} 正常")
            if self.debug:
                for story_info in story_m.info:
                    self.info(story_info)
            for story_warning in story_m.warning:
                self.warning(story_warning)
            for story_error in story_m.error:
                self.error(story_error)
            print("\n")

    @staticmethod
    def info(message):
        print(f"\033[32m[INFO]: \033[0m{message}")

    @staticmethod
    def warning(message):
        print(f"\033[33m[WARNING]: \033[0m{message}")

    @staticmethod
    def error(message):
        print(f"\033[31m[ERROR]: \033[0m{message}")

    def check_agent(self):
        """
        检查步骤第一步, 检查bkunifylogbeat, gse_agent的状态
        """
        story_report = Report(CHECK_STORY_1)
        if self.hosts:
            target_server = {"ip_list": self.hosts}
        else:
            topo_node_list = [
                {"id": i["bk_inst_id"], "node_type": i["bk_obj_id"]} for i in self.collector_config.target_nodes
            ]
            target_server = {"topo_node_list": topo_node_list}
        # 快速执行脚本
        fast_execute_script_result = fast_execute_script(
            bk_biz_id=self.collector_config.bk_biz_id,
            target_server=target_server,
            subscription_id=self.collector_config.subscription_id,
        )
        if not fast_execute_script_result["status"]:
            story_report.add_error(fast_execute_script_result["message"])
            return story_report

        # 获取脚本执行结果
        get_job_instance_log_result = get_job_instance_log(
            bk_biz_id=self.collector_config.bk_biz_id,
            job_instance_id=fast_execute_script_result["data"]["job_instance_id"],
        )
        if not get_job_instance_log_result["status"]:
            story_report.add_error(get_job_instance_log_result["message"])
            return story_report

        instance_logs = get_job_instance_log_result["data"]
        # 处理执行日志
        for i in instance_logs:
            bk_cloud_id = i["bk_cloud_id"]
            ip = i["ip"]
            log_contents = i["log_content"].split("\n")
            for log_content in log_contents:
                if not log_content:
                    continue
                try:
                    log_content = json.loads(log_content)
                    module = log_content["module"]
                    item = log_content["item"]
                    data = dict_to_str(log_content["data"])
                    message = log_content["message"]
                    if log_content["status"]:
                        story_report.add_info(f"[{bk_cloud_id}:{ip}] [{module}:{item}], data: {data}, {message}")
                    else:
                        story_report.add_error(f"[{bk_cloud_id}:{ip}] [{module}:{item}], data: {data}, 报错信息: {message}")
                except Exception as e:  # pylint: disable=broad-except
                    story_report.add_error(f"[{bk_cloud_id}:{ip}] 获取脚本执行结果失败, 报错为: {str(e)}")

        return story_report

    def check_route(self):
        """
        检查步骤第二步, 会把获得的kafka信息放到类实例里供第三步使用
        """
        story_report = Report(CHECK_STORY_2)
        get_route_result = get_route(self.collector_config.bk_data_id)
        if not get_route_result["status"]:
            story_report.add_error(get_route_result["message"])
            return story_report

        for r in get_route_result["data"]:
            story_report.add_info(
                "[ROUTE] route_name: {}, stream_name: {}, topic_name: {}, partition: {}, ip: {}, port: {}".format(
                    r["route_name"], r["stream_name"], r["kafka_topic_name"], r["kafka_partition"], r["ip"], r["port"]
                )
            )

        self.kafka = get_route_result["data"]
        return story_report

    def check_kafka(self):
        """
        检查步骤第三步, 通过第二步获取到的kafka信息, 以及测试消费组查看是否有数据
        """
        story_report = Report(CHECK_STORY_3)
        for kafka_info in self.kafka:
            get_kafka_latest_log_result = get_kafka_test_group_latest_log(kafka_info)
            if not get_kafka_latest_log_result["status"]:
                story_report.add_error(get_kafka_latest_log_result["message"])
                continue

            self.latest_log.extend(get_kafka_latest_log_result["data"])
            story_report.info(
                "[Kafka] topic_name: {}, partition: {}有数据".format(
                    kafka_info["kafka_topic_name"], kafka_info["kafka_partition"]
                )
            )

        return story_report
