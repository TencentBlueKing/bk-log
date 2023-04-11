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
import datetime
import traceback

from pipeline.builder import ServiceActivity, Var
from pipeline.component_framework.component import Component
from pipeline.core.flow import StaticIntervalGenerator

from apps.log_measure.events import PIPELINE_MONITOR_EVENT
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
            raise Exception(_("service name 不能为None"))
        super().__init__(name=self.name)

    def execute(self, data, parent_data, is_raise_exception=False):
        reason = ""
        username = data.get_one_of_inputs("username")
        root_pipeline_id = getattr(self, "root_pipeline_id", "")
        node_id = getattr(self, "id", "")
        exc_info = ""
        if username:
            set_request_username(username)
        logger.info(
            _("开始{name} pipeline_id=>{pipeline_id} node_id=>{node_id} ").format(
                name=self.name, pipeline_id=root_pipeline_id, node_id=node_id
            )
        )
        try:
            result = self._execute(data, parent_data)
            if not result:
                logger.info(_("{name}失败").format(name=self.name))
        except Exception as err:  # pylint:disable=broad-except
            logger.exception(f"[{self.name}]pipeline_id=>{self.root_pipeline_id} node_id=>{self.id} {err}")
            reason = _("[{name}] {reason}").format(name=self.name, reason=str(err))
            data.outputs.ex_data = reason
            logger.error(_("{name}失败: {reason}").format(name=self.name, reason=reason))

            if is_raise_exception:
                raise Exception(reason)
            result = False
            exc_info = traceback.format_exc()

        if not result:
            PIPELINE_MONITOR_EVENT(
                content=f"{exc_info} => {reason}",
                dimensions={"pipeline_id": root_pipeline_id, "node_id": node_id, "pipeline_name": str(self.name)},
            )
        return result

    def schedule(self, data, parent_data, callback_data=None):
        root_pipeline_id = getattr(self, "root_pipeline_id", "")
        node_id = getattr(self, "id", "")
        exec_info = ""
        logger.info(
            _("开始轮询结果：{name} pipeline_id=>{pipeline_id} node_id=>{node_id} ").format(
                name=self.name, pipeline_id=root_pipeline_id, node_id=node_id
            )
        )
        reason = ""
        try:
            result = self._schedule(data, parent_data, callback_data)
            if not result:
                logger.info(_("{name}失败").format(name=self.name))
        except Exception as err:  # pylint:disable=broad-except
            logger.exception(f"[{self.name}]pipeline_id=>{self.root_pipeline_id} node_id=>{self.id} {err}")
            reason = _("[{name}] {reason}").format(name=self.name, reason=str(err))
            logger.error(_("{name}失败: {reason}").format(name=self.name, reason=reason))
            exec_info = traceback.format_exc()
            result = False

        if not result:
            PIPELINE_MONITOR_EVENT(
                content=f"{exec_info} => {reason}",
                dimensions={"pipeline_id": root_pipeline_id, "node_id": node_id, "pipeline_name": str(self.name)},
            )
        return result

    def _execute(self, data, parent_data):
        raise NotImplementedError

    def _schedule(self, data, parent_data, callback_data=None):
        raise NotImplementedError


class SleepTimerService(BaseService):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(0)
    BK_TIMEMING_TICK_INTERVAL = int(60 * 60 * 24)
    name = "sleep_timer"

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("定时时间"),
                key="bk_timing",
                type="int",
            ),
            self.InputItem(
                name=_("是否强制晚于当前时间"),
                key="force_check",
                type="bool",
            ),
        ]

    def outputs_format(self):
        return []

    def _execute(self, data, parent_data):
        timing = data.get_one_of_inputs("bk_timing")

        now = datetime.datetime.now()
        eta = now + datetime.timedelta(seconds=int(timing))
        self.logger.info("planning time: {}".format(eta))
        data.outputs.timing_time = eta
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        timing_time = data.outputs.timing_time

        now = datetime.datetime.now()
        t_delta = timing_time - now
        if t_delta.total_seconds() < 1:
            self.finish_schedule()

        # 如果定时时间距离当前时间的时长大于唤醒消息的有效期，则设置下一次唤醒时间为消息有效期之内的时长
        # 避免唤醒消息超过消息的有效期被清除，导致定时节点永远不会被唤醒
        if t_delta.total_seconds() > self.BK_TIMEMING_TICK_INTERVAL > 60 * 5:
            self.interval.interval = self.BK_TIMEMING_TICK_INTERVAL - 60 * 5
            wake_time = now + datetime.timedelta(seconds=self.interval.interval)
            self.logger.info("wake time: {}".format(wake_time))
            return True

        # 这里减去 0.5s 的目的是尽可能的减去 execute 执行带来的误差
        self.interval.interval = t_delta.total_seconds() - 0.5
        self.logger.info("wake time: {}".format(timing_time))
        return True


class SleepTimerComponent(Component):
    name = _("定时")
    code = "sleep_timer"
    bound_service = SleepTimerService


class SleepTimer:
    def __init__(self, bk_timing: int):
        self.sleep_timer = ServiceActivity(component_code="sleep_timer", name="sleep_timer")
        self.sleep_timer.component.inputs.bk_timing = Var(type=Var.SPLICE, value=bk_timing)
