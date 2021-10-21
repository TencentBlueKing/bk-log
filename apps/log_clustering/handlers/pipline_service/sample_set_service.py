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
from dataclasses import dataclass

from pipeline.parser import PipelineParser
from pipeline.builder import Data, Var, EmptyStartEvent, EmptyEndEvent, build_tree

from apps.log_clustering.components.collections.sample_set_component import (
    CreateSampleSet,
    AddRtToSampleSet,
    CollectConfigs,
    ApplySampleSet,
)
from apps.log_clustering.handlers.pipline_service.base_pipline_service import BasePipeLineService


@dataclass
class SampleSetDataCls:
    sample_set_name: str
    description: str
    result_table_id: str


class SampleSetService(BasePipeLineService):
    def build_data_context(self, params: SampleSetDataCls, *args, **kwargs):
        data_context = Data()
        data_context.inputs["${sample_set_name}"] = Var(type=Var.PLAIN, value=params.sample_set_name)
        data_context.inputs["${description}"] = Var(type=Var.PLAIN, value=params.description)
        data_context.inputs["${result_table_id}"] = Var(type=Var.PLAIN, value=params.result_table_id)
        return data_context

    def build_pipeline(self, data_context: Data, *args, **kwargs):
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        sample_set_name = kwargs.get("sample_set_name")
        start.extend(CreateSampleSet(sample_set_name=sample_set_name).create_sample_set).extend(
            AddRtToSampleSet(sample_set_name=sample_set_name).add_rt_to_sample_set
        ).extend(CollectConfigs(sample_set_name=sample_set_name).collect_config).extend(
            ApplySampleSet(sample_set_name=sample_set_name).apply_sample_set
        ).extend(
            end
        )
        tree = build_tree(start, data=data_context)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()
        return pipeline
