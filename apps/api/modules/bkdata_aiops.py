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
from django.utils.translation import ugettext_lazy as _  # noqa

from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user  # noqa
from config.domains import AIOPS_APIGATEWAY_ROOT, AIOPS_MODEL_APIGATEWAY_ROOT  # noqa
from apps.api.base import DataAPI, DataApiRetryClass  # noqa  pylint: disable=unused-import


class _BkDataAIOPSApi:
    MODULE = _("数据平台aiops模块")

    def __init__(self):
        self.create_sample_set = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/",
            module=self.MODULE,
            description=u"创建样本集",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.add_rt_to_sample_set = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/result_table/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"RT提交, 把RT添加到 stage表中",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.collect_configs = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/collect_configs/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"创建或更新样本采集配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.auto_collect = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT
            + "sample_set/{sample_set_id}/result_table/{result_table_id}/extract/auto_collect/",
            module=self.MODULE,
            url_keys=["sample_set_id", "result_table_id"],
            description=u"创建或更新自动修改样本集配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.apply_sample_set = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/submit/apply/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"执行样本集提交",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.submit_status = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/submit/status/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"查询提交后的固化任务执行状态",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.sample_set_info = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"获取样本集详情",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.delete_sample_set = DataAPI(
            method="DELETE",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"删除样本集",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.create_model = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/",
            module=self.MODULE,
            description=u"模型创建",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.create_experiment = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/",
            module=self.MODULE,
            url_keys=["model_id"],
            description=u"AIOps 创建实验",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.put_experiment = DataAPI(
            method="PUT",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"AIOps 更新实验",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.experiments_config = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/config/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"获取实验配置信息",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.retrieve_execute_config = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "meta_data/retrieve_execute_config/",
            module=self.MODULE,
            description=u"获取实验执行配置信息",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.update_execute_config = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "meta_data/update_execute_config/",
            module=self.MODULE,
            description=u"更新实验执行配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.execute_experiments = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/node/execute/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"执行实验配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.execute_experiments_node_status = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/node/execute/status/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"实验步骤状态 （当前用于切分状态捕获）",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.basic_models_training_status = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/basic_models/training_status/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"备选模型训练状态列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.aiops_get_costum_algorithm = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "algorithm/{algorithm_name}/",
            module=self.MODULE,
            url_keys=["algorithm_name"],
            description=u"获取单个自定义算法(最新版本)",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.basic_models_evaluation_status = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/basic_models/evaluation_status/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"备选模型评估状态列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.basic_model_evaluation_result = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT
            + "models/{model_id}/experiments/{experiment_id}/basic_models/{basic_model_id}/evaluation_result/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id", "basic_model_id"],
            description=u"备选模型评估结果",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.pre_commit = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/pre_commit/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"实验提交前查看配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.experiment_commit = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/commit/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"实验提交",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.release_config = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/release/{experiment_id}/{basic_model_id}/config/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id", "basic_model_id"],
            description=u"获取模型发布配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.release = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/release/{experiment_id}/{basic_model_id}",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id", "basic_model_id"],
            description=u"模型发布",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.update_model_info = DataAPI(
            method="PUT",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/",
            module=self.MODULE,
            url_keys=["model_id"],
            description=u"修改模型",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )

        self.aiops_release = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/release/",
            module=self.MODULE,
            url_keys=["model_id"],
            description=u"备选模型列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )

        self.aiops_release_model_release_id_model_file = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/release/{model_release_id}/model_file/",
            module=self.MODULE,
            url_keys=["model_id", "model_release_id"],
            description=u"获取发布的模型对应的模型文件",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.aiops_experiments_debug = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "experiments/debug/",
            module=self.MODULE,
            description=u"训练和预测调试",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.serving_data_processing_id_config = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "serving/{data_processing_id}/config/",
            module=self.MODULE,
            url_keys=["data_processing_id"],
            description=u"AIOps 模型实例信息",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.aiops_get_model_storage_cluster = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/storage_clusters/",
            module=self.MODULE,
            description=u"获取模型存储集群列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )
        self.aiops_get_model_release_info = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "releases/{model_release_id}/",
            module=self.MODULE,
            description=u"获取模型发布信息",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
            default_timeout=300,
        )


BkDataAIOPSApi = _BkDataAIOPSApi()
