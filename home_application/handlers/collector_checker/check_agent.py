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
import time
import json
import base64
import logging
from collections import defaultdict

from blueapps.conf.default_settings import BASE_DIR
from apps.api import JobApi
from home_application.constants import (
    DEFAULT_BK_USERNAME,
    DEFAULT_EXECUTE_SCRIPT_ACCOUNT,
    ScriptType,
    RETRY_TIMES,
    WAIT_FOR_RETRY,
    CHECK_STORY_1,
    JOB_SUCCESS_STATUS,
    CHECK_AGENT_STEP,
    JOB_STATUS,
    GSE_PATH,
    IPC_PATH,
)
from home_application.handlers.collector_checker.base import BaseStory

logger = logging.getLogger()


class CheckAgentStory(BaseStory):
    name = CHECK_STORY_1

    def __init__(self, bk_biz_id: int, target_server: dict, subscription_id: int, gse_path: str, ipc_path: str):
        super().__init__()
        self.bk_biz_id = bk_biz_id
        self.target_server = target_server
        self.subscription_id = subscription_id
        self.gse_path = gse_path or GSE_PATH
        self.ipc_path = ipc_path or IPC_PATH
        self.job_instance_id = 0
        self.step_instance_id = 0
        self.ip_status = []
        self.ip_logs = []

    def check(self):
        self.execute_script()
        self.get_job_ip_status()
        self.get_job_ip_logs()
        self.format_ip_logs()

    def execute_script(self):
        script_param = (
            f"--subscription_id={self.subscription_id} --ipc_socket_file={self.ipc_path} --gse_path={self.gse_path}"
        )
        params = {
            "bk_biz_id": self.bk_biz_id,
            "bk_username": DEFAULT_BK_USERNAME,
            "account_alias": DEFAULT_EXECUTE_SCRIPT_ACCOUNT,
            "script_content": "",
            "target_server": self.target_server,
            "script_language": ScriptType.PYTHON.value,
            "script_param": base64.b64encode(script_param.encode()).decode(),
            "timeout": 7200,
            "task_name": "检查采集项配置",
        }
        script_pwd = os.path.join(BASE_DIR, "scripts/check_bkunifylogbeat/check.py")
        try:
            with open(script_pwd, "r") as f:
                params["script_content"] = base64.b64encode(f.read().encode()).decode()
                f.close()
        except Exception as e:  # pylint: disable=broad-except
            self.report.add_error(f"[快速执行脚本] 打开脚本{script_pwd}失败, 报错为: {e}")
            return

        try:
            result = JobApi.fast_execute_script(params)
            self.job_instance_id = result.get("job_instance_id", 0)
            self.step_instance_id = result.get("step_instance_id", 0)
        except Exception as e:  # pylint: disable=broad-except
            self.report.add_error(f"[快速执行脚本], 报错为: {e}")
            return

    def get_job_ip_status(self):
        """
        获取作业执行的各个cloud_id:ip的执行状态 -> self.ip_status
        """
        error_msg = ""
        params = {
            "bk_biz_id": self.bk_biz_id,
            "job_instance_id": self.job_instance_id,
            "bk_username": DEFAULT_BK_USERNAME,
            "return_ip_result": True,
        }
        for i in range(RETRY_TIMES):
            time.sleep(WAIT_FOR_RETRY)
            try:
                result = JobApi.get_job_instance_status(params=params, request_cookies=False)
                if not result.get("finished"):
                    continue
                step_instance_status = result.get("step_instance_list", [])
                if not step_instance_status:
                    error_msg = f"[获取作业执行状态] 作业: {self.job_instance_id}, 执行状态为空"
                for step in step_instance_status:
                    if step["step_instance_id"] == self.step_instance_id:
                        self.ip_status = step.get("step_ip_result_list", [])
                break

            except Exception as e:  # pylint: disable=broad-except
                error_msg = f"[获取作业执行状态] 作业: {self.job_instance_id}] 报错为: {e}"

        if not self.ip_status and not error_msg:
            error_msg = f"[获取作业执行状态] 作业: {self.job_instance_id}, 超时: {RETRY_TIMES*WAIT_FOR_RETRY}s"

        if error_msg != "":
            self.report.add_error(error_msg)

    def get_job_ip_logs(self):
        error_msg = ""
        if not self.ip_status:
            return
        params = {
            "bk_biz_id": self.bk_biz_id,
            "ip_list": [{"bk_cloud_id": i["bk_cloud_id"], "ip": i["ip"]} for i in self.ip_status],
            "job_instance_id": self.job_instance_id,
            "step_instance_id": self.step_instance_id,
        }
        try:
            result = JobApi.batch_get_job_instance_ip_log(params=params, request_cookies=False)
            self.ip_logs = result.get("script_task_logs", [])
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"[获取作业执行结果] 作业: {self.job_instance_id}, 报错为: {e}"
        if not self.ip_logs:
            error_msg = f"[获取作业执行结果] 作业: {self.job_instance_id}, 数据为空"
        if len(self.ip_status) != len(self.ip_logs):
            self.report.add_warning(f"[获取作业执行结果] 作业: {self.job_instance_id}, 数据不完整")
        if error_msg != "":
            self.report.add_error(error_msg)

    def format_ip_logs(self):
        format_ip_status = defaultdict(int)
        format_ip_log = defaultdict(str)

        for i in self.ip_status:
            format_ip_status["{}:{}".format(i["bk_cloud_id"], i["ip"])] = i["status"]

        for i in self.ip_logs:
            format_ip_log["{}:{}".format(i["bk_cloud_id"], i["ip"])] = i["log_content"]

        for host, status in format_ip_status.items():
            if status == JOB_SUCCESS_STATUS:
                if not format_ip_log.get(host, ""):
                    continue
                contents = format_ip_log[host].split("\n")
                for log_content in contents:
                    if not log_content:
                        continue
                    try:
                        log_content = json.loads(log_content)
                        report_message = []
                        if not log_content["status"]:
                            report_message.append(f"[{host}] 失败, 查看详情")
                        else:
                            report_message.append(f"[{host}] 成功")

                        for step in log_content["data"]:
                            module = step["module"]
                            item = CHECK_AGENT_STEP[step["item"]]
                            message = step["message"]
                            if step["status"]:
                                report_message.append(f"[{module}] [{item}] [成功] {message}")
                            else:
                                report_message.append(f"[{module}] [{item}] [失败] {message}")
                        # 增加个换行, 方便阅读
                        report_message.append("")
                        if not log_content["status"]:
                            self.report.add_error("\n".join(report_message))
                        else:
                            self.report.add_info("\n".join(report_message))

                    except Exception as e:  # pylint: disable=broad-except
                        self.report.add_error(f"[获取作业执行结果] [{host}] 获取脚本执行结果失败, 报错为: {str(e)}")
            else:
                self.report.add_error(f"[获取作业执行结果] [{host}] 脚本执行结果, 执行状态为: {JOB_STATUS.get(status, status)}")
