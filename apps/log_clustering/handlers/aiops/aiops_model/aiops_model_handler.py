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
import base64
from typing import List

from apps.api import BkDataAIOPSApi
from apps.log_clustering.exceptions import NodeConfigException, NotSupportStepNameQueryException
from apps.log_clustering.handlers.aiops.aiops_model.constants import (
    StepName,
    TRAINING_INPUT_VALUE,
    ALGORITHM_CONFIG_FEATURE_COLUMNS,
    ALGORITHM_CONFIG_PREDICT_OUTPUT,
    DELIMETER_DEFAULT_VALUE,
    PREDEFINED_VARIBLES_DEFAULT_VALUE,
)
from apps.log_clustering.handlers.aiops.base import BaseAiopsHandler
from apps.log_clustering.handlers.aiops.aiops_model.data_cls import (
    CreateModelCls,
    CreateExperimentsCls,
    GetExperimentsConfigCls,
    GetExperimentsMetaDataCls,
    UpdateExecuteConfigCls,
    ExecuteConfigCls,
    ChunkedReadSampleSet,
    PipelineResourcesCls,
    PythonBackendCls,
    SampleLoadingCls,
    NodeCls,
    ContentCls,
    SampleLoadingContentNodeConfigCls,
    NodeConfigCls,
    ExecuteStatusCls,
    SamplePreparationCls,
    SamplePreparationContentNodeConfigCls,
    SamplePreparationContentAlgorithmConfigCls,
    ModelTrainCls,
    ModelTrainContentNodeConfigCls,
    ModelTrainContentAlgorithmConfigCls,
    AlgorithmConfigConfCls,
    ModelTrainTrainingStatusCls,
    AiopsGetCostumAlgorithm,
    ModelEvaluationCls,
    ModelEvaluationContentNodeConfigCls,
    EvaluationStatusCls,
    EvaluationResultCls,
)


