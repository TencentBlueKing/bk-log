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
import datetime
import os
import time
from collections import defaultdict
from typing import Union, List

from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.transaction import atomic
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from jinja2 import Environment, FileSystemLoader

from apps.exceptions import BizNotExistError
from apps.feature_toggle.handlers.toggle import feature_switch
from apps.log_clustering.constants import PatternEnum, YearOnYearEnum
from apps.log_databus.constants import EsSourceType
from apps.log_search.exceptions import (
    SourceDuplicateException,
    IndexSetNameDuplicateException,
    ScenarioNotSupportedException,
    CouldNotFindTemplateException,
    DefaultConfigNotAllowedDelete,
)
from apps.models import JsonField, MultiStrSplitByCommaField, SoftDeleteModel, OperateRecordModel, model_to_dict
from apps.utils.base_crypt import BaseCrypt
from apps.utils.db import array_group
from apps.utils.db import array_hash
from apps.utils.local import get_request_username, get_request_app_code
from apps.log_search.constants import (
    GlobalTypeEnum,
    CollectorScenarioEnum,
    GlobalCategoriesEnum,
    EtlConfigEnum,
    FieldDataTypeEnum,
    FieldDateFormatEnum,
    FieldBuiltInEnum,
    TimeZoneEnum,
    SeparatorEnum,
    StorageDurationTimeEnum,
    TimeFieldTypeEnum,
    TimeFieldUnitEnum,
    DEFAULT_TIME_FIELD,
    EncodingsEnum,
    TagColor,
    InnerTag,
    CustomTypeEnum,
    INDEX_SET_NO_DATA_CHECK_PREFIX,
    INDEX_SET_NO_DATA_CHECK_INTERVAL,
    DEFAULT_INDEX_SET_FIELDS_CONFIG_NAME,
    FavoriteGroupType,
    FavoriteVisibleType,
    FavoriteListOrderType,
    INDEX_SET_NOT_EXISTED,
)
from bkm_space.api import AbstractSpaceApi
from bkm_space.define import Space as SpaceDefine
from bkm_space.utils import space_uid_to_bk_biz_id
from bkm_ipchooser.constants import CommonEnum
from apps.utils.time_handler import timestamp_to_datetime, datetime_to_timestamp, timestamp_to_timeformat


class GlobalConfig(models.Model):
    """
    全局变量：统一管理全局变量
    - category 数据分类（二级分类，目前只支持HOST方式，不使用CMDB服务实例变量）
    - data_encoding 编码格式
    - data_delimiter 分隔符列表
    - storage_duration_time：数据保存时间
    - collector_scenario：采集场景：行日志、段日志、window event等
    """

    config_id = models.CharField(_("配置标识"), max_length=32, primary_key=True)
    configs = JsonField(_("具体配置"))

    @classmethod
    def get_configs(cls) -> dict:
        """
        获取所有全局配置
        :return: dict[config_id: configs] 所有全局配置
        """
        configs = {
            config.config_id: config.configs
            for config in cls.objects.all()
            if config.config_id not in ["APIGW_PUBLIC_KEY"]
        }
        # 过期时间
        configs[GlobalTypeEnum.STORAGE_DURATION_TIME.value] = StorageDurationTimeEnum.get_choices_list_dict()
        # 分类
        configs[GlobalTypeEnum.CATEGORY.value] = GlobalCategoriesEnum.get_init_categories()
        # 接入场景
        configs[GlobalTypeEnum.COLLECTOR_SCENARIO.value] = CollectorScenarioEnum.get_choices_list_dict()
        # 清洗场景
        configs[GlobalTypeEnum.ETL_CONFIG.value] = EtlConfigEnum.get_choices_list_dict()
        # 字段类型
        configs[GlobalTypeEnum.FIELD_DATA_TYPE.value] = FieldDataTypeEnum.get_choices_list_dict()
        # 时间格式
        configs[GlobalTypeEnum.Field_DATE_FORMAT.value] = FieldDateFormatEnum.get_choices_list_dict()
        # 系统内置字段
        configs[GlobalTypeEnum.FIELD_BUILT_IN.value] = FieldBuiltInEnum.get_choices_list_dict()
        # 时区
        configs[GlobalTypeEnum.TIME_ZONE.value] = TimeZoneEnum.get_choices_list_dict()
        # 分隔符
        configs[GlobalTypeEnum.DATA_DELIMITER.value] = SeparatorEnum.get_choices_list_dict()
        # 时间字段类型
        configs[GlobalTypeEnum.TIME_FIELD_TYPE.value] = TimeFieldTypeEnum.get_choices_list_dict()
        # 时间字段单位
        configs[GlobalTypeEnum.TIME_FIELD_UNIT.value] = TimeFieldUnitEnum.get_choices_list_dict()
        # 日志编码
        configs[GlobalTypeEnum.DATA_ENCODING.value] = EncodingsEnum.get_choices_list_dict()
        # ES日志来源类型
        configs[GlobalTypeEnum.ES_SOURCE_TYPE.value] = EsSourceType.get_choices_list_dict()
        # 日志聚类
        configs[GlobalTypeEnum.LOG_CLUSTERING_LEVEL.value] = list(PatternEnum.get_dict_choices().keys())
        configs[GlobalTypeEnum.LOG_CLUSTERING_YEAR_ON_YEAR.value] = YearOnYearEnum.get_choices_list_dict()
        # 自定义上报
        configs[GlobalTypeEnum.DATABUS_CUSTOM.value] = CustomTypeEnum.get_choices_list_dict()
        # 主机标识优先级
        configs[GlobalTypeEnum.HOST_IDENTIFIER_PRIORITY.value] = []
        host_identifier_priority = settings.HOST_IDENTIFIER_PRIORITY.split(",")
        for i in host_identifier_priority:
            if i in CommonEnum.DEFAULT_HOST_FIELDS.value and i in CommonEnum.IPCHOOSER_FIELD_MAP.value:
                configs[GlobalTypeEnum.HOST_IDENTIFIER_PRIORITY.value].append(CommonEnum.IPCHOOSER_FIELD_MAP.value[i])
        return configs

    class Meta:
        verbose_name = _("00_全局配置")
        verbose_name_plural = _("00_全局配置")


