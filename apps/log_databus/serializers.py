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
import base64

from django.conf import settings
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as SlzValidationError

from apps.exceptions import ValidationError
from apps.generic import DataModelSerializer
from apps.log_databus.constants import (
    ArchiveInstanceType,
    CLUSTER_NAME_EN_REGEX,
    COLLECTOR_CONFIG_NAME_EN_REGEX,
    ContainerCollectorType,
    Environment,
    EsSourceType,
    LabelSelectorOperator,
    TopoType,
    VisibleEnum,
    EtlConfig,
)
from apps.log_databus.models import CleanTemplate, CollectorConfig, CollectorPlugin
from apps.log_search.constants import (
    CollectorScenarioEnum,
    ConditionFilterTypeEnum,
    ConditionTypeEnum,
    CustomTypeEnum,
    EncodingsEnum,
    EtlConfigEnum,
    FieldBuiltInEnum,
)
from bkm_space.serializers import SpaceUIDField
from bkm_space.utils import space_uid_to_bk_biz_id


class LabelsSerializer(serializers.Serializer):
    key = serializers.CharField(label=_("标签key"))
    operator = serializers.CharField(label=_("标签连接符"), required=False, default="=")
    value = serializers.CharField(label=_("标签value"), allow_blank=True)


class ExtraLabelsSerializer(serializers.Serializer):
    key = serializers.CharField(label=_("标签key"))
    value = serializers.JSONField(label=_("标签value"))


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
    bk_host_id = serializers.IntegerField(label=_("主机ID"), required=False)
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
        attrs = super().validate(attrs)

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

    paths = serializers.ListField(
        label=_("日志路径"), child=serializers.CharField(max_length=255, allow_blank=True), required=False
    )
    conditions = PluginConditionSerializer(required=False)
    multiline_pattern = serializers.CharField(label=_("行首正则"), required=False, allow_blank=True)
    multiline_max_lines = serializers.IntegerField(label=_("最多匹配行数"), required=False, max_value=1000)
    multiline_timeout = serializers.IntegerField(label=_("最大耗时"), required=False, max_value=10)
    tail_files = serializers.BooleanField(label=_("是否增量采集"), required=False, default=True)
    ignore_older = serializers.IntegerField(label=_("文件扫描忽略时间"), required=False, default=2678400)
    max_bytes = serializers.IntegerField(label=_("单行日志最大长度"), required=False, default=204800)

    scan_frequency = serializers.IntegerField(label=_("文件扫描间隔"), required=False, min_value=1)
    close_inactive = serializers.IntegerField(label=_("FD关联间隔"), required=False, min_value=1)
    harvester_limit = serializers.IntegerField(label=_("同时采集数"), required=False, min_value=1)
    clean_inactive = serializers.IntegerField(label=_("采集进度清理时间"), required=False, min_value=1)
    # winlog相关参数
    winlog_name = serializers.ListField(
        label=_("windows事件名称"), child=serializers.CharField(max_length=255), required=False
    )
    winlog_level = serializers.ListField(
        label=_("windows事件等级"), child=serializers.CharField(max_length=255), required=False
    )
    winlog_event_id = serializers.ListField(
        label=_("windows事件ID"), child=serializers.CharField(max_length=255), required=False
    )
    # Redis慢日志相关参数
    redis_hosts = serializers.ListField(
        label=_("redis目标"), child=serializers.CharField(max_length=255), required=False, default=[]
    )
    redis_password = serializers.CharField(label=_("redis密码"), required=False, allow_blank=True)
    redis_password_file = serializers.CharField(label=_("redis密码文件"), required=False, allow_blank=True)
    # 标签, List[str], 会以kv的形式传递给采集器
    extra_labels = serializers.ListSerializer(label=_("额外标签"), required=False, child=LabelsSerializer())
    # 额外模板标签, List[Dict], 会以列表的形式传递给采集器
    extra_template_labels = serializers.ListSerializer(label=_("额外模板标签"), required=False, child=ExtraLabelsSerializer())


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


class ContainerSerializer(serializers.Serializer):
    workload_type = serializers.CharField(label=_("workload类型"), default="", allow_blank=True)
    workload_name = serializers.CharField(label=_("workload名称"), allow_blank=True, default="")
    container_name = serializers.CharField(label=_("容器名称"), required=False, allow_blank=True, default="")


class LabelSelectorSerializer(serializers.Serializer):
    match_labels = serializers.ListSerializer(
        child=LabelsSerializer(), label=_("指定标签"), required=False, allow_empty=True
    )
    match_expressions = serializers.ListSerializer(
        child=LabelsSerializer(), label=_("指定表达式"), required=False, allow_empty=True
    )


