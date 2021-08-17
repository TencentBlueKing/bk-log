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
"""
databus
1. 采集（collector）
2. 清洗（clean)
3. 入库
"""

from django.db import models  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa
from django_jsonfield_backport.models import JSONField  # noqa

from apps.log_databus.constants import (  # noqa
    TargetObjectTypeEnum,  # noqa
    TargetNodeTypeEnum,  # noqa
    CollectItsmStatus,  # noqa
    ADMIN_REQUEST_USER,
    EtlConfig,  # noqa
)
from apps.log_search.constants import CollectorScenarioEnum, GlobalCategoriesEnum  # noqa
from apps.log_search.models import ProjectInfo  # noqa
from apps.models import MultiStrSplitByCommaField, JsonField, SoftDeleteModel, OperateRecordModel  # noqa


class CollectorConfig(SoftDeleteModel):
    """
    配置后不能修改：collector_scenario_id、category_id、collector_plugin_id、bk_biz_id、target_object_type
    节点管理允许修改的字段
      - 修改 `scope` 的 `nodes` 和 `node_type` 字段
      - `steps` 的 `params` 字段
      - 若需要修改其他字段，则需要把原来的订阅删除，然后创建一个新的

    插件具体配置放在CollectorDeployment.params
     - bkunifylogbeat：日志路径(paths)、过滤方式(conditions)

    日志采集步骤
    1. 写入采集配置表: CollectorConfig
    2. 申请dataid: CollectorConfig.bk_data_id
    3. 通过节点管理订阅采集器：subscription_id
    4. 立即执行节点管理采集任务: task_id_list
    5. 配置默认的清洗策略: CleanConfig
    6. 配置result_table: CleanConfig.result_table_id
    """

    collector_config_id = models.AutoField(_("采集配置ID"), primary_key=True)
    collector_config_name = models.CharField(_("采集配置名称"), max_length=64)
    bk_app_code = models.CharField(_("接入的来源APP"), max_length=64, default="bk_log_search")
    collector_scenario_id = models.CharField(_("采集场景"), max_length=64)
    bk_biz_id = models.IntegerField(_("业务id"))
    category_id = models.CharField(_("数据分类"), max_length=64)
    target_object_type = models.CharField(_("对象类型"), max_length=32, choices=TargetObjectTypeEnum.get_choices())
    target_node_type = models.CharField(_("节点类型"), max_length=32, choices=TargetNodeTypeEnum.get_choices())
    target_nodes = JsonField(_("采集目标"), null=True, default=None)
    target_subscription_diff = JsonField(_("与上一次采集订阅的差异"), null=True)
    description = models.TextField(_("描述"), default="")
    is_active = models.BooleanField(_("是否可用"), default=True)
    data_link_id = models.IntegerField(_("采集链路id"), null=True, default=None)
    bk_data_id = models.IntegerField(_("采集链路data_id"), null=True, default=None)
    bk_data_name = models.CharField(_("采集链路data_name"), null=True, default=None, max_length=64)
    table_id = models.CharField(_("结果表ID"), max_length=255, null=True, default=None)
    etl_config = models.CharField(_("清洗配置"), max_length=32, null=True, default=None)
    subscription_id = models.IntegerField(_("节点管理订阅ID"), null=True, default=None)
    task_id_list = MultiStrSplitByCommaField(_("最后一次部署任务"), max_length=255, null=True, default=None)
    bkdata_data_id = models.IntegerField(_("接入数据平台data id"), null=True, default=None)
    index_set_id = models.IntegerField(_("索引集id"), null=True, default=None)
    data_encoding = models.CharField(_("日志字符集"), max_length=30, null=True, default=None)
    params = JsonField(_("params"), null=True, default=None)
    itsm_ticket_sn = models.CharField(_("itsm单据号"), max_length=255, null=True, default=None, blank=True)
    itsm_ticket_status = models.CharField(
        _("采集接入单据状态"), max_length=20, choices=CollectItsmStatus.get_choices(), default=CollectItsmStatus.NOT_APPLY.value
    )
    can_use_independent_es_cluster = models.BooleanField(_("是否能够使用独立es集群"), default=True, blank=True)
    collector_package_count = models.IntegerField(_("采集打包数量"), null=True, default=10)
    collector_output_format = models.CharField(_("输出格式"), null=True, default=None, max_length=32, blank=True)
    collector_config_overlay = JSONField(_("采集器配置覆盖"), null=True, default=None, max_length=32, blank=True)
    storage_shards_nums = models.IntegerField(_("ES分片数量"), null=True, default=None, blank=True)
    storage_shards_size = models.IntegerField(_("单shards分片大小"), null=True, default=None, blank=True)
    storage_replies = models.IntegerField(_("ES副本数"), null=True, default=1, blank=True)
    bkdata_data_id_sync_times = models.IntegerField(_("调用数据平台创建data_id失败数"), default=0)
    collector_config_name_en = models.CharField(_("采集项英文名"), max_length=255, null=True, blank=True, default="")

    @property
    def category_name(self):
        """
        分类名称
        """
        return GlobalCategoriesEnum.get_display(self.category_id)

    @property
    def create_clean_able(self):
        """
        是否可以创建基础清洗
        """
        return self.etl_config == EtlConfig.BK_LOG_TEXT or not self.etl_config

    @property
    def bkdata_index_set_ids(self):
        """
        数据平台生成的索引集id列表
        """
        log_index_set_ids = BKDataClean.objects.filter(collector_config_id=self.collector_config_id).values_list(
            "log_index_set_id", flat=True
        )
        if not log_index_set_ids:
            return []
        return log_index_set_ids

    def get_collector_scenario_id_display(self):
        return CollectorScenarioEnum.get_choice_label(self.collector_scenario_id)

    class Meta:
        verbose_name = _("用户采集配置")
        verbose_name_plural = _("用户采集配置")
        ordering = ("-updated_at",)
        unique_together = [("collector_config_name", "bk_biz_id")]

    def has_apply_itsm(self):
        if self.itsm_ticket_status:
            return self.itsm_ticket_status != CollectItsmStatus.NOT_APPLY.value
        return False

    def can_apply_itsm(self):
        return self.itsm_ticket_status == "" or self.itsm_ticket_status in [
            CollectItsmStatus.NOT_APPLY.value,
            CollectItsmStatus.FAIL_APPLY.value,
            CollectItsmStatus.SUCCESS_APPLY.value,
        ]

    def itsm_has_success(self):
        return self.itsm_ticket_status == CollectItsmStatus.SUCCESS_APPLY.value

    def set_itsm_success(self):
        self.itsm_ticket_status = CollectItsmStatus.SUCCESS_APPLY.value
        self.save()

    def set_itsm_fail(self):
        self.itsm_ticket_status = CollectItsmStatus.FAIL_APPLY.value
        self.save()

    def set_itsm_applying(self, sn: str):
        self.itsm_ticket_sn = sn
        self.itsm_ticket_status = CollectItsmStatus.APPLYING.value
        self.save()

    def set_can_use_es_cluster(self, itsm_field_value: str):
        self.can_use_independent_es_cluster = itsm_field_value == "true"
        self.save()

    def generate_itsm_title(self):
        bk_biz_name = ProjectInfo.objects.filter(bk_biz_id=self.bk_biz_id).first().project_name
        return str(
            _("【日志采集】{}-{}-{}".format(bk_biz_name, self.collector_config_name, self.created_at.strftime("%Y%m%d")))
        )

    def get_cur_cap(self, bytes="mb"):
        from apps.log_esquery.esquery.client.QueryClientLog import QueryClientLog

        es_client = QueryClientLog()
        result = es_client.cat_indices(index=self.table_id, bytes=bytes)
        return sum([float(indices["store.size"]) for indices in result])

    def get_updated_by(self):
        if self.updated_by == ADMIN_REQUEST_USER:
            return self.created_by
        return self.updated_by


