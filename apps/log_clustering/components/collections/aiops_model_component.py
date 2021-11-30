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
from apps.log_clustering.handlers.aiops.aiops_model.aiops_model_handler import AiopsModelHandler
from apps.log_clustering.handlers.aiops.aiops_model.constants import StepName
from apps.log_clustering.models import AiopsModel, AiopsModelExperiment, SampleSet, ClusteringConfig
from apps.log_clustering.tasks.sync_pattern import sync
from apps.utils.pipline import BaseService
from django.utils.translation import ugettext_lazy as _
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
from pipeline.builder import ServiceActivity, Var


class CreateModelService(BaseService):
    name = _("创建模型")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="description", key="description", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        description = data.get_one_of_inputs("description")
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        aiops_models = AiopsModelHandler().create_model(model_name=model_name, description=description)
        AiopsModel.objects.create(**{"model_id": aiops_models["model_id"], "model_name": model_name})
        ClusteringConfig.objects.filter(collector_config_id=collector_config_id).update(
            model_id=aiops_models["model_id"]
        )
        return True


class CreateModelComponent(Component):
    name = "CreateModel"
    code = "create_model"
    bound_service = CreateModelService


class CreateModel(object):
    def __init__(self, model_name: str):
        self.create_model = ServiceActivity(component_code="create_model", name=f"create_model:{model_name}")
        self.create_model.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.create_model.component.inputs.description = Var(type=Var.SPLICE, value="${description}")
        self.create_model.component.inputs.collector_config_id = Var(type=Var.SPLICE, value="${collector_config_id}")


class UpdateTrainingScheduleService(BaseService):
    name = _("更新持续训练")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        AiopsModelHandler().update_training_schedule(model_id=model_id)
        return True


class UpdateTrainingScheduleComponent(Component):
    name = "UpdateTrainingSchedule"
    code = "update_training_schedule"
    bound_service = UpdateTrainingScheduleService


class UpdateTrainingSchedule(object):
    def __init__(self, model_name: str):
        self.update_training_schedule = ServiceActivity(
            component_code="update_training_schedule", name=f"update_training_schedule:{model_name}"
        )
        self.update_training_schedule.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")


class CreateExperimentService(BaseService):
    name = _("创建实验")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment = AiopsModelHandler().create_experiment(model_id=model_id, experiment_alias=experiment_alias)
        AiopsModelExperiment.objects.create(
            **{"model_id": model_id, "experiment_id": experiment["experiment_id"], "experiment_alias": experiment_alias}
        )
        return True


class CreateExperimentComponent(Component):
    name = "CreateExperiment"
    code = "create_experiment"
    bound_service = CreateExperimentService


class CreateExperiment(object):
    def __init__(self, experiment_alias: str):
        self.create_experiment = ServiceActivity(
            component_code="create_experiment", name=f"create_experiment:{experiment_alias}"
        )
        self.create_experiment.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.create_experiment.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")


class UpdateExecuteConfigService(BaseService):
    name = _("变更实验meta配置")

    def inputs_format(self):
        return [Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True)]

    def _execute(self, data, parent_data):
        # todo 决定是否需要变更配置
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        AiopsModelHandler().update_execute_config(experiment_id)
        experiment_model.status = "update_execute_config"
        experiment_model.save()
        return True


class UpdateExecuteConfigComponent(Component):
    name = "UpdateExecuteConfig"
    code = "update_execute_config"
    bound_service = UpdateExecuteConfigService


class UpdateExecuteConfig(object):
    def __init__(self, experiment_alias: str):
        self.update_execute_config = ServiceActivity(
            component_code="update_execute_config", name=f"update_execute_config:{experiment_alias}"
        )
        self.update_execute_config.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.update_execute_config.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")


class SampleSetLoadingService(BaseService):
    name = _("执行样本准备")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="sample set name", key="sample_set_name", type="str", required=True),
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        sample_set_name = data.get_one_of_inputs("sample_set_name")
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        sample_set_id = SampleSet.objects.get(sample_set_name=sample_set_name).sample_set_id
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        sample_set_loading_result = AiopsModelHandler().sample_set_loading(
            sample_set_id=sample_set_id, model_id=model_id, experiment_id=experiment_id
        )
        experiment_model.node_id_list = sample_set_loading_result["nodes"]
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        node_id_list = experiment_model.node_id_list
        get_execute_status_result = AiopsModelHandler().get_execute_status(
            step_name=StepName.SAMPLE_LOADING, node_id_list=node_id_list, model_id=model_id, experiment_id=experiment_id
        )
        if get_execute_status_result["step_status"] == "failed":
            return False
        if get_execute_status_result["step_status"] == "finished":
            experiment_model.status = StepName.SAMPLE_LOADING
            experiment_model.save()
            self.finish_schedule()
        return True


