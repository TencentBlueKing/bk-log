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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from apps.exceptions import ValidationError
from apps.generic import DataModelSerializer
from apps.log_databus.constants import COLLECTOR_CONFIG_NAME_EN_REGEX
from apps.log_databus.models import CollectorConfig, CleanTemplate

from apps.log_search.constants import (
    CollectorScenarioEnum,
    EncodingsEnum,
    ConditionFilterTypeEnum,
    ConditionTypeEnum,
    EtlConfigEnum,
    FieldBuiltInEnum,
)


class PermissionGroupSerializer(serializers.Serializer):
    """
    权限组序列化
    """

    manage_group_ids = serializers.ListField(label=_("管理组id列表"), child=serializers.IntegerField())
    members = serializers.ListField(label=_("可见人员列表"), child=serializers.CharField(max_length=64))


class ChildrenCategorySerializer(serializers.Serializer):
    """
    子数据分类序列化
    """

    id = serializers.CharField(label=_("分类标识"), max_length=64)
    name = serializers.CharField(label=_("分类名称"), max_length=64)
    children = serializers.ListField()


class CategorySerializer(serializers.Serializer):
    """
    数据分类序列化
    """

    id = serializers.CharField(label=_("分类标识"), max_length=64)
    name = serializers.CharField(label=_("分类名称"), max_length=64)
    children = serializers.ListField(child=ChildrenCategorySerializer())


class TargetNodeSerializer(serializers.Serializer):
    """
    采集目标序列化
    """

    id = serializers.IntegerField(label=_("服务实例id"), required=False)
    bk_inst_id = serializers.IntegerField(label=_("节点实例id"), required=False)
    bk_obj_id = serializers.CharField(label=_("节点对象"), max_length=64, required=False)
    ip = serializers.CharField(label=_("主机实例ip"), max_length=15, required=False)
    bk_cloud_id = serializers.IntegerField(label=_("蓝鲸云区域id"), required=False)
    bk_supplier_id = serializers.CharField(label=_("供应商id"), required=False)


class PluginConditionSeparatorFiltersSerializer(serializers.Serializer):
    fieldindex = serializers.CharField(label=_("匹配项所在位置"))
    word = serializers.CharField(label=_("匹配值"))
    op = serializers.CharField(label=_("匹配方式"))
    logic_op = serializers.CharField(label=_("逻辑操作符"))


class PluginConditionSerializer(serializers.Serializer):
    """
    插件过滤方式序列化
    """

    type = serializers.ChoiceField(label=_("过滤方式类型"), choices=ConditionTypeEnum.get_choices())
    match_type = serializers.ChoiceField(
        label=_("过滤方式"),
        choices=ConditionFilterTypeEnum.get_choices(),
        required=False,
        allow_blank=False,
        allow_null=False,
    )
    match_content = serializers.CharField(
        label=_("过滤内容"), max_length=255, required=False, allow_null=True, allow_blank=True
    )
    separator = serializers.CharField(
        label=_("分隔符"), trim_whitespace=False, required=False, allow_null=True, allow_blank=True
    )
    separator_filters = PluginConditionSeparatorFiltersSerializer(label=_("过滤规则"), required=False, many=True)

    def validate(self, attrs):
        super().validate(attrs)

        condition_type = attrs["type"]
        separator_filters = attrs["separator_filters"] if "separator_filters" in attrs else []
        separator_str = attrs["separator"] if "separator" in attrs else ""
        if condition_type == "separator" and separator_filters and len(separator_str) == 0:
            raise ValidationError(_("过滤分隔符不能为空"))

        return attrs


