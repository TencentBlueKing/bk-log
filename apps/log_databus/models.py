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

from typing import Union

from apps.exceptions import ApiResultError
from apps.log_databus.exceptions import ArchiveNotFound, CollectorPluginNotImplemented
from apps.models import MultiStrSplitByCommaFieldText
from apps.utils.cache import cache_one_hour
from apps.utils.function import map_if
from apps.utils.local import get_request_username
from apps.utils.log import logger
from apps.utils.thread import MultiExecuteFunc

"""
databus
1. 采集（collector）
2. 清洗（clean)
3. 入库
"""

from django.db import models, transaction  # noqa
from django.utils import timezone  # noqa
from django.utils.functional import cached_property  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa
from django_jsonfield_backport.models import JSONField  # noqa  pylint: disable=unused-import

from apps.api import CmsiApi, TransferApi  # noqa
from apps.log_databus.constants import (  # noqa
    ArchiveInstanceType,
    ETLProcessorChoices,
    EtlConfigChoices,
    TargetObjectTypeEnum,  # noqa
    TargetNodeTypeEnum,  # noqa
    CollectItsmStatus,  # noqa
    ADMIN_REQUEST_USER,
    EtlConfig,  # noqa
    VisibleEnum,
    ContainerCollectStatus,
    Environment,
)
from apps.log_search.constants import CollectorScenarioEnum, GlobalCategoriesEnum, InnerTag, CustomTypeEnum  # noqa
from apps.log_search.models import LogIndexSet, Space  # noqa
from apps.models import MultiStrSplitByCommaField, JsonField, SoftDeleteModel, OperateRecordModel  # noqa


class CollectorBase(SoftDeleteModel):
    """
    采集插件&采集项基类
    """

    bk_biz_id = models.BigIntegerField(_("业务id"))
    bkdata_biz_id = models.BigIntegerField(_("数据归属业务ID"), null=True, blank=True)

    class Meta:
        abstract = True

    def get_bk_biz_id(self):
        bk_biz_id = self.bkdata_biz_id or self.bk_biz_id
        return bk_biz_id

    def get_name(self):
        raise NotImplementedError

    def get_en_name(self):
        raise NotImplementedError


