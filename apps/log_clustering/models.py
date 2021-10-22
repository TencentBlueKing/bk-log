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
from apps.models import SoftDeleteModel
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_jsonfield_backport.models import JSONField


class SampleSet(SoftDeleteModel):
    sample_set_id = models.IntegerField(_("样本集ID"), db_index=True)
    sample_set_name = models.CharField(_("样本集名称"), db_index=True, max_length=128)


class AiopsModel(SoftDeleteModel):
    model_id = models.CharField(_("模型ID"), db_index=True, max_length=128)
    model_name = models.CharField(_("模型名称"), db_index=True, max_length=128)


class AiopsModelExperiment(SoftDeleteModel):
    model_id = models.CharField(_("模型ID"), db_index=True, max_length=128)
    experiment_id = models.IntegerField(_("实验id"), db_index=True)
    experiment_alias = models.CharField(_("实验名称"), db_index=True, max_length=128)
    status = models.CharField(_("实验状态"), null=True, blank=True, max_length=128)
    basic_model_id = models.CharField(_("最新模型实例id"), null=True, blank=True, max_length=128)
    node_id_list = JSONField(_("节点列表"), null=True, blank=True)

    @classmethod
    def get_experiment(cls, model_name: str, experiment_alias: str):
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        return AiopsModelExperiment.objects.get(model_id=model_id, experiment_alias=experiment_alias)
