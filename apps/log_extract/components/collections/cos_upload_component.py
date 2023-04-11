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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow import StaticIntervalGenerator, Service
from apps.log_extract.constants import DownloadStatus, ExtractLinkType
from apps.log_extract.fileserver import FileServer
from apps.log_extract.models import Tasks, ExtractLink
from apps.utils.pipline import BaseService
from apps.log_extract.utils.packing import get_packed_file_name
from apps.utils.remote_storage import BKREPOStorage


class CosUploadService(BaseService):
    name = _("Cos 文件上传")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def outputs(self):
        return [
            Service.OutputItem(name=_("任务实例ID"), key="task_instance_id", type="int"),
            Service.OutputItem(name=_("打包文件名称"), key="pack_file_name", type="str"),
        ]

    def _poll_status(self, task_instance_id, operator, bk_biz_id):
        return FileServer.query_task_result(task_instance_id, operator, bk_biz_id)

    def _execute(self, data, parent_data):
        task_id = data.get_one_of_inputs("task_id")
        task = Tasks.objects.get(task_id=task_id)
        extract_link: ExtractLink = task.get_link()
        bk_biz_id = extract_link.op_bk_biz_id
        operator = extract_link.operator
        account = data.get_one_of_inputs("account")
        transit_server, *_ = data.get_one_of_inputs("transit_server")
        transit_server_file_path, *_ = data.get_one_of_inputs("transit_server_file_path")
        cos_pack_file_name = get_packed_file_name(task_id)
        shell_args = {
            "dst_path": transit_server.target_dir,
            "cos_pack_file_name": cos_pack_file_name,
            "target_dir": transit_server_file_path,
            "run_ver": settings.RUN_VER,
        }
        script = FileServer.get_script_info(action="cos", args=shell_args)
        Tasks.objects.filter(task_id=task_id).update(download_status=DownloadStatus.CSTONE_UPLOADING.value)
        task_result = FileServer.execute_script(
            content=script["content"],
            script_params=script["script_params"],
            ip=[
                {
                    "ip": transit_server.ip,
                    "bk_cloud_id": transit_server.bk_cloud_id,
                    "bk_host_id": transit_server.bk_host_id,
                }
            ],
            bk_biz_id=bk_biz_id,
            operator=operator,
            account=account,
            task_name="[BKLOG] Cos Upload By {}".format(data.get_one_of_inputs("username")),
        )
        data.outputs.task_instance_id = FileServer.get_task_id(task_result)
        data.outputs.pack_file_name = cos_pack_file_name
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        task_id = data.get_one_of_inputs("task_id")
        task = Tasks.objects.get(task_id=task_id)
        extract_link: ExtractLink = task.get_link()
        bk_biz_id = extract_link.op_bk_biz_id
        operator = extract_link.operator
        query_result = self._poll_status(
            task_instance_id=data.get_one_of_outputs("task_instance_id"),
            operator=operator,
            bk_biz_id=bk_biz_id,
        )
        # 判断脚本是否执行结束
        if not FileServer.is_finished_for_single_ip(query_result):
            data.outputs.ex_data = _("Cos Upload 正在执行中")
            return True

        for item in FileServer.get_detail_for_ips(query_result):
            if item["exit_code"] != 0:
                raise Exception(
                    _("上传网盘异常: {}, status: {}").format(FileServer.get_job_tag(item), item.get("status", ""))
                )

        # 如果是提取链路bkrepo类型 需要上传bkrepo
        if extract_link.link_type == ExtractLinkType.BK_REPO.value:
            transit_server = data.get_one_of_inputs("transit_server")[0]
            cos_pack_file_name = get_packed_file_name(task_id)
            BKREPOStorage().export_upload(
                file_path=os.path.join(transit_server.target_dir, cos_pack_file_name), file_name=cos_pack_file_name
            )

        task.download_status = DownloadStatus.DOWNLOADABLE.value
        task.cos_file_name = data.get_one_of_outputs("pack_file_name")
        task.save()
        self.finish_schedule()
        return True


class CosUploadComponent(Component):
    name = "CosUploadComponent"
    code = "cos_upload_comp"
    bound_service = CosUploadService