class SampleSetLoadingComponent(Component):
    name = "SampleSetLoading"
    code = "sample_set_loading"
    bound_service = SampleSetLoadingService


class SampleSetLoading(object):
    def __init__(self, experiment_alias: str):
        self.sample_set_loading = ServiceActivity(
            component_code="sample_set_loading", name=f"sample_set_loading:{experiment_alias}"
        )
        self.sample_set_loading.component.inputs.sample_set_name = Var(type=Var.SPLICE, value="${sample_set_name}")
        self.sample_set_loading.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.sample_set_loading.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")


class SampleSetPreparationService(BaseService):
    name = _("执行样本切分")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        sample_set_preparation_result = AiopsModelHandler().sample_set_preparation(
            model_id=model_id, experiment_id=experiment_id
        )
        experiment_model.node_id_list = sample_set_preparation_result["nodes"]
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        node_id_list = experiment_model.node_id_list
        get_execute_status_result = AiopsModelHandler().get_execute_status(
            step_name=StepName.SAMPLE_PREPARATION,
            node_id_list=node_id_list,
            model_id=model_id,
            experiment_id=experiment_id,
        )
        if get_execute_status_result["step_status"] == "failed":
            return False
        if get_execute_status_result["step_status"] == "finished":
            experiment_model.status = StepName.SAMPLE_PREPARATION
            experiment_model.save()
            self.finish_schedule()
        return True


class SampleSetPreparationComponent(Component):
    name = "SampleSetPreparation"
    code = "sample_set_preparation"
    bound_service = SampleSetPreparationService


class SampleSetPreparation(object):
    def __init__(self, experiment_alias: str):
        self.sample_set_preparation = ServiceActivity(
            component_code="sample_set_preparation", name=f"sample_set_preparation:{experiment_alias}"
        )
        self.sample_set_preparation.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.sample_set_preparation.component.inputs.experiment_alias = Var(
            type=Var.SPLICE, value="${experiment_alias}"
        )