class ContainerConfigSerializer(serializers.Serializer):
    namespaces = serializers.ListSerializer(child=serializers.CharField(), required=False, label=_("命名空间"), default=[])
    container = ContainerSerializer(required=False, label=_("指定容器"))
    label_selector = LabelSelectorSerializer(required=False, label=_("标签"))
    paths = serializers.ListSerializer(child=serializers.CharField(), required=False, label=_("日志路径"))
    data_encoding = serializers.CharField(required=False, label=_("日志字符集"))
    params = PluginParamSerializer(required=True, label=_("插件参数"))
    collector_type = serializers.CharField(label=_("容器采集类型"))


class BcsContainerConfigSerializer(serializers.Serializer):
    namespaces = serializers.ListSerializer(child=serializers.CharField(), required=False, label=_("命名空间"), default=[])
    container = ContainerSerializer(required=False, label=_("指定容器"), default={})
    label_selector = LabelSelectorSerializer(required=False, label=_("标签"), default={})
    paths = serializers.ListSerializer(child=serializers.CharField(), required=False, label=_("日志路径"), default=[])
    data_encoding = serializers.CharField(required=False, label=_("日志字符集"))
    enable_stdout = serializers.BooleanField(required=False, label=_("是否采集标准输出"), default=False)


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
    environment = serializers.ChoiceField(
        label=_("环境"), default=Environment.LINUX, choices=[Environment.LINUX, Environment.WINDOWS]
    )
    params = PluginParamSerializer()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs["collector_scenario_id"] == "section":
            for field in ["multiline_pattern", "multiline_max_lines", "multiline_timeout"]:
                if field not in attrs["params"]:
                    raise ValidationError(_("{} 该字段为必填项").format(field))

        if attrs["collector_scenario_id"] == "wineventlog":
            for field in ["winlog_name"]:
                if field not in attrs["params"]:
                    raise ValidationError(_("{} 该字段为必填项").format(field))
        return attrs


class CreateContainerCollectorSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    collector_plugin_id = serializers.IntegerField(label=_("采集插件ID"), required=False)
    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    data_link_id = serializers.CharField(label=_("数据链路id"), required=False, allow_blank=True, allow_null=True)
    collector_scenario_id = serializers.ChoiceField(label=_("日志类型"), choices=CollectorScenarioEnum.get_choices())
    category_id = serializers.CharField(label=_("分类ID"))
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    configs = serializers.ListSerializer(label=_("容器日志配置"), child=ContainerConfigSerializer())
    bcs_cluster_id = serializers.CharField(label=_("bcs集群id"))
    add_pod_label = serializers.BooleanField(label=_("是否自动添加pod中的labels"), default=False)
    extra_labels = serializers.ListSerializer(label=_("额外标签"), required=False, child=LabelsSerializer())
    yaml_config_enabled = serializers.BooleanField(label=_("是否使用yaml配置模式"), default=False)
    yaml_config = serializers.CharField(label=_("yaml配置内容"), default="", allow_blank=True)
    platform_username = serializers.CharField(label=_("平台用户"), required=False)

    def validate_yaml_config(self, value):
        try:
            yaml_text = base64.b64decode(value).decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            raise ValidationError(_("base64编码解析失败"))
        return yaml_text


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
    environment = serializers.ChoiceField(
        label=_("环境"), required=False, choices=[Environment.LINUX, Environment.WINDOWS]
    )
    params = PluginParamSerializer()


class UpdateContainerCollectorSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    collector_scenario_id = serializers.ChoiceField(label=_("日志类型"), choices=CollectorScenarioEnum.get_choices())
    configs = serializers.ListSerializer(label=_("容器日志配置"), child=ContainerConfigSerializer())
    bcs_cluster_id = serializers.CharField(label=_("bcs集群id"))
    add_pod_label = serializers.BooleanField(label=_("是否自动添加pod中的labels"))
    extra_labels = serializers.ListSerializer(label=_("额外标签"), required=False, child=LabelsSerializer())
    yaml_config_enabled = serializers.BooleanField(label=_("是否使用yaml配置模式"), default=False)
    yaml_config = serializers.CharField(label=_("yaml配置内容"), default="", allow_blank=True)

    def validate_yaml_config(self, value):
        try:
            yaml_text = base64.b64decode(value).decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            raise ValidationError(_("base64编码解析失败"))
        return yaml_text


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
        bk_host_id = serializers.IntegerField(label=_("主机ID"), required=False)
        ip = serializers.CharField(label=_("主机实例ip"), required=True)
        bk_cloud_id = serializers.IntegerField(label=_("蓝鲸云区域id"), required=True)
        bk_supplier_id = serializers.CharField(label=_("供应商id"), required=False)

    target_nodes = InstanceObjectSerializer(label=_("采集目标"), required=True, many=True, allow_empty=False)