class PluginParamSerializer(serializers.Serializer):
    """
    插件参数序列化
    """

    paths = serializers.ListField(label=_("日志路径"), child=serializers.CharField(max_length=255))
    conditions = PluginConditionSerializer(required=False)
    multiline_pattern = serializers.CharField(label=_("行首正则"), required=False)
    multiline_max_lines = serializers.IntegerField(label=_("最多匹配行数"), required=False, max_value=1000)
    multiline_timeout = serializers.IntegerField(label=_("最大耗时"), required=False, max_value=10)
    tail_files = serializers.BooleanField(label=_("是否增量采集"), required=False, default=True)
    ignore_older = serializers.IntegerField(label=_("文件扫描忽略时间"), required=False, default=2678400)
    max_bytes = serializers.IntegerField(label=_("单行日志最大长度"), required=False, default=204800)

    scan_frequency = serializers.IntegerField(label=_("文件扫描间隔"), required=False, min_value=1)
    close_inactive = serializers.IntegerField(label=_("FD关联间隔"), required=False, min_value=1)
    harvester_limit = serializers.IntegerField(label=_("同时采集数"), required=False, min_value=1)
    clean_inactive = serializers.IntegerField(label=_("采集进度清理时间"), required=False, min_value=1)


class DataLinkListSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)


class CollectorDataLinkListSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class DataLinkCreateUpdateSerializer(serializers.Serializer):
    """
    创建数据链路序列化
    """

    link_group_name = serializers.CharField(label=_("链路集群名称"), required=True)
    bk_biz_id = serializers.CharField(label=_("链路允许的业务id"), required=True, allow_blank=True)
    kafka_cluster_id = serializers.IntegerField(label=_("kafka集群id"), required=True)
    transfer_cluster_id = serializers.CharField(label=_("transfer集群id"), required=True)
    es_cluster_ids = serializers.JSONField(label=_("es集群id"), required=True)
    is_active = serializers.BooleanField(label=_("是否启用"), required=True)
    description = serializers.CharField(label=_("备注"), max_length=64, required=True, allow_null=True, allow_blank=True)


class ClusterListSerializer(serializers.Serializer):
    cluster_type = serializers.CharField(label=_("集群种类"), required=True)


class CollectorCreateSerializer(serializers.Serializer):
    """
    创建采集项序列化
    """

    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    data_link_id = serializers.CharField(label=_("数据链路id"), required=False, allow_blank=True, allow_null=True)
    collector_scenario_id = serializers.ChoiceField(label=_("日志类型"), choices=CollectorScenarioEnum.get_choices())
    category_id = serializers.CharField(label=_("分类ID"))
    target_object_type = serializers.CharField(label=_("目标类型"))
    target_node_type = serializers.CharField(label=_("节点类型"))
    target_nodes = TargetNodeSerializer(label=_("目标节点"), many=True)
    data_encoding = serializers.ChoiceField(label=_("日志字符集"), choices=EncodingsEnum.get_choices())
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    params = PluginParamSerializer()

    def validate(self, attrs):
        if attrs["collector_scenario_id"] == "section":
            for field in ["multiline_pattern", "multiline_max_lines", "multiline_timeout"]:
                if field not in attrs["params"]:
                    raise ValidationError(_("{} 该字段为必填项").format(field))
        return attrs


class CollectorUpdateSerializer(serializers.Serializer):
    """
    更新采集项序列化
    """

    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    target_object_type = serializers.CharField(label=_("目标类型"))
    target_node_type = serializers.CharField(label=_("节点类型"))
    target_nodes = TargetNodeSerializer(label=_("目标节点"), many=True)
    data_encoding = serializers.ChoiceField(label=_("日志字符集"), choices=EncodingsEnum.get_choices())
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    params = PluginParamSerializer()


class HostInstanceByIpSerializer(serializers.Serializer):
    """
    根据ip获取主机实例序列化
    """

    ip_list = serializers.ListField(child=serializers.CharField())
    bk_biz_ids = serializers.ListField(child=serializers.IntegerField())


def validate_param_value(value):
    value_list = value.split(",")
    for value_obj in value_list:
        if not value_obj.isdigit():
            return False
    return True


class RunSubscriptionSerializer(serializers.Serializer):
    """
    任务重试序列化
    """

    class InstanceObjectSerializer(serializers.Serializer):
        ip = serializers.CharField(label=_("主机实例ip"), required=True)
        bk_cloud_id = serializers.IntegerField(label=_("蓝鲸云区域id"), required=True)
        bk_supplier_id = serializers.CharField(label=_("供应商id"), required=False)

    target_nodes = InstanceObjectSerializer(label=_("采集目标"), required=True, many=True, allow_empty=False)