class ModelTrainService(BaseService):
    name = _("执行模型训练")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
            Service.InputItem(name="min members", key="min_members", type="int", required=True),
            Service.InputItem(name="max dist list", key="max_dist_list", type="str", required=True),
            Service.InputItem(name="predefined varibles", key="predefined_varibles", type="str", required=True),
            Service.InputItem(name="delimeter", key="delimeter", type="str", required=True),
            Service.InputItem(name="max log length", key="max_log_length", type="int", required=True),
            Service.InputItem(name="is case sensitive", key="is_case_sensitive", type="int", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        min_members = data.get_one_of_inputs("min_members")
        max_dist_list = data.get_one_of_inputs("max_dist_list")
        predefined_varibles = data.get_one_of_inputs("predefined_varibles")
        delimeter = data.get_one_of_inputs("delimeter")
        max_log_length = data.get_one_of_inputs("max_log_length")
        is_case_sensitive = data.get_one_of_inputs("is_case_sensitive")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id

        model_train_result = AiopsModelHandler().model_train(
            model_id=model_id,
            experiment_id=experiment_id,
            is_case_sensitive=is_case_sensitive,
            max_log_length=max_log_length,
            delimeter=delimeter,
            predefined_varibles=predefined_varibles,
            max_dist_list=max_dist_list,
            min_members=min_members,
        )
        experiment_model.node_id_list = model_train_result["nodes"]
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        training_status_result = AiopsModelHandler().training_status(model_id=model_id, experiment_id=experiment_id)
        if training_status_result["step_status"] == "failed":
            return False
        if training_status_result["step_status"] == "finished":
            experiment_model.status = StepName.MODEL_TRAIN
            experiment_model.save()
            self.finish_schedule()
        return True


class ModelTrainComponent(Component):
    name = "ModelTrain"
    code = "model_train"
    bound_service = ModelTrainService


class ModelTrain(object):
    def __init__(self, experiment_alias: str):
        self.model_train = ServiceActivity(component_code="model_train", name=f"model_train:{experiment_alias}")
        self.model_train.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.model_train.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")
        self.model_train.component.inputs.min_members = Var(type=Var.SPLICE, value="${min_members}")
        self.model_train.component.inputs.max_dist_list = Var(type=Var.SPLICE, value="${max_dist_list}")
        self.model_train.component.inputs.predefined_varibles = Var(type=Var.SPLICE, value="${predefined_varibles}")
        self.model_train.component.inputs.delimeter = Var(type=Var.SPLICE, value="${delimeter}")
        self.model_train.component.inputs.max_log_length = Var(type=Var.SPLICE, value="${max_log_length}")
        self.model_train.component.inputs.is_case_sensitive = Var(type=Var.SPLICE, value="${is_case_sensitive}")


class ModelEvaluationService(BaseService):
    name = _("执行模型评估")
    __need_schedule__ = True
    interval = StaticIntervalGenerator(BaseService.TASK_POLLING_INTERVAL)

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        model_evaluation_result = AiopsModelHandler().model_evaluation(model_id=model_id, experiment_id=experiment_id)
        experiment_model.node_id_list = model_evaluation_result["nodes"]
        return True

    def _schedule(self, data, parent_data, callback_data=None):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        get_execute_status_result = AiopsModelHandler().basic_models_evaluation_status(
            model_id=model_id, experiment_id=experiment_id
        )
        if get_execute_status_result["step_status"] == "failed":
            return False
        if get_execute_status_result["step_status"] == "finished":
            experiment_model.status = StepName.MODEL_EVALUATION
            basic_model, *_ = get_execute_status_result["list"]
            experiment_model.basic_model_id = basic_model["basic_model_id"]
            experiment_model.save()
            self.finish_schedule()
        return True


class ModelEvaluationComponent(Component):
    name = "ModelEvaluation"
    code = "model_valuation"
    bound_service = ModelEvaluationService


class ModelEvaluation(object):
    def __init__(self, experiment_alias: str):
        self.model_valuation = ServiceActivity(
            component_code="model_valuation", name=f"model_valuation:{experiment_alias}"
        )
        self.model_valuation.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.model_valuation.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")


class BasicModelEvaluationResultService(BaseService):
    name = _("获取模型评估结果")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        basic_model_id = experiment_model.basic_model_id
        AiopsModelHandler().basic_model_evaluation_result(
            model_id=model_id, experiment_id=experiment_id, basic_model_id=basic_model_id
        )
        return True


class BasicModelEvaluationResultComponent(Component):
    name = "BasicModelEvaluationResult"
    code = "basic_model_evaluation_result"
    bound_service = BasicModelEvaluationResultService


class BasicModelEvaluationResult(object):
    def __init__(self, experiment_alias: str):
        self.basic_model_evaluation_result = ServiceActivity(
            component_code="basic_model_evaluation_result", name=f"basic_model_evaluation_result:{experiment_alias}"
        )
        self.basic_model_evaluation_result.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.basic_model_evaluation_result.component.inputs.experiment_alias = Var(
            type=Var.SPLICE, value="${experiment_alias}"
        )


class CommitService(BaseService):
    name = _("执行提交")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        AiopsModelHandler().commit(model_id=model_id, experiment_id=experiment_id)
        return True


class CommitComponent(Component):
    name = "Commit"
    code = "commit"
    bound_service = CommitService


class CommitResult(object):
    def __init__(self, experiment_alias: str):
        self.commit = ServiceActivity(component_code="commit", name=f"commit:{experiment_alias}")
        self.commit.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.commit.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")


class ReleaseService(BaseService):
    name = _("执行发布")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
            Service.InputItem(name="experiment alias", key="experiment_alias", type="str", required=True),
            Service.InputItem(name="description", key="description", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        experiment_alias = data.get_one_of_inputs("experiment_alias")
        description = data.get_one_of_inputs("description")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        experiment_model = AiopsModelExperiment.get_experiment(experiment_alias=experiment_alias, model_name=model_name)
        experiment_id = experiment_model.experiment_id
        basic_model_id = experiment_model.basic_model_id
        AiopsModelHandler().release(
            model_id=model_id, experiment_id=experiment_id, basic_model_id=basic_model_id, description=description
        )
        return True


class ReleaseComponent(Component):
    name = "Release"
    code = "release"
    bound_service = ReleaseService


class Release(object):
    def __init__(self, experiment_alias: str):
        self.release = ServiceActivity(component_code="release", name=f"release:{experiment_alias}")
        self.release.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
        self.release.component.inputs.experiment_alias = Var(type=Var.SPLICE, value="${experiment_alias}")
        self.release.component.inputs.description = Var(type=Var.SPLICE, value="${description}")


class SyncPatternService(BaseService):
    name = _("获取pattern")

    def inputs_format(self):
        return [
            Service.InputItem(name="model name", key="model_name", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        model_name = data.get_one_of_inputs("model_name")
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        sync(model_id=model_id)
        return True


class SyncPatternComponent(Component):
    name = "SyncPattern"
    code = "sync_pattern"
    bound_service = SyncPatternService


class SyncPattern(object):
    def __init__(self, model_name: str):
        self.sync_pattern = ServiceActivity(component_code="sync_pattern", name=f"sync_pattern:{model_name}")
        self.sync_pattern.component.inputs.model_name = Var(type=Var.SPLICE, value="${model_name}")