class BatchSubscriptionStatusSerializer(serializers.Serializer):
    collector_id_list = serializers.CharField(label=_("采集项ID"))

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if not validate_param_value(attrs["collector_id_list"]):
            raise ValidationError(_("collector_id_list不符合格式，采集项ID（多个ID用半角,分隔）"))
        return attrs


class TaskStatusSerializer(serializers.Serializer):
    task_id_list = serializers.CharField(label=_("部署任务ID"), allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

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
            raise ValidationError(_("task_id请填写合法的整数值"))
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
    instance_id_list = serializers.ListField(label=_("实例ID列表"), required=False, default=[])


class StorageListSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)
    enable_archive = serializers.BooleanField(label=_("是否启用归档"), required=False)


class StorageIndicesInfoSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class AuthInfoSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("用户名"), allow_blank=True)
    password = serializers.CharField(label=_("密码"), allow_blank=True)


class VisibleSerializer(serializers.Serializer):
    visible_type = serializers.ChoiceField(label=_("可见类型"), choices=VisibleEnum.get_choices())
    visible_bk_biz = serializers.ListField(
        label=_("可见业务范围"), child=serializers.IntegerField(), required=False, default=[]
    )
    bk_biz_labels = serializers.DictField(label=_("业务标签"), required=False, default={})

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs["visible_type"] == VisibleEnum.MULTI_BIZ.value and not attrs.get("visible_bk_biz"):
            raise ValidationError(_("可见类型为多业务时，可见业务范围不能为空"))

        if attrs["visible_type"] == VisibleEnum.BIZ_ATTR.value and not attrs.get("bk_biz_labels"):
            raise ValidationError(_("可见类型为业务属性时，业务标签不能为空"))
        return attrs


class SetupSerializer(serializers.Serializer):
    retention_days_max = serializers.IntegerField(label=_("最大保留天数"), default=7)
    retention_days_default = serializers.IntegerField(label=_("默认保留天数"), default=7)
    number_of_replicas_max = serializers.IntegerField(label=_("最大副本数"), default=0)
    number_of_replicas_default = serializers.IntegerField(label=_("默认副本数"), default=0)
    es_shards_default = serializers.IntegerField(label=_("ES默认分片数"), default=3)
    es_shards_max = serializers.IntegerField(label=_("ES最大分片数"), default=64)


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

    bk_biz_id = serializers.IntegerField(label=_("集群创建业务id"))
    source_type = serializers.ChoiceField(label=_("ES来源类型"), choices=EsSourceType.get_choices())
    visible_config = VisibleSerializer(label=_("可见范围配置"))
    setup_config = SetupSerializer(label=_("es设置"))
    admin = serializers.ListField(label=_("负责人"))
    description = serializers.CharField(label=_("集群描述"), required=False, default="", allow_blank=True)
    enable_archive = serializers.BooleanField(label=_("是否开启日志归档"))
    enable_assessment = serializers.BooleanField(label=_("是否开启容量评估"))
    create_bkbase_cluster = serializers.BooleanField(label=_("是否同步到数据平台"), required=False)
    cluster_namespace = serializers.CharField(label=_("命名空间"), required=False)
    bkbase_tags = serializers.ListField(label=_("标签"), required=False, child=serializers.CharField())
    bkbase_cluster_en_name = serializers.RegexField(label=_("集群英文名称"), regex=CLUSTER_NAME_EN_REGEX, required=False)
    option = serializers.JSONField(label=_("第三方平台配置"), required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if not attrs["enable_hot_warm"]:
            return attrs
        if not all(
            [attrs["hot_attr_name"], attrs["hot_attr_value"], attrs["warm_attr_name"], attrs["warm_attr_value"]]
        ):
            raise ValidationError(_("当冷热数据处于开启状态时，冷热节点属性配置不能为空"))
        if attrs.get("create_bkbase_cluster") and not attrs.get("bkbase_cluster_en_name"):
            raise ValidationError(_("同步到数据平台需要提供集群英文名"))
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
        attrs = super().validate(attrs)

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

    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)
    source_type = serializers.ChoiceField(label=_("ES来源类型"), choices=EsSourceType.get_choices())
    visible_config = VisibleSerializer(label=_("可见范围配置"))
    setup_config = SetupSerializer(label=_("es设置"))
    admin = serializers.ListField(label=_("负责人"))
    description = serializers.CharField(label=_("集群描述"), required=False, default="", allow_blank=True)
    enable_archive = serializers.BooleanField(label=_("是否开启日志归档"))
    enable_assessment = serializers.BooleanField(label=_("是否开启容量评估"))
    cluster_namespace = serializers.CharField(label=_("命名空间"), required=False)
    bkbase_tags = serializers.ListField(label=_("标签"), required=False, child=serializers.CharField())
    option = serializers.JSONField(label=_("第三方平台配置"), required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)

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