class BatchSubscriptionStatusSerializer(serializers.Serializer):
    collector_id_list = serializers.CharField(label=_("采集项ID"))

    def validate(self, attrs):
        if not validate_param_value(attrs["collector_id_list"]):
            raise ValidationError(_("collector_id_list不符合格式，采集项ID（多个ID用半角,分隔）"))
        return attrs


class TaskStatusSerializer(serializers.Serializer):
    task_id_list = serializers.CharField(label=_("部署任务ID"), allow_blank=True)

    def validate(self, attrs):
        # 当task_is_list为空的情况不需要做相关验证
        if not attrs["task_id_list"]:
            return attrs
        if not validate_param_value(attrs["task_id_list"]):
            raise ValidationError(_("task_id_list不符合格式，部署任务ID（多个ID用半角,分隔）"))
        return attrs


class TaskDetailSerializer(serializers.Serializer):
    instance_id = serializers.CharField(label=_("实例ID"))
    task_id = serializers.CharField(label=_("任务ID"), required=False)

    def validate_task_id(self, value):
        if not value.isdigit():
            raise ValidationError("task_id请填写合法的整数值")
        return int(value)


class CollectorListSerializer(DataModelSerializer):
    collector_scenario_name = serializers.ReadOnlyField(source="get_collector_scenario_id_display")
    category_name = serializers.ReadOnlyField(label=_("数据分类名称"))
    target_nodes = serializers.JSONField(label=_("采集目标"))
    task_id_list = serializers.JSONField(label=_("任务ID列表"))
    target_subscription_diff = serializers.JSONField(label=_("订阅目标变更情况"))
    create_clean_able = serializers.BooleanField(label=_("是否可以创建基础清洗"))
    bkdata_index_set_ids = serializers.ListField(child=serializers.IntegerField(), label=_("数据平台索引集id列表"))

    class Meta:
        model = CollectorConfig
        fields = "__all__"


class RetrySerializer(serializers.Serializer):
    target_nodes = serializers.ListField(label=_("采集目标"), required=False, default=[])


class StorageListSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)
    data_link_id = serializers.IntegerField(label=_("链路ID"), default=0, allow_null=True)


class StorageIndicesInfoSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class AuthInfoSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("用户名"), allow_blank=True)
    password = serializers.CharField(label=_("密码"), allow_blank=True)


class StorageCreateSerializer(serializers.Serializer):
    """
    创建集群序列化
    """

    cluster_name = serializers.CharField(label=_("集群名称"), required=True)
    domain_name = serializers.CharField(label=_("集群域名"), required=True)
    port = serializers.IntegerField(label=_("集群端口"), required=True)
    schema = serializers.CharField(label=_("集群协议"), required=True)
    auth_info = AuthInfoSerializer(label=_("凭据信息"), required=True)
    enable_hot_warm = serializers.BooleanField(label=_("是否开启冷热数据"), default=False)
    hot_attr_name = serializers.CharField(label=_("热节点属性名称"), default="", allow_blank=True)
    hot_attr_value = serializers.CharField(label=_("热节点属性值"), default="", allow_blank=True)
    warm_attr_name = serializers.CharField(label=_("冷节点属性名称"), default="", allow_blank=True)
    warm_attr_value = serializers.CharField(label=_("冷节点属性值"), default="", allow_blank=True)

    def validate(self, attrs):
        if not attrs["enable_hot_warm"]:
            return attrs
        if not all(
            [attrs["hot_attr_name"], attrs["hot_attr_value"], attrs["warm_attr_name"], attrs["warm_attr_value"]]
        ):
            raise ValidationError(_("当冷热数据处于开启状态时，冷热节点属性配置不能为空"))
        return attrs


