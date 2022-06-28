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
import base64
import logging
from blueapps.conf.default_settings import BASE_DIR
from apps.api import JobApi
from home_application.constants import (
    DEFAULT_BK_USERNAME,
    DEFAULT_EXECUTE_SCRIPT_ACCOUNT,
    SCRIPT_TYPE_PYTHON,
    RETRY_TIMES,
    WAIT_FOR_RETRY,
)

logger = logging.getLogger()


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


def get_job_instance_status(bk_biz_id, job_instance_id) -> dict:
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


def get_job_instance_log(bk_biz_id, job_instance_id) -> dict:
    result = {"status": False, "data": [], "message": ""}
    params = {"bk_biz_id": bk_biz_id, "job_instance_id": job_instance_id}
    for i in range(RETRY_TIMES):
        try:
            get_job_instance_log_result = JobApi.get_job_instance_log(params)[0]
            if get_job_instance_log_result.get("is_finished", False):
                result["data"] = get_job_instance_log_result["step_results"][0]["ip_logs"]
                result["status"] = True
                break
            time.sleep(WAIT_FOR_RETRY)
        except Exception as e:  # pylint: disable=broad-except
            result["message"] = f"获取作业执行日志失败, 报错为: {e}"
            return result

    if not result["status"]:
        result["message"] = "获取作业执行日志超时"
        return result

    return result


def dict_to_str(data):
    if data:
        kv_list = []
        for k, v in data.items():
            kv_list.append(f"{k}={v}")
        return ",".join(kv_list)
    return ""