# todo 翻译映射表（key(中文), language(和settings.language对应), content(翻译语言内容)）
# 全量获取后获得 (key, language): content内容  根据key中文 + language 获取对应翻译内容
# class TranslateRelationship


class Scenario(object):
    """
    接入场景
    """

    LOG = "log"
    BKDATA = "bkdata"
    ES = "es"

    CHOICES = (
        (LOG, _("采集接入")),
        (BKDATA, _("数据平台")),
        (ES, _("第三方ES")),
    )

    @classmethod
    def get_scenarios(cls):
        data = []
        for (key, value) in cls.CHOICES:
            if feature_switch(f"scenario_{key}"):
                data.append({"scenario_id": key, "scenario_name": value})
        return data


class ProjectInfo(SoftDeleteModel):
    project_id = models.AutoField(_("项目ID"), primary_key=True)
    project_name = models.CharField(_("项目名称"), max_length=64)
    bk_biz_id = models.IntegerField(_("业务ID"), null=True, default=None)
    bk_app_code = models.CharField(_("接入的来源APP"), max_length=64)
    time_zone = models.CharField(_("时区"), max_length=64)
    description = models.TextField(_("描述"), null=True)
    ip_topo_switch = models.BooleanField(_("是否可以使用ip快选"), default=True)
    is_v3_biz = models.BooleanField(_("是否为 CMDB V3 业务"), default=True)
    is_v3_mixed = models.BooleanField(_("是否混合使用CMDB V3 业务"), default=False)
    feature_toggle = models.CharField(_("功能白名单"), max_length=255, default=None, null=True)

    @classmethod
    def get_cmdb_projects(cls):
        return array_hash(
            ProjectInfo.objects.exclude(bk_biz_id__isnull=True).values("project_id", "bk_biz_id"),
            "bk_biz_id",
            "project_id",
        )

    @classmethod
    def get_bizs(cls, biz_ids=None):
        """
        获取CMDB业务列表
        """
        qs = ProjectInfo.objects.filter()
        if biz_ids:
            qs = qs.filter(bk_biz_id__in=biz_ids)
        return [{"bk_biz_id": item.bk_biz_id, "bk_biz_name": item.project_name} for item in qs.all()]

    def get_feature_toggle(self):
        if not self.feature_toggle:
            return []
        feature_toggles = []
        for item in self.feature_toggle.split(","):
            if not item:
                continue
            feature_toggles.append(item.strip())
        return feature_toggles

    @classmethod
    def get_biz(cls, biz_id=None):
        projects = ProjectInfo.objects.filter(bk_biz_id=biz_id)
        if not projects.exists():
            raise BizNotExistError(BizNotExistError.MESSAGE.format(bk_biz_id=biz_id))

        project = projects.first()
        return {"bk_biz_id": project.bk_biz_id, "bk_biz_name": project.project_name}

    @classmethod
    def get_project(cls, biz_id=None):
        projects = ProjectInfo.objects.filter(bk_biz_id=biz_id)
        if not projects.exists():
            raise BizNotExistError(BizNotExistError.MESSAGE.format(bk_biz_id=biz_id))
        project = projects.first()
        return {"project_id": project.project_id, "bk_biz_name": project.project_name}

    class Meta:
        verbose_name = _("项目列表")
        verbose_name_plural = _("02_项目列表")


class AccessSourceConfig(SoftDeleteModel):
    """
    properties: 对于用户ES的敏感信息必须使用加密方式写入
    """

    source_id = models.AutoField(_("数据源ID"), primary_key=True)
    source_name = models.CharField(_("数据源名称"), max_length=64)
    scenario_id = models.CharField(_("接入场景标识"), max_length=64, choices=Scenario.CHOICES)
    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256)
    project_id = models.IntegerField(_("项目ID"), null=True, default=None)

    properties = JsonField(_("属性"), default=None, null=True)
    orders = models.IntegerField(_("顺序"), default=0)
    is_editable = models.BooleanField(_("是否可以编辑"), default=True)

    def save(self, *args, **kwargs):
        queryset = AccessSourceConfig.objects.filter(space_uid=self.space_uid, source_name=self.source_name).first()

        # 判断名称是否重复
        if queryset and queryset.source_id != self.source_id:
            raise SourceDuplicateException(SourceDuplicateException.MESSAGE.format(source_name=self.source_name))

        if self.scenario_id == Scenario.ES and not self.is_deleted:
            # 同项目下，不允许添加相同ip和端口的数据源
            for source in AccessSourceConfig.objects.filter(space_uid=self.space_uid):
                if (
                    source.properties["es_host"] == self.properties["es_host"]
                    and source.properties["es_port"] == self.properties["es_port"]
                    and source.source_id != self.source_id
                ):
                    raise SourceDuplicateException(
                        _(
                            f"此空间[{self.space_uid}]下已存在"
                            f"{self.properties['es_host']}:{self.properties['es_port']}的ES数据源"
                            f"——名称为：[{source.source_name}]"
                        )
                    )

        self.properties["es_password"] = BaseCrypt().encrypt(self.properties["es_password"])

        super().save(*args, **kwargs)

    def decode_password(self):
        """
        ES属性加密（仅针对ES密码）
        """
        if self.scenario_id == Scenario.ES:
            if not self.properties.get("es_password"):
                return ""
            return BaseCrypt().decrypt(self.properties["es_password"])
        else:
            raise ScenarioNotSupportedException(_("暂不支持除ES自定义场景意外的其它场景"))

    class Meta:
        ordering = ("-orders", "-source_id")
        verbose_name = _("ES集群配置")
        verbose_name_plural = _("03_ES集群配置")


