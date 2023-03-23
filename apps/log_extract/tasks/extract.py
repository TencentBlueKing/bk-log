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
import os
import random
import time
from celery.task import task as celery_task

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from apps.log_extract import constants
from apps.log_extract.constants import (
    PACK_TASK_SCRIPT_NOT_HAVE_ENOUGH_CAP_ERROR_CODE,
    ScheduleStatus,
    BKREPO_CHILD_PACKING_PATH,
    DownloadStatus,
    ExtractLinkType,
    TASK_POLLING_INTERVAL,
    MAX_SCHEDULE_TIMES,
    BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE,
)
from apps.log_extract.fileserver import FileServer
from apps.log_extract.models import Tasks, ExtractLink
from apps.log_extract.utils.packing import (
    get_packed_dir_name,
    get_packed_file_name,
    get_filter_content,
)
from apps.log_extract.utils.transit_server import TransitServer
from apps.utils.db import array_chunk
from apps.utils.remote_storage import BKREPOStorage
from apps.utils.log import logger


@celery_task(ignore_result=True, queue="async_export")
def log_extract_task(
    task_id,
    operator,
    bk_biz_id,
    ip_list,
    file_path,
    filter_type,
    filter_content,
    account,
    os_type,
    username,
):
    LogExtractUtils(
        task_id=task_id,
        operator=operator,
        bk_biz_id=bk_biz_id,
        ip_list=ip_list,
        file_path=file_path,
        filter_type=filter_type,
        filter_content=filter_content,
        account=account,
        os_type=os_type,
        username=username,
    ).extract()


