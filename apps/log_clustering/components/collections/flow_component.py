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
from django.utils.translation import ugettext_lazy as _
from pipeline.builder import ServiceActivity, Var
from pipeline.component_framework.component import Component

from pipeline.core.flow.activity import Service, StaticIntervalGenerator

from apps.api import CmsiApi
from apps.log_clustering.handlers.dataflow.dataflow_handler import DataFlowHandler
from apps.log_clustering.models import ClusteringConfig
from apps.utils.function import ignored
from apps.utils.pipline import BaseService


class CreatePreTreatFlowService(BaseService):
    name = _("创建预处理flow")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="collector_config_id", key="collector_config_id", type="int", required=True),
        ]

    def _execute(self, data, parent_data):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        flow = DataFlowHandler().create_pre_treat_flow(collector_config_id=collector_config_id)
        DataFlowHandler().start(flow_id=flow["flow_id"])
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        clustering_config = ClusteringConfig.objects.get(collector_config_id=collector_config_id)
        deploy_data = DataFlowHandler().get_latest_deploy_data(flow_id=clustering_config.pre_treat_flow_id)
        if deploy_data["status"] == "failed":
            return False
        if deploy_data["status"] == "success":
            self.finish_schedule()
        return True


class CreatePreTreatFlowComponent(Component):
    name = "CreatePreTreatFlow"
    code = "create_pre_treat_flow"
    bound_service = CreatePreTreatFlowService


class CreatePreTreatFlow(object):
    def __init__(self, collector_config_id: int):
        self.create_pre_treat_flow = ServiceActivity(
            component_code="create_pre_treat_flow", name=f"create_pre_treat_flow:{collector_config_id}"
        )
        self.create_pre_treat_flow.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )


class CreateAfterTreatFlowService(BaseService):
    name = _("创建After处理flow")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="collector_config_id", key="collector_config_id", type="int", required=True),
        ]

    def _execute(self, data, parent_data):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        flow = DataFlowHandler().create_after_treat_flow(collector_config_id=collector_config_id)
        DataFlowHandler().start(flow_id=flow["flow_id"])
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        clustering_config = ClusteringConfig.objects.get(collector_config_id=collector_config_id)
        deploy_data = DataFlowHandler().get_latest_deploy_data(flow_id=clustering_config.after_treat_flow_id)
        if deploy_data["status"] == "failed":
            return False
        if deploy_data["status"] == "success":
            with ignored(Exception):
                send_params = {
                    "receivers": clustering_config.created_by,
                    "content": "聚类流程已经完成",
                    "title": str(_("【日志平台】")),
                }
                CmsiApi.send_mail(send_params)
                CmsiApi.send_wechat(send_params)
            self.finish_schedule()
        return True


class CreateAfterTreatFlowComponent(Component):
    name = "CreateAfterTreatFlow"
    code = "create_after_treat_flow"
    bound_service = CreateAfterTreatFlowService


class CreateAfterTreatFlow(object):
    def __init__(self, collector_config_id: int):
        self.create_after_treat_flow = ServiceActivity(
            component_code="create_after_treat_flow", name=f"create_after_treat_flow:{collector_config_id}"
        )
        self.create_after_treat_flow.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )
