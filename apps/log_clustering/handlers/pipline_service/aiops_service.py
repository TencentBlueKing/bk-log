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
from django.conf import settings
from pipeline.builder import Data, EmptyStartEvent, EmptyEndEvent, Var, build_tree
from pipeline.parser import PipelineParser

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import BKDATA_CLUSTERING_TOGGLE
from apps.log_clustering.components.collections.aiops_model_component import (
    CreateModel,
    UpdateTrainingSchedule,
    CreateExperiment,
    UpdateExecuteConfig,
    SampleSetLoading,
    SampleSetPreparation,
    ModelTrain,
    ModelEvaluation,
    BasicModelEvaluationResult,
    CommitResult,
    Release,
    SyncPattern,
)
from apps.log_clustering.components.collections.data_access_component import (
    ChangeDataStream,
    CreateBkdataAccess,
    SyncBkdataEtl,
    AddProjectData,
)
from apps.log_clustering.components.collections.flow_component import CreatePreTreatFlow, CreateAfterTreatFlow
from apps.log_clustering.components.collections.sample_set_component import (
    CreateSampleSet,
    AddRtToSampleSet,
    CollectConfigs,
    ApplySampleSet,
)
from apps.log_clustering.constants import SAMPLE_SET_SLEEP_TIMER
from apps.log_clustering.handlers.pipline_service.base_pipline_service import BasePipeLineService
from apps.log_clustering.models import ClusteringConfig
from apps.utils.pipline import SleepTimer


class AiopsService(BasePipeLineService):
    def build_data_context(self, params, *args, **kwargs) -> Data:
        data_context = Data()
        data_context.inputs["${sample_set_name}"] = Var(type=Var.PLAIN, value=params["sample_set_name"])
        data_context.inputs["${description}"] = Var(type=Var.PLAIN, value=params["description"])
        data_context.inputs["${model_name}"] = Var(type=Var.PLAIN, value=params["model_name"])
        data_context.inputs["${experiment_alias}"] = Var(type=Var.PLAIN, value=params["experiment_alias"])
        data_context.inputs["${min_members}"] = Var(type=Var.PLAIN, value=params["min_members"])
        data_context.inputs["${max_dist_list}"] = Var(type=Var.PLAIN, value=params["max_dist_list"])
        data_context.inputs["${predefined_varibles}"] = Var(type=Var.PLAIN, value=params["predefined_varibles"])
        data_context.inputs["${delimeter}"] = Var(type=Var.PLAIN, value=params["delimeter"])
        data_context.inputs["${max_log_length}"] = Var(type=Var.PLAIN, value=params["max_log_length"])
        data_context.inputs["${is_case_sensitive}"] = Var(type=Var.PLAIN, value=params["is_case_sensitive"])
        data_context.inputs["${topic_name}"] = Var(type=Var.PLAIN, value=params["topic_name"])
        data_context.inputs["${collector_config_id}"] = Var(type=Var.PLAIN, value=params["collector_config_id"])
        data_context.inputs["${project_id}"] = Var(type=Var.PLAIN, value=params["project_id"])
        data_context.inputs["${bk_biz_id}"] = Var(type=Var.PLAIN, value=params["bk_biz_id"])
        return data_context

    def build_pipeline(self, data_context: Data, *args, **kwargs):
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        sample_set_name = kwargs.get("sample_set_name")
        collector_config_id = kwargs.get("collector_config_id")
        model_name = kwargs.get("model_name")
        experiment_alias = kwargs.get("experiment_alias")
        start.extend(ChangeDataStream(collector_config_id).change_data_stream).extend(
            CreateBkdataAccess(collector_config_id).create_bkdata_access
        ).extend(SyncBkdataEtl(collector_config_id).sync_bkdata_etl).extend(
            AddProjectData(collector_config_id).add_project_data
        ).extend(
            CreatePreTreatFlow(collector_config_id).create_pre_treat_flow
        ).extend(
            CreateSampleSet(sample_set_name=sample_set_name).create_sample_set
        ).extend(
            AddRtToSampleSet(sample_set_name=sample_set_name).add_rt_to_sample_set
        ).extend(
            CollectConfigs(sample_set_name=sample_set_name).collect_config
        ).extend(
            ApplySampleSet(sample_set_name=sample_set_name).apply_sample_set
        ).extend(
            SleepTimer(SAMPLE_SET_SLEEP_TIMER).sleep_timer
        ).extend(
            CreateModel(model_name=model_name).create_model
        ).extend(
            UpdateTrainingSchedule(model_name=model_name).update_training_schedule
        ).extend(
            CreateExperiment(experiment_alias=experiment_alias).create_experiment
        ).extend(
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
            CreateAfterTreatFlow(collector_config_id).create_after_treat_flow
        ).extend(
            end
        )
        tree = build_tree(start, data=data_context)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()
        return pipeline


def create_aiops_service(collector_config_id):
    conf = FeatureToggleObject.toggle(BKDATA_CLUSTERING_TOGGLE).feature_config
    clustering_config = ClusteringConfig.objects.get(collector_config_id=collector_config_id)
    if clustering_config.pre_treat_flow_id:
        return
    params = {
        "bk_biz_id": conf["bk_biz_id"],
        "sample_set_name": f"{clustering_config.bk_biz_id}_bklog_sample_set_"
        f"{clustering_config.collector_config_name_en}",
        "model_name": f"{clustering_config.bk_biz_id}_bklog_model_{clustering_config.collector_config_name_en}",
        "description": f"{clustering_config.bk_biz_id}_bklog_{clustering_config.collector_config_name_en}",
        "experiment_alias": f"{clustering_config.bk_biz_id}_bklog_"
        f"{clustering_config.collector_config_name_en}_experiment",
        "collector_config_id": collector_config_id,
        "topic_name": f"queue_{conf['bk_biz_id']}_bklog_{settings.ENVIRONMENT}_"
        f"{clustering_config.collector_config_name_en}",
        "project_id": conf["project_id"],
        "is_case_sensitive": clustering_config.is_case_sensitive,
        "max_log_length": clustering_config.max_log_length,
        "delimeter": clustering_config.delimeter,
        "predefined_varibles": clustering_config.predefined_varibles,
        "max_dist_list": clustering_config.max_dist_list,
        "min_members": clustering_config.min_members,
    }
    data = AiopsService().build_data_context(params)
    pipeline = AiopsService().build_pipeline(data, **params)
    AiopsService().start_pipeline(pipeline)
