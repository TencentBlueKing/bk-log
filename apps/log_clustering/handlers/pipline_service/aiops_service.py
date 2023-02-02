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
import arrow
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
    CloseContinuousTraining,
)
from apps.log_clustering.components.collections.data_access_component import (
    ChangeDataStream,
    CreateBkdataAccess,
    SyncBkdataEtl,
    AddProjectData,
    AddResourceGroupSet,
)
from apps.log_clustering.components.collections.flow_component import (
    CreatePreTreatFlow,
    CreateAfterTreatFlow,
    CreateNewClsStrategy,
    CreateNewIndexSet,
)
from apps.log_clustering.components.collections.sample_set_component import (
    CreateSampleSet,
    AddRtToSampleSet,
    CollectConfigs,
    ApplySampleSet,
)
from apps.log_clustering.handlers.pipline_service.base_pipline_service import BasePipeLineService
from apps.log_clustering.handlers.pipline_service.constants import OperatorServiceEnum
from apps.log_clustering.models import ClusteringConfig, AiopsModel, AiopsModelExperiment, SampleSet


class AiopsLogService(BasePipeLineService):
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
        data_context.inputs["${index_set_id}"] = Var(type=Var.PLAIN, value=params["index_set_id"])
        return data_context

    def build_pipeline(self, data_context: Data, *args, **kwargs):
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        sample_set_name = kwargs.get("sample_set_name")
        collector_config_id = kwargs.get("collector_config_id")
        model_name = kwargs.get("model_name")
        experiment_alias = kwargs.get("experiment_alias")
        index_set_id = kwargs.get("index_set_id")
        start.extend(
            ChangeDataStream(index_set_id=index_set_id, collector_config_id=collector_config_id).change_data_stream
        ).extend(
            CreateBkdataAccess(index_set_id=index_set_id, collector_config_id=collector_config_id).create_bkdata_access
        ).extend(
            SyncBkdataEtl(index_set_id=index_set_id, collector_config_id=collector_config_id).sync_bkdata_etl
        ).extend(
            AddProjectData(index_set_id=index_set_id, collector_config_id=collector_config_id).add_project_data
        ).extend(
            CreatePreTreatFlow(index_set_id=index_set_id, collector_config_id=collector_config_id).create_pre_treat_flow
        ).extend(
            CreateSampleSet(sample_set_name=sample_set_name).create_sample_set
        ).extend(
            AddRtToSampleSet(sample_set_name=sample_set_name).add_rt_to_sample_set
        ).extend(
            CollectConfigs(sample_set_name=sample_set_name).collect_config
        ).extend(
            ApplySampleSet(sample_set_name=sample_set_name).apply_sample_set
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
            CreateAfterTreatFlow(
                index_set_id=index_set_id, collector_config_id=collector_config_id
            ).create_after_treat_flow
        ).extend(
            CreateNewClsStrategy(
                index_set_id=index_set_id, collector_config_id=collector_config_id
            ).create_new_cls_strategy
        ).extend(
            end
        )
        tree = build_tree(start, data=data_context)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()
        return pipeline


class AiopsBkdataService(BasePipeLineService):
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
        data_context.inputs["${project_id}"] = Var(type=Var.PLAIN, value=params["project_id"])
        data_context.inputs["${bk_biz_id}"] = Var(type=Var.PLAIN, value=params["bk_biz_id"])
        data_context.inputs["${index_set_id}"] = Var(type=Var.PLAIN, value=params["index_set_id"])
        data_context.inputs["${collector_config_id}"] = Var(type=Var.PLAIN, value=params["collector_config_id"])
        return data_context

    def build_pipeline(self, data_context: Data, *args, **kwargs):
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        sample_set_name = kwargs.get("sample_set_name")
        index_set_id = kwargs.get("index_set_id")
        model_name = kwargs.get("model_name")
        experiment_alias = kwargs.get("experiment_alias")
        start.extend(AddResourceGroupSet(index_set_id=index_set_id).add_resource_group).extend(
            AddProjectData(index_set_id=index_set_id).add_project_data
        ).extend(CreatePreTreatFlow(index_set_id=index_set_id).create_pre_treat_flow).extend(
            CreateSampleSet(sample_set_name=sample_set_name).create_sample_set
        ).extend(
            AddRtToSampleSet(sample_set_name=sample_set_name).add_rt_to_sample_set
        ).extend(
            CollectConfigs(sample_set_name=sample_set_name).collect_config
        ).extend(
            ApplySampleSet(sample_set_name=sample_set_name).apply_sample_set
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
            CreateAfterTreatFlow(index_set_id=index_set_id).create_after_treat_flow
        ).extend(
            CreateNewIndexSet(index_set_id=index_set_id).create_new_index_set
        ).extend(
            end
        )
        tree = build_tree(start, data=data_context)
        parser = PipelineParser(pipeline_tree=tree)
        pipeline = parser.parse()
        return pipeline