class CollectorConfig(CollectorBase):
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
    collector_plugin_id = models.BigIntegerField(_("采集插件ID"), db_index=True, null=True)
    bk_app_code = models.CharField(_("接入的来源APP"), max_length=64, default="bk_log_search")
    collector_scenario_id = models.CharField(_("采集场景"), max_length=64)
    custom_type = models.CharField(
        _("自定义类型"), max_length=30, choices=CustomTypeEnum.get_choices(), default=CustomTypeEnum.LOG.value
    )
    category_id = models.CharField(_("数据分类"), max_length=64)
    target_object_type = models.CharField(
        _("对象类型"), max_length=32, choices=TargetObjectTypeEnum.get_choices(), default=TargetObjectTypeEnum.HOST.value
    )
    target_node_type = models.CharField(
        _("节点类型"), max_length=32, choices=TargetNodeTypeEnum.get_choices(), default=TargetNodeTypeEnum.INSTANCE.value
    )
    target_nodes = JsonField(_("采集目标"), null=True, default=None)
    target_subscription_diff = JsonField(_("与上一次采集订阅的差异"), null=True)
    description = models.TextField(_("描述"), default="")
    is_active = models.BooleanField(_("是否可用"), default=True)
    data_link_id = models.IntegerField(_("采集链路id"), null=True, default=None)
    bk_data_id = models.IntegerField(_("采集链路data_id"), null=True, default=None)
    bk_data_name = models.CharField(_("采集链路data_name"), null=True, default=None, max_length=64)
    table_id = models.CharField(_("结果表ID"), max_length=255, null=True, default=None)
    bkbase_table_id = models.CharField(_("BKBASE结果表ID"), max_length=255, null=True, default=None)
    processing_id = models.CharField(_("计算平台清洗id"), max_length=255, null=True, blank=True)
    etl_processor = models.CharField(
        _("数据处理引擎"),
        max_length=32,
        choices=ETLProcessorChoices.get_choices(),
        default=ETLProcessorChoices.TRANSFER.value,
    )
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
    collector_config_overlay = models.JSONField(_("采集器配置覆盖"), null=True, default=None, max_length=32, blank=True)
    storage_shards_nums = models.IntegerField(_("ES分片数量"), null=True, default=None, blank=True)
    storage_shards_size = models.IntegerField(_("单shards分片大小"), null=True, default=None, blank=True)
    storage_replies = models.IntegerField(_("ES副本数"), null=True, default=1, blank=True)
    bkdata_data_id_sync_times = models.IntegerField(_("调用数据平台创建data_id失败数"), default=0)
    collector_config_name_en = models.CharField(_("采集项英文名"), max_length=255, null=True, blank=True, default="")
    environment = models.CharField(_("环境"), max_length=128, null=True, blank=True)
    bcs_cluster_id = models.CharField(_("bcs集群id"), max_length=128, null=True, blank=True)
    extra_labels = models.JSONField(_("额外字段添加"), null=True, blank=True)
    add_pod_label = models.BooleanField(_("是否自动添加pod中的labels"), default=False)

    yaml_config_enabled = models.BooleanField(_("是否使用yaml配置模式"), default=False)
    yaml_config = models.TextField(_("yaml配置内容"), default="")
    rule_id = models.IntegerField(_("bcs规则集id"), default=0)
    is_display = models.BooleanField(_("采集项是否对用户可见"), default=True)
    log_group_id = models.BigIntegerField(_("自定义日志组ID"), null=True, blank=True)

    def get_name(self):
        return self.collector_config_name

    def get_en_name(self):
        return self.collector_config_name_en

    @property
    def is_clustering(self) -> bool:
        from apps.log_clustering.models import ClusteringConfig

        return ClusteringConfig.objects.filter(
            collector_config_id=self.collector_config_id, signature_enable=True
        ).exists()

    def get_etl_config(self):
        multi_execute_func = MultiExecuteFunc()
        multi_execute_func.append(
            "result_table_config",
            TransferApi.get_result_table,
            params={"table_id": self.table_id, "no_request": True},
            use_request=False,
        )
        multi_execute_func.append(
            "result_table_storage",
            TransferApi.get_result_table_storage,
            params={"result_table_list": self.table_id, "storage_type": "elasticsearch", "no_request": True},
            use_request=False,
        )
        result = multi_execute_func.run()
        from apps.log_databus.handlers.etl_storage import EtlStorage

        self.etl_config = EtlStorage.get_etl_config(result["result_table_config"], default=self.etl_config)
        etl_storage = EtlStorage.get_instance(etl_config=self.etl_config)
        etl_config = etl_storage.parse_result_table_config(
            result_table_config=result["result_table_config"],
            result_table_storage=result["result_table_storage"][self.table_id],
        )
        etl_config["fields"] = map_if(etl_config["fields"], if_func=lambda x: not x["is_built_in"])
        return etl_config

    def get_all_etl_fields(self):
        result_table_conf = TransferApi.get_result_table(params={"table_id": self.table_id})
        return result_table_conf.get("field_list", [])

    def get_result_table_kafka_config(self):
        return TransferApi.get_data_id({"bk_data_id": self.bk_data_id})["mq_config"]

    def get_bk_data_by_name(self):
        try:
            bk_data = TransferApi.get_data_id({"data_name": self.bk_data_name})
            return bk_data
        except ApiResultError:
            logger.debug(f"bk_data_name: {self.bk_data_name} is not exist.")

        return None

    def get_result_table_by_id(self):
        try:
            result_table = TransferApi.get_result_table({"table_id": self.table_id})
            return result_table
        except ApiResultError:
            logger.debug(f"result_table_id: {self.table_id} is not exist.")

        return None

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
        index_together = [["custom_type", "log_group_id"]]

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

    def itsm_has_appling(self):
        return self.itsm_ticket_status == CollectItsmStatus.APPLYING.value

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
        space = Space.objects.get(bk_biz_id=self.bk_biz_id)
        return str(
            _("【日志采集】{}-{}-{}".format(space.space_name, self.collector_config_name, self.created_at.strftime("%Y%m%d")))
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

    @staticmethod
    @cache_one_hour("data_id_conf_{bk_data_id}", need_md5=True)
    def get_data_id_conf(bk_data_id):
        return TransferApi.get_data_id({"bk_data_id": bk_data_id, "no_request": True})

    @property
    def is_container_environment(self):
        """
        是否为容器类型
        """
        return self.environment == Environment.CONTAINER

    @property
    def is_custom_scenario(self):
        """
        是否为自定义上报场景
        """
        return self.collector_scenario_id == CollectorScenarioEnum.CUSTOM.value


class ContainerCollectorConfig(SoftDeleteModel):
    collector_config_id = models.IntegerField(_("采集项id"), db_index=True)
    collector_type = models.CharField(_("容器采集类型"), max_length=64, null=True, blank=True)
    namespaces = models.JSONField(_("namespace选择"), null=True, blank=True)
    any_namespace = models.BooleanField(_("所有namespace"), default=False)
    data_encoding = models.CharField(_("日志字符集"), max_length=30, null=True, default=None)
    params = models.JSONField(_("params"), null=True, blank=True)
    workload_type = models.CharField(_("应用类型"), max_length=128, null=True, blank=True)
    workload_name = models.CharField(_("应用名称"), max_length=128, null=True, blank=True)
    container_name = models.CharField(_("容器名"), max_length=128, null=True, blank=True)
    match_labels = models.JSONField(_("匹配标签"), null=True, blank=True)
    match_expressions = models.JSONField(_("匹配表达式"), null=True, blank=True)
    all_container = models.BooleanField(_("所有容器"), default=False)
    status = models.CharField(
        _("下发状态"), null=True, blank=True, max_length=30, choices=ContainerCollectStatus.get_choices()
    )
    status_detail = models.TextField("状态详情", default="", blank=True)
    raw_config = models.JSONField(_("原始配置"), null=True, blank=True)
    parent_container_config_id = models.IntegerField(_("父配置id"), default=0)
    rule_id = models.IntegerField(_("bcs规则集id"), default=0)


class BcsRule(SoftDeleteModel):
    rule_name = models.CharField(_("采集配置名称"), max_length=64)
    bcs_project_id = models.CharField(_("项目ID"), max_length=64, default="")


class ItsmEtlConfig(SoftDeleteModel):
    ticket_sn = models.CharField(_("itsm单据号"), max_length=255)
    request_param = models.JSONField(_("请求参数"))


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
    CLUSTER_INFO_BIZ_ID = 0

    bk_biz_id = models.IntegerField(_("业务id"))
    storage_cluster_id = models.IntegerField(_("集群ID"))
    storage_used = models.FloatField(_("已用容量"), default=0)
    storage_usage = models.IntegerField(_("容量使用率"), default=0)
    storage_total = models.BigIntegerField(_("总容量"), default=0)
    index_count = models.IntegerField(_("索引数量"), default=0)
    biz_count = models.IntegerField(_("业务数量"), default=0)

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
    etl_config = models.CharField(_("清洗配置"), max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = _("高级清洗列表")
        verbose_name_plural = _("高级清洗列表")
        ordering = ("-updated_at",)


class CleanTemplate(SoftDeleteModel):
    clean_template_id = models.AutoField(_("清洗id"), primary_key=True)
    name = models.CharField(_("模板名"), max_length=128)
    clean_type = models.CharField(_("模板类型"), max_length=64)
    etl_params = models.JSONField(_("etl配置"), null=True, blank=True)
    etl_fields = models.JSONField(_("etl字段"), null=True, blank=True)
    bk_biz_id = models.IntegerField(_("业务id"))
    visible_type = models.CharField(_("可见类型"), max_length=64, default=VisibleEnum.CURRENT_BIZ.value)
    visible_bk_biz_id = MultiStrSplitByCommaFieldText(_("可见业务ID"), default="")

    class Meta:
        verbose_name = _("清洗模板")
        verbose_name_plural = _("清洗模板")
        ordering = ("-updated_at",)


class CleanStash(SoftDeleteModel):
    clean_stash_id = models.AutoField(_("清洗缓存id"), primary_key=True)
    clean_type = models.CharField(_("模板类型"), max_length=64)
    etl_params = models.JSONField(_("etl配置"), null=True, blank=True)
    etl_fields = models.JSONField(_("etl字段"), null=True, blank=True)
    collector_config_id = models.IntegerField(_("采集项列表"), db_index=True)
    bk_biz_id = models.IntegerField(_("业务id"))

    class Meta:
        verbose_name = _("未完成入库暂存清洗")
        verbose_name_plural = _("未完成入库暂存清洗")
        ordering = ("-updated_at",)


class ArchiveConfig(SoftDeleteModel):
    archive_config_id = models.AutoField(_("归档配置id"), primary_key=True)
    instance_id = models.IntegerField(_("关联采集项id"))
    instance_type = models.CharField(
        _("实例类型"),
        max_length=64,
        choices=ArchiveInstanceType.choices,
        default=ArchiveInstanceType.COLLECTOR_CONFIG.value,
    )
    bk_biz_id = models.IntegerField(_("业务id"))
    # 快照存储天数
    snapshot_days = models.IntegerField(_("快照天数"), default=0)
    # 快照所在的快照仓库
    target_snapshot_repository_name = models.CharField(_("快照仓库名称"), max_length=255, default="")

    class Meta:
        ordering = ("-archive_config_id",)
        verbose_name = _("归档配置表")
        verbose_name_plural = _("归档配置表")

    @cached_property
    def instance(self) -> Union["CollectorConfig", "CollectorPlugin"]:
        if self.instance_type == ArchiveInstanceType.COLLECTOR_CONFIG.value:
            return CollectorConfig.objects.get(collector_config_id=self.instance_id)
        if self.instance_type == ArchiveInstanceType.COLLECTOR_PLUGIN.value:
            return CollectorPlugin.objects.get(collector_plugin_id=self.instance_id)

    @property
    def table_id(self) -> str:
        return self.instance.table_id

    @property
    def instance_name(self) -> str:
        return self.instance.get_name()

    @property
    def collector_config_id(self) -> int:
        # 对采集插件归档时，获取采集插件下首个采集项ID
        if self.instance_type == ArchiveInstanceType.COLLECTOR_PLUGIN.value:
            return CollectorPlugin.get_collector_config_id(self.instance_id)
        if self.instance_type == ArchiveInstanceType.COLLECTOR_CONFIG.value:
            return self.instance_id

    @classmethod
    def get_collector_config_id(cls, archive_config_id) -> int:
        try:
            archive_config: cls = cls.objects.get(archive_config_id=archive_config_id)
            return archive_config.collector_config_id
        except cls.DoesNotExist:
            raise ArchiveNotFound


class RestoreConfig(SoftDeleteModel):
    restore_config_id = models.AutoField(_("采集配置ID"), primary_key=True)
    bk_biz_id = models.IntegerField(_("业务id"))
    archive_config_id = models.IntegerField(_("归档id"))
    meta_restore_id = models.IntegerField(_("meta回溯id"), null=True, default=None)
    start_time = models.DateTimeField(_("开始时间"))
    end_time = models.DateTimeField(_("结束时间"))
    expired_time = models.DateTimeField(_("到期时间"))
    is_done = models.BooleanField(_("是否完成"), default=False)
    duration = models.IntegerField(_("耗时"), default=-1)
    total_store_size = models.BigIntegerField(_("存储大小"), null=True, default=None)
    total_doc_count = models.BigIntegerField(_("文档数量"), null=True, default=None)
    index_set_name = models.CharField(_("索引集名称"), max_length=64)
    index_set_id = models.IntegerField(_("索引集id"), null=True, default=None)
    notice_user = models.TextField(_("结果通知人"))

    class Meta:
        ordering = ("-restore_config_id",)
        verbose_name = _("回溯配置表")
        verbose_name_plural = _("回溯配置表")

    @cached_property
    def archive(self) -> "ArchiveConfig":
        return ArchiveConfig.objects.get(archive_config_id=self.archive_config_id)

    def is_expired(self) -> bool:
        return timezone.now() > self.expired_time

    def done(self, duration):
        self.is_done = True
        self.duration = duration
        self.save()
        LogIndexSet.delete_tag_by_name(self.index_set_id, InnerTag.RESTORING.value)
        LogIndexSet.set_tag(self.index_set_id, InnerTag.RESTORED.value)
        # notify user
        send_params = {
            "receivers": self.notice_user,
            "content": "你创建的归档回溯已经完成",
            "title": str(_("【日志平台】")),
        }
        CmsiApi.send_mail(send_params)
        CmsiApi.send_weixin(send_params)

    @classmethod
    def get_collector_config_id(cls, restore_config_id):
        restore: "RestoreConfig" = cls.objects.get(restore_config_id=restore_config_id)
        return restore.archive.collector_config_id


class CollectorPlugin(CollectorBase):
    """
    采集插件，控制采集项行为
    """

    collector_plugin_id = models.BigAutoField(_("采集插件ID"), primary_key=True)
    collector_plugin_name = models.CharField(_("采集插件名称"), max_length=64)
    collector_plugin_name_en = models.CharField(_("英文采集插件名称"), max_length=64)
    collector_scenario_id = models.CharField(_("采集场景ID"), max_length=64)
    description = models.CharField(_("插件描述"), max_length=64)
    category_id = models.CharField(_("数据分类"), max_length=64)
    data_encoding = models.CharField(_("日志字符集"), max_length=30, null=True, default=None)
    is_display_collector = models.BooleanField(_("采集项是否对用户可见"), default=False)
    is_allow_alone_data_id = models.BooleanField(_("是否允许使用独立DATAID"), default=True)
    bk_data_id = models.IntegerField(_("DATAID"), null=True)
    data_link_id = models.IntegerField(_("数据链路ID"), null=True)
    processing_id = models.CharField(_("计算平台清洗id"), max_length=255, null=True, blank=True)
    is_allow_alone_etl_config = models.BooleanField(_("是否允许独立配置清洗规则"), default=True)
    etl_processor = models.CharField(
        _("数据处理器"), max_length=32, choices=ETLProcessorChoices.get_choices(), default=ETLProcessorChoices.TRANSFER.value
    )
    etl_config = models.CharField(
        _("清洗配置"), max_length=32, null=True, default=None, choices=EtlConfigChoices.get_choices()
    )
    etl_params = models.JSONField(_("清洗参数"), null=True)
    fields = models.JSONField(_("清洗字段"), null=True)
    params = models.JSONField(_("采集插件参数"), default=dict, null=True)
    table_id = models.CharField(_("结果表ID"), max_length=255, null=True)
    bkbase_table_id = models.CharField(_("BKBASE结果表ID"), max_length=255, null=True)
    is_allow_alone_storage = models.BooleanField(_("是否允许独立存储"), default=True)
    storage_cluster_id = models.IntegerField(_("存储集群ID"), null=True)
    retention = models.IntegerField(_("数据有效时间"), null=True)
    allocation_min_days = models.IntegerField(_("冷热数据生效时间"), null=True)
    storage_replies = models.IntegerField(_("副本数量"), null=True)
    storage_shards_nums = models.IntegerField(_("ES分片数量"), null=True, default=None, blank=True)
    storage_shards_size = models.IntegerField(_("单shards分片大小"), null=True, default=None, blank=True)
    index_settings = models.JSONField(_("索引Settings"), default=dict)

    class Meta:
        verbose_name = _("用户采集插件")
        verbose_name_plural = verbose_name
        ordering = ("-updated_at",)
        unique_together = [
            ("collector_plugin_name", "bk_biz_id"),
            ("collector_plugin_name_en", "bk_biz_id"),
        ]

    def get_updated_by(self):
        if self.updated_by == ADMIN_REQUEST_USER:
            return self.created_by
        return self.updated_by

    def get_name(self):
        return self.collector_plugin_name

    def get_en_name(self):
        return self.collector_plugin_name_en

    def get_transfer_table_id(self):
        return self.transfer_table_id

    def set_transfer_table_id(self, table_id: str):
        self.transfer_table_id = table_id
        self.save()

    def get_table_id(self):
        if self.etl_processor == ETLProcessorChoices.BKBASE.value:
            return self.bkbase_table_id
        return self.table_id

    @transaction.atomic()
    def change_collector_display_status(self, display_status: bool):
        """更改采集项可见状态"""
        request_user = get_request_username()
        self.is_display_collector = display_status
        self.save()
        CollectorConfig.objects.filter(collector_plugin_id=self.collector_plugin_id).update(
            is_display=display_status, updated_at=timezone.now(), updated_by=request_user
        )
        logger.info("[Change Collector Plugin Display Status] %s %s", self.collector_plugin_id, request_user)

    @classmethod
    def get_collector_config_id(cls, collector_plugin_id: int) -> int:
        """获取任一采集项ID (默认返回ID最小的)"""
        collector = (
            CollectorConfig.objects.filter(collector_plugin_id=collector_plugin_id)
            .order_by("collector_config_id")
            .first()
        )
        if collector is None:
            raise CollectorPluginNotImplemented()
        return collector.collector_config_id