class LogExtractUtils(object):
    def __init__(
        self,
        task_id,
        operator,
        bk_biz_id,
        ip_list,
        file_path,
        filter_type,
        filter_content,
        account,
        os_type,
        username,
        packing_path=None,
    ):
        self.task_id = task_id
        self.bk_biz_id = bk_biz_id
        self.account = account
        self.username = username
        self.operator = operator
        self.file_path = file_path
        self.filter_type = filter_type
        self.filter_content = filter_content
        self.ip_list = ip_list
        self.os_type = os_type
        # 分发后打包组件的文件路径
        self.transit_server_file_path = None
        # 分发组件的打包路径
        self.transit_server_packing_file_path = None
        # 分发后打包组件中，用于获取分发服务器的IP
        self.transit_server_ip_list = None
        # 分发组件的文件列表
        self.file_source_list = None
        self.distribution_source_file_list = None
        self.task_instance_id = None
        self.packing_path = packing_path
        self.ex_data = ""
        self.task_script_output = ""
        self.distribution_ip = None
        self.pack_file_name = ""
        self.task_polling_interval = TASK_POLLING_INTERVAL

    def _packing(self):
        task_id = self.task_id
        Tasks.objects.filter(task_id=task_id).update(download_status=constants.DownloadStatus.PACKING.value)
        ip_list = self.ip_list
        file_path = self.file_path
        bk_biz_id = self.bk_biz_id
        filter_content = self.filter_content
        filter_type = self.filter_type
        os_type = self.os_type
        operator = self.operator
        packed_file_name = get_packed_file_name(task_id)
        packing_path = self.packing_path
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
            account=self.account,
            task_name="[BKLOG] {} File By {}".format(task_name, self.username),
            script_params=script_content["script_params"],
        )
        self.task_instance_id = FileServer.get_task_id(task_result)

        # 以下代码为数据上下文传输数据
        # 拼接打包后的文件路径
        distribution_path = packed_dir_name
        if os_type == constants.WINDOWS:
            distribution_path = FileServer.parse_windows_path(packed_dir_name)

        if isinstance(ip_list, str):
            ip_list = [ip_list]
        distribution_source_file_list = [
            {
                "account": {"alias": self.account},
                # 转换IP格式
                "server": {"ip_list": [ip]},
                # 这里是直接分发目录
                "file_list": [f"{distribution_path}{packed_file_name}"],
            }
            for ip in ip_list
        ]
        # 分发组件的源文件
        self.distribution_source_file_list = distribution_source_file_list
        return True

    def _packing_schedule(self):
        query_result = self._poll_status(
            task_instance_id=self.task_instance_id,
            operator=self.operator,
            bk_biz_id=self.bk_biz_id,
        )
        # 判断脚本是否执行结束
        if not FileServer.is_finished_for_single_ip(query_result):
            self.ex_data = _("脚本正在执行中")
            return ScheduleStatus.EXECUTING
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

        ip_list_group = array_chunk(
            [
                {"ip": item["ip"], "bk_cloud_id": item["bk_cloud_id"], "bk_host_id": item.get("bk_host_id", 0)}
                for item in step_ip_result_list
            ],
            BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE,
        )
        ip_log_output_kv = {}
        step_instance_id = FileServer.get_step_instance_id(query_result)
        try:
            for ip_list in ip_list_group:
                ip_list_log = FileServer.get_host_list_log(
                    ip_list, self.task_instance_id, step_instance_id, self.bk_biz_id
                )
                for log_content in ip_list_log.get("script_task_logs", []):
                    content = html.unescape(log_content.get("log_content"))
                    log_output_kv = FileServer.get_bk_kv_log(content)
                    log_output_kv = {kv[constants.BKLOG_LOG_KEY]: kv[constants.BKLOG_LOG_VALUE] for kv in log_output_kv}
                    if log_content["bk_host_id"]:
                        ip_log_output_kv[log_content["bk_host_id"]] = log_output_kv
                    else:
                        ip_log_output_kv[log_content["ip"]] = log_output_kv
        except Exception as e:
            logger.exception(f"[packing get bklog] get log content failed => {e}")

        task = Tasks.objects.get(task_id=self.task_id)
        task.ex_data.update(ip_log_output_kv)
        task.download_status = constants.DownloadStatus.DISTRIBUTING.value
        task.save()
        return ScheduleStatus.SUCCESS

    @staticmethod
    def _poll_status(task_instance_id, operator, bk_biz_id):
        return FileServer.query_task_result(task_instance_id, operator, bk_biz_id)

    @staticmethod
    def _get_transit_server(extract_link: ExtractLink, task_id):
        packed_dir_name = get_packed_dir_name("", task_id=task_id)
        if extract_link.link_type == ExtractLinkType.BK_REPO.value:
            return (
                [
                    TransitServer(
                        ip=settings.BKLOG_NODE_IP,
                        target_dir=settings.BKLOG_STORAGE_ROOT_PATH,
                        bk_cloud_id=settings.BKLOG_CLOUD_ID,
                    )
                ],
                constants.TRANSIT_SERVER_PACKING_PATH,
                os.path.join(settings.BKLOG_STORAGE_ROOT_PATH, BKREPO_CHILD_PACKING_PATH, packed_dir_name),
            )
        hosts = extract_link.extractlinkhost_set.all()
        if not hosts:
            raise Exception(_("请配置链路中转服务器"))
        return (
            [TransitServer(ip=host.ip, target_dir=host.target_dir, bk_cloud_id=host.bk_cloud_id) for host in hosts],
            constants.TRANSIT_SERVER_PACKING_PATH,
            os.path.join(constants.TRANSIT_SERVER_DISTRIBUTION_PATH, packed_dir_name),
        )

    def _distribution(self):
        # 更新任务状态
        task_id = self.task_id
        operator = self.operator
        bk_biz_id = self.bk_biz_id
        Tasks.objects.filter(task_id=task_id).update(download_status=constants.DownloadStatus.DISTRIBUTING.value)
        task = Tasks.objects.get(task_id=task_id)
        extract_link: ExtractLink = ExtractLink.objects.filter(link_id=task.link_id).first()
        transit_servers, transit_server_packing_file_path, transit_server_file_path = self._get_transit_server(
            extract_link, task_id=task_id
        )
        transit_server = random.choice(transit_servers)
        file_target_path = os.path.join(transit_server_file_path, "[FILESRCIP]")
        # 将文件分发到中转服务器目录
        task_result = FileServer.file_distribution(
            file_source_list=self.distribution_source_file_list,
            file_target_path=file_target_path,
            target_server=[transit_server],
            bk_biz_id=bk_biz_id,
            operator=operator,
            account=self.account,
            task_name="[BKLOG] File Distribution By {}".format(self.username),
        )

        task_instance_id = FileServer.get_task_id(task_result)
        self.task_instance_id = task_instance_id

        # 分发任务ID写入数据库
        Tasks.objects.filter(task_id=task_id).update(job_task_id=task_instance_id)

        # 以下代码为下载, 中转后打包组件传递数据
        self.distribution_ip = [transit_server]
        # 输出中转后打包步骤的文件路径和打包路径
        self.transit_server_file_path = [transit_server_file_path]
        self.transit_server_packing_file_path = transit_server_packing_file_path
        return True

    def _distribution_schedule(self):
        task_id = self.task_id
        operator = self.operator
        bk_biz_id = self.bk_biz_id
        Tasks.objects.filter(task_id=task_id).update(download_status=constants.DownloadStatus.DISTRIBUTING.value)
        task_instance_id = self.task_instance_id
        query_result = self._poll_status(task_instance_id, operator, bk_biz_id)

        # 判断脚本是否执行结束
        if not FileServer.is_finished_for_single_ip(query_result):
            self.ex_data = _("脚本正在执行中")
            return ScheduleStatus.EXECUTING

        # 判断文件分发是否成功
        ip_status = FileServer.get_job_instance_status(query_result)
        if ip_status != constants.JOB_SUCCESS_STATUS:
            raise Exception(_("文件分发异常({})".format(ip_status)))

        return ScheduleStatus.SUCCESS

    def _cos_upload(self):
        task_id = self.task_id
        task = Tasks.objects.get(task_id=task_id)
        extract_link: ExtractLink = task.get_link()
        bk_biz_id = extract_link.op_bk_biz_id
        operator = extract_link.operator
        account = self.account
        transit_server, *_ = self.distribution_ip
        transit_server_file_path, *_ = self.transit_server_file_path
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
            task_name="[BKLOG] Cos Upload By {}".format(self.username),
        )
        self.task_instance_id = FileServer.get_task_id(task_result)
        self.pack_file_name = cos_pack_file_name
        return True

    def _cos_upload_schedule(self):
        task_id = self.task_id
        task = Tasks.objects.get(task_id=task_id)
        extract_link: ExtractLink = task.get_link()
        bk_biz_id = extract_link.op_bk_biz_id
        operator = extract_link.operator
        query_result = self._poll_status(
            task_instance_id=self.task_instance_id,
            operator=operator,
            bk_biz_id=bk_biz_id,
        )
        # 判断脚本是否执行结束
        if not FileServer.is_finished_for_single_ip(query_result):
            self.ex_data = _("Cos Upload 正在执行中")
            return ScheduleStatus.EXECUTING

        for item in FileServer.get_detail_for_ips(query_result):
            if item["exit_code"] != 0:
                raise Exception(_("上传网盘异常: {}").format(FileServer.get_job_tag(query_result)))

        task.download_status = DownloadStatus.DOWNLOADABLE.value
        task.cos_file_name = self.pack_file_name
        task.save()
        return ScheduleStatus.SUCCESS

    def _bkrepo_upload(self):
        # 如果是提取链路bkrepo类型 需要上传bkrepo
        transit_server, *_ = self.distribution_ip
        cos_pack_file_name = get_packed_file_name(task_id=self.task_id)
        full_file_path = os.path.join(transit_server.target_dir, cos_pack_file_name)
        BKREPOStorage().export_upload(file_path=full_file_path, file_name=cos_pack_file_name)
        os.remove(full_file_path)

    def extract(self):
        logger.info(_("文件提取开始: {}").format(self.task_id))
        logger.info(_("文件打包ka: {}").format(self.task_id))
        try:
            self._packing()
            for val in range(MAX_SCHEDULE_TIMES):
                time.sleep(self.task_polling_interval)
                logger.info(_("确认文件打包结果: {}, 确认次数: {}").format(self.task_id, val))
                result = self._packing_schedule()
                if result == ScheduleStatus.SUCCESS:
                    logger.info(_("文件打包成功: {}").format(self.task_id))
                    break
            else:
                raise Exception(_("文件打包异常(超出设定次数: {})").format(self.task_polling_interval))

            logger.info(_("文件分发中: {}").format(self.task_id))
            self._distribution()
            for val in range(MAX_SCHEDULE_TIMES):
                time.sleep(self.task_polling_interval)
                logger.info(_("确认文件分发结果: {}, 确认次数: {}").format(self.task_id, val))
                result = self._distribution_schedule()
                if result == ScheduleStatus.SUCCESS:
                    logger.info(_("文件分发成功: {}").format(self.task_id))
                    break
            else:
                raise Exception(_("文件分发异常(超出设定次数: {})").format(self.task_polling_interval))

            logger.info(_("文件上传至cos中: {}").format(self.task_id))
            self._cos_upload()
            for val in range(MAX_SCHEDULE_TIMES):
                time.sleep(self.task_polling_interval)
                logger.info(_("确认文件上传至cos结果: {}, 确认次数: {}").format(self.task_id, val))
                result = self._cos_upload_schedule()
                if result == ScheduleStatus.SUCCESS:
                    logger.info(_("文件上传至cos成功: {}").format(self.task_id))
                    break
            else:
                raise Exception(_("文件上传至cos异常(超出设定次数: {})").format(self.task_polling_interval))

            task = Tasks.objects.get(task_id=self.task_id)
            extract_link: ExtractLink = task.get_link()
            if extract_link.link_type == ExtractLinkType.BK_REPO.value:
                logger.info(_("文件上传至bkrepo准备中: {}").format(self.task_id))
                self._bkrepo_upload()
                logger.info(_("文件上传至bkrepo成功: {}").format(self.task_id))
        except BaseException as e:  # pylint: disable=broad-except
            logger.info(_("文件提取失败: {}, 失败原因: {}").format(self.task_id, e))
            Tasks.objects.filter(task_id=self.task_id).update(
                download_status=constants.DownloadStatus.FAILED.value, task_process_info=e
            )
            raise
        logger.info(_("文件提取成功: {}").format(self.task_id))
