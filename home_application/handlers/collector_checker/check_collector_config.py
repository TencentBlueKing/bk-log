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
import logging
from apps.api import JobApi
from home_application.handlers.collector_checker.base import BaseSuggestion, BaseChecker, BaseResult
from home_application.constants import SELF_CHECK_STEP_1

logger = logging.getLogger()


class CheckCollectorConfig(BaseChecker):
    step_name = SELF_CHECK_STEP_1

    def __init__(self, collector_config, hosts):
        super().__init__()
        self.collector_config = collector_config
        self.hosts = hosts

    def diff_config(self, content):
        # TODO: 先拆分content, 然后对比collector_config和服务器对应目录上的配置文件内容是否一致
        if content == self.collector_config:
            return True, content
        return False, content

    def check_config(self):
        result = BaseResult()
        try:
            fast_execute_script_params = {"bk_biz_id": self.collector_config.bk_biz_id}
            fast_execute_script_result = JobApi.fast_execute_script(fast_execute_script_params)
            get_job_instance_log_params = {
                "bk_biz_id": self.collector_config.bk_biz_id,
                "job_instance_id": fast_execute_script_result.get("job_instance_id", ""),
            }
            get_job_instance_log_result = JobApi.get_job_instance_log(get_job_instance_log_params)
            content, status = self.diff_config(get_job_instance_log_result)
            result.data.append(content)
            if status:
                result = True
                return result

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"[check_config] failed to call JobApi, err: {e}")
            result.message = str(e)

        result.message = BaseSuggestion(f"请求JobAPI失败, 报错为: {result.message}", "检查请求JobAPI的参数以及Job的可用情况")

        return result

    def run(self):
        result = self.check_config()
        self.result.data.append(result)
        if not result.status:
            return self.result
