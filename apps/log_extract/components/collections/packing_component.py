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
import html

from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from apps.log_extract import constants
from apps.log_extract.constants import (
    PACK_TASK_SCRIPT_NOT_HAVE_ENOUGH_CAP_ERROR_CODE,
    BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE,
)
from apps.log_extract.fileserver import FileServer
from apps.log_extract.models import Tasks
from apps.log_extract.utils.packing import (
    get_packed_dir_name,
    get_packed_file_name,
    get_filter_content,
)
from apps.utils.pipline import BaseService
from apps.utils.db import array_chunk
from apps.utils.log import logger


class FilePackingService(BaseService):
    name = _("文件打包")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name=_("任务ID"), key="task_id", type="int", required=True),
            Service.InputItem(name=_("文件列表"), key="file_path", type="list", required=True),
            Service.InputItem(name=_("目标ip列表"), key="ip_list", type="list", required=True),
            Service.InputItem(name=_("业务id"), key="bk_biz_id", type="str", required=True),
            Service.InputItem(name=_("作业执行人"), key="operator", type="str", required=False),
            Service.InputItem(name=_("用户名"), key="username", type="str", required=False),
            Service.InputItem(name=_("过滤类型"), key="filter_type", type="str", required=True),
            Service.InputItem(name=_("过滤内容"), key="filter_content", type="str", required=True),
            Service.InputItem(name=_("打包路径"), key="packing_path", type="str", required=True),
            Service.InputItem(name=_("执行脚本机器的用户名"), key="account", type="str", required=False),
        ]

    def outputs(self):
        return [
            Service.OutputItem(name=_("任务实例ID"), key="task_instance_id", type="int"),
            Service.OutputItem(name=_("task输出内容"), key="task_script_output", type="str"),
            Service.OutputItem(name=_("打包后的文件路径"), key="distribution_source_file_list", type="list"),
            Service.OutputItem(name=_("上传的服务器IP"), key="upload_source_ip", type="str"),
        ]

    def _poll_status(self, task_instance_id, operator, bk_biz_id):
        return FileServer.query_task_result(task_instance_id, operator, bk_biz_id)

    def _execute(self, data, parent_data):
        # 更新任务状态
        task_id = data.get_one_of_inputs("task_id")
        Tasks.objects.filter(task_id=task_id).update(download_status=constants.DownloadStatus.PACKING.value)
        ip_list = data.get_one_of_inputs("ip_list")
        file_path = data.get_one_of_inputs("file_path")
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        filter_content = data.get_one_of_inputs("filter_content")
        filter_type = data.get_one_of_inputs("filter_type")
        os_type = data.get_one_of_inputs("os_type")
        operator = data.get_one_of_inputs("operator")

        packed_file_name = get_packed_file_name(task_id)
        packing_path = data.get_one_of_inputs("packing_path")
        if not packing_path:
            packing_path = FileServer.get_packing_path(os_type=os_type)
        packed_dir_name = get_packed_dir_name(packing_path, task_id)
        task_name = "Packing"

        packing_context_kwargs = {
            "dst_path": packed_dir_name,
            "log_files": " ".join(file_path),
            "target_file_name": packed_file_name,
            "is_distributing_packing": "0",
            "filter_type": filter_type,
            "filter_cond1": "",
            "filter_cond2": "",
            "max_file_size_limit": FileServer.get_max_file_size_limit(),
        }

        # 内容过滤
        if filter_type in constants.ALLOWED_FILTER_TYPES:
            filter_content = get_filter_content(filter_type, filter_content)
            packing_context_kwargs.update(
                {
                    "filter_cond1": filter_content.get("filter_cond1", ""),
                    "filter_cond2": filter_content.get("filter_cond2", ""),
                }
            )

        script_content = FileServer.get_script_info(action="pack", args=packing_context_kwargs, bk_os_type=os_type)
        # 渲染脚本
        task_result = FileServer.execute_script(
            content=script_content["content"],
            ip=ip_list,
            bk_biz_id=bk_biz_id,
            operator=operator,
            account=data.get_one_of_inputs("account"),
            task_name="[BKLOG] {} File By {}".format(task_name, data.get_one_of_inputs("username")),
            script_params=script_content["script_params"],
        )
        data.outputs.task_instance_id = FileServer.get_task_id(task_result)

        # 以下代码为数据上下文传输数据
        # 拼接打包后的文件路径
        distribution_path = packed_dir_name
        if os_type == constants.WINDOWS:
            distribution_path = FileServer.parse_windows_path(packed_dir_name)

        if isinstance(ip_list, str):
            ip_list = [ip_list]
        distribution_source_file_list = [
            {
                "account": {"alias": data.get_one_of_inputs("account")},
                # 转换IP格式
                "server": {"ip_list": [ip]},
                # 这里是直接分发目录
                "file_list": [f"{distribution_path}{packed_file_name}"],
            }
            for ip in ip_list
        ]
        # 分发组件的源文件
        data.outputs.distribution_source_file_list = distribution_source_file_list
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        task_instance_id = data.get_one_of_outputs("task_instance_id")
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        query_result = self._poll_status(
            task_instance_id=task_instance_id,
            operator=data.get_one_of_inputs("operator"),
            bk_biz_id=bk_biz_id,
        )

        # 判断脚本是否执行结束
        if not FileServer.is_finished_for_single_ip(query_result):
            data.outputs.ex_data = _("脚本正在执行中")
            return True
        # 输出脚本内容, 如果所有IP都失败了，则返回异常
        has_success = False
        job_message = ""
        step_ip_result_list = FileServer.get_detail_for_ips(query_result)
        for item in step_ip_result_list:
            if item["exit_code"] == 0:
                has_success = True
                break
            elif item["exit_code"] == PACK_TASK_SCRIPT_NOT_HAVE_ENOUGH_CAP_ERROR_CODE:
                job_message = _("目标机器没有足够的储存")
            else:
                job_message = FileServer.get_job_tag(item)

        if not has_success:
            raise Exception(_("任务打包异常: {}").format(job_message))

        host_list_group = array_chunk(
            [
                {"ip": item["ip"], "bk_cloud_id": item["bk_cloud_id"], "bk_host_id": item.get("bk_host_id", 0)}
                for item in step_ip_result_list
            ],
            BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE,
        )
        ip_log_output_kv = {}
        step_instance_id = FileServer.get_step_instance_id(query_result)
        try:
            for host_list in host_list_group:
                host_list_log = FileServer.get_host_list_log(host_list, task_instance_id, step_instance_id, bk_biz_id)
                for log_content in host_list_log.get("script_task_logs", []):
                    content = html.unescape(log_content.get("log_content"))
                    log_output_kv = FileServer.get_bk_kv_log(content)
                    log_output_kv = {kv[constants.BKLOG_LOG_KEY]: kv[constants.BKLOG_LOG_VALUE] for kv in log_output_kv}
                    ip_log_output_kv[log_content["ip"]] = log_output_kv
        except Exception as e:
            logger.exception(f"[packing get bklog] get log content failed => {e}")

        task = Tasks.objects.get(task_id=data.get_one_of_inputs("task_id"))
        task.ex_data.update(ip_log_output_kv)
        task.download_status = constants.DownloadStatus.DISTRIBUTING.value
        task.save()
        self.finish_schedule()
        return True


class FilePackingComponent(Component):
    name = "FilePackingComponent"
    code = "file_packing_comp"
    bound_service = FilePackingService