class LogIndexSet(SoftDeleteModel):
    class Status(object):
        """
        审批状态
        """

        PENDING = "pending"
        NORMAL = "normal"

    index_set_id = models.AutoField(_("索引集ID"), primary_key=True)
    index_set_name = models.CharField(_("索引集名称"), max_length=64)
    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256, db_index=True)
    project_id = models.IntegerField(_("项目ID"), default=0, db_index=True)
    category_id = models.CharField(_("数据分类"), max_length=64, null=True, default=None)
    bkdata_project_id = models.IntegerField(_("绑定的数据平台项目ID"), null=True, default=None)
    collector_config_id = models.IntegerField(_("绑定Transfer采集ID"), null=True, default=None)
    scenario_id = models.CharField(_("接入场景标识"), max_length=64, choices=Scenario.CHOICES)
    storage_cluster_id = models.IntegerField(_("存储集群ID"), default=None, null=True, blank=True)
    source_id = models.IntegerField(_("数据源ID"), default=None, null=True, blank=True)
    orders = models.IntegerField(_("顺序"), default=0)
    view_roles = MultiStrSplitByCommaField(
        _("查看权限"), max_length=255, sub_type=int, null=True, blank=True
    )  # 冗余字段: 权限由AUTH模块处理
    # 预查询校验
    pre_check_tag = models.BooleanField(_("是否通过"), default=True)
    pre_check_msg = models.TextField(_("预查询描述"), null=True)
    is_active = models.BooleanField(_("是否可用"), default=True)
    # 字段快照
    fields_snapshot = JsonField(_("字段快照"), default=None, null=True)

    #  是否trace索引集
    is_trace_log = models.BooleanField(_("是否trace"), default=False)

    source_app_code = models.CharField(verbose_name=_("来源系统"), default=get_request_app_code, max_length=32, blank=True)

    # 时间字段
    time_field = models.CharField(_("时间字段"), max_length=32, default=None, null=True)
    time_field_type = models.CharField(_("时间字段类型"), max_length=32, default=None, null=True)
    time_field_unit = models.CharField(_("时间字段单位"), max_length=32, default=None, null=True)
    tag_ids = MultiStrSplitByCommaField(_("标签id记录"), max_length=255, default="")
    bcs_project_id = models.CharField(_("项目ID"), max_length=64, default="")
    is_editable = models.BooleanField(_("是否可以编辑"), default=True)

    def list_operate(self):
        return format_html(
            '<a href="../logindexsetdata/?index_set_id=%s">详情</a>&nbsp;&nbsp;' % self.index_set_id
            + '<a href="../../log_auth/authpolicyinfo/?action_id=index_set.retrieve&resource_scope_id=%s">'
            "查看权限</a>&nbsp;&nbsp;" % self.index_set_id
        )

    list_operate.__name__ = "操作列表"

    def save(self, *args, **kwargs):
        queryset = LogIndexSet.objects.filter(
            space_uid=self.space_uid, index_set_name=self.index_set_name, is_deleted=False
        )
        if queryset.exists() and queryset[0].index_set_id != self.index_set_id:
            raise IndexSetNameDuplicateException(
                IndexSetNameDuplicateException.MESSAGE.format(index_set_name=self.index_set_name)
            )
        super().save(*args, **kwargs)

    @property
    def indexes(self):
        """
        返回当前索引集下的索引列表
        :return:
        """
        return self.get_indexes()

    @classmethod
    def get_bcs_index_set(cls, space_uid, bcs_project_id):
        src_index_list = LogIndexSet.objects.filter(space_uid=space_uid, bcs_project_id=bcs_project_id)
        bcs_path_index_set = None
        bcs_std_index_set = None
        for src_index in src_index_list:
            if "bcs_path_log_" in src_index.index_set_name:
                bcs_path_index_set = src_index
                continue
            if "bcs_stdout_log_" in src_index.index_set_name:
                bcs_std_index_set = src_index
        return bcs_path_index_set, bcs_std_index_set

    @property
    def scenario_name(self):
        return self.get_scenario_id_display()

    @property
    def source_name(self):
        if not self.source_id:
            return "--"
        return AccessSourceConfig.objects.get(source_id=self.source_id).source_name

    @property
    def bkdata_auth_url(self):
        from apps.utils.bk_data_auth import BkDataAuthHandler

        # 获取数据平台权限申请url
        if self.scenario_id != Scenario.BKDATA:
            return ""
        not_applied_indices = (
            LogIndexSetData.objects.filter(index_set_id=self.index_set_id)
            .exclude(apply_status=LogIndexSetData.Status.NORMAL)
            .values_list("result_table_id", flat=True)
        )
        if not not_applied_indices:
            return ""

        return BkDataAuthHandler.get_auth_url(not_applied_indices)

    @property
    def no_data_check_time(self):
        result = cache.get(INDEX_SET_NO_DATA_CHECK_PREFIX + str(self.index_set_id))
        if result is None:
            temp = timestamp_to_datetime(time.time()) - datetime.timedelta(minutes=INDEX_SET_NO_DATA_CHECK_INTERVAL)
            result = datetime_to_timestamp(temp)
        return timestamp_to_timeformat(result)

    def get_indexes(self, has_applied=None, project_info=True):
        """
        返回当前索引集下的索引列表
        :return:
        """
        index_set_data = LogIndexSetData.objects.filter(index_set_id=self.index_set_id)
        if has_applied:
            index_set_data = index_set_data.filter(apply_status=LogIndexSetData.Status.NORMAL)
        bizs = {}
        if self.scenario_id == Scenario.BKDATA:
            if project_info is True:
                bizs = {
                    space.bk_biz_id: space.space_name
                    for space in Space.objects.filter(bk_biz_id__in=list({data.bk_biz_id for data in index_set_data}))
                }
        source_name = self.source_name

        return [
            {
                "index_id": data.index_id,
                "index_set_id": self.index_set_id,
                "bk_biz_id": data.bk_biz_id,
                "bk_biz_name": bizs.get(data.bk_biz_id, "") if project_info is False else None,
                "source_id": self.source_id,
                "source_name": source_name,
                "result_table_id": data.result_table_id,
                "time_field": data.time_field,
                "result_table_name": data.result_table_name,
                "apply_status": data.apply_status,
                "apply_status_name": data.get_apply_status_display(),
            }
            for data in index_set_data
        ]

    @classmethod
    def get_index_set(cls, index_set_ids=None, scenarios=None, space_uid=None, is_trace_log=False, show_indices=True):
        qs = cls.objects.filter(is_active=True)
        if index_set_ids:
            qs = qs.filter(index_set_id__in=index_set_ids)
        if scenarios and isinstance(scenarios, list):
            qs = qs.filter(scenario_id__in=scenarios)
        if space_uid:
            qs = qs.filter(space_uid=space_uid)
        if is_trace_log:
            qs = qs.filter(is_trace_log=is_trace_log)

        no_data_check_time_list = [item.no_data_check_time for item in qs]

        index_sets = qs.values(
            "space_uid",
            "index_set_id",
            "index_set_name",
            "collector_config_id",
            "scenario_id",
            "storage_cluster_id",
            "category_id",
            "created_at",
            "time_field",
            "time_field_type",
            "time_field_unit",
            "tag_ids",
        )

        # 获取接入场景
        scenarios = array_hash(Scenario.get_scenarios(), "scenario_id", "scenario_name")

        # 获取索引详情
        index_set_ids = [index_set["index_set_id"] for index_set in index_sets]
        mark_index_set_ids = set(IndexSetUserFavorite.batch_get_mark_index_set(index_set_ids, get_request_username()))

        index_set_data = array_group(
            list(
                LogIndexSetData.objects.filter(
                    index_set_id__in=index_set_ids, apply_status=LogIndexSetData.Status.NORMAL
                )
                .values("bk_biz_id", "index_set_id", "result_table_id", "result_table_name", "time_field")
                .all()
            ),
            "index_set_id",
        )

        result = []
        for index_set, no_data_check_time in zip(index_sets, no_data_check_time_list):
            if show_indices:
                index_set["indices"] = index_set_data.get(index_set["index_set_id"], [])
                if not index_set["indices"]:
                    continue

            if not index_set["time_field"]:
                time_field = None
                indices = index_set_data.get(index_set["index_set_id"], [])
                if indices:
                    time_field = indices[0].get("time_field")
                if index_set["scenario_id"] in [Scenario.BKDATA, Scenario.LOG] and not time_field:
                    time_field = DEFAULT_TIME_FIELD
                index_set["time_field_type"] = TimeFieldTypeEnum.DATE.value
                index_set["time_field_unit"] = TimeFieldUnitEnum.MILLISECOND.value
                index_set["time_field"] = time_field

            index_set["scenario_name"] = scenarios.get(index_set["scenario_id"])
            index_set["bk_biz_id"] = space_uid_to_bk_biz_id(index_set["space_uid"])

            index_set["tags"] = IndexSetTag.batch_get_tags(index_set["tag_ids"])
            index_set["is_favorite"] = index_set["index_set_id"] in mark_index_set_ids
            index_set["no_data_check_time"] = no_data_check_time
            for del_field in ["tag_ids"]:
                index_set.pop(del_field)
            result.append(index_set)

        return sorted(result, key=lambda i: i["is_favorite"], reverse=True)

    def get_fields(self, use_snapshot=True):
        """
        取出或更新字段快照
        """
        if not isinstance(self.fields_snapshot, dict) or not self.fields_snapshot or not use_snapshot:
            self.sync_fields_snapshot()
        return self.fields_snapshot

    def sync_fields_snapshot(self, pre_check_enable=True):
        from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler

        fields = {}
        try:
            search_handler_esquery = SearchHandler(self.index_set_id, {}, pre_check_enable=pre_check_enable)
            fields = search_handler_esquery.fields()
            fields = self.fields_to_string(fields=fields)
            self.fields_snapshot = fields
        except Exception as e:  # pylint: disable=broad-except
            # 如果字段获取失败，则不修改原来的值
            self.fields_snapshot = self.fields_snapshot or fields
            raise e
        finally:
            self.save(update_fields=["fields_snapshot"])
        return fields

    @classmethod
    @atomic
    def set_tag(cls, index_set_id, *names):
        index_set = cls.objects.select_for_update().get(index_set_id=index_set_id)
        add_tag_ids = [str(IndexSetTag.get_tag_id(name)) for name in names]
        tag_ids = set(index_set.tag_ids)
        for add_tag_id in add_tag_ids:
            tag_ids.add(add_tag_id)
        index_set.tag_ids = list(tag_ids)
        index_set.save()

    @classmethod
    def delete_tag_by_name(cls, index_set_id, tag_name):
        delete_tag_id = IndexSetTag.get_tag_id(tag_name)
        cls.delete_tag(index_set_id, delete_tag_id)

    @classmethod
    @atomic
    def delete_tag(cls, index_set_id, *tag_ids):
        index_set = cls.objects.select_for_update().get(index_set_id=index_set_id)
        original_tag_ids = set(index_set.tag_ids)
        delete_tag_ids = {str(tag_id) for tag_id in tag_ids}
        remain_tag_ids = original_tag_ids - delete_tag_ids
        index_set.tag_ids = list(remain_tag_ids)
        index_set.save()

    def mark_favorite(self, username: str):
        IndexSetUserFavorite.mark(username, self.index_set_id)

    def cancel_favorite(self, username: str):
        IndexSetUserFavorite.cancel(username, self.index_set_id)

    @staticmethod
    def fields_to_string(fields):
        """
        translate __proxy__ obj usable_reason to str
        @params fields {dict}
        """
        fields["usable_reason"] = str(fields.get("usable_reason", ""))
        return fields

    class Meta:
        ordering = ("-orders", "-index_set_id")
        verbose_name = _("索引集配置")
        verbose_name_plural = _("21_索引集配置")


