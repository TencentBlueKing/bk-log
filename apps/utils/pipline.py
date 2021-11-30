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

from apps.utils.log import logger

from django.utils.translation import ugettext_lazy as _

from apps.utils.local import set_request_username
from pipeline.core.flow.activity import Service


class BaseService(Service):
    """
    服务基类
    """

    TASK_POLLING_INTERVAL = 2
    name = None

    def __init__(self):
        if not self.name:
            raise Exception("service name 不能为None")
        super().__init__(name=self.name)

    def execute(self, data, parent_data, is_raise_exception=False):
        username = data.get_one_of_inputs("username")
        if username:
            set_request_username(username)
        if hasattr(self, "logger"):
            self.logger.info(_("开始{name}").format(name=self.name))
        try:
            result = self._execute(data, parent_data)
            if not result and hasattr(self, "logger"):
                self.logger.info(_("{name}失败").format(name=self.name))
        except Exception as err:
            if hasattr(self, "root_pipeline_id"):
                logger.exception(f"[{self.name}]pipeline_id=>{self.root_pipeline_id} node_id=>{self.id} {err}")
            else:
                logger.exception(f"[{self.name}] {err}")

            reason = _("[{name}] {reason}").format(name=self.name, reason=str(err))
            data.outputs.ex_data = reason
            if hasattr(self, "logger"):
                self.logger.error(_("{name}失败: {reason}").format(name=self.name, reason=reason))

            if is_raise_exception:
                raise Exception(reason)
            result = False

        return result

    def schedule(self, data, parent_data, callback_data=None):
        if hasattr(self, "logger"):
            self.logger.info(_("开始轮询结果：{name}").format(name=self.name))
        try:
            result = self._schedule(data, parent_data, callback_data)
            if not result and hasattr(self, "logger"):
                self.logger.info(_("{name}失败").format(name=self.name))
        except Exception as err:
            logger.exception(f"[{self.name}]pipeline_id=>{self.root_pipeline_id} node_id=>{self.id} {err}")

            reason = _("[{name}] {reason}").format(name=self.name, reason=str(err))
            if hasattr(self, "logger"):
                self.logger.error(_("{name}失败: {reason}").format(name=self.name, reason=reason))
            result = False

        return result

    def _execute(self, data, parent_data):
        raise NotImplementedError

    def _schedule(self, data, parent_data, callback_data=None):
        raise NotImplementedError
