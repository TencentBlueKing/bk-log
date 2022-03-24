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

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
from pipeline.builder import ServiceActivity, Var

from apps.log_clustering.handlers.aiops.sample_set.sample_set_handler import SampleSetHandler
from apps.log_clustering.models import SampleSet, ClusteringConfig
from apps.utils.pipline import BaseService


class CreateSampleSetService(BaseService):
    name = _("创建样本集")

    def inputs_format(self):
        return [
            Service.InputItem(name="sample set name", key="sample_set_name", type="str", required=True),
            Service.InputItem(name="description", key="description", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        sample_set_name = data.get_one_of_inputs("sample_set_name")
        description = data.get_one_of_inputs("description")
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        sample_set = SampleSetHandler().create(sample_set_name=sample_set_name, description=description)
        SampleSet.objects.create(**{"sample_set_id": sample_set["id"], "sample_set_name": sample_set_name})
        ClusteringConfig.objects.filter(collector_config_id=collector_config_id).update(sample_set_id=sample_set["id"])
        return True


class CreateSampleSetComponent(Component):
    name = "CreateSampleSet"
    code = "create_sample_set"
    bound_service = CreateSampleSetService


class CreateSampleSet(object):
    def __init__(self, sample_set_name: str):
        self.create_sample_set = ServiceActivity(
            component_code="create_sample_set", name=f"create_sample_set:{sample_set_name}"
        )
        self.create_sample_set.component.inputs.sample_set_name = Var(type=Var.SPLICE, value="${sample_set_name}")
        self.create_sample_set.component.inputs.description = Var(type=Var.SPLICE, value="${description}")
        self.create_sample_set.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )


class AddRtToSampleSetService(BaseService):
    name = _("把rt添加到stag表")

    def inputs_format(self):
        return [
            Service.InputItem(name="sample set name", key="sample_set_name", type="str", required=True),
            Service.InputItem(name="result table id", key="result_table_id", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        sample_set_name = data.get_one_of_inputs("sample_set_name")
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        sample_set_id = SampleSet.objects.get(sample_set_name=sample_set_name).sample_set_id
        clustering_config = ClusteringConfig.objects.get(collector_config_id=collector_config_id)
        SampleSetHandler().add_rt_to_sample_set(
            sample_set_id=sample_set_id,
            result_table_id=clustering_config.pre_treat_flow["sample_set"]["result_table_id"],
        )
        return True


class AddRtToSampleSetComponent(Component):
    name = "AddRtToSampleSet"
    code = "add_rt_to_sample_set"
    bound_service = AddRtToSampleSetService


class AddRtToSampleSet(object):
    def __init__(self, sample_set_name: str):
        self.add_rt_to_sample_set = ServiceActivity(
            component_code="add_rt_to_sample_set", name=f"add_rt_to_sample_set:{sample_set_name}"
        )
        self.add_rt_to_sample_set.component.inputs.sample_set_name = Var(type=Var.SPLICE, value="${sample_set_name}")
        self.add_rt_to_sample_set.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )


class CollectConfigsService(BaseService):
    name = _("创建或更新样本采集配置")

    def inputs_format(self):
        return [Service.InputItem(name="sample set name", key="sample_set_name", type="str", required=True)]

    def _execute(self, data, parent_data):
        sample_set_name = data.get_one_of_inputs("sample_set_name")
        sample_set_id = SampleSet.objects.get(sample_set_name=sample_set_name).sample_set_id
        SampleSetHandler().collect_configs(sample_set_id=sample_set_id)
        return True


class CollectConfigsComponent(Component):
    name = "CollectConfigs"
    code = "collect_config"
    bound_service = CollectConfigsService


class CollectConfigs(object):
    def __init__(self, sample_set_name: str):
        self.collect_config = ServiceActivity(component_code="collect_config", name=f"collect_config:{sample_set_name}")
        self.collect_config.component.inputs.sample_set_name = Var(type=Var.SPLICE, value="${sample_set_name}")


class ApplySampleSetService(BaseService):
    name = _("执行样本集提交")
    __need_schedule__ = True
    TASK_POLLING_INTERVAL = 300
    interval = StaticIntervalGenerator(TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="sample set name", key="sample_set_name", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        sample_set_name = data.get_one_of_inputs("sample_set_name")
        sample_set_id = SampleSet.objects.get(sample_set_name=sample_set_name).sample_set_id
        SampleSetHandler().apply_sample_set(sample_set_id=sample_set_id)
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        sample_set_name = data.get_one_of_inputs("sample_set_name")
        sample_set_id = SampleSet.objects.get(sample_set_name=sample_set_name).sample_set_id
        submit_status_result = SampleSetHandler().submit_status(sample_set_id=sample_set_id)
        if submit_status_result["status"] == "finished":
            self.finish_schedule()
        return True


class ApplySampleSetComponent(Component):
    name = "ApplySampleSet"
    code = "apply_sample_set"
    bound_service = ApplySampleSetService


class ApplySampleSet(object):
    def __init__(self, sample_set_name: str):
        self.apply_sample_set = ServiceActivity(
            component_code="apply_sample_set", name=f"apply_sample_set:{sample_set_name}"
        )
        self.apply_sample_set.component.inputs.sample_set_name = Var(type=Var.SPLICE, value="${sample_set_name}")
