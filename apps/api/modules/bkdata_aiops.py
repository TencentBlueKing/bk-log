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
from django.utils.translation import ugettext_lazy as _  # noqa
from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user  # noqa
from config.domains import AIOPS_APIGATEWAY_ROOT  # noqa
from apps.api.base import DataAPI  # noqa


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
        )
        self.add_rt_to_sample_set = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/result_table/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"RT提交, 把RT添加到 stage表中",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.auto_collect = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT
            + "sample_set/{sample_set_id}/result_table/215_trace_log_demo/extract/auto_collect/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"创建或更新自动修改样本集配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.apply_sample_set = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/submit/apply/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"执行样本集提交",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.submit_status = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/submit/status/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"查询提交后的固化任务执行状态",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.delete_sample_set = DataAPI(
            method="DELETE",
            url=AIOPS_APIGATEWAY_ROOT + "sample_set/{sample_set_id}/",
            module=self.MODULE,
            url_keys=["sample_set_id"],
            description=u"删除样本集",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.models = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/",
            module=self.MODULE,
            description=u"模型创建",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.create_experiments = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/",
            module=self.MODULE,
            url_keys=["model_id"],
            description=u"AIOps 创建实验",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.experiments_config = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/config/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"获取实验配置信息",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.retrieve_execute_config = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "meta_data/retrieve_execute_config/",
            module=self.MODULE,
            description=u"获取实验执行配置信息",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.update_execute_config = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "meta_data/update_execute_config/",
            module=self.MODULE,
            description=u"更新实验执行配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.execute_experiments = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/node/execute/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"执行实验配置",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.excute_experiments_node_status = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/node/execute/status/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"实验步骤状态 （当前用于切分状态捕获）",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.basic_models_training_status = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/basic_models/training_status/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"备选模型训练状态列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.basic_models_evaluation_status = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/basic_models/evaluation_status/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"备选模型评估状态列表",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.basic_model_evaluation_result = DataAPI(
            method="GET",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/basic_models/evaluation_result/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"备选模型评估结果",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.experiment_commit = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/commit/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"实验提交",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.release = DataAPI(
            method="POST",
            url=AIOPS_APIGATEWAY_ROOT + "models/{model_id}/experiments/{experiment_id}/release/",
            module=self.MODULE,
            url_keys=["model_id", "experiment_id"],
            description=u"模型发布",
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )


BkDataAIOPSApi = _BkDataAIOPSApi()
