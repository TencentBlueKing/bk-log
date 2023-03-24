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
from django.utils.translation import ugettext_lazy as _

from apps.api.base import DataAPI
from apps.api.modules.utils import add_esb_info_before_request, adapt_non_bkcc
from config.domains import JOB_APIGATEWAY_ROOT_V2, JOB_APIGATEWAY_ROOT_V3


def get_job_request_before(params):
    params = adapt_non_bkcc(params)
    return params


def get_job_request_before_with_esb(params):
    params = add_esb_info_before_request(params)
    params = adapt_non_bkcc(params)
    return params


class _JobApi:
    MODULE = _("JOB")

    def __init__(self):
        self.get_public_script_list = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_public_script_list",
            description=_("查询公共脚本列表"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.fast_execute_script = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_execute_script/",
            description=_("快速执行脚本"),
            module=self.MODULE,
            before_request=get_job_request_before_with_esb,
        )
        self.fast_transfer_file = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_transfer_file/",
            description=_("快速分发文件"),
            module=self.MODULE,
            before_request=get_job_request_before_with_esb,
        )
        self.fast_transfer_file = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_transfer_file/",
            description=_("快速分发文件"),
            module=self.MODULE,
            before_request=get_job_request_before_with_esb,
        )
        self.get_job_instance_log = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_log",
            description=_("根据作业id获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before_with_esb,
        )
        self.get_job_instance_status = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_status/",
            description=_("根据作业实例 ID 查询作业执行状态"),
            module=self.MODULE,
            before_request=get_job_request_before_with_esb,
        )
        self.batch_get_job_instance_ip_log = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "batch_get_job_instance_ip_log/",
            description=_("根据ip列表批量查询作业执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before_with_esb,
        )


JobApi = _JobApi()