class DataLinkConfig(SoftDeleteModel):
    """
    数据采集链路配置
    bk_biz_id为0时表示允许所有业务使用

    一条数据链路包括三个部分：
    1、kafka集群（唯一）
    2、transfer集群（唯一）
    3、es集群（不唯一）
    """

    data_link_id = models.AutoField(_("链路ID"), primary_key=True)
    link_group_name = models.CharField(_("集群名称"), max_length=64)
    bk_biz_id = models.IntegerField(_("业务id"))
    kafka_cluster_id = models.IntegerField(_("kafka集群ID"))
    transfer_cluster_id = models.CharField(_("transfer集群ID"), max_length=128)
    es_cluster_ids = JsonField(_("es集群ID"), null=True, default=[])
    is_active = models.BooleanField(_("是否可用"), default=True)
    description = models.TextField(_("备注"), default="")

    class Meta:
        verbose_name = _("数据链路配置")
        verbose_name_plural = _("数据链路配置")
        ordering = ("-updated_at",)


class StorageCapacity(OperateRecordModel):
    bk_biz_id = models.IntegerField(_("业务id"))
    storage_capacity = models.FloatField(_("容量"))

    class Meta:
        verbose_name = _("公共集群容量限制")
        verbose_name_plural = _("存储集群容量限制")
        ordering = ("-updated_at",)