class AiopsModelHandler(BaseAiopsHandler):
    def create_model(self, model_name: str, description: str):
        """
        创建模型
        @param model_name str 模型名
        @param description str 模型描述
        """
        create_model_request = CreateModelCls(
            project_id=self.conf.get("project_id"),
            model_name=model_name,
            description=description,
            processing_cluster_id=self.conf.get("processing_cluster_id"),
            storage_cluster_id=self.conf.get("storage_cluster_id"),
        )
        request_dict = self._set_username(create_model_request)
        return BkDataAIOPSApi.create_model(params=request_dict)

    def create_experiment(self, model_id: str, experiment_alias: str):
        """
        创建实验
        @param model_id str 模型id
        @param experiment_alias 实验别名
        """
        create_experiment_request = CreateExperimentsCls(
            project_id=self.conf.get("project_id"),
            template_id=self.conf.get("template_id"),
            model_id=model_id,
            experiment_alias=experiment_alias,
        )
        request_dict = self._set_username(create_experiment_request)
        return BkDataAIOPSApi.create_experiment(params=request_dict)

    def get_experiments_config(self, model_id: str, experiment_id: int):
        """
        查询实验配置
        @param model_id str 模型id
        @param experiment_id int 实验id
        """
        get_experiments_config_request = GetExperimentsConfigCls(
            project_id=self.conf.get("project_id"), model_id=model_id, experiment_id=experiment_id
        )
        request_dict = self._set_username(get_experiments_config_request)
        return BkDataAIOPSApi.experiments_config(params=request_dict)

    def retrieve_execute_config(self, experiment_id: int):
        """
        查询实验meta配置
        @param experiment_id int 实验id
        """
        retrieve_execute_config_request = GetExperimentsMetaDataCls(filter_id=experiment_id)
        request_dict = self._set_username(retrieve_execute_config_request)
        return BkDataAIOPSApi.retrieve_execute_config(params=request_dict)

    def update_execute_config(self, experiment_id: int, window: str = "4h", worker_nums: int = 8, memory: int = 4096):
        """
        变价实验meta配置
        @param experiment_id int 实验id
        @param window str 窗口时间大小
        @param worker_nums int 使用worker数
        @param memory int 使用内存大小
        """
        update_execute_config_request = UpdateExecuteConfigCls(
            filter_id=experiment_id,
            execute_config=ExecuteConfigCls(
                chunked_read_sample_set=ChunkedReadSampleSet(
                    window=window,
                ),
                pipeline_resources=PipelineResourcesCls(
                    python_backend=PythonBackendCls(worker_nums=worker_nums, memory=memory)
                ),
            ),
        )
        request_dict = self._set_username(update_execute_config_request)
        return BkDataAIOPSApi.update_execute_config(request_dict)

    def sample_set_loading(self, sample_set_id: int, model_id: str, experiment_id: int):
        """
        执行样本准备
        @param sample_set_id int 样本集id
        @param model_id str 模型id
        @param experiment_id int 实验id
        """
        experiment_config = self.get_experiments_config(model_id=model_id, experiment_id=experiment_id)
        if not experiment_config["steps"]["sample_loading"]["node"]:
            raise NodeConfigException(NodeConfigException.MESSAGE.format(steps="sample_loading"))

        sample_set_loading_steps_config, *_ = experiment_config["steps"]["sample_loading"]["node"]
        sample_set_loading_request = SampleLoadingCls(
            model_id=model_id,
            experiment_id=experiment_id,
            model_experiment_id=experiment_id,
            nodes=[
                NodeCls(
                    node_id=sample_set_loading_steps_config["node_id"],
                    model_id=sample_set_loading_steps_config["model_id"],
                    node_name=sample_set_loading_steps_config["node_name"],
                    node_alias=sample_set_loading_steps_config["node_alias"],
                    node_index=sample_set_loading_steps_config["node_index"],
                    run_status=sample_set_loading_steps_config["run_status"],
                    operate_status=sample_set_loading_steps_config["operate_status"],
                    model_experiment_id=experiment_id,
                    step_name=sample_set_loading_steps_config["step_name"],
                    action_name=sample_set_loading_steps_config["action_name"],
                    action_alias=sample_set_loading_steps_config["action_alias"],
                    properties=sample_set_loading_steps_config["properties"],
                    active=sample_set_loading_steps_config["active"],
                    node_role=sample_set_loading_steps_config["node_role"],
                    execute_config=sample_set_loading_steps_config["execute_config"],
                    content=ContentCls(
                        input_config=sample_set_loading_steps_config["content"]["input_config"],
                        output_config=sample_set_loading_steps_config["content"]["output_config"],
                        node_config=SampleLoadingContentNodeConfigCls(
                            sample_set_id=NodeConfigCls(
                                id=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"]["id"],
                                arg_name=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "arg_name"
                                ],
                                action_name=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "action_name"
                                ],
                                arg_alias=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "arg_alias"
                                ],
                                arg_index=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "arg_index"
                                ],
                                data_type=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "data_type"
                                ],
                                properties=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "properties"
                                ],
                                description=sample_set_loading_steps_config["content"]["node_config"]["sample_set_id"][
                                    "description"
                                ],
                                default_value=sample_set_loading_steps_config["content"]["node_config"][
                                    "sample_set_id"
                                ]["default_value"],
                                advance_config=sample_set_loading_steps_config["content"]["node_config"][
                                    "sample_set_id"
                                ]["advance_config"],
                                value=sample_set_id,
                            ),
                            data_sampling=NodeConfigCls(
                                id=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"]["id"],
                                arg_name=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "arg_name"
                                ],
                                action_name=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "action_name"
                                ],
                                arg_alias=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "arg_alias"
                                ],
                                arg_index=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "arg_index"
                                ],
                                data_type=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "data_type"
                                ],
                                properties=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "properties"
                                ],
                                description=sample_set_loading_steps_config["content"]["node_config"]["data_sampling"][
                                    "description"
                                ],
                                default_value=sample_set_loading_steps_config["content"]["node_config"][
                                    "data_sampling"
                                ]["default_value"],
                                advance_config=sample_set_loading_steps_config["content"]["node_config"][
                                    "data_sampling"
                                ]["advance_config"],
                                value="",
                            ),
                            sampling_time_range=sample_set_loading_steps_config["content"]["node_config"][
                                "sampling_time_range"
                            ],
                            sampling_conditions=sample_set_loading_steps_config["content"]["node_config"][
                                "sampling_conditions"
                            ],
                            sampling_func=sample_set_loading_steps_config["content"]["node_config"]["sampling_func"],
                        ),
                        algorithm_config=sample_set_loading_steps_config["content"]["algorithm_config"],
                    ),
                )
            ],
        )
        request_dict = self._set_username(sample_set_loading_request)
        return BkDataAIOPSApi.execute_experiments(request_dict)

    def get_execute_status(self, step_name: str, node_id_list: list, model_id: str, experiment_id: int):
        """
        获取执行状态（目前仅用于样本准备及样本切分）（为了契合计算平台step_name）
        @param step_name str 步骤
        @param node_id_list list 节点列表
        @param model_id str 模型id
        @param experiment_id int 实验id
        """
        if step_name not in [StepName.SAMPLE_LOADING, StepName.SAMPLE_PREPARATION]:
            raise NotSupportStepNameQueryException(NotSupportStepNameQueryException.MESSAGE.format(step_name=step_name))

        execute_experiments_node_status_request = ExecuteStatusCls(
            step_name=step_name, model_id=model_id, experiment_id=experiment_id, node_id_list=node_id_list
        )
        request_dict = self._set_username(execute_experiments_node_status_request)
        return BkDataAIOPSApi.execute_experiments_node_status(request_dict)

    def sample_set_preparation(self, model_id: str, experiment_id: int):
        """
        模型切分
        @param model_id 模型切分
        @param experiment_id 实验id
        """
        experiment_config = self.get_experiments_config(model_id=model_id, experiment_id=experiment_id)
        if not experiment_config["steps"]["sample_preparation"]["node"]:
            raise NodeConfigException(NodeConfigException.MESSAGE.format(steps="sample_preparation"))
        sample_preparation_steps_config, *_ = experiment_config["steps"]["sample_preparation"]["node"]
        sample_preparation_request = SamplePreparationCls(
            model_id=model_id,
            experiment_id=experiment_id,
            model_experiment_id=experiment_id,
            nodes=[
                NodeCls(
                    node_id=sample_preparation_steps_config["node_id"],
                    model_id=sample_preparation_steps_config["model_id"],
                    node_name=sample_preparation_steps_config["node_name"],
                    node_alias=sample_preparation_steps_config["node_alias"],
                    node_index=sample_preparation_steps_config["node_index"],
                    run_status=sample_preparation_steps_config["run_status"],
                    operate_status=sample_preparation_steps_config["operate_status"],
                    model_experiment_id=experiment_id,
                    step_name=sample_preparation_steps_config["step_name"],
                    action_name=sample_preparation_steps_config["action_name"],
                    action_alias=sample_preparation_steps_config["action_alias"],
                    properties=sample_preparation_steps_config["properties"],
                    active=sample_preparation_steps_config["active"],
                    node_role=sample_preparation_steps_config["node_role"],
                    execute_config=sample_preparation_steps_config["execute_config"],
                    content=ContentCls(
                        input_config=sample_preparation_steps_config["content"]["input_config"],
                        output_config=sample_preparation_steps_config["content"]["output_config"],
                        node_config=SamplePreparationContentNodeConfigCls(
                            data_split=NodeConfigCls(
                                id=sample_preparation_steps_config["content"]["node_config"]["data_split"]["id"],
                                arg_name=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "arg_name"
                                ],
                                action_name=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "action_name"
                                ],
                                arg_alias=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "arg_alias"
                                ],
                                arg_index=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "arg_index"
                                ],
                                data_type=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "data_type"
                                ],
                                properties=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "properties"
                                ],
                                description=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "description"
                                ],
                                default_value=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "default_value"
                                ],
                                advance_config=sample_preparation_steps_config["content"]["node_config"]["data_split"][
                                    "advance_config"
                                ],
                                value=False,
                            ),
                            split_func=sample_preparation_steps_config["content"]["node_config"]["split_func"],
                            group_enable=NodeConfigCls(
                                id=sample_preparation_steps_config["content"]["node_config"]["group_enable"]["id"],
                                arg_name=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "arg_name"
                                ],
                                action_name=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "action_name"
                                ],
                                arg_alias=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "arg_alias"
                                ],
                                arg_index=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "arg_index"
                                ],
                                data_type=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "data_type"
                                ],
                                properties=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "properties"
                                ],
                                description=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "description"
                                ],
                                default_value=sample_preparation_steps_config["content"]["node_config"]["group_enable"][
                                    "default_value"
                                ],
                                advance_config=sample_preparation_steps_config["content"]["node_config"][
                                    "group_enable"
                                ]["advance_config"],
                                value="",
                            ),
                            group_fields=sample_preparation_steps_config["content"]["node_config"]["group_fields"],
                            group_mode=sample_preparation_steps_config["content"]["node_config"]["group_mode"],
                        ),
                        algorithm_config=SamplePreparationContentAlgorithmConfigCls(),
                    ),
                )
            ],
        )
        request_dict = self._set_username(sample_preparation_request)
        return BkDataAIOPSApi.execute_experiments(request_dict)

    def model_train(
        self,
        min_members: int,
        max_dist_list: List[str],
        predefined_varibles: str,
        delimeter: str,
        max_log_length: int,
        is_case_sensitive: int,
        model_id: str,
        experiment_id: int,
    ):
        """
        执行模型训练
        @param min_members 最少日志数量
        @param max_dist_list 敏感度
        @param predefined_varibles 预先定义的正则表达式
        @param delimeter 分词符
        @param max_log_length 最大日志长度
        @param is_case_sensitive 是否大小写
        @param model_id 模型切分
        @param experiment_id 实验id
        """
        experiment_config = self.get_experiments_config(model_id=model_id, experiment_id=experiment_id)
        if not experiment_config["steps"]["model_train"]["node"]:
            raise NodeConfigException(NodeConfigException.MESSAGE.format(steps="model_train"))
        model_train_steps_config, *_ = experiment_config["steps"]["model_train"]["node"]
        model_train_request = ModelTrainCls(
            model_id=model_id,
            experiment_id=experiment_id,
            model_experiment_id=experiment_id,
            nodes=[
                NodeCls(
                    node_id=model_train_steps_config["node_id"],
                    model_id=model_train_steps_config["model_id"],
                    node_name=model_train_steps_config["node_name"],
                    node_alias=model_train_steps_config["node_alias"],
                    node_index=model_train_steps_config["node_index"],
                    run_status=model_train_steps_config["run_status"],
                    operate_status=model_train_steps_config["operate_status"],
                    model_experiment_id=experiment_id,
                    step_name=model_train_steps_config["step_name"],
                    action_name=model_train_steps_config["action_name"],
                    action_alias=model_train_steps_config["action_alias"],
                    properties=model_train_steps_config["properties"],
                    active=model_train_steps_config["active"],
                    node_role=model_train_steps_config["node_role"],
                    execute_config=model_train_steps_config["execute_config"],
                    content=ContentCls(
                        input_config=model_train_steps_config["content"]["input_config"],
                        output_config=model_train_steps_config["content"]["output_config"],
                        node_config=ModelTrainContentNodeConfigCls(
                            upload_model_file=NodeConfigCls(
                                id=model_train_steps_config["content"]["node_config"]["upload_model_file"]["id"],
                                arg_name=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "arg_name"
                                ],
                                action_name=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "action_name"
                                ],
                                arg_alias=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "arg_alias"
                                ],
                                arg_index=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "arg_index"
                                ],
                                data_type=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "data_type"
                                ],
                                properties=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "properties"
                                ],
                                description=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "description"
                                ],
                                default_value=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "default_value"
                                ],
                                advance_config=model_train_steps_config["content"]["node_config"]["upload_model_file"][
                                    "advance_config"
                                ],
                                value="",
                            ),
                            algorithm_selection=NodeConfigCls(
                                id=model_train_steps_config["content"]["node_config"]["algorithm_selection"]["id"],
                                arg_name=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "arg_name"
                                ],
                                action_name=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "action_name"
                                ],
                                arg_alias=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "arg_alias"
                                ],
                                arg_index=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "arg_index"
                                ],
                                data_type=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "data_type"
                                ],
                                properties=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "properties"
                                ],
                                description=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "description"
                                ],
                                default_value=model_train_steps_config["content"]["node_config"]["algorithm_selection"][
                                    "default_value"
                                ],
                                advance_config=model_train_steps_config["content"]["node_config"][
                                    "algorithm_selection"
                                ]["advance_config"],
                                value=self.conf.get("model_train_algorithm"),
                            ),
                            training_input=NodeConfigCls(
                                id=model_train_steps_config["content"]["node_config"]["training_input"]["id"],
                                arg_name=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "arg_name"
                                ],
                                action_name=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "action_name"
                                ],
                                arg_alias=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "arg_alias"
                                ],
                                arg_index=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "arg_index"
                                ],
                                data_type=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "data_type"
                                ],
                                properties=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "properties"
                                ],
                                description=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "description"
                                ],
                                default_value=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "default_value"
                                ],
                                advance_config=model_train_steps_config["content"]["node_config"]["training_input"][
                                    "advance_config"
                                ],
                                value=TRAINING_INPUT_VALUE,
                            ),
                            upload_method=model_train_steps_config["content"]["node_config"]["upload_method"],
                            model_file=NodeConfigCls(
                                id=model_train_steps_config["content"]["node_config"]["model_file"]["id"],
                                arg_name=model_train_steps_config["content"]["node_config"]["model_file"]["arg_name"],
                                action_name=model_train_steps_config["content"]["node_config"]["model_file"][
                                    "action_name"
                                ],
                                arg_alias=model_train_steps_config["content"]["node_config"]["model_file"]["arg_alias"],
                                arg_index=model_train_steps_config["content"]["node_config"]["model_file"]["arg_index"],
                                data_type=model_train_steps_config["content"]["node_config"]["model_file"]["data_type"],
                                properties=model_train_steps_config["content"]["node_config"]["model_file"][
                                    "properties"
                                ],
                                description=model_train_steps_config["content"]["node_config"]["model_file"][
                                    "description"
                                ],
                                default_value=model_train_steps_config["content"]["node_config"]["model_file"][
                                    "default_value"
                                ],
                                advance_config=model_train_steps_config["content"]["node_config"]["model_file"][
                                    "advance_config"
                                ],
                                value="",
                            ),
                            param_adjust_type=model_train_steps_config["content"]["node_config"]["param_adjust_type"],
                            evaluation_func=model_train_steps_config["content"]["node_config"]["evaluation_func"],
                            optimize_targets=model_train_steps_config["content"]["node_config"]["optimize_targets"],
                            optimize_algorithm=model_train_steps_config["content"]["node_config"]["optimize_algorithm"],
                            stop_policy_config=model_train_steps_config["content"]["node_config"]["stop_policy_config"],
                            visualization=model_train_steps_config["content"]["node_config"]["visualization"],
                        ),
                        algorithm_config=ModelTrainContentAlgorithmConfigCls(
                            sample_set_table_name=None,
                            sample_set_table_desc=None,
                            feature_columns=ALGORITHM_CONFIG_FEATURE_COLUMNS,
                            predict_output=ALGORITHM_CONFIG_PREDICT_OUTPUT,
                            training_args=self._generate_training_args(
                                min_members=min_members,
                                max_dist_list=max_dist_list,
                                predefined_varibles=predefined_varibles,
                                delimeter=delimeter,
                                max_log_length=max_log_length,
                                is_case_sensitive=is_case_sensitive,
                            ),
                            basic_model_id=model_train_steps_config["content"]["algorithm_config"].get(
                                "basic_model_id", ""
                            ),
                        ),
                    ),
                )
            ],
        )
        request_dict = self._set_username(model_train_request)
        return BkDataAIOPSApi.execute_experiments(request_dict)

    @staticmethod
    def _generate_training_args(
        min_members: int,
        max_dist_list: List[str],
        predefined_varibles: str,
        delimeter: str,
        max_log_length: int,
        is_case_sensitive: int,
    ):
        return [
            AlgorithmConfigConfCls(
                field_name="min_members",
                field_alias="最少日志数量",
                field_index=1,
                default_value=1,
                sample_value=None,
                value=min_members,
                data_field_name=None,
                data_field_alias=None,
                field_type="int",
                allowed_values=[],
                roles={},
                properties={
                    "input_type": "int",
                    "support": True,
                    "allow_null": False,
                    "allow_modified": True,
                    "is_advanced": False,
                    "allowed_values_map": [],
                    "used_by": "user",
                    "closed": None,
                    "is_required": False,
                    "placeholder": "",
                },
                origin=[],
                description=None,
                used_by="user",
            ),
            AlgorithmConfigConfCls(
                field_name="max_dist_list",
                field_alias="敏感度",
                field_index=2,
                default_value="0.1,0.3,0.5,0.7,0.9",
                sample_value=None,
                value=",".join(max_dist_list),
                data_field_name=None,
                data_field_alias=None,
                field_type="string",
                allowed_values=[],
                roles={},
                properties={
                    "input_type": "text",
                    "support": True,
                    "allow_null": False,
                    "allow_modified": True,
                    "is_advanced": False,
                    "allowed_values_map": [],
                    "used_by": "user",
                    "closed": None,
                    "is_required": False,
                    "placeholder": "",
                },
                origin=[],
                description=None,
                used_by="user",
            ),
            AlgorithmConfigConfCls(
                field_name="predefined_varibles",
                field_alias="预先定义的正则表达式",
                field_index=3,
                default_value=PREDEFINED_VARIBLES_DEFAULT_VALUE,
                sample_value=None,
                value=base64.b64encode(predefined_varibles.encode("utf-8")).decode("utf-8"),
                data_field_name=None,
                data_field_alias=None,
                field_type="text",
                allowed_values=[],
                roles={},
                properties={
                    "input_type": "text",
                    "support": True,
                    "allow_null": False,
                    "allow_modified": True,
                    "is_advanced": False,
                    "allowed_values_map": [],
                    "used_by": "user",
                    "closed": None,
                    "is_required": False,
                    "placeholder": "",
                },
                origin=[],
                description=None,
                used_by="user",
            ),
            AlgorithmConfigConfCls(
                field_name="delimeter",
                field_alias="分词符",
                field_index=4,
                default_value=DELIMETER_DEFAULT_VALUE,
                sample_value=None,
                value=base64.b64encode(delimeter.encode("utf-8")).decode("utf-8"),
                data_field_name=None,
                data_field_alias=None,
                field_type="text",
                allowed_values=[],
                roles={},
                properties={
                    "input_type": "text",
                    "support": True,
                    "allow_null": False,
                    "allow_modified": True,
                    "is_advanced": False,
                    "allowed_values_map": [],
                    "used_by": "user",
                    "closed": None,
                    "is_required": False,
                    "placeholder": "",
                },
                origin=[],
                description=None,
                used_by="user",
            ),
            AlgorithmConfigConfCls(
                field_name="max_log_length",
                field_alias="最大日志长度",
                field_index=5,
                default_value=100,
                sample_value=None,
                value=max_log_length,
                data_field_name=None,
                data_field_alias=None,
                field_type="int",
                allowed_values=[],
                roles={},
                properties={
                    "input_type": "int",
                    "support": True,
                    "allow_null": False,
                    "allow_modified": True,
                    "is_advanced": False,
                    "allowed_values_map": [],
                    "used_by": "user",
                    "closed": None,
                    "is_required": False,
                    "placeholder": "",
                },
                origin=[],
                description=None,
                used_by="user",
            ),
            AlgorithmConfigConfCls(
                field_name="is_case_sensitive",
                field_alias="是否大小写敏感",
                field_index=6,
                default_value=1,
                sample_value=None,
                value=is_case_sensitive,
                data_field_name=None,
                data_field_alias=None,
                field_type="int",
                allowed_values=[],
                roles={},
                properties={
                    "input_type": "int",
                    "support": True,
                    "allow_null": False,
                    "allow_modified": True,
                    "is_advanced": False,
                    "allowed_values_map": [],
                    "used_by": "user",
                    "closed": None,
                    "is_required": False,
                    "placeholder": "",
                },
                origin=[],
                description=None,
                used_by="user",
            ),
        ]

    def training_status(self, model_id: str, experiment_id: int):
        """
        备选模型训练状态列表
        @param model_id 模型id
        @param experiment_id 实验id
        """
        training_status_request = ModelTrainTrainingStatusCls(
            model_id=model_id, experiment_id=experiment_id, project_id=self.conf.get("project_id")
        )
        request_dict = self._set_username(training_status_request)
        return BkDataAIOPSApi.basic_models_training_status(request_dict)

    def aiops_get_costum_algorithm(self, algorithm_name: str):
        """
        获取算法详情（最新版）
        @param algorithm_name 算法名
        """
        aiops_get_costum_algorithm_request = AiopsGetCostumAlgorithm(
            algorithm_name=algorithm_name, project_id=self.conf.get("project_id")
        )
        request_dict = self._set_username(aiops_get_costum_algorithm_request)
        return BkDataAIOPSApi.aiops_get_costum_algorithm(request_dict)

    def model_evaluation(self, model_id: str, experiment_id: int):
        experiment_config = self.get_experiments_config(model_id=model_id, experiment_id=experiment_id)
        if not experiment_config["steps"]["model_evaluation"]["node"]:
            raise NodeConfigException(NodeConfigException.MESSAGE.format(steps="model_evaluation"))
        model_evaluation_steps_config, *_ = experiment_config["steps"]["model_evaluation"]["node"]
        model_evaluation_request = ModelEvaluationCls(
            model_id=model_id,
            experiment_id=experiment_id,
            model_experiment_id=experiment_id,
            nodes=[
                NodeCls(
                    node_id=model_evaluation_steps_config["node_id"],
                    model_id=model_evaluation_steps_config["model_id"],
                    node_name=model_evaluation_steps_config["node_name"],
                    node_alias=model_evaluation_steps_config["node_alias"],
                    node_index=model_evaluation_steps_config["node_index"],
                    run_status=model_evaluation_steps_config["run_status"],
                    operate_status=model_evaluation_steps_config["operate_status"],
                    model_experiment_id=experiment_id,
                    step_name=model_evaluation_steps_config["step_name"],
                    action_name=model_evaluation_steps_config["action_name"],
                    action_alias=model_evaluation_steps_config["action_alias"],
                    properties=model_evaluation_steps_config["properties"],
                    active=model_evaluation_steps_config["active"],
                    node_role=model_evaluation_steps_config["node_role"],
                    execute_config=model_evaluation_steps_config["execute_config"],
                    content=ContentCls(
                        input_config=model_evaluation_steps_config["content"]["input_config"],
                        output_config=model_evaluation_steps_config["content"]["output_config"],
                        node_config=ModelEvaluationContentNodeConfigCls(
                            algorithm_node_id=model_evaluation_steps_config["content"]["node_config"][
                                "algorithm_node_id"
                            ],
                            evaluation_func=NodeConfigCls(
                                id=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"]["id"],
                                arg_name=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "arg_name"
                                ],
                                action_name=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "action_name"
                                ],
                                arg_alias=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "arg_alias"
                                ],
                                arg_index=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "arg_index"
                                ],
                                data_type=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "data_type"
                                ],
                                properties=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "properties"
                                ],
                                description=model_evaluation_steps_config["content"]["node_config"]["evaluation_func"][
                                    "description"
                                ],
                                default_value=model_evaluation_steps_config["content"]["node_config"][
                                    "evaluation_func"
                                ]["default_value"],
                                advance_config=model_evaluation_steps_config["content"]["node_config"][
                                    "evaluation_func"
                                ]["advance_config"],
                                value=self.conf.get("evaluation_func"),
                            ),
                        ),
                        algorithm_config=model_evaluation_steps_config["content"]["algorithm_config"],
                    ),
                )
            ],
        )
        request_dict = self._set_username(model_evaluation_request)
        return BkDataAIOPSApi.execute_experiments(request_dict)

    def basic_models_evaluation_status(self, model_id: str, experiment_id: int):
        basic_models_evaluation_status_request = EvaluationStatusCls(
            project_id=self.conf.get("project_id"),
            model_id=model_id,
            experiment_id=experiment_id,
            filter_extra={"offset": 1},
        )
        request_dict = self._set_username(basic_models_evaluation_status_request)
        return BkDataAIOPSApi.basic_models_evaluation_status(request_dict)

    def basic_model_evaluation_result(self, model_id: str, experiment_id: int, basic_module_id: str):
        basic_model_evaluation_result_request = EvaluationResultCls(
            project_id=self.conf.get("project_id"),
            model_id=model_id,
            experiment_id=experiment_id,
            basic_model_id=basic_module_id,
        )
        request_dict = self._set_username(basic_model_evaluation_result_request)
        return BkDataAIOPSApi.basic_model_evaluation_result(request_dict)