class AssessmentConfig(serializers.Serializer):
    log_assessment = serializers.CharField(label=_("日志评估 （单机日志量）"))
    need_approval = serializers.BooleanField(label=_("是否需要审批"), default=False)
    approvals = serializers.ListField(label=_("审批人"), child=serializers.CharField(), required=True)


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
    es_shards = serializers.IntegerField(
        label=_("ES分片数量"), required=False, default=settings.ES_SHARDS, min_value=1, max_value=64
    )
    view_roles = serializers.ListField(label=_("查看权限"), required=False, default=[])
    need_assessment = serializers.BooleanField(label=_("是否需要评估配置"), required=False, default=False)
    assessment_config = AssessmentConfig(label=_("评估配置"), required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs.get("need_assessment", False) and not attrs.get("assessment_config"):
            raise ValidationError(_("评估配置不能为空"))

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
        attrs = super().validate(attrs)
        if attrs["page"] < 0 or attrs["pagesize"] < 0:
            raise ValidationError(_("分页参数不能为负数"))
        return attrs


class PageSerializer(serializers.Serializer):
    page = serializers.IntegerField(label=_("页码"))
    pagesize = serializers.IntegerField(label=_("页面大小"))

    def validate(self, attrs):
        attrs = super().validate(attrs)
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
    visible_type = serializers.CharField(label=_("可见类型"), required=False)
    visible_bk_biz_id = serializers.ListField(label=_("可见业务ID"), required=False)


class CleanTemplateDestroySerializer(serializers.Serializer):
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


class CleanTemplateListFilterSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"), required=True)
    keyword = serializers.CharField(label=_("检索关键词"), required=False)
    clean_type = serializers.CharField(label=_("模板类型"), required=False)
    page = serializers.IntegerField(label=_("页码"), default=1)
    pagesize = serializers.IntegerField(label=_("页面大小"), default=10)

    def validate(self, attrs):
        super().validate(attrs)
        if attrs["page"] < 0 or attrs["pagesize"] < 0:
            raise ValidationError(_("分页参数不能为负数"))
        return attrs


class StorageRepositorySerlalizer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class ListArhiveSwitchSerlalizer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class ListArchiveSerlalizer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)
    page = serializers.IntegerField(label=_("分页page"), required=True)
    pagesize = serializers.IntegerField(label=_("分页pagesize"), required=True)


class CreateArchiveSerlalizer(serializers.Serializer):
    instance_id = serializers.IntegerField(required=True, label=_("实例id"))
    instance_type = serializers.ChoiceField(required=True, label=_("实例类型"), choices=ArchiveInstanceType.choices)
    target_snapshot_repository_name = serializers.CharField(required=True, label=_("目标es集群快照仓库"))
    snapshot_days = serializers.IntegerField(required=True, label=_("快照存储时间配置"), min_value=0)
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class UpdateArchiveSerlalizer(serializers.Serializer):
    snapshot_days = serializers.IntegerField(required=True, label=_("快照存储时间配置"), min_value=0)


class RestoreArchiveSerlalizer(serializers.Serializer):
    archive_config_id = serializers.IntegerField(label=_("业务ID"), required=True)
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)
    index_set_name = serializers.CharField(label=_("索引集名称"), required=True)
    start_time = serializers.DateTimeField(required=True, label=_("数据开始时间"), format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(required=True, label=_("数据结束时间"), format="%Y-%m-%d %H:%M:%S")
    expired_time = serializers.DateTimeField(required=True, label=_("指定过期时间"), format="%Y-%m-%d %H:%M:%S")
    notice_user = serializers.ListField(required=True, label=_("通知人"))


class UpdateRestoreArchiveSerlalizer(serializers.Serializer):
    expired_time = serializers.DateTimeField(required=True, label=_("指定过期时间"), format="%Y-%m-%d %H:%M:%S")


class DeleteRestoreArchiveSerlalizer(serializers.Serializer):
    restore_config_id = serializers.IntegerField(label=_("回溯id"))


class ListRestoreSerlalizer(ListArchiveSerlalizer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)
    page = serializers.IntegerField(label=_("分页page"), required=True)
    pagesize = serializers.IntegerField(label=_("分页pagesize"), required=True)


class ListCollectorSerlalizer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=True)


