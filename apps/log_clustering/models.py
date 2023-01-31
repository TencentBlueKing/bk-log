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
from apps.log_clustering.constants import StrategiesType
from apps.models import SoftDeleteModel
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SampleSet(SoftDeleteModel):
    sample_set_id = models.IntegerField(_("样本集ID"), db_index=True)
    sample_set_name = models.CharField(_("样本集名称"), db_index=True, max_length=128)


class AiopsModel(SoftDeleteModel):
    model_id = models.CharField(_("模型ID"), db_index=True, max_length=128)
    model_name = models.CharField(_("模型名称"), db_index=True, max_length=128)


class AiopsModelExperiment(SoftDeleteModel):
    model_id = models.CharField(_("模型ID"), db_index=True, max_length=128)
    # experiment_id后续可能会变化，如需要进一步使用，需要手动维护
    experiment_id = models.IntegerField(_("实验id"), db_index=True)
    experiment_alias = models.CharField(_("实验名称"), db_index=True, max_length=128)
    status = models.CharField(_("实验状态"), null=True, blank=True, max_length=128)
    basic_model_id = models.CharField(_("最新模型实例id"), null=True, blank=True, max_length=128)
    node_id_list = models.JSONField(_("节点列表"), null=True, blank=True)

    @classmethod
    def get_experiment(cls, model_name: str, experiment_alias: str):
        model_id = AiopsModel.objects.get(model_name=model_name).model_id
        return AiopsModelExperiment.objects.filter(model_id=model_id, experiment_alias=experiment_alias).first()


class AiopsSignatureAndPattern(SoftDeleteModel):
    model_id = models.CharField(_("模型ID"), max_length=128)
    signature = models.CharField(_("数据指纹"), max_length=256)
    pattern = models.TextField("pattern")

    class Meta:
        index_together = ["model_id", "signature"]


class ClusteringConfig(SoftDeleteModel):
    collector_config_id = models.IntegerField(_("采集项id"), null=True, blank=True)
    collector_config_name_en = models.CharField(_("采集项英文名"), max_length=255, null=True, blank=True)
    index_set_id = models.IntegerField(_("索引集id"), db_index=True)
    sample_set_id = models.IntegerField(_("样本集id"), null=True, blank=True)
    model_id = models.CharField(_("模型id"), max_length=128, null=True, blank=True)
    min_members = models.IntegerField(_("最小日志数量"))
    max_dist_list = models.CharField(_("敏感度"), max_length=128)
    predefined_varibles = models.TextField(_("预先定义的正则表达式"))
    delimeter = models.TextField(_("分词符"))
    max_log_length = models.IntegerField(_("最大日志长度"))
    is_case_sensitive = models.IntegerField(_("是否大小写忽略"), default=0)
    clustering_fields = models.CharField(_("聚合字段"), max_length=128)
    filter_rules = models.JSONField(_("过滤规则"), null=True, blank=True)
    bk_biz_id = models.IntegerField(_("业务id"))
    pre_treat_flow = models.JSONField(_("预处理flow配置"), null=True, blank=True)
    new_cls_pattern_rt = models.CharField(_("新类结果表id"), max_length=255, default="", null=True, blank=True)
    bkdata_data_id = models.IntegerField(_("计算平台接入dataid"), null=True, blank=True)
    bkdata_etl_result_table_id = models.CharField(_("计算平台清洗结果表"), max_length=255, null=True, blank=True)
    bkdata_etl_processing_id = models.CharField(_("计算平台清洗id"), max_length=255, null=True, blank=True)
    log_bk_data_id = models.IntegerField(_("入库数据源"), null=True, blank=True)
    signature_enable = models.BooleanField(_("数据指纹开关"), default=False)
    pre_treat_flow_id = models.IntegerField(_("预处理flowid"), null=True, blank=True)
    after_treat_flow = models.JSONField(_("after_treat_flow配置"), null=True, blank=True)
    after_treat_flow_id = models.IntegerField(_("模型应用flowid"), null=True, blank=True)
    source_rt_name = models.CharField(_("源rt名"), max_length=255, null=True, blank=True)
    category_id = models.CharField(_("数据分类"), max_length=64, null=True, blank=True, default=None)
    python_backend = models.JSONField(_("模型训练配置"), null=True, blank=True)
    es_storage = models.CharField(_("es 集群"), max_length=64, null=True, blank=True, default=None)
    modify_flow = models.JSONField(_("修改after_treat_flow调用的配置"), null=True, blank=True)
    options = models.JSONField(_("额外配置"), null=True, blank=True)
    task_records = models.JSONField(_("任务记录"), default=list)


class SignatureStrategySettings(SoftDeleteModel):
    signature = models.CharField(_("数据指纹"), max_length=256, db_index=True, blank=True)
    index_set_id = models.IntegerField(_("索引集id"), db_index=True)
    strategy_id = models.IntegerField(_("监控策略id"), null=True, blank=True)
    enabled = models.BooleanField(_("是否启用"), default=True)
    bk_biz_id = models.IntegerField(_("业务id"))
    pattern_level = models.CharField(_("聚类级别"), max_length=64, null=True, blank=True)
    strategy_type = models.CharField(
        _("策略类型"), max_length=64, null=True, blank=True, default=StrategiesType.NORMAL_STRATEGY
    )

    @classmethod
    def get_monitor_config(cls, signature, index_set_id, pattern_level):
        signature_strategy_settings = SignatureStrategySettings.objects.filter(
            signature=signature, index_set_id=index_set_id, pattern_level=pattern_level
        ).first()
        if not signature_strategy_settings:
            return {
                "is_active": False,
                "strategy_id": None,
            }
        return {"is_active": True, "strategy_id": signature_strategy_settings.strategy_id}


class NoticeGroup(SoftDeleteModel):
    index_set_id = models.IntegerField(_("索引集id"), db_index=True)
    notice_group_id = models.IntegerField(_("通知人组id"))
    bk_biz_id = models.IntegerField(_("业务id"), null=True, blank=True)