class LogIndexSetData(SoftDeleteModel):
    class Status(object):
        """
        审批状态维护
        """

        PENDING = "pending"
        NORMAL = "normal"
        DENY = "deny"
        ABNORMAL = "abnormal"

        StatusChoices = (
            (PENDING, _("审批中")),
            (NORMAL, _("正常")),
            (DENY, _("拒绝")),
            (ABNORMAL, _("异常")),
        )

    index_id = models.AutoField(_("索引ID"), primary_key=True)
    index_set_id = models.IntegerField(_("索引集ID"), db_index=True)
    bk_biz_id = models.IntegerField(_("业务ID"), null=True, default=None)
    result_table_id = models.CharField(_("结果表"), max_length=255)
    result_table_name = models.CharField(_("结果表名称"), max_length=255, null=True, default=None, blank=True)
    time_field = models.CharField(_("时间字段"), max_length=64, null=True, default=True, blank=True)
    apply_status = models.CharField(_("审核状态"), max_length=64, choices=Status.StatusChoices, default=Status.PENDING)

    def list_operate(self):
        return format_html('<a href="../logindexset/?index_set_id=%s">索引集</a>&nbsp;&nbsp;' % self.index_set_id)

    list_operate.__name__ = "操作列表"

    class Meta:
        ordering = ("-index_id",)
        verbose_name = _("索引集数据")
        verbose_name_plural = _("22_索引集详情")