class BatchGetStateSerlalizer(serializers.Serializer):
    restore_config_ids = serializers.ListField(label=_("归档回溯配置list"), required=True)


class PreCheckSerializer(serializers.Serializer):
    """
    预检查bk_data_name
    """

    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    bk_data_name = serializers.CharField(label=_("采集链路data_name"), required=False)
    result_table_id = serializers.CharField(label=_("结果表ID"), required=False)


class CollectorPluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectorPlugin
        fields = "__all__"


class MultiAttrCheckSerializer:
    def _check_multi_attrs(self, attrs: dict, *args):
        """
        校验多个参数是否存在
        """

        err_msg = ""
        for key in args:
            if key not in attrs.keys():
                msg = "{}{};".format(key, _("不存在"))
                err_msg += msg
        if err_msg:
            raise serializers.ValidationError(err_msg)


class CollectorPluginCreateSerializer(MultiAttrCheckSerializer, serializers.ModelSerializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), allow_null=True)
    is_create_public_data_id = serializers.BooleanField(label=(_("创建DATAID")), default=False)
    collector_plugin_name_en = serializers.RegexField(
        label=_("采集插件英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )

    class Meta:
        model = CollectorPlugin
        fields = "__all__"

    def _is_create_data_id(self, attrs: dict) -> bool:
        """
        判断是否需要创建DATAID
        1. 不允许独立DATAID时
        2. 指定创建DATAID时
        """

        is_allow_alone_data_id = attrs.get("is_allow_alone_data_id", True)
        create_public_data_id = attrs.get("create_public_data_id", False)
        return not is_allow_alone_data_id or create_public_data_id

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)

        # bk_biz_id 允许为空，默认置0
        if not attrs.get("bk_biz_id"):
            attrs["bk_biz_id"] = 0

        # 不允许独立存储或有dataid时
        is_allow_alone_storage = attrs.get("is_allow_alone_storage", True)
        if not is_allow_alone_storage or self._is_create_data_id(attrs):
            self._check_multi_attrs(
                attrs,
                "storage_cluster_id",
                "retention",
                "allocation_min_days",
                "storage_replies",
                "storage_shards_nums",
                "storage_shards_size",
            )

        # 不允许独立清洗规则或有dataid时
        is_allow_alone_etl_config = attrs.get("is_allow_alone_etl_config", True)
        if not is_allow_alone_etl_config or self._is_create_data_id(attrs):
            self._check_multi_attrs(attrs, "etl_config", "etl_params", "fields")

        return attrs


class CreateCollectorPluginInstanceSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    bkdata_biz_id = serializers.IntegerField(label=_("数据平台业务ID"), required=False)
    platform_username = serializers.CharField(label=_("平台用户"), required=False)
    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    data_link_id = serializers.CharField(label=_("数据链路id"), required=False, allow_blank=True, allow_null=True)
    target_object_type = serializers.CharField(label=_("目标类型"))
    target_node_type = serializers.CharField(label=_("节点类型"))
    target_nodes = TargetNodeSerializer(label=_("目标节点"), many=True)
    data_encoding = serializers.CharField(label=_("日志编码"))
    params = PluginParamSerializer()


class UpdateCollectorPluginInstanceSerializer(serializers.Serializer):
    platform_username = serializers.CharField(label=_("平台用户"), required=False)
    collector_config_id = serializers.IntegerField(label=_("采集项ID"))
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


class CreateColelctorConfigEtlSerializer(serializers.Serializer):
    collector_config_id = serializers.IntegerField(label=_("采集项ID"))
    etl_config = serializers.JSONField(label=_("清洗规则参数"), required=False)
    etl_params = serializers.JSONField(label=_("清洗规则参数"), required=False)
    fields = serializers.JSONField(label=_("清洗字段"), required=False)
    storage_cluster_id = serializers.IntegerField(label=_("存储集群ID"), required=False)
    retention = serializers.IntegerField(label=_("有效天数"), required=False)
    allocation_min_days = serializers.IntegerField(label=_("冷热天书"), required=False)
    storage_replies = serializers.IntegerField(label=_("存储副本数"), required=False)
    storage_shards_nums = serializers.IntegerField(label=_("存储分片数"), required=False)
    storage_shards_size = serializers.IntegerField(label=_("单shards分片大小"), required=False)


class CollectorPluginUpdateSerializer(MultiAttrCheckSerializer, serializers.ModelSerializer):
    collector_plugin_name = serializers.CharField()

    class Meta:
        model = CollectorPlugin
        fields = [
            "collector_plugin_name",
            "description",
            "data_encoding",
            "is_display_collector",
            "is_allow_alone_data_id",
            "is_allow_alone_etl_config",
            "is_allow_alone_storage",
            "storage_cluster_id",
            "retention",
            "allocation_min_days",
            "storage_replies",
            "storage_shards_nums",
            "storage_shards_size",
            "etl_config",
            "etl_params",
            "fields",
            "params",
            "index_settings",
        ]

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)

        # 不允许独立清洗规则或有dataid时
        if attrs.get("is_allow_alone_etl_config") is False or attrs.get("is_allow_alone_data_id"):
            self._check_multi_attrs(attrs, "etl_config", "etl_params", "fields")

        # 不允许独立存储或有dataid时
        if attrs.get("is_allow_alone_storage") is False or attrs.get("is_allow_alone_data_id"):
            self._check_multi_attrs(
                attrs,
                "storage_cluster_id",
                "retention",
                "allocation_min_days",
                "storage_replies",
                "storage_shards_nums",
                "storage_shards_size",
            )

        return attrs


class ListBCSCollectorSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"), required=False)
    bcs_cluster_id = serializers.CharField(label=_("bcs集群id"))


class BCSCollectorSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"))
    project_id = serializers.CharField(label=_("项目id"))
    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX, required=False, default=""
    )
    custom_type = serializers.CharField(label=_("日志类型"), required=False, default="log")
    category_id = serializers.CharField(label=_("分类"), required=False, default="kubernetes")
    description = serializers.CharField(label=_("解释说明"), allow_null=True, allow_blank=True, default="")
    environment = serializers.CharField(label=_("环境"), required=False, default="container")
    bcs_cluster_id = serializers.CharField(label=_("bcs集群id"))
    add_pod_label = serializers.BooleanField(label=_("是否自动添加pod中的labels"))
    extra_labels = serializers.ListSerializer(label=_("额外标签"), required=False, child=LabelsSerializer(), default=[])
    config = serializers.ListSerializer(label=_("容器日志配置"), child=BcsContainerConfigSerializer())


class PreviewContainersSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"))
    bcs_cluster_id = serializers.CharField(label=_("bcs集群id"))
    type = serializers.ChoiceField(label=_("类型"), choices=TopoType.get_choices())
    label_selector = LabelSelectorSerializer(
        required=False, label=_("标签"), default={"match_labels": [], "match_expressions": []}
    )
    namespaces = serializers.ListSerializer(child=serializers.CharField(), required=False, label=_("命名空间"), default=[])
    container = ContainerSerializer(required=False, label=_("指定容器"))


class ValidateContainerCollectorYamlSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务id"))
    bcs_cluster_id = serializers.CharField(label=_("bcs集群id"))
    yaml_config = serializers.CharField(label=_("YAML配置的base64"), allow_blank=True)

    def validate_yaml_config(self, value):
        try:
            yaml_text = base64.b64decode(value).decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            raise ValidationError(_("base64编码解析失败"))
        return yaml_text


