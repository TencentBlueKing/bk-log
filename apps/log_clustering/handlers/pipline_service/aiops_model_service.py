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

from apps.log_clustering.components.collections.aiops_model_component import (
    CreateModel,
    CreateExperiment,
    UpdateExecuteConfig,
    SampleSetLoading,
    SampleSetPreparation,
    ModelTrain,
    ModelEvaluation,
    BasicModelEvaluationResult,
    CommitResult,
    Release,
    UpdateTrainingSchedule,
    SyncPattern,
)
from apps.log_clustering.handlers.pipline_service.base_pipline_service import BasePipeLineService


@dataclass
class AiopsModelDataCls(object):
    model_name: str
    description: str
    experiment_alias: str
    min_members: int
    max_dist_list: str
    predefined_varibles: str
    delimeter: str
    max_log_length: int
    is_case_sensitive: int
    sample_set_name: str


class AiopsModelService(BasePipeLineService):
    def build_data_context(self, params: AiopsModelDataCls, *args, **kwargs) -> Data:
        data_context = Data()
        data_context.inputs["${model_name}"] = Var(type=Var.PLAIN, value=params.model_name)
        data_context.inputs["${description}"] = Var(type=Var.PLAIN, value=params.description)
        data_context.inputs["${experiment_alias}"] = Var(type=Var.PLAIN, value=params.experiment_alias)
        data_context.inputs["${min_members}"] = Var(type=Var.PLAIN, value=params.min_members)
        data_context.inputs["${max_dist_list}"] = Var(type=Var.PLAIN, value=params.max_dist_list)
        data_context.inputs["${predefined_varibles}"] = Var(type=Var.PLAIN, value=params.predefined_varibles)
        data_context.inputs["${delimeter}"] = Var(type=Var.PLAIN, value=params.delimeter)
        data_context.inputs["${max_log_length}"] = Var(type=Var.PLAIN, value=params.max_log_length)
        data_context.inputs["${is_case_sensitive}"] = Var(type=Var.PLAIN, value=params.is_case_sensitive)
        data_context.inputs["${sample_set_name}"] = Var(type=Var.PLAIN, value=params.sample_set_name)
        return data_context

    def build_pipeline(self, data_context: Data, *args, **kwargs):
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        model_name = kwargs.get("model_name")
        experiment_alias = kwargs.get("experiment_alias")
        start.extend(CreateModel(model_name=model_name).create_model).extend(
            UpdateTrainingSchedule(model_name=model_name).update_training_schedule
        ).extend(CreateExperiment(experiment_alias=experiment_alias).create_experiment).extend(
            UpdateExecuteConfig(experiment_alias=experiment_alias).update_execute_config
        ).extend(
            SampleSetLoading(experiment_alias=experiment_alias).sample_set_loading
        ).extend(
            SampleSetPreparation(experiment_alias=experiment_alias).sample_set_preparation
        ).extend(
            ModelTrain(experiment_alias=experiment_alias).model_train
        ).extend(
            ModelEvaluation(experiment_alias=experiment_alias).model_valuation
        ).extend(
            BasicModelEvaluationResult(experiment_alias=experiment_alias).basic_model_evaluation_result
        ).extend(
            CommitResult(experiment_alias=experiment_alias).commit
        ).extend(
            Release(experiment_alias=experiment_alias).release
        ).extend(
            SyncPattern(model_name=model_name).sync_pattern
        ).extend(
            end
        )
        tree = build_tree(start, data=data_context)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()
        return pipeline