class UserIndexSetConfig(SoftDeleteModel):
    index_set_id = models.IntegerField(_("索引集ID"), db_index=True)
    display_fields = JsonField(_("字段配置"))
    sort_list = JsonField(_("排序规则"), null=True, default=None)
    scope = models.CharField(_("应用范围"), max_length=32, default="default")

    class Meta:
        verbose_name = _("索引集自定义显示")
        verbose_name_plural = _("31_搜索-索引集自定义显示")


class UserIndexSetSearchHistory(SoftDeleteModel):
    index_set_id = models.IntegerField(_("索引集ID"))
    params = JsonField(_("检索条件"), null=True, default=None)
    search_type = models.CharField(_("检索类型"), max_length=32, default="default")
    duration = models.FloatField(_("查询耗时"), null=True, default=None)
    rank = models.IntegerField(_("排序"), default=0)

    class Meta:
        verbose_name = _("索引集用户检索记录")
        verbose_name_plural = _("32_搜索-索引集用户检索记录")


class ResourceChange(OperateRecordModel):
    """
    数据平台索引集变更记录
    1. 用户组变更：找出用户组对应的索引集
    2. 索引集变更：同步索引集角色信息

    同步方式：
    1. project.manage => project.manage
    2. index_set.retrieve => project.flow_member
    """

    class ChangeType(object):
        """
        变更类型
        """

        USER_GROUP = "user_group"
        RESOURCE = "resource"

        ChangeTypeChoices = (
            (USER_GROUP, _("用户组")),
            (RESOURCE, _("资源")),
        )

    class SyncStatus(object):
        """
        变更类型
        """

        PENDING = "pending"
        SUCCESS = "success"
        FAILED = "failed"

        SyncStatusChoices = (
            (PENDING, _("待处理")),
            (SUCCESS, _("同步完成")),
            (FAILED, _("同步失败")),
        )

    class ResourceType(object):
        """
        资源类型
        """

        INDEX_SET = "index_set"

        ResourceTypeChoices = ((INDEX_SET, _("索引集")),)

    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256, db_index=True)
    project_id = models.IntegerField(_("项目ID"), default=0, db_index=True)
    change_type = models.CharField(_("变更类型"), max_length=64, choices=ChangeType.ChangeTypeChoices)
    group_id = models.IntegerField(_("用户组ID"), null=True, default=None)
    resource_id = models.CharField(_("资源类型"), max_length=64, choices=ResourceType.ResourceTypeChoices)
    resource_scope_id = models.CharField(_("范围"), max_length=64)
    sync_status = models.CharField(_("同步状态"), max_length=32, db_index=True)
    sync_time = models.DateTimeField(_("同步时间"), null=True, default=None)

    @classmethod
    def change_index_set(cls, index_set: LogIndexSet):
        """
        索引集用户组变更后调用此函数同步数据平台权限
        """
        index_set = LogIndexSet.objects.get(index_set_id=index_set.index_set_id)
        if index_set.scenario_id != Scenario.BKDATA:
            return True

        return ResourceChange(
            space_uid=index_set.space_uid,
            change_type=cls.ChangeType.RESOURCE,
            resource_id=cls.ResourceType.INDEX_SET,
            resource_scope_id=index_set.index_set_id,
            sync_status=cls.SyncStatus.PENDING,
        ).save()

    class Meta:
        verbose_name = _("资源变更任务")
        verbose_name_plural = _("23_资源变更任务")


