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
import sys
import time
import base64
import json
import logging
from blueapps.conf.default_settings import BASE_DIR
from apps.api import JobApi
from apps.log_databus.models import CollectorConfig
from home_application.handlers.collector_checker.base import (
    BaseStory,
    BaseStep,
    register_story,
    register_step,
    StepReport,
)
from home_application.constants import (
    CHECK_STORY_1,
    CHECK_STORY_1_STEP_1,
    DEFAULT_BK_USERNAME,
    DEFAULT_EXECUTE_SCRIPT_ACCOUNT,
    SCRIPT_TYPE_PYTHON,
)

logger = logging.getLogger()


@register_story()
class CheckAgentStory(BaseStory):
    name = CHECK_STORY_1

    def __init__(self):
        self.hosts = []
        for i in sys.argv:
            if "collector_config_id" in i:
                collector_config_id = i.split("=")[1]
                self.collector_config = CollectorConfig.objects.get(collector_config_id=collector_config_id)
                continue
            if "hosts" in i:
                try:
                    # "0:ip1,0:ip2,1:ip3"
                    ip_list = []
                    hosts = i.split("=")[1].split(",")
                    for host in hosts:
                        ip_list.append({"bk_cloud_id": int(host.split(":")[0]), "ip": host.split(":")[1]})
                    self.hosts = ip_list
                except Exception as e:  # pylint: disable=broad-except
                    print(f"输入合法的hosts, {e}")


@register_step(CheckAgentStory)
class CheckAgent(BaseStep):
    name = CHECK_STORY_1_STEP_1

    def check(self):
        step_r = StepReport(self)
        if self.story.hosts:
            target_server = {"ip_list": self.story.hosts}
        else:
            topo_node_list = [
                {"id": i["bk_inst_id"], "node_type": i["bk_obj_id"]} for i in self.story.collector_config.target_nodes
            ]
            target_server = {"topo_node_list": topo_node_list}
        fast_execute_script_result = fast_execute_script(
            bk_biz_id=self.story.collector_config.bk_biz_id,
            target_server=target_server,
            subscription_id=self.story.collector_config.subscription_id,
        )
        if not fast_execute_script_result["status"]:
            step_r.error.append(fast_execute_script_result["message"])
            return step_r

        get_job_instance_log_result = get_job_instance_log(
            bk_biz_id=self.story.collector_config.bk_biz_id,
            job_instance_id=fast_execute_script_result["data"]["job_instance_id"],
        )
        step_r.info.extend(get_job_instance_log_result["data"])
        if not get_job_instance_log_result["status"]:
            step_r.error.append(get_job_instance_log_result["message"])
            return step_r
        return step_r


def fast_execute_script(bk_biz_id, target_server, subscription_id):
    result = {"status": False, "data": {}, "message": ""}
    script_param = f"--subscription_id={subscription_id}"
    params = {
        "bk_biz_id": bk_biz_id,
        "bk_username": DEFAULT_BK_USERNAME,
        "account": DEFAULT_EXECUTE_SCRIPT_ACCOUNT,
        "script_content": "",
        "target_server": target_server,
        "script_type": SCRIPT_TYPE_PYTHON,
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
        result["message"] = f"打开脚本{script_pwd}失败, 报错为: {e}"
        return result

    try:
        result["data"] = JobApi.fast_execute_script(params)
        result["status"] = True
    except Exception as e:  # pylint: disable=broad-except
        result["message"] = f"快速执行脚本失败, 报错为: {e}"
        return result

    return result


def get_job_instance_status(bk_biz_id, job_instance_id):
    result = {"status": False, "data": [], "message": ""}
    params = {"bk_biz_id": bk_biz_id, "job_instance_id": job_instance_id}
    for i in range(3):
        try:
            get_job_instance_status_result = JobApi.get_job_instance_status(params)
            if get_job_instance_status_result.get("is_finished", False):
                result["data"] = get_job_instance_status_result["blocks"][0]["step_ip_status"]
                result["status"] = True
                break
            time.sleep(10)
        except Exception as e:  # pylint: disable=broad-except
            result["message"] = f"获取作业执行状态失败, 报错为: {e}"
            return result
    if not result["status"]:
        result["message"] = "获取作业执行状态超时"

    return result


def get_job_instance_log(bk_biz_id, job_instance_id):
    result = {"status": False, "data": [], "message": ""}
    params = {"bk_biz_id": bk_biz_id, "job_instance_id": job_instance_id}
    instance_log = []
    is_finished = False
    for i in range(3):
        try:
            get_job_instance_log_result = JobApi.get_job_instance_log(params)[0]
            if get_job_instance_log_result.get("is_finished", False):
                instance_log = get_job_instance_log_result["step_results"][0]["ip_logs"]
                is_finished = True
                break
            time.sleep(5)
        except Exception as e:  # pylint: disable=broad-except
            result["message"] = f"获取作业执行日志失败, 报错为: {e}"
            return result
    if not is_finished:
        result["message"] = "获取作业执行日志超时"
        return result

    # 处理执行日志
    if [i["exit_code"] for i in instance_log].count(0) == len(instance_log):
        result["status"] = True
        result["message"] = "主机检查成功"
    else:
        result["message"] = "部分主机检查失败"

    for i in instance_log:
        bk_cloud_id = i["bk_cloud_id"]
        ip = i["ip"]
        is_success = "成功" if i["exit_code"] == 0 else "失败"
        result["data"].extend(["", ""])
        result["data"].append(f"主机: {bk_cloud_id}:{ip} {is_success}")
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
                    log_data = f"{module}:{item} 成功, data: {data}, {message}"
                else:
                    log_data = f"{module}:{item} 失败, data: {data}, 报错信息: {message}"
            except Exception as e:  # pylint: disable=broad-except
                log_data = f"获取脚本执行结果失败, 报错为: {e}"

            result["data"].append(log_data)

    return result


def dict_to_str(data):
    if data:
        kv_list = []
        for k, v in data.items():
            kv_list.append(f"{k}={v}")
        return ",".join(kv_list)
    return ""
