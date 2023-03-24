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

from datetime import timedelta
from typing import List

from django.utils import timezone
from rest_framework.response import Response

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pipeline.engine.exceptions import InvalidOperationException
from pipeline.service import task_service

from apps.log_extract.tasks.extract import log_extract_task
from apps.utils.log import logger
from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.iam import ActionEnum, Permission
from apps.log_extract import constants, exceptions
from apps.log_extract.constants import TASK_IP_INDEX, TASK_BK_CLOUD_ID_INDEX, ExtractLinkType, TASK_HOST_ID_INDEX
from apps.log_extract.handlers.explorer import ExplorerHandler
from apps.log_extract.handlers.extract import ExtractLinkBase
from apps.log_extract.models import Tasks, ExtractLink
from apps.log_extract.serializers import PollingResultSerializer
from apps.utils.local import get_request_username, get_local_param
from apps.decorators import user_operation_record
from apps.utils.time_handler import format_user_time_zone


class TasksHandler(object):
    @classmethod
    def list(cls, tasks_views, bk_biz_id, keyword):
        request_user = get_request_username()

        # 运维人员可以看到完整的任务列表
        has_biz_manage = Permission().is_allowed(ActionEnum.MANAGE_EXTRACT_CONFIG)
        tasks = Tasks.objects.search(keyword).filter(bk_biz_id=bk_biz_id)
        if not has_biz_manage:
            tasks = tasks.filter(created_by=request_user)
        queryset = tasks_views.filter_queryset(tasks)

        page = tasks_views.paginate_queryset(queryset)

        if page is not None:
            serializer = tasks_views.get_serializer(page, many=True)
            response = tasks_views.get_paginated_response(serializer.data)
            response.data["list"] = cls.post_list(response.data["list"])
            response.data["list"] = cls.get_ip_and_bk_cloud_id(response.data["list"])
            response.data["timeout"] = constants.POLLING_TIMEOUT
            return response

        serializer = tasks_views.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def recreate(self, task_id):
        request_user = get_request_username()
        try:
            task = Tasks.objects.get(task_id=task_id)
        except Tasks.DoesNotExist:
            raise exceptions.TaskIDDoesNotExist
        if task.created_by != request_user:
            raise exceptions.TasksRecreateFailed

        return self.create(
            bk_biz_id=task.bk_biz_id,
            ip_list=task.ip_list,
            request_file_list=task.file_path,
            filter_type=task.filter_type,
            filter_content=task.filter_content,
        )

    def create(
        self,
        bk_biz_id,
        ip_list,
        request_file_list,
        filter_type,
        remark,
        filter_content,
        preview_directory,
        preview_ip,
        preview_time_range,
        preview_is_search_child,
        preview_start_time,
        preview_end_time,
        link_id,
    ):
        # K8S部署情况下禁止使用内网链路, 所以已有的内网链路不能创建任务
        extract_link: ExtractLink = ExtractLink.objects.filter(link_id=link_id).first()
        if extract_link and extract_link.link_type == ExtractLinkType.COMMON.value and settings.IS_K8S_DEPLOY_MODE:
            raise exceptions.TaskCannotCreateByCommonLink

        # step 2：用户任务鉴权
        list_strategies_dict = ExplorerHandler().get_strategies(bk_biz_id, ip_list)
        allowed_dir_file_list = list_strategies_dict.get("allowed_dir_file_list")
        allowed_download_file_list = []
        for request_file in request_file_list:
            if ExplorerHandler.filter_server_access_file(allowed_dir_file_list, request_file):
                allowed_download_file_list.append(request_file)

        if allowed_download_file_list != request_file_list:
            raise exceptions.TaskCreateFailed(
                exceptions.TaskCreateFailed.MESSAGE.format(
                    failed_download_file_list=set(request_file_list) - set(allowed_download_file_list)
                )
            )

        # step 3：创建任务并启动pipeline
        formatted_ip_list = []
        for ip in ip_list:
            ip_key = f"{ip['bk_cloud_id']}:{ip['ip']}"
            if ip.get("bk_host_id"):
                ip_key = f"{ip_key}:{ip['bk_host_id']}"
            formatted_ip_list.append(ip_key)

        params = {
            "bk_biz_id": bk_biz_id,
            "ip_list": formatted_ip_list,
            "file_path": request_file_list,
            "filter_type": filter_type,
            "filter_content": {} if not filter_type else filter_content,
            "download_status": constants.DownloadStatus.INIT.value,
            "expiration_date": timezone.now() + timedelta(days=settings.EXTRACT_EXPIRED_DAYS),
            "remark": remark,
            "preview_directory": preview_directory,
            "preview_ip": preview_ip,
            "preview_time_range": preview_time_range,
            "preview_is_search_child": preview_is_search_child,
            "preview_start_time": preview_start_time,
            "preview_end_time": preview_end_time,
            "link_id": link_id,
        }
        task = Tasks.objects.create(**params)
        params["ip_list"] = ip_list
        for pop_field in [
            "download_status",
            "expiration_date",
            "remark",
            "preview_directory",
            "preview_ip",
            "preview_time_range",
            "preview_is_search_child",
            "preview_start_time",
            "preview_end_time",
            "link_id",
        ]:
            params.pop(pop_field)

        params.update(
            {
                "operator": list_strategies_dict["operator"],
                "account": ExplorerHandler().get_account(list_strategies_dict.get("bk_os_type")),
                "os_type": list_strategies_dict.get("bk_os_type"),
                "username": get_request_username(),
            }
        )
        # 其他参数在运行pipeline的过程中更新
        extract_link: ExtractLink = ExtractLink.objects.filter(link_id=task.link_id).first()
        # bkrepo时为worker调用
        if extract_link.link_type == ExtractLinkType.BK_REPO.value:
            log_extract_task.delay(task_id=task.task_id, **params)
        else:
            self.run_pipeline(task=task, **params)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": bk_biz_id,
            "record_type": UserOperationTypeEnum.LOG_EXTRACT_TASKS,
            "record_object_id": task.task_id,
            "action": UserOperationActionEnum.CREATE,
            "params": params,
        }
        user_operation_record.delay(operation_record)

        # 返回 task_id 用于轮询任务执行状态
        return {"task_id": task.task_id}

    def retrieve(self, tasks_views):
        request_user = get_request_username()
        instance = tasks_views.get_object()
        serializer = tasks_views.get_serializer(instance)
        task = serializer.data
        # 只有创建者或运维人员才可获取详情
        if not self.is_operator_or_creator(instance.bk_biz_id, request_user, instance.created_by):
            raise exceptions.TasksRetrieveFailed
        # 主机显示优化
        task["ip_list"] = self.get_ip_and_bk_cloud_id([task])[0]["ip_list"]
        pipeline_id = instance.pipeline_id
        pipeline_components_id = instance.pipeline_components_id
        task["download_status_display"] = constants.DownloadStatus.get_dict_choices().get(task["download_status"])

        if not (pipeline_id or pipeline_components_id):
            return Response(task)
        try:
            task_status = task_service.get_state(pipeline_id)
        except Exception:  # pylint: disable=broad-except
            # 存在多主机，单主机日志下载的情况，因此有可能有些pipeline节点未执行
            logger.info("pipeline任务不存在，pipeline_id=>[{}]".format(pipeline_id))
            task["task_step_status"] = []
            return Response(task)

        component_status_list = []
        for component_id, component_info in pipeline_components_id["activities"].items():
            # 这里有可能有些pipeline组件并未执行
            try:
                task_status["children"][component_id]["name"] = component_info["name"]
                # 失败节点输出异常信息
                if task_status["children"][component_id]["state"] == "FAILED":
                    task_status["children"][component_id]["failed_reason"] = task["task_process_info"]
                component_status_list.append(task_status["children"][component_id])
            except KeyError as e:
                logger.error(f"receive a KeyError: {e}")

        # 根据start_time，finish_time排序
        component_status_list = sorted(component_status_list, key=lambda x: (x["start_time"], x["finish_time"]))
        # 输出组件名称用户状态可视化字段
        for component_status in component_status_list:
            component_status["start_time"] = format_user_time_zone(
                component_status["start_time"], get_local_param("time_zone", settings.TIME_ZONE)
            )
            component_status["finish_time"] = format_user_time_zone(
                component_status["finish_time"], get_local_param("time_zone", settings.TIME_ZONE)
            )
            if component_status["name"] in [
                constants.DownloadStatus.DOWNLOADABLE.value,
                constants.DownloadStatus.COS_UPLOAD.value,
            ]:
                component_status["name_display"] = _("分发到网盘中")
            else:
                component_status["name_display"] = constants.DownloadStatus.get_dict_choices().get(
                    component_status["name"]
                )
            component_status["state_display"] = constants.TaskPipelineState.get_dict_choices().get(
                component_status["state"]
            )
        task["task_step_status"] = component_status_list

        return Response(task)

    def partial_update(self, tasks_views, *args, **kwargs):
        instance = tasks_views.get_object()
        if not self.is_operator_or_creator(instance.bk_biz_id, get_request_username(), instance.created_by):
            raise exceptions.TaskUpdateFailed
        kwargs["partial"] = True
        return tasks_views.update(tasks_views.request, *args, **kwargs)

    def get_polling_result(self, task_list):
        request_user = get_request_username()
        task_list = task_list.split(",")

        records = Tasks.objects.filter(created_by=request_user, task_id__in=task_list)

        # 处理pipeline中发生错误而task状态未更新的情况
        self.pipeline_failure_to_task_status(records)

        serializer = PollingResultSerializer(instance=records, many=True)
        response = self.post_list(serializer.data)
        res = []
        # 按照请求task_list中task_id的顺序返回
        for task_id in task_list:
            for task_res in response:
                if task_res["task_id"] == int(task_id):
                    res.append(task_res)

        return res

    @staticmethod
    def pipeline_failure_to_task_status(task_list: List[Tasks]):
        task_have_failed_component = []
        skip_status = [
            constants.DownloadStatus.FAILED,
            constants.DownloadStatus.DOWNLOADABLE,
            constants.DownloadStatus.EXPIRED,
        ]
        for task in task_list:
            if task.download_status in skip_status:
                continue
            try:
                task_status = task_service.get_state(task.pipeline_id)
            except InvalidOperationException:
                continue
            task_status_children = task_status.get("children", {}).values()
            task_status = list(filter(lambda status: status["state"] == "FAILED", task_status_children))
            if task_status:
                task_have_failed_component.append(task.task_id)
                break
        if task_have_failed_component:
            Tasks.objects.filter(task_id__in=task_have_failed_component).update(
                download_status=constants.DownloadStatus.FAILED.value
            )

    @staticmethod
    def post_list(task_list):
        # 输出下载状态可视化字段
        for task in task_list:
            task["download_status_display"] = constants.DownloadStatus.get_dict_choices().get(task["download_status"])
        return task_list

    @staticmethod
    def get_ip_and_bk_cloud_id(task_list):
        for task in task_list:
            ip_list = []
            for ip in task["ip_list"]:
                if ":" not in ip:
                    ip_list.append({"bk_host_id": ip})
                else:
                    items = ip.split(":")
                    if len(items) == 2:
                        ip_list.append({"ip": items[TASK_IP_INDEX], "bk_cloud_id": int(items[TASK_BK_CLOUD_ID_INDEX])})
                    elif len(items) == 3:
                        ip_list.append(
                            {
                                "ip": items[TASK_IP_INDEX],
                                "bk_cloud_id": int(items[TASK_BK_CLOUD_ID_INDEX]),
                                "bk_host_id": int(items[TASK_HOST_ID_INDEX]),
                            }
                        )
            task["ip_list"] = ip_list
        return task_list

    @classmethod
    def run_pipeline(
        cls, task, operator, bk_biz_id, ip_list, file_path, filter_type, filter_content, account, os_type, username
    ):
        extract: ExtractLinkBase = task.get_extract()
        data = extract.build_common_data_context(
            task.task_id,
            bk_biz_id,
            ip_list,
            file_path,
            filter_type,
            filter_content,
            operator,
            account,
            username,
            os_type,
        )
        pipeline = extract.build_pipeline(task, data)
        extract.start_pipeline(task, pipeline)

    def download(self, task_id):
        request_user = get_request_username()
        try:
            task = Tasks.objects.get(task_id=task_id)
        except Tasks.DoesNotExist:
            raise exceptions.TaskIDDoesNotExist
        # 只有创建者或运维人员才可下载
        if not self.is_operator_or_creator(task.bk_biz_id, request_user, task.created_by):
            raise exceptions.TaskDownloadNotAvailable

        # 只有处于downloadable状态才可以下载
        if task.download_status != constants.DownloadStatus.DOWNLOADABLE.value:
            raise exceptions.TaskDownloadNotAvailable
        # 任务是否过期
        if task.download_status == constants.DownloadStatus.DOWNLOADABLE and task.expiration_date <= timezone.now():
            task.download_status = constants.DownloadStatus.EXPIRED.value
            task.save()
            raise exceptions.TaskDownloadExpired
        return task.get_extract().generate_download_url(task)

    @staticmethod
    def is_operator_or_creator(bk_biz_id, request_user, task_creator):
        has_biz_manage = Permission().is_allowed(ActionEnum.MANAGE_EXTRACT_CONFIG)
        if not has_biz_manage and task_creator != request_user:
            return False
        return True
