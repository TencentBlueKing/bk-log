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
from ..base import ComponentAPI


class CollectionsJOB(object):
    """Collections of JOB APIS"""

    def __init__(self, client):
        self.client = client

        self.execute_job = ComponentAPI(
            client=self.client, method="POST", path="/api/c/compapi{bk_api_ver}/job/execute_job/", description="启动作业"
        )
        self.fast_execute_sql = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/fast_execute_sql/",
            description="快速执行SQL脚本",
        )
        self.get_cron_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_cron_list/",
            description="查询业务下定时作业信息",
        )
        self.get_job_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_job_detail/",
            description="查询作业模板详情",
        )
        self.get_job_instance_log = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_job_instance_log/",
            description="根据作业实例ID查询作业执行日志",
        )
        self.get_job_instance_status = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_job_instance_status/",
            description="查询作业执行状态",
        )
        self.get_job_list = ComponentAPI(
            client=self.client, method="GET", path="/api/c/compapi{bk_api_ver}/job/get_job_list/", description="查询作业模板"
        )
        self.get_os_account = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_os_account/",
            description="查询业务下的执行账号",
        )
        self.get_own_db_account_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_own_db_account_list/",
            description="查询用户有权限的DB帐号列表",
        )
        self.get_public_script_list = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/get_public_script_list/",
            description="查询公共脚本列表",
        )
        self.get_script_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_script_detail/",
            description="查询脚本详情",
        )
        self.get_script_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_script_list/",
            description="查询脚本列表",
        )
        self.get_step_instance_status = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/get_step_instance_status/",
            description="查询作业步骤的执行状态",
        )
        self.update_cron_status = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/update_cron_status/",
            description="更新定时作业状态",
        )
        self.fast_execute_script = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/fast_execute_script/",
            description="快速执行脚本",
        )
        self.fast_push_file = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/fast_push_file/",
            description="快速分发文件",
        )
        self.save_cron = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/save_cron/",
            description="新建或保存定时作业",
        )
        self.change_cron_status = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/change_cron_status/",
            description="更新定时作业状态",
        )
        self.execute_task = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/execute_task/",
            description="根据作业模板ID启动作业",
        )
        self.execute_task_ext = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/execute_task_ext/",
            description="启动作业Ext(带全局变量启动)",
        )
        self.get_agent_status = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/get_agent_status/",
            description="查询Agent状态",
        )
        self.get_cron = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_cron/",
            description="查询业务下定时作业信息",
        )
        self.get_task = ComponentAPI(
            client=self.client, method="GET", path="/api/c/compapi{bk_api_ver}/job/get_task/", description="查询作业模板"
        )
        self.get_task_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_task_detail/",
            description="查询作业模板详情",
        )
        self.get_task_ip_log = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_task_ip_log/",
            description="根据作业实例ID查询作业执行日志",
        )
        self.get_task_result = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/job/get_task_result/",
            description="根据作业实例 ID 查询作业执行状态",
        )