class FavoriteSearch(SoftDeleteModel):
    """检索收藏记录"""

    search_history_id = models.IntegerField(_("用户检索历史记录ID"), db_index=True)
    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256, db_index=True)
    project_id = models.IntegerField(_("项目ID"), default=0, db_index=True)
    description = models.CharField(_("收藏描述"), max_length=255)


class Favorite(OperateRecordModel):
    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256, db_index=True)
    index_set_id = models.IntegerField(_("索引集ID"))
    name = models.CharField(_("收藏名称"), max_length=255)
    group_id = models.IntegerField(_("收藏组ID"), db_index=True)
    params = JsonField(_("检索条件"), null=True, default=None)
    visible_type = models.CharField(_("可见类型"), max_length=64, choices=FavoriteVisibleType.get_choices())  # 个人 | 公开
    is_enable_display_fields = models.BooleanField(_("是否同时显示字段"), default=False)
    display_fields = models.JSONField(_("显示字段"), blank=True, default=None)

    class Meta:
        verbose_name = _("检索收藏")
        verbose_name_plural = _("34_搜索-检索收藏")
        ordering = ("-updated_at",)
        unique_together = [("name", "space_uid")]

    @classmethod
    def get_user_favorite(
        cls, space_uid: str, username: str, order_type: str = FavoriteListOrderType.NAME_ASC.value
    ) -> list:
        favorites = []
        qs = cls.objects.filter(
            Q(space_uid=space_uid, created_by=username, visible_type=FavoriteVisibleType.PRIVATE.value)
            | Q(space_uid=space_uid, visible_type=FavoriteVisibleType.PUBLIC.value)
        )
        if order_type == FavoriteListOrderType.NAME_ASC.value:
            qs = qs.order_by("name")
        elif order_type == FavoriteListOrderType.NAME_DESC.value:
            qs = qs.order_by("-name")
        else:
            qs = qs.order_by("-updated_at")

        index_set_id_list = list(qs.all().values_list("index_set_id", flat=True).distinct())
        active_index_set_id_dict = {
            i["index_set_id"]: {"index_set_name": i["index_set_name"], "is_active": i["is_active"]}
            for i in LogIndexSet.objects.filter(index_set_id__in=index_set_id_list).values(
                "index_set_id", "index_set_name", "is_active"
            )
        }
        for fi in qs.all():
            fi_dict = model_to_dict(fi)
            if active_index_set_id_dict.get(fi.index_set_id):
                fi_dict["is_active"] = active_index_set_id_dict[fi.index_set_id]["is_active"]
                fi_dict["index_set_name"] = active_index_set_id_dict[fi.index_set_id]["index_set_name"]
            else:
                fi_dict["is_active"] = False
                fi_dict["index_set_name"] = INDEX_SET_NOT_EXISTED
            fi_dict["created_at"] = fi_dict["created_at"]
            fi_dict["updated_at"] = fi_dict["updated_at"]
            favorites.append(fi_dict)

        return favorites

    @classmethod
    def get_favorite_index_set_ids(cls, username: str, index_set_ids: list = None) -> list:
        if not index_set_ids:
            return []
        return cls.objects.filter(index_set_id__in=index_set_ids, created_by=username).values_list(
            "index_set_id", flat=True
        )


class FavoriteGroup(OperateRecordModel):
    """收藏组"""

    name = models.CharField(_("收藏组名称"), max_length=64)
    group_type = models.CharField(_("收藏组类型"), max_length=64, choices=FavoriteGroupType.get_choices())
    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256, db_index=True)

    class Meta:
        verbose_name = _("检索收藏组")
        verbose_name_plural = _("34_搜索-检索收藏组")
        ordering = ("-updated_at",)
        unique_together = [("name", "space_uid", "created_by")]

    @classmethod
    def get_or_create_private_group(cls, space_uid: str, username: str) -> "FavoriteGroup":
        obj, __ = cls.objects.get_or_create(
            group_type=FavoriteGroupType.PRIVATE.value,
            space_uid=space_uid,
            created_by=username,
            defaults={"name": FavoriteGroupType.get_choice_label(str(FavoriteGroupType.PRIVATE.value))},
        )
        return obj

    @classmethod
    def get_or_create_ungrouped_group(cls, space_uid: str) -> "FavoriteGroup":
        obj, __ = cls.objects.get_or_create(
            group_type=FavoriteGroupType.UNGROUPED.value,
            space_uid=space_uid,
            defaults={"name": FavoriteGroupType.get_choice_label(str(FavoriteGroupType.UNGROUPED.value))},
        )
        return obj

    @classmethod
    def get_user_groups(cls, space_uid: str, username: str) -> dict:
        """获取用户所有能看到的组"""
        groups = dict()
        # 个人组，使用get_or_create是为了减少同步
        private_group = cls.get_or_create_private_group(space_uid=space_uid, username=username)
        groups[private_group.id] = model_to_dict(private_group)
        # 未归类组，使用get_or_create是为了减少同步
        ungrouped_group = cls.get_or_create_ungrouped_group(space_uid=space_uid)
        groups[ungrouped_group.id] = model_to_dict(ungrouped_group)
        # 公共组
        public_groups = cls.objects.filter(
            group_type=FavoriteGroupType.PUBLIC.value,
            space_uid=space_uid,
        )
        for gi in public_groups:
            groups[gi.id] = model_to_dict(gi)
        return groups


class FavoriteGroupCustomOrder(models.Model):
    """
    space_uid: 空间唯一标识
    username: 用户名
    group_order: 用户自定义收藏组ID顺序
    """

    space_uid = models.CharField(_("空间唯一标识"), blank=True, default="", max_length=256, db_index=True)
    username = models.CharField(_("用户名"), max_length=255, db_index=True)
    group_order = models.JSONField(_("用户自定义收藏组ID顺序"), blank=True, null=True)

    class Meta:
        verbose_name = _("用户检索收藏组顺序")
        verbose_name_plural = _("34_搜索-用户检索收藏组顺序")