class StorageDetectSerializer(serializers.Serializer):
    cluster_id = serializers.IntegerField(label=_("集群ID"), required=False)
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)
    domain_name = serializers.CharField(label=_("集群域名"), required=False, allow_blank=True, default="")
    port = serializers.IntegerField(label=_("端口"), allow_null=True, required=False, default=0)
    schema = serializers.CharField(label=_("集群协议"), allow_null=True, required=False, default="")
    username = serializers.CharField(label=_("用户"), allow_blank=True, required=False, default="")
    password = serializers.CharField(label=_("密码"), allow_blank=True, required=False, default="")
    version_info = serializers.BooleanField(label=_("是否包含集群信息"), allow_null=True, required=False, default=False)
    default_auth = serializers.BooleanField(label=_("是否使用默认用户信息"), allow_null=True, required=False, default=False)
    es_auth_info = AuthInfoSerializer(label=_("凭据信息"), required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get("es_auth_info"):
            return attrs
        attrs["username"] = attrs["es_auth_info"].get("username", "")
        attrs["password"] = attrs["es_auth_info"].get("password", "")
        return attrs


class StorageBathcDetectSerializer(serializers.Serializer):
    cluster_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class StorageUpdateSerializer(serializers.Serializer):
    cluster_name = serializers.CharField(label=_("集群名称"), required=False)
    domain_name = serializers.CharField(label=_("集群域名"), required=True)
    port = serializers.IntegerField(label=_("端口"), required=True)
    schema = serializers.CharField(label=_("集群协议"), required=True)
    auth_info = AuthInfoSerializer(label=_("凭据信息"), required=True)
    enable_hot_warm = serializers.BooleanField(label=_("是否开启冷热数据"), default=False)
    hot_attr_name = serializers.CharField(label=_("热节点属性名称"), default="", allow_blank=True)
    hot_attr_value = serializers.CharField(label=_("热节点属性值"), default="", allow_blank=True)
    warm_attr_name = serializers.CharField(label=_("冷节点属性名称"), default="", allow_blank=True)
    warm_attr_value = serializers.CharField(label=_("冷节点属性值"), default="", allow_blank=True)

    def validate(self, attrs):
        if not attrs["enable_hot_warm"]:
            return attrs
        if not all(
            [attrs["hot_attr_name"], attrs["hot_attr_value"], attrs["warm_attr_name"], attrs["warm_attr_value"]]
        ):
            raise ValidationError(_("当冷热数据处于开启状态时，冷热节点属性配置不能为空"))
        return attrs


class CollectorEtlParamsSerializer(serializers.Serializer):
    separator_regexp = serializers.CharField(label=_("正则表达式"), required=False, allow_null=True, allow_blank=True)
    separator = serializers.CharField(
        label=_("分隔符"), trim_whitespace=False, required=False, allow_null=True, allow_blank=True
    )
    retain_original_text = serializers.BooleanField(label=_("是否保留原文"), required=False, default=True)


class CollectorEtlSerializer(serializers.Serializer):
    etl_config = serializers.CharField(label=_("清洗类型"), required=True)
    etl_params = CollectorEtlParamsSerializer(required=False)
    data = serializers.CharField(label=_("日志内容"), required=True)


class CollectorRegexDebugSerializer(serializers.Serializer):
    log_sample = serializers.CharField(label=_("日志样例"), required=True)
    multiline_pattern = serializers.CharField(label=_("行首正则表达式"), required=True)


class CollectorEtlTimeSerializer(serializers.Serializer):
    time_format = serializers.CharField(label=_("时间格式"), required=True)
    time_zone = serializers.IntegerField(label=_("时区"), required=True)
    data = serializers.CharField(label=_("时间内容"), required=True)


class CollectorEtlFieldsSerializer(serializers.Serializer):
    field_index = serializers.IntegerField(label=_("字段顺序"), required=False, allow_null=True)
    field_name = serializers.CharField(label=_("字段名称"), required=False, allow_null=True, allow_blank=True)
    alias_name = serializers.CharField(label=_("别名"), required=False, allow_blank=True, allow_null=True)
    field_type = serializers.CharField(label=_("类型"), required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(label=_("描述"), required=False, allow_blank=True, allow_null=True, default="")
    is_analyzed = serializers.BooleanField(label=_("是否分词"), required=False, default=False)
    is_dimension = serializers.BooleanField(label=_("是否维度"), required=False, default=True)
    is_time = serializers.BooleanField(label=_("是否时间字段"), required=False, default=False)
    is_delete = serializers.BooleanField(label=_("是否删除"), required=True)
    is_built_in = serializers.BooleanField(label=_("是否内置字段"), required=False, default=False)
    option = serializers.DictField(label=_("字段配置"), required=False)

    def validate(self, field):
        built_in_keys = FieldBuiltInEnum.get_choices()
        if not field.get("is_delete"):
            if not field.get("field_name") or not field.get("field_type"):
                raise ValidationError(_("参数不能为空：field_name/field_type"))

            if not field.get("is_built_in", False):
                if field.get("alias_name"):
                    if field["alias_name"].lower() in built_in_keys:
                        raise ValidationError(_("字段别名不能与标准字段重复") + f":{field['alias_name']}")
                elif field["field_name"].lower() in built_in_keys:
                    raise ValidationError(_("字段名称不能与标准字段重复") + f":{field['field_name']}")

                # 时间字段
                if field["is_time"]:
                    self.validate_time_field(field)

                # 分词
                field["is_dimension"] = True
                if field["is_analyzed"]:
                    field["is_dimension"] = False
                    if field["field_type"] != "string":
                        raise ValidationError(_("只有字符串类型的字段才可以设置为分词"))
        return field

    def validate_time_field(self, field):
        if not field.get("option") or "time_zone" not in field["option"] or "time_format" not in field["option"]:
            raise ValidationError(_("时间字段需配置时区、格式"))

        if field["field_type"] in ["int", "long"]:
            if field["option"]["time_format"] not in ["epoch_millis", "epoch_second", "epoch_minute", "epoch_micros"]:
                raise ValidationError(_("时间字段类型与格式不匹配"))
        else:
            if field["option"]["time_format"] in ["epoch_millis", "epoch_second", "epoch_minute", "epoch_micros"]:
                raise ValidationError(_("时间字段类型与格式不匹配"))
        return True


class CollectorEtlStorageSerializer(serializers.Serializer):
    table_id = serializers.CharField(label=_("结果表ID"), required=True)
    etl_config = serializers.CharField(label=_("清洗类型"), required=True)
    etl_params = CollectorEtlParamsSerializer(required=False)
    fields = serializers.ListField(child=CollectorEtlFieldsSerializer(), label=_("字段配置"), required=False)
    storage_cluster_id = serializers.IntegerField(label=_("集群ID"), required=True)
    retention = serializers.IntegerField(label=_("有效时间"), required=True)
    allocation_min_days = serializers.IntegerField(label=_("冷热数据生效时间"), required=True)
    storage_replies = serializers.IntegerField(
        label=_("ES副本数量"), required=False, default=settings.ES_REPLICAS, min_value=0, max_value=3
    )
    view_roles = serializers.ListField(label=_("查看权限"), required=False, default=[])

    def validate(self, attrs):
        super().validate(attrs)

        if attrs["etl_config"] in EtlConfigEnum.get_dict_choices():
            if not attrs.get("fields"):
                raise ValidationError(_("[字段提取]请输入需要提取的字段信息"))

            # table_id 不能包含 bklog
            if "bklog" in attrs["table_id"]:
                raise ValidationError(_("存储索引名不能包含bklog关键字"))

            # 过滤掉标准字段，并检查time_field数量
            fields = []
            valid_fields = []
            time_fields = []
            for item in attrs["fields"]:
                if item.get("is_built_in"):
                    continue
                if item.get("is_time"):
                    time_fields.append(item)

                # 分隔符必须必指field_index
                if attrs["etl_config"] == EtlConfigEnum.BK_LOG_DELIMITER.value:
                    if "field_index" not in item:
                        raise ValidationError(_("分隔符必须指定field_index"))

                # 字段检查
                CollectorEtlFieldsSerializer().validate(item)
                fields.append(item)

                if not item.get("is_delete", False):
                    valid_fields.append(item)
            if len(time_fields) > 1:
                raise ValidationError(_("仅可以设置一个时间字段"))

            if len(valid_fields) == 0:
                raise ValidationError(_("清洗需要配置有效字段"))
            attrs["fields"] = fields
        else:
            attrs["fields"] = []
        return attrs


class CollectItsmCallbackSerializer(serializers.Serializer):
    sn = serializers.CharField(label=_("itsm单号"), required=True)
    title = serializers.CharField(label=_("itsm单据标题"), required=True)
    ticket_url = serializers.CharField(label=_("itsm单据地址"), required=True)
    current_status = serializers.CharField(label=_("itsm单据状态"), required=True)
    updated_by = serializers.CharField(label=_("itsm最近更新者"), required=True)
    update_at = serializers.CharField(label=_("itsm最近更新时间"), required=True)
    approve_result = serializers.BooleanField(label=_("itsm审批结果"), required=True)
    token = serializers.CharField(label=_("itsmtoken"), required=True)


class CollectItsmApplySerializer(serializers.Serializer):
    expect_access_data = serializers.CharField(label=_("期待接入日期"), required=True)
    single_log_size = serializers.IntegerField(label=_("单条日志大小(bytes)"), required=True)
    single_host_peak = serializers.IntegerField(label=_("单机流量峰值（kB/S）"), required=True)
    single_host_log_volume = serializers.FloatField(label=_("单机增长日志量"), required=True)
    expect_host_size = serializers.IntegerField(label=_("预计接入主机数"), required=True)
    log_keep_days = serializers.IntegerField(label=_("日志保留天数"), required=True)
    hot_data_days = serializers.IntegerField(label=_("热数据天数"), required=True)
    apply_reason = serializers.CharField(label=_("申请原因"), required=False, default="")


class ListCollectorsByHostSerializer(serializers.Serializer):
    bk_host_innerip = serializers.IPAddressField(label=_("内网ip"), required=False)
    bk_cloud_id = serializers.IntegerField(label=_("云区域Id"), required=False, default=0)
    bk_host_id = serializers.IntegerField(label=_("主机id"), required=False)
    bk_biz_id = serializers.IntegerField(label=_("业务id"), required=True)


class CleanSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"))
    keyword = serializers.CharField(label=_("检索关键词"), required=False)
    etl_config = serializers.CharField(label=_("清洗配置类型"), required=False)
    page = serializers.IntegerField(label=_("页码"))
    pagesize = serializers.IntegerField(label=_("页面大小"))

    def validate(self, attrs):
        super().validate(attrs)
        if attrs["page"] < 0 or attrs["pagesize"] < 0:
            raise ValidationError(_("分页参数不能为负数"))
        return attrs


class CleanRefreshSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"))
    bk_data_id = serializers.IntegerField(label=_("数据源id"))


class CleanSyncSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"))
    polling = serializers.BooleanField(label=_("是否是轮询请求"), required=False, default=False)


class CleanTemplateSerializer(serializers.Serializer):
    name = serializers.CharField(label=_("清洗模板名"), required=True)
    clean_type = serializers.CharField(label=_("清洗类型"), required=True)
    etl_params = serializers.DictField(label=_("清洗配置"), required=True)
    etl_fields = serializers.ListField(child=serializers.DictField(), label=_("字段配置"), required=True)
    bk_biz_id = serializers.IntegerField(label=_("业务id"), required=True)


class CleanStashSerializer(serializers.Serializer):
    clean_type = serializers.CharField(label=_("清洗类型"), required=True)
    etl_params = serializers.DictField(label=_("清洗配置"), required=True)
    etl_fields = serializers.ListField(child=serializers.DictField(), label=_("字段配置"), required=True)
    bk_biz_id = serializers.IntegerField(label=_("业务id"), required=True)


class CleanTemplateListSerializer(DataModelSerializer):
    class Meta:
        model = CleanTemplate
        fields = "__all__"