class StorageUsed(OperateRecordModel):
    bk_biz_id = models.IntegerField(_("业务id"))
    storage_cluster_id = models.IntegerField(_("集群ID"))
    storage_used = models.FloatField(_("已用容量"))

    class Meta:
        verbose_name = _("业务已用容量")
        verbose_name_plural = _("业务已用容量")
        ordering = ("-updated_at",)
        unique_together = ("bk_biz_id", "storage_cluster_id")


class BKDataClean(SoftDeleteModel):
    status = models.CharField(_("状态"), max_length=64)
    status_en = models.CharField(_("状态英文名"), max_length=64)
    result_table_id = models.CharField(_("结果表id"), max_length=128, db_index=True)
    result_table_name = models.CharField(_("结果表名"), max_length=128)
    result_table_name_alias = models.CharField(_("结果表中文名"), max_length=128, null=True, blank=True)
    raw_data_id = models.IntegerField(_("数据源id"), db_index=True)
    data_name = models.CharField(_("数据源名称"), max_length=128)
    data_alias = models.CharField(_("数据源中文名"), max_length=128, null=True, blank=True)
    data_type = models.CharField(_("数据类型"), max_length=64)
    storage_type = models.CharField(_("存储类型"), max_length=64)
    storage_cluster = models.CharField(_("存储集群"), max_length=64)
    collector_config_id = models.IntegerField(_("采集项id"), db_index=True)
    bk_biz_id = models.IntegerField(_("业务id"))
    log_index_set_id = models.IntegerField(_("索引集id"), blank=True, null=True, db_index=True)
    is_authorized = models.BooleanField(_("索引集是否被授权"), default=False)

    class Meta:
        verbose_name = _("高级清洗列表")
        verbose_name_plural = _("高级清洗列表")
        ordering = ("-updated_at",)


class CleanTemplate(SoftDeleteModel):
    clean_template_id = models.AutoField(_("清洗id"), primary_key=True)
    name = models.CharField(_("模板名"), max_length=128)
    clean_type = models.CharField(_("模板类型"), max_length=64)
    etl_params = JSONField(_("etl配置"), null=True, blank=True)
    etl_fields = JSONField(_("etl字段"), null=True, blank=True)
    bk_biz_id = models.IntegerField(_("业务id"))

    class Meta:
        verbose_name = _("清洗模板")
        verbose_name_plural = _("清洗模板")
        ordering = ("-updated_at",)


class CleanStash(SoftDeleteModel):
    clean_stash_id = models.AutoField(_("清洗缓存id"), primary_key=True)
    clean_type = models.CharField(_("模板类型"), max_length=64)
    etl_params = JSONField(_("etl配置"), null=True, blank=True)
    etl_fields = JSONField(_("etl字段"), null=True, blank=True)
    collector_config_id = models.IntegerField(_("采集项列表"), db_index=True)
    bk_biz_id = models.IntegerField(_("业务id"))

    class Meta:
        verbose_name = _("未完成入库暂存清洗")
        verbose_name_plural = _("未完成入库暂存清洗")
        ordering = ("-updated_at",)