class IndexSetUserFavorite(models.Model):
    id = models.AutoField(_("id"), primary_key=True)
    index_set_id = models.IntegerField(_("索引集id"))
    username = models.CharField(_("用户name"), max_length=255)

    class Meta:
        verbose_name = _("检索收藏记录")
        verbose_name_plural = _("33_搜索-检索收藏记录")
        unique_together = ("index_set_id", "username")

    @classmethod
    def is_mark(cls, username: str, index_set_id: int):
        return cls.objects.filter(username, index_set_id).exists()

    @classmethod
    def mark(cls, username: str, index_set_id: int):
        if not cls.objects.filter(username=username, index_set_id=index_set_id).exists():
            cls.objects.create(username=username, index_set_id=index_set_id)

    @classmethod
    def cancel(cls, username: str, index_set_id: int):
        cls.objects.filter(username=username, index_set_id=index_set_id).delete()

    @classmethod
    def batch_get_mark_index_set(cls, index_set_ids: list, username: str):
        return cls.objects.filter(index_set_id__in=index_set_ids, username=username).values_list(
            "index_set_id", flat=True
        )


class IndexSetTag(models.Model):
    tag_id = models.AutoField(_("标签id"), primary_key=True)
    name = models.CharField(_("标签名称"), max_length=255, unique=True)
    color = models.CharField(_("配色"), max_length=255, choices=TagColor.get_choices(), default=TagColor.GREEN.value)

    class Meta:
        verbose_name = _("标签表")
        verbose_name_plural = _("标签表")

    @classmethod
    def get_tag_id(cls, name: str) -> int:
        if cls.objects.filter(name=name).exists():
            return cls.objects.get(name=name).tag_id
        return cls.objects.create(name=name).tag_id

    @classmethod
    def batch_get_tags(cls, tag_ids: list):
        tags = cls.objects.filter(tag_id__in=tag_ids).values("name", "color", "tag_id")
        return [
            {"name": InnerTag.get_choice_label(tag["name"]), "color": tag["color"], "tag_id": tag["tag_id"]}
            for tag in tags
        ]


class AsyncTask(OperateRecordModel):
    """
    导出任务状态表
    """

    request_param = models.JSONField(_("检索请求参数"))
    sorted_param = models.JSONField(_("异步导出排序字段"), null=True, blank=True)
    scenario_id = models.CharField(_("接入场景"), max_length=64)
    index_set_id = models.IntegerField(_("索引集id"))
    result = models.BooleanField(_("异步导出结果"), default=False)
    failed_reason = models.TextField(_("异步导出异常原因"), null=True, blank=True)
    file_name = models.CharField(_("文件名"), max_length=256, null=True, blank=True)
    file_size = models.FloatField(_("文件大小"), null=True, blank=True)
    download_url = models.TextField(_("下载地址"), null=True, blank=True)
    is_clean = models.BooleanField(_("是否被清理"), default=False)
    export_status = models.CharField(_("导出状态"), max_length=128, null=True, blank=True)
    start_time = models.CharField(_("导出选择请求时间"), max_length=64, null=True, blank=True)
    end_time = models.CharField(_("导出选择结束时间"), max_length=64, null=True, blank=True)
    export_type = models.CharField(_("导出类型"), max_length=64, null=True, blank=True)
    bk_biz_id = models.IntegerField(_("业务ID"), null=True, default=None)
    completed_at = models.DateTimeField(_("任务完成时间"), null=True, blank=True)

    class Meta:
        db_table = "export_task"
        verbose_name = _("导出任务")
        verbose_name_plural = _("42_导出任务")


class EmailTemplate(OperateRecordModel):
    """
    邮件模板
    """

    name = models.CharField(_("模板名"), max_length=128, db_index=True)
    path = models.TextField(_("模板路径"), max_length=256)
    language = models.CharField(_("语言级别"), max_length=128, default="")

    @classmethod
    def get_content(cls, name, language, **kwargs):
        """
        获取初始化模板
        @param name: str 模板名
        @param language: str 语言
        @param kwargs: dict 需要渲染的参数
        """
        email_template = (
            EmailTemplate.objects.filter(name=name, language__in=(language, "")).filter().order_by("-language").first()
        )
        if not email_template:
            raise CouldNotFindTemplateException(
                CouldNotFindTemplateException.MESSAGE.format(template_name=name, language=language)
            )

        path = email_template.path
        if not os.path.isabs(path):
            path = os.path.join(settings.BASE_DIR, path)

        file_path, file_name = os.path.split(path)
        file_loader = FileSystemLoader(file_path)
        env = Environment(loader=file_loader)
        template = env.get_template(file_name)
        return template.render(kwargs)

    class Meta:
        verbose_name = _("邮件模板")
        verbose_name_plural = _("43_邮件模板")


class UserMetaConf(models.Model):
    username = models.CharField(_("创建者"), max_length=32, default="")
    conf = models.JSONField(_("用户meta配置"), default=dict)
    type = models.CharField(_("数据类型"), max_length=64)

    class Meta:
        verbose_name = _("用户元配置")
        verbose_name_plural = _("44_用户元配置")
        unique_together = (("username", "type"),)