class ContainerCollectorYamlSerializer(serializers.Serializer):
    class NamespaceSelector(serializers.Serializer):
        any = serializers.BooleanField(label=_("是否匹配全部命名空间"), required=False)
        matchNames = serializers.ListField(label=_("关键字列表"), allow_empty=True, required=False)

    class MultilineSerializer(serializers.Serializer):
        pattern = serializers.CharField(label=_("行首正则"), required=False, allow_blank=True, allow_null=True)
        maxLines = serializers.IntegerField(label=_("最多匹配行数"), required=False, max_value=1000, allow_null=True)
        timeout = serializers.CharField(label=_("最大耗时"), required=False, allow_blank=True, allow_null=True)

    class LabelSelectorSerializer(serializers.Serializer):
        class ExprSerializer(serializers.Serializer):
            key = serializers.CharField(label=_("标签key"))
            operator = serializers.ChoiceField(
                label=_("标签连接符"),
                choices=[
                    LabelSelectorOperator.IN,
                    LabelSelectorOperator.NOT_IN,
                    LabelSelectorOperator.EXISTS,
                    LabelSelectorOperator.DOES_NOT_EXIST,
                ],
            )
            values = serializers.ListField(
                label=_("标签value"), allow_empty=True, child=serializers.CharField(), required=False
            )

        matchLabels = serializers.DictField(
            child=serializers.CharField(), label=_("指定标签"), required=False, allow_empty=True
        )
        matchExpressions = serializers.ListSerializer(
            child=ExprSerializer(), label=_("指定表达式"), required=False, allow_empty=True
        )

    class FilterSerializer(serializers.Serializer):
        class ConditionSerializer(serializers.Serializer):
            index = serializers.IntegerField()
            key = serializers.CharField()
            op = serializers.CharField()

        conditions = ConditionSerializer(many=True)

    path = serializers.ListField(
        label=_("日志采集路径"), child=serializers.CharField(allow_blank=True), required=False, allow_empty=True
    )
    encoding = serializers.ChoiceField(label=_("日志字符集"), choices=EncodingsEnum.get_choices(), default="utf-8")
    multiline = MultilineSerializer(label=_("段日志配置"), required=False)
    extMeta = serializers.DictField(label=_("额外的元数据"), required=False, allow_empty=True)
    logConfigType = serializers.ChoiceField(
        label=_("日志类型"),
        choices=[ContainerCollectorType.STDOUT, ContainerCollectorType.CONTAINER, ContainerCollectorType.NODE],
    )
    allContainer = serializers.BooleanField(label=_("是否匹配全量容器"), default=False)
    namespaceSelector = NamespaceSelector(label=_("匹配命名空间"), required=False)
    workloadType = serializers.CharField(label=_("匹配工作负载类型"), required=False, allow_blank=True)
    workloadName = serializers.CharField(label=_("匹配工作负载名称"), required=False, allow_blank=True)
    containerNameMatch = serializers.ListField(
        label=_("容器名称匹配"), child=serializers.CharField(), required=False, allow_empty=True
    )
    labelSelector = LabelSelectorSerializer(label=_("匹配标签"), required=False)
    delimiter = serializers.CharField(
        label=_("分隔符"), allow_null=True, allow_blank=True, required=False, trim_whitespace=False
    )
    filters = FilterSerializer(label=_("过滤规则"), many=True, required=False)
    addPodLabel = serializers.BooleanField(label=_("上报时是否把标签带上"), default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["logConfigType"] != ContainerCollectorType.STDOUT and not attrs.get("path"):
            raise SlzValidationError(_("当日志类型不为标准输出时，日志采集路径为必填项"))
        return attrs


class CustomCollectorBaseSerializer(serializers.Serializer):
    collector_config_name = serializers.CharField(label=_("采集名称"), max_length=50)
    category_id = serializers.CharField(label=_("分类ID"))

    # 清洗配置
    etl_config = serializers.CharField(label=_("清洗类型"), required=False, default=EtlConfig.BK_LOG_TEXT)
    etl_params = CollectorEtlParamsSerializer(required=False)
    fields = serializers.ListField(child=CollectorEtlFieldsSerializer(), label=_("字段配置"), required=False)

    # 存储配置
    storage_cluster_id = serializers.IntegerField(label=_("集群ID"), required=False)
    retention = serializers.IntegerField(label=_("有效时间"), required=False)
    allocation_min_days = serializers.IntegerField(label=_("冷热数据生效时间"), required=False)
    storage_replies = serializers.IntegerField(
        label=_("ES副本数量"), required=False, default=settings.ES_REPLICAS, min_value=0, max_value=3
    )
    es_shards = serializers.IntegerField(
        label=_("ES分片数量"), required=False, default=settings.ES_SHARDS, min_value=1, max_value=64
    )

    # 其他配置
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    is_display = serializers.BooleanField(label=_("是否展示"), default=True, required=False)

    def validate(self, attrs: dict) -> dict:
        # 先进行校验
        attrs = super().validate(attrs)
        # 在传入集群ID时校验其他参数
        keys = attrs.keys()
        if "storage_cluster_id" in keys:
            if "retention" not in keys:
                raise serializers.ValidationError(ugettext("有效时间不能为空"))
            if "allocation_min_days" not in keys:
                raise serializers.ValidationError(ugettext("冷热数据生效时间不能为空"))
        return attrs


class CustomCreateSerializer(CustomCollectorBaseSerializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"), required=False)
    space_uid = SpaceUIDField(label=_("空间唯一标识"), required=False)

    collector_config_name_en = serializers.RegexField(
        label=_("采集英文名称"), min_length=5, max_length=50, regex=COLLECTOR_CONFIG_NAME_EN_REGEX
    )
    data_link_id = serializers.CharField(label=_("数据链路id"), required=False, allow_blank=True, allow_null=True)
    custom_type = serializers.ChoiceField(label=_("日志类型"), choices=CustomTypeEnum.get_choices())

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        if attrs.get("space_uid", ""):
            attrs["bk_biz_id"] = space_uid_to_bk_biz_id(attrs["space_uid"])
        elif not attrs.get("bk_biz_id", ""):
            raise ValueError("bk_biz_id or space_uid not found")

        return attrs


class CustomUpdateSerializer(CustomCollectorBaseSerializer):
    ...


class FastCollectorCreateSerializer(serializers.Serializer):
    """
    API快速创建采集项序列化
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
    data_encoding = serializers.ChoiceField(
        label=_("日志字符集"), choices=EncodingsEnum.get_choices(), required=False, default=EncodingsEnum.UTF.value
    )
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    environment = serializers.ChoiceField(
        label=_("环境"), default=Environment.LINUX, choices=[Environment.LINUX, Environment.WINDOWS]
    )
    params = PluginParamSerializer()
    etl_config = serializers.CharField(label=_("清洗类型"), required=False, default=EtlConfig.BK_LOG_TEXT)
    etl_params = CollectorEtlParamsSerializer(required=False)
    fields = serializers.ListField(child=CollectorEtlFieldsSerializer(), label=_("字段配置"), required=False)
    storage_cluster_id = serializers.IntegerField(label=_("集群ID"), required=False)
    retention = serializers.IntegerField(label=_("有效时间"), required=False, default=settings.ES_PUBLIC_STORAGE_DURATION)
    allocation_min_days = serializers.IntegerField(label=_("冷热数据生效时间"), required=False, default=0)
    storage_replies = serializers.IntegerField(
        label=_("ES副本数量"), required=False, default=settings.ES_REPLICAS, min_value=0, max_value=3
    )
    es_shards = serializers.IntegerField(
        label=_("ES分片数量"), required=False, default=settings.ES_SHARDS, min_value=1, max_value=64
    )

    def validate(self, attrs):
        if attrs["collector_scenario_id"] == "section":
            for field in ["multiline_pattern", "multiline_max_lines", "multiline_timeout"]:
                if field not in attrs["params"]:
                    raise ValidationError(_("{} 该字段为必填项").format(field))

        if attrs["collector_scenario_id"] == "wineventlog":
            for field in ["winlog_name"]:
                if field not in attrs["params"]:
                    raise ValidationError(_("{} 该字段为必填项").format(field))

        if attrs["etl_config"] in EtlConfigEnum.get_dict_choices():
            if not attrs.get("fields"):
                raise ValidationError(_("[字段提取]请输入需要提取的字段信息"))

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


class FastCollectorUpdateSerializer(serializers.Serializer):
    collector_config_name = serializers.CharField(label=_("采集名称"), required=False, max_length=50)
    description = serializers.CharField(
        label=_("备注说明"), max_length=64, required=False, allow_null=True, allow_blank=True
    )
    target_node_type = serializers.CharField(label=_("节点类型"), required=False)
    target_nodes = TargetNodeSerializer(label=_("目标节点"), required=False, many=True)
    params = PluginParamSerializer(required=False)
    data_encoding = serializers.ChoiceField(
        label=_("日志字符集"), choices=EncodingsEnum.get_choices(), required=False, default=EncodingsEnum.UTF.value
    )
    etl_config = serializers.CharField(label=_("清洗类型"), required=False)
    etl_params = CollectorEtlParamsSerializer(required=False)
    fields = serializers.ListField(child=CollectorEtlFieldsSerializer(), label=_("字段配置"), required=False)
    retention = serializers.IntegerField(label=_("有效时间"), required=False)
    allocation_min_days = serializers.IntegerField(label=_("冷热数据生效时间"), required=False)
    storage_replies = serializers.IntegerField(label=_("ES副本数量"), required=False, min_value=0, max_value=3)
    es_shards = serializers.IntegerField(label=_("ES分片数量"), required=False, min_value=1, max_value=64)

    def validate(self, attrs):
        if attrs.get("etl_config") and attrs["etl_config"] in EtlConfigEnum.get_dict_choices():
            if not attrs.get("fields"):
                raise ValidationError(_("[字段提取]请输入需要提取的字段信息"))

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


class ContainerCollectorConfigToYamlSerializer(serializers.Serializer):
    configs = serializers.ListSerializer(label=_("容器日志配置"), child=ContainerConfigSerializer())
    add_pod_label = serializers.BooleanField(label=_("上报时是否把标签带上"), default=False)
    extra_labels = serializers.ListSerializer(label=_("额外标签"), required=False, child=LabelsSerializer())


class CheckCollectorSerializer(serializers.Serializer):
    collector_config_id = serializers.IntegerField(label=_("采集项ID"))
    hosts = serializers.CharField(label=_("指定检查某些主机"), required=False)


class GetCollectorCheckResultSerializer(serializers.Serializer):
    check_record_id = serializers.CharField(label=_("采集项检查唯一标识"))
