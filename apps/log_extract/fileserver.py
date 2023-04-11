# coding=utf-8
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
from __future__ import division

import base64
import re
import shlex
from typing import List, Tuple

from django.conf import settings
from django.template import engines
from django.utils.translation import ugettext_lazy as _

from apps.api import JobApi
from apps.log_extract import constants
from apps.log_extract.constants import JOB_SCRIPT_TYPE
from apps.log_extract.exceptions import PipelineApiFailed


class FileServer(object):
    @classmethod
    def execute_script(cls, content, ip, bk_biz_id, operator, account, task_name, script_params=None):
        # 调用JOB平台的fast_execute_script 执行脚本
        # content：为脚本内容
        # 返回值：字典
        kwargs = {
            "bk_username": operator,
            "bk_biz_id": bk_biz_id,
            "script_content": content,
            "script_type": JOB_SCRIPT_TYPE,
            "script_language": JOB_SCRIPT_TYPE,
            "account_alias": account,
            "task_name": task_name,
            "target_server": {},
        }
        if settings.ENABLE_DHCP:
            kwargs["target_server"]["host_id_list"] = [item["bk_host_id"] for item in ip]
        else:
            kwargs["target_server"]["ip_list"] = [{"ip": item["ip"], "bk_cloud_id": item["bk_cloud_id"]} for item in ip]

        if script_params:
            kwargs["script_param"] = script_params
        return JobApi.fast_execute_script(kwargs, request_cookies=False)

    @staticmethod
    def get_task_id(task_result):
        return task_result["job_instance_id"]

    @staticmethod
    def is_finished_for_single_ip(query_result):
        return query_result["finished"]

    @staticmethod
    def get_detail_for_ips(query_result):
        step_instance, *_ = query_result["step_instance_list"]
        return step_instance["step_ip_result_list"]

    @staticmethod
    def get_step_instance(query_result):
        step_instance, *_ = query_result["step_instance_list"]
        return step_instance

    @staticmethod
    def get_step_instance_id(query_result):
        step_instance, *_ = query_result["step_instance_list"]
        return step_instance["step_instance_id"]

    @staticmethod
    def get_job_instance_status(query_result):
        return query_result["job_instance"]["status"]

    @staticmethod
    def get_job_tag(query_result):
        return query_result.get("tag", "")

    @staticmethod
    def get_host_list_log(host_list, job_instance_id, step_instance_id, bk_biz_id):
        # 有bk_host_id优先取bk_host_id
        host_id_list = []
        ip_list = []
        for ip in host_list:
            if ip.get("bk_host_id"):
                host_id_list.append(ip["bk_host_id"])
                continue
            ip.pop("bk_host_id", None)
            ip_list.append(ip)

        return JobApi.batch_get_job_instance_ip_log(
            params={
                "bk_biz_id": bk_biz_id,
                "ip_list": ip_list,
                "host_id_list": host_id_list,
                "job_instance_id": job_instance_id,
                "step_instance_id": step_instance_id,
            },
            request_cookies=False,
        )

    @classmethod
    def query_task_result(cls, task_instance_id, operator, bk_biz_id):
        result = JobApi.get_job_instance_status(
            params={
                "bk_biz_id": bk_biz_id,
                "job_instance_id": task_instance_id,
                "bk_username": operator,
                "return_ip_result": True,
            },
            request_cookies=False,
        )
        return result

    @classmethod
    def file_distribution(
        cls, file_source_list, file_target_path, target_server, bk_biz_id, operator, account, task_name
    ):
        # file_source_list:文件源信息
        # file_target_path:目标路径
        # target_ip_list:目标IP列表
        # bk_biz_id: 业务ID
        for file_source in file_source_list:
            ip_list = file_source["server"].pop("ip_list", [])
            if settings.ENABLE_DHCP:
                file_source["server"]["host_id_list"] = [item["bk_host_id"] for item in ip_list]
            else:
                file_source["server"]["ip_list"] = [
                    {"ip": item["ip"], "bk_cloud_id": item["bk_cloud_id"]} for item in ip_list
                ]

        kwargs = {
            "bk_username": operator,
            "bk_biz_id": bk_biz_id,
            "file_source_list": file_source_list,
            "account": account,
            "account_alias": account,
            "file_target_path": file_target_path,
            "task_name": task_name,
            "target_server": {},
        }
        if settings.ENABLE_DHCP:
            kwargs["target_server"]["host_id_list"] = [item.bk_host_id for item in target_server]
        else:
            kwargs["target_server"]["ip_list"] = [
                {"ip": item.ip, "bk_cloud_id": item.bk_cloud_id} for item in target_server
            ]

        task_result = JobApi.fast_transfer_file(kwargs, raw=True, request_cookies=False)
        if not task_result["result"]:
            raise PipelineApiFailed(PipelineApiFailed.MESSAGE.format(message=task_result["message"]))
        return task_result["data"]

    @classmethod
    def get_script_info(cls, action, args=None, bk_os_type=constants.LINUX):
        action_map = {
            "list_file": lambda: [
                args["file_path"],
                args["file_type"],
                args["is_search_child"],
                args["time_range"],
                args["start_time"],
                args["end_time"],
            ],
            "pack": lambda: [
                args["dst_path"],
                "",
                args["target_file_name"],
                args["is_distributing_packing"],
                args["filter_type"],
                args["filter_cond1"],
                args["filter_cond2"],
                args["max_file_size_limit"],
            ],
            "cos": lambda: [args["dst_path"], args["cos_pack_file_name"], args["target_dir"], args["run_ver"]],
        }
        params = action_map.get(action, lambda: [])()
        params = " ".join([shlex.quote(str(param_str)) for param_str in params])
        content = cls._render(cls._get_script_content(action), args)
        return {"content": content, "script_params": cls.job_encode(params)}

    @classmethod
    def _render(cls, content, params: dict):
        engine = engines["django"]
        template = engine.from_string(content)
        return cls.job_encode(template.render(params))

    @classmethod
    def _get_script_content(cls, action):
        script_path = f"{action}.sh"
        with open(f"{constants.SCRIPT_PATH}{script_path}", "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def get_packing_path(cls, os_type):
        if os_type == constants.WINDOWS:
            return constants.PACKING_PATH_WINDOWS
        return constants.PACKING_PATH_LINUX

    @staticmethod
    def get_max_file_size_limit() -> int:
        return 1024 * 1024 * settings.EXTRACT_PACK_MAX_FILE_SZIE_LIMIT

    @classmethod
    def get_bk_log(cls, log_content):
        try:
            log_content = re.search(r"#####bklog_begin######(.*)#####bklog_end######", log_content).groups()[0]
        except AttributeError as e:
            raise Exception(_("获取脚本内容异常({})".format(e)))
        return log_content

    @classmethod
    def parse_windows_path(cls, path: str):
        if not path.startswith("/cygdrive/"):
            return path
        path = path.replace("/cygdrive/", "")
        paths = path.split("/")
        return f"{paths[0]}:\\" + "\\".join(paths[1:])

    @classmethod
    def job_encode(cls, content):
        return base64.b64encode(content.encode("utf-8")).decode("utf-8")

    @staticmethod
    def get_bk_kv_log(log_content: str) -> List[Tuple[str, str]]:
        return re.findall(constants.BKLOG_TASK_LOG_REG_MATCH, log_content)