class UpdateModelService(BasePipeLineService):
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
        data_context.inputs["${project_id}"] = Var(type=Var.PLAIN, value=params["project_id"])
        data_context.inputs["${bk_biz_id}"] = Var(type=Var.PLAIN, value=params["bk_biz_id"])
        data_context.inputs["${index_set_id}"] = Var(type=Var.PLAIN, value=params["index_set_id"])
        return data_context

    def build_pipeline(self, data_context: Data, *args, **kwargs):
        start = EmptyStartEvent()
        end = EmptyEndEvent()
        model_name = kwargs.get("model_name")
        experiment_alias = kwargs.get("experiment_alias")
        start.extend(CloseContinuousTraining(experiment_alias=experiment_alias).close_continuous_training).extend(
            CreateExperiment(experiment_alias=experiment_alias).create_experiment
        ).extend(UpdateExecuteConfig(experiment_alias=experiment_alias).update_execute_config).extend(
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


def operator_aiops_service(index_set_id, operator=OperatorServiceEnum.CREATE):
    conf = FeatureToggleObject.toggle(BKDATA_CLUSTERING_TOGGLE).feature_config
    clustering_config = ClusteringConfig.objects.get(index_set_id=index_set_id)
    rt_name = (
        clustering_config.collector_config_name_en
        if clustering_config.collector_config_name_en
        else "bkdata_{}".format(clustering_config.source_rt_name.split("_", 2)[-1])
    )
    now_time = arrow.now()
    time_format = now_time.format("YYYYMMDDHHmmssSSS")
    if operator == OperatorServiceEnum.UPDATE:
        sample_set_name = SampleSet.objects.get(sample_set_id=clustering_config.sample_set_id).sample_set_name
        model_name = AiopsModel.objects.get(model_id=clustering_config.model_id).model_name
        experiment_alias = AiopsModelExperiment.objects.get(model_id=clustering_config.model_id).experiment_alias
    else:
        model_name = f"{clustering_config.bk_biz_id}_bklog_model_{index_set_id}_{time_format}"
        experiment_alias = f"{clustering_config.bk_biz_id}_bklog_{index_set_id}_experiment_{time_format}"
        sample_set_name = f"{clustering_config.bk_biz_id}_bklog_sample_set_{index_set_id}_{time_format}"
    params = {
        "bk_biz_id": conf["bk_biz_id"],
        "sample_set_name": sample_set_name,
        "model_name": model_name,
        "description": f"{clustering_config.bk_biz_id}_bklog_{rt_name}",
        "experiment_alias": experiment_alias,
        "collector_config_id": clustering_config.collector_config_id,
        "topic_name": f"queue_{conf['bk_biz_id']}_bklog_{settings.ENVIRONMENT}_" f"{rt_name}",
        "project_id": conf["project_id"],
        "is_case_sensitive": clustering_config.is_case_sensitive,
        "max_log_length": clustering_config.max_log_length,
        "delimeter": clustering_config.delimeter,
        "predefined_varibles": clustering_config.predefined_varibles,
        "max_dist_list": clustering_config.max_dist_list,
        "min_members": clustering_config.min_members,
        "index_set_id": clustering_config.index_set_id,
    }
    service = ClusteringService.get_instance(clustering_config=clustering_config, operator=operator)
    data = service.build_data_context(params)
    pipeline = service.build_pipeline(data, **params)
    service.start_pipeline(pipeline)

    clustering_config.task_records.append({"operate": operator, "task_id": pipeline.id, "time": now_time.timestamp})
    clustering_config.save()

    return pipeline.id


class ClusteringService(object):
    @classmethod
    def get_instance(cls, clustering_config, operator):
        if operator == OperatorServiceEnum.UPDATE:
            return UpdateModelService()
        if clustering_config.collector_config_id:
            return AiopsLogService()
        return AiopsBkdataService()
