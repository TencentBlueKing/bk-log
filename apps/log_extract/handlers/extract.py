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
"""
import time
from abc import ABC

import typing

from django.utils.http import urlencode
from rest_framework.reverse import reverse
from pipeline.builder import EmptyStartEvent, EmptyEndEvent, Data, Var, ServiceActivity, NodeOutput, builder
from pipeline.conf import settings
from pipeline.core.pipeline import Pipeline
from pipeline.parser import PipelineParser
from pipeline.service import task_service
from apps.utils.log import logger
from apps.log_extract import constants, exceptions
from apps.log_extract.constants import ExtractLinkType
from apps.log_extract.exceptions import TaskExtractLinkNotExist
from apps.log_extract.models import Tasks, ExtractLink
from apps.utils.cos import QcloudCos
from apps.utils.base_crypt import BaseCrypt
from apps.utils.local import get_request


def try_op(op: typing.Callable[[], bool], n=3) -> bool:
    if not n:
        return False
    if op():
        return True
    time.sleep(1)
    return try_op(op, n - 1)


class ExtractLinkBase(ABC):
    def build_pipeline(self, task: Tasks, data: Data) -> Pipeline:
        raise NotImplementedError

    def start_pipeline(self, task: Tasks, pipeline: Pipeline):
        pipeline_result = None
        task.save()

        def _op():
            nonlocal pipeline_result
            pipeline_result = task_service.run_pipeline(pipeline)
            if pipeline_result and pipeline_result.result:
                return True
            logger.error(f"[run_pipeline][{task.task_id}]{pipeline_result}")
            return False

        if not try_op(_op):
            Tasks.objects.filter(task_id=task.task_id).update(
                download_status=constants.DownloadStatus.FAILED.value, task_process_info=pipeline_result.message
            )
            raise exceptions.TaskRunPipelineError

    def generate_download_url(self, task: Tasks):
        raise NotImplementedError

    @staticmethod
    def build_common_data_context(
        task_id, bk_biz_id, ip_list, file_path, filter_type, filter_content, operator, account, username, os_type
    ) -> Data:
        pipeline_data = Data()
        pipeline_data.inputs["${task_id}"] = Var(Var.PLAIN, value=task_id)
        pipeline_data.inputs["${bk_biz_id}"] = Var(Var.PLAIN, value=bk_biz_id)
        pipeline_data.inputs["${account}"] = Var(Var.PLAIN, value=account)
        pipeline_data.inputs["${username}"] = Var(Var.PLAIN, value=username)
        pipeline_data.inputs["${operator}"] = Var(Var.PLAIN, value=operator)
        pipeline_data.inputs["${file_path}"] = Var(Var.PLAIN, value=file_path)
        pipeline_data.inputs["${filter_type}"] = Var(Var.PLAIN, value=filter_type)
        pipeline_data.inputs["${filter_content}"] = Var(Var.PLAIN, value=filter_content)
        pipeline_data.inputs["${ip_list}"] = Var(Var.PLAIN, value=ip_list)
        pipeline_data.inputs["${os_type}"] = Var(Var.PLAIN, value=os_type)
        return pipeline_data


class DummyExtractLink(ExtractLinkBase):
    def generate_download_url(self, task: Tasks):
        return ""

    def start_pipeline(self, task: Tasks, pipeline: Pipeline):
        pass

    def build_pipeline(self, task: Tasks, data: Data):
        pass


class QcloudCosExtractLink(ExtractLinkBase):
    def generate_download_url(self, task: Tasks) -> str:
        extract_link: ExtractLink = ExtractLink.objects.filter(link_id=task.link_id).first()
        if not extract_link:
            raise TaskExtractLinkNotExist
        qcloud_cos = QcloudCos(
            extract_link.qcloud_secret_id,
            extract_link.qcloud_secret_key,
            extract_link.qcloud_cos_region,
            extract_link.qcloud_cos_bucket,
        )
        return qcloud_cos.get_download_url(task.cos_file_name)

    def build_pipeline(self, task: Tasks, data: Data) -> Pipeline:
        start = EmptyStartEvent()
        packing = Packing().packing
        distribution = Distribution().distribution
        cos_upload = CosUpload().cos_upload
        end = EmptyEndEvent()
        distribution.extend(cos_upload).extend(end)
        start.extend(packing).extend(distribution)
        pipeline_data = self._build_data_context(data, distribution, packing)
        tree = builder.build_tree(start_elem=start, data=pipeline_data)
        pipeline = PipelineParser(pipeline_tree=tree).parse()
        task.pipeline_id = pipeline.id
        task.pipeline_components_id = tree
        task.download_status = constants.DownloadStatus.PIPELINE.value
        task.save()
        return pipeline

    def _build_data_context(self, pipeline_data, distribution, packing) -> Data:
        # 分发后打包组件的文件路径
        pipeline_data.inputs["${transit_server_file_path}"] = NodeOutput(
            source_act=distribution.id, source_key="transit_server_file_path", type=Var.SPLICE, value=""
        )
        # 分发组件的打包路径
        pipeline_data.inputs["${transit_server_packing_file_path}"] = NodeOutput(
            source_act=distribution.id, source_key="transit_server_packing_file_path", type=Var.SPLICE, value=""
        )
        # 分发后打包组件中，用于获取分发服务器的IP
        pipeline_data.inputs["${transit_server_ip_list}"] = NodeOutput(
            source_act=distribution.id, source_key="distribution_ip", type=Var.SPLICE, value=""
        )
        # 分发组件的文件列表
        pipeline_data.inputs["${file_source_list}"] = NodeOutput(
            source_act=packing.id, source_key="distribution_source_file_list", type=Var.SPLICE, value=""
        )
        return pipeline_data


class CommonExtractLink(QcloudCosExtractLink):
    def generate_download_url(self, task: Tasks):
        url_params = {"target_file": BaseCrypt().encrypt(task.cos_file_name.encode())}
        url_params = urlencode(url_params)
        url = reverse("tasks-download-file", request=get_request())
        return f"{url}?{url_params}"


class BKRepoExtractLink(QcloudCosExtractLink):
    def generate_download_url(self, task: Tasks) -> str:
        pass


class ExtractLinkFactory:

    if settings.FEATURE_TOGGLE["extract_cos"] == "on":
        _LINK_MAP = {
            ExtractLinkType.COMMON.value: CommonExtractLink,
            ExtractLinkType.QCLOUD_COS.value: QcloudCosExtractLink,
            ExtractLinkType.BK_REPO.value: BKRepoExtractLink,
        }
    else:
        _LINK_MAP = {ExtractLinkType.COMMON.value: CommonExtractLink, ExtractLinkType.BK_REPO.value: BKRepoExtractLink}

    @classmethod
    def get_link(cls, type: ExtractLinkType) -> ExtractLinkBase:
        return cls._LINK_MAP.get(type, DummyExtractLink)


class Packing(object):
    """
    继承BasePack，创建打包的ServiceActivity
    """

    def __init__(self):
        super().__init__()
        self.packing = ServiceActivity(component_code="file_packing_comp", name="packing")
        self.packing.component.inputs.task_id = Var(type=Var.SPLICE, value="${task_id}")
        self.packing.component.inputs.os_type = Var(type=Var.SPLICE, value="${os_type}")
        self.packing.component.inputs.username = Var(type=Var.SPLICE, value="${username}")
        self.packing.component.inputs.bk_biz_id = Var(type=Var.SPLICE, value="${bk_biz_id}")
        self.packing.component.inputs.account = Var(type=Var.SPLICE, value="${account}")
        self.packing.component.inputs.operator = Var(type=Var.SPLICE, value="${operator}")
        self.packing.component.inputs.ip_list = Var(type=Var.SPLICE, value="${ip_list}")
        self.packing.component.inputs.filter_type = Var(type=Var.SPLICE, value="${filter_type}")
        self.packing.component.inputs.filter_content = Var(type=Var.SPLICE, value="${filter_content}")
        self.packing.component.inputs.file_path = Var(type=Var.SPLICE, value="${file_path}")


class Distribution(object):
    """
    创建分发组件
    """

    def __init__(self):
        self.distribution = ServiceActivity(component_code="file_dist_comp", name="distributing")
        self.distribution.component.inputs.task_id = Var(type=Var.SPLICE, value="${task_id}")
        self.distribution.component.inputs.file_source_list = Var(type=Var.SPLICE, value="${file_source_list}")
        self.distribution.component.inputs.account = Var(type=Var.SPLICE, value="root")
        self.distribution.component.inputs.username = Var(type=Var.SPLICE, value="${username}")
        self.distribution.component.inputs.operator = Var(type=Var.SPLICE, value="${operator}")
        self.distribution.component.inputs.bk_biz_id = Var(type=Var.SPLICE, value="${bk_biz_id}")


class CosUpload(object):
    def __init__(self):
        self.cos_upload = ServiceActivity(component_code="cos_upload_comp", name="cos_upload")
        self.cos_upload.component.inputs.task_id = Var(type=Var.SPLICE, value="${task_id}")
        self.cos_upload.component.inputs.account = Var(type=Var.SPLICE, value="root")
        self.cos_upload.component.inputs.transit_server = Var(type=Var.SPLICE, value="${transit_server_ip_list}")
        self.cos_upload.component.inputs.transit_server_file_path = Var(
            type=Var.SPLICE, value="${transit_server_file_path}"
        )
        self.cos_upload.component.inputs.username = Var(type=Var.SPLICE, value="${username}")