class BizProperty(models.Model):
    bk_biz_id = models.IntegerField(_("业务ID"), null=True, default=None)
    biz_property_id = models.CharField(_("业务属性ID"), max_length=64, null=True, default="")
    biz_property_name = models.CharField(_("业务属性名称"), max_length=64, null=True, default="")
    biz_property_value = models.CharField(_("业务属性值"), max_length=256, null=True, default="")

    class Meta:
        verbose_name = _("业务属性")
        verbose_name_plural = _("45_业务属性")

    @classmethod
    def list_biz_property(cls) -> list:
        biz_properties = BizProperty.objects.all()
        biz_properties_dict = defaultdict(lambda: {"biz_property_name": "", "biz_property_value": []})
        for bi in biz_properties:
            biz_properties_dict[bi.biz_property_id]["biz_property_name"] = bi.biz_property_name
            biz_properties_dict[bi.biz_property_id]["biz_property_value"].append(bi.biz_property_value)

        return [
            {
                "biz_property_id": biz_property_id,
                "biz_property_name": biz_properties_dict[biz_property_id]["biz_property_name"],
                "biz_property_value": list(set(biz_properties_dict[biz_property_id]["biz_property_value"])),
            }
            for biz_property_id in biz_properties_dict
        ]


class SpaceType(SoftDeleteModel):
    """
    空间类型
    """

    type_id = models.CharField(_("空间类型英文名称"), max_length=64, primary_key=True)
    type_name = models.CharField(_("空间类型中文名称"), max_length=64, unique=True)

    properties = models.JSONField(_("额外属性"), default=dict)

    class Meta:
        verbose_name = _("空间类型")
        verbose_name_plural = _("空间类型")

    @classmethod
    def get_name_by_id(cls, type_id: str):
        try:
            return cls.objects.get(type_id=type_id).type_name
        except cls.DoesNotExist:
            return type_id


class Space(SoftDeleteModel):
    """
    空间信息
    """

    id = models.AutoField(_("空间自增ID"), primary_key=True)

    space_uid = models.CharField(_("空间唯一标识"), max_length=256)
    bk_biz_id = models.IntegerField(_("业务ID"), unique=True)

    space_type_id = models.CharField(_("空间类型英文名称"), max_length=64)
    space_type_name = models.CharField(_("空间类型中文名称"), max_length=64)

    space_id = models.CharField(_("空间 ID"), max_length=128)
    space_name = models.CharField(_("空间中文名称"), max_length=128)
    space_code = models.CharField(_("空间英文名称"), max_length=64, blank=True, null=True)

    properties = models.JSONField(_("额外属性"), default=dict)

    class Meta:
        verbose_name = _("空间信息")
        verbose_name_plural = _("空间信息")


class SpaceApi(AbstractSpaceApi):
    """
    空间的API实现
    """

    @classmethod
    def _init_space(cls, space: Space) -> SpaceDefine:
        # 补充 space_type 描述
        return SpaceDefine(
            id=space.id,
            space_type_id=space.space_type_id,
            space_id=space.space_id,
            space_name=space.space_name,
            status=space.properties.get("status"),
            space_code=space.space_code,
            space_uid=space.space_uid,
            type_name=space.space_type_name,
            bk_biz_id=space.bk_biz_id,
            extend=space.properties,
        )

    @classmethod
    def get_space_detail(cls, space_uid: str = "", id: int = 0) -> Union[None, SpaceDefine]:
        space = None
        if space_uid:
            space = Space.objects.filter(space_uid=space_uid).first()
        if not space and id:
            space = Space.objects.filter(id=id).first()
        if space:
            return cls._init_space(space)

    @classmethod
    def list_spaces(cls) -> List[SpaceDefine]:
        return [cls._init_space(space) for space in Space.objects.all()]


class IndexSetFieldsConfig(models.Model):
    """索引集展示字段以及排序配置"""

    name = models.CharField(_("配置名称"), max_length=255)
    index_set_id = models.IntegerField(_("索引集ID"), db_index=True)
    display_fields = JsonField(_("字段配置"))
    sort_list = JsonField(_("排序规则"), null=True, default=None)

    class Meta:
        verbose_name = _("索引集自定义显示")
        verbose_name_plural = _("31_搜索-索引集自定义显示")
        unique_together = [("index_set_id", "name")]

    @classmethod
    @atomic
    def delete_config(cls, config_id: int):
        """删除配置"""
        obj = cls.objects.get(pk=config_id)
        # 默认配置不允许删除
        if obj.name == DEFAULT_INDEX_SET_FIELDS_CONFIG_NAME:
            raise DefaultConfigNotAllowedDelete()

        index_set_id = obj.index_set_id
        # 删除配置的时候
        default_config_id = cls.objects.get(index_set_id=index_set_id, name=DEFAULT_INDEX_SET_FIELDS_CONFIG_NAME).id
        UserIndexSetFieldsConfig.objects.filter(config_id=config_id).update(config_id=default_config_id)
        cls.objects.filter(id=config_id).delete()


class UserIndexSetFieldsConfig(models.Model):
    """用户索引集展示字段以及排序配置"""

    index_set_id = models.IntegerField(_("索引集ID"), db_index=True)
    config_id = models.IntegerField(_("索引集ID"), db_index=True)
    username = models.CharField(_("用户名"), max_length=32, default="", db_index=True)

    class Meta:
        verbose_name = _("用户索引集配置")
        verbose_name_plural = _("31_搜索-用户索引集配置")
        unique_together = [("index_set_id", "username")]

    @classmethod
    @atomic
    def get_config(cls, index_set_id: int, username: str):
        """
        获取用户索引集配置
        """
        try:
            obj = cls.objects.get(index_set_id=index_set_id, username=username)
            return IndexSetFieldsConfig.objects.get(pk=obj.config_id)
        except cls.DoesNotExist:
            obj = IndexSetFieldsConfig.objects.filter(
                index_set_id=index_set_id, name=DEFAULT_INDEX_SET_FIELDS_CONFIG_NAME
            ).first()
            if obj:
                return obj
        return None
