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
import re

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField

from apps.log_search.constants import InstanceTypeEnum
from apps.log_extract import models
from apps.log_extract import constants
from apps.log_extract.constants import KeywordType, PREDATEMODE_CUSTOM_TIME_FORMAT
from apps.log_extract.models import ExtractLink
from apps.utils.base_crypt import BaseCrypt
from apps.utils.drf import GeneralSerializer


def is_file_path_legal(file_path):
    if not file_path.startswith(constants.ALLOWED_DIR_PREFIX):
        return False

    # 不能包含 '//', 特殊字符('.'在后面处理，创建任务时可以包含'.'
    if re.findall(r"//+", file_path):
        return False
    # 不能有 '/.' 或者 './'
    if re.findall(r"/\.", file_path) or re.findall(r"\./", file_path):
        return False
    # 正则匹配
    pattern = re.compile(rf"^[{settings.EXTRACT_FILE_PATTERN_CHARACTERS}]+$")
    if not pattern.match(file_path):
        return False
    return True


class BkIpSerializer(serializers.Serializer):
    bk_host_id = serializers.IntegerField(label=_("主机ID"), required=False)
    ip = serializers.IPAddressField(label=_("业务机器ip"), required=False, allow_null=True, allow_blank=True)
    bk_cloud_id = serializers.IntegerField(label=_("业务机器云区域id"), required=False)

    def validate(self, attrs):
        if "bk_host_id" in attrs or ("ip" in attrs and "bk_cloud_id" in attrs):
            return attrs
        raise ValidationError(_("bk_host_id 和 ip+bk_cloud_id 至少提供一项"))


class ExplorerListSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    ip_list = serializers.ListSerializer(label=_("业务机器列表"), child=BkIpSerializer(), required=True)
    path = serializers.CharField(label=_("文件路径"))
    is_search_child = serializers.BooleanField(label=_("是否搜索子目录"))
    time_range = serializers.CharField(label=_("时间跨度"))
    start_time = serializers.CharField(label=_("开始时间"), required=False, default=None)
    end_time = serializers.CharField(label=_("结束时间"), required=False, default=None)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not is_file_path_legal(attrs["path"]):
            raise serializers.ValidationError(_("请指定正确的目录"))
        if attrs["time_range"] not in constants.ALLOWED_TIME_RANGE:
            raise serializers.ValidationError(_("请指定正确的时间跨度"))
        if attrs["time_range"] in [constants.PreDateMode.CUSTOM.value]:
            if attrs["start_time"] and attrs["end_time"]:
                try:
                    start_time = attrs["start_time"].replace("&nbsp;", " ")
                    end_time = attrs["end_time"].replace("&nbsp;", " ")
                    datetime.datetime.strptime(start_time, PREDATEMODE_CUSTOM_TIME_FORMAT)
                    datetime.datetime.strptime(end_time, PREDATEMODE_CUSTOM_TIME_FORMAT)
                    attrs["start_time"] = start_time
                    attrs["end_time"] = end_time
                except ValueError:
                    raise serializers.ValidationError(_("时间格式不正确"))
            else:
                raise serializers.ValidationError(_("请指定开始和结束时间"))

        attrs["time_range"] = constants.ALLOWED_TIME_RANGE.get(attrs["time_range"])
        return attrs


class ExplorerStrategiesSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    ip_list = serializers.ListSerializer(label=_("业务机器列表"), child=BkIpSerializer(), required=True)


class ListTaskSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    keyword = serializers.CharField(label=_("搜索关键字"), max_length=255, allow_blank=True, allow_null=True, default=None)


class CreateTaskSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    ip_list = serializers.ListField(label=_("业务机器IP"), child=BkIpSerializer())
    file_path = serializers.ListField(label=_("目标文件路径"))
    filter_type = serializers.CharField(label=_("过滤类型"), allow_blank=True)
    filter_content = serializers.JSONField(label=_("过滤参数"))
    remark = serializers.CharField(label=_("备注"), allow_blank=True, max_length=255, default="")
    preview_directory = serializers.CharField(label=_("预览目录"), max_length=255)
    preview_ip_list = serializers.ListField(label=_("预览机器IP"), child=BkIpSerializer())
    preview_time_range = serializers.CharField(label=_("预览日期"), max_length=10)
    preview_start_time = serializers.CharField(label=_("预览开始时间"), max_length=20, default="", required=False)
    preview_end_time = serializers.CharField(label=_("预览结束时间"), max_length=20, default="", required=False)
    preview_is_search_child = serializers.BooleanField(label=_("预览是否搜索子目录"))
    link_id = serializers.IntegerField(label=_("提取链路id"))

    def validate(self, attrs):
        attrs = super().validate(attrs)
        filter_type = attrs["filter_type"]
        filter_content = attrs["filter_content"]
        if filter_type and filter_type not in constants.ALLOWED_FILTER_TYPES:
            raise serializers.ValidationError(_("请指定正确的过滤类型"))

        validate_func = self._get_filter_validate(filter_type)
        validate_func(filter_content)
        return attrs

    def validate_link_id(self, value):
        if ExtractLink.objects.filter(link_id=value).exists():
            return value
        raise serializers.ValidationError(_("提取链路不存在"))

    def validate_file_path(self, value):
        if len(value) > settings.CSTONE_DOWNLOAD_FILES_LIMIT:
            raise serializers.ValidationError(_("同时下载的文件数不能超过{}".format(settings.CSTONE_DOWNLOAD_FILES_LIMIT)))

        for file_path in value:
            # 创建任务时对路径前缀做校验
            if not is_file_path_legal(file_path):
                raise serializers.ValidationError(_("请指定正确的目录"))
        return value

    def validate_preview_time_range(self, value):
        if value not in constants.PreDateMode.get_dict_choices().keys():
            raise serializers.ValidationError(_("请指定正确的预览日期模式"))
        return value

    def _get_filter_validate(self, filter_type):
        func_prefix = "_validate_"
        func = getattr(self, f"{func_prefix}{filter_type}", lambda _: _)
        return func

    @staticmethod
    def _validate_keyword_match(filter_content):
        keyword = filter_content.get("keyword")
        if not isinstance(keyword, str):
            raise serializers.ValidationError(_("过滤关键词必须为字符串类型"))
        if not keyword or keyword.isspace():
            raise serializers.ValidationError(_("过滤关键词不可为空"))
        if len(keyword) > constants.KEYWORD_MAX_LENGTH:
            raise serializers.ValidationError(_("过滤关键字超过长度"))
        keyword = keyword.strip()
        if " " in keyword:
            raise serializers.ValidationError(_("过滤关键词请勿包含空格"))
        # 对keyword做了修改，需要重新赋值
        filter_content["keyword"] = keyword
        keyword_type = filter_content.get("keyword_type")
        if keyword_type not in [KeywordType.OR.value, KeywordType.NOT.value, KeywordType.AND.value]:
            raise serializers.ValidationError(_("过滤关键字类型不正确"))

    @staticmethod
    def _validate_line_range(filter_content):
        start_line = filter_content.get("start_line")
        end_line = filter_content.get("end_line")

        if any(not isinstance(key, int) for key in [start_line, end_line]):
            raise serializers.ValidationError(_("行数必须为整型"))

        if any(filter_content.get(key) is None for key in ["start_line", "end_line"]):
            raise serializers.ValidationError(_("行数不可为空"))

        if start_line >= end_line:
            raise serializers.ValidationError(_("请确认起始行数与终止行数的大小关系"))

        if min(start_line, end_line) < 0:
            raise serializers.ValidationError(_("请确认起始行数与终止行数的大小关系"))

    @staticmethod
    def _validate_tail_line(filter_content):
        line_num = filter_content.get("line_num")
        if line_num is None:
            raise serializers.ValidationError(_("行数不可为空"))
        if not isinstance(line_num, int):
            raise serializers.ValidationError(_("最新行数请输入整数"))
        if line_num <= 0:
            raise serializers.ValidationError(_("请保证最新行数大于0"))

    @staticmethod
    def _validate_match_range(filter_content):
        if any(not filter_content.get(key) for key in ["start", "end"]):
            raise serializers.ValidationError(_("过滤条件包含空关键词"))
        if any(not isinstance(filter_content.get(key), str) for key in ["start", "end"]):
            raise serializers.ValidationError(_("过滤关键词必须为字符串类型"))
        if any(filter_content.get(key).isspace() for key in ["start", "end"]):
            raise serializers.ValidationError(_("过滤条件包含空关键词"))
        if any(len(filter_content.get(key)) > constants.KEYWORD_MAX_LENGTH for key in ["start", "end"]):
            raise serializers.ValidationError(_("过滤关键字超过长度"))


class RetrieveTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(label=_("下载任务ID"))


class DownloadSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(label=_("下载任务ID"))
    is_url = serializers.CharField(label=_("是否直接返回url"), allow_null=True, allow_blank=True, required=False)


class TaskPollingSerializer(serializers.Serializer):
    task_list = serializers.CharField(label=_("下载任务ID列表"), source="task_id")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # 数据库中字段名为 task_id
        task_list = attrs["task_id"].split(",")
        for task_id in task_list:
            if not re.findall(r"^\d+", task_id):
                raise serializers.ValidationError(_("任务列表类型错误,请输入正确的整型数组"))
        return attrs


class PollingResultSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(label=_("下载任务ID"))
    download_status = serializers.CharField(label=_("当前下载状态"))
    task_process_info = serializers.CharField(label=_("任务过程信息"))
    remark = serializers.CharField(label=_("备注"))


class RecreateTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(label=_("下载任务ID"))


class ChildrenModulesSerializer(serializers.Serializer):
    bk_inst_id = serializers.IntegerField(label=_("实例ID"))
    bk_inst_name = serializers.CharField(label=_("实例名称"))
    bk_obj_id = serializers.CharField(label=_("对象ID"))
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))


class StrategiesSerializer(GeneralSerializer):
    user_list = serializers.ListField(label=_("用户ID"))
    select_type = serializers.CharField(label=_("目标选择类型"))
    modules = serializers.ListField(label=_("模块列表"))
    visible_dir = serializers.ListField(label=_("目录列表"))
    file_type = serializers.ListField(label=_("文件类型"))

    class Meta:
        model = models.Strategies
        fields = [
            "strategy_id",
            "strategy_name",
            "user_list",
            "bk_biz_id",
            "select_type",
            "modules",
            "visible_dir",
            "file_type",
            "operator",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class UpdateOrCreateStrategiesSerializer(serializers.ModelSerializer):
    # 创建和更新都用这个序列化器
    strategy_name = serializers.CharField(label=_("策略名称"))
    user_list = serializers.ListField(label=_("用户组ID"))
    bk_biz_id = serializers.IntegerField(label=_("授权的业务ID"))
    select_type = serializers.CharField(label=_("目标选择类型"))
    modules = serializers.ListField(label=_("授权的模板实例列表"), child=ChildrenModulesSerializer())
    visible_dir = serializers.ListField(label=_("授权的目录列表"))
    file_type = serializers.ListField(label=_("授权的文件类型"))
    operator = serializers.CharField(label=_("作业执行人"))

    class Meta:
        model = models.Strategies
        fields = [
            "strategy_name",
            "user_list",
            "bk_biz_id",
            "select_type",
            "modules",
            "visible_dir",
            "file_type",
            "operator",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["select_type"] not in ["module", "topo"]:
            raise serializers.ValidationError(_("请指定正确的目标选择类型"))
        for v_dir in attrs["visible_dir"]:
            if not is_file_path_legal(v_dir):
                # if not v_dir.startswith(ALLOWED_DIR_PREFIX) or re.findall(r"\./", v_dir):
                raise serializers.ValidationError(_("请指定正确的目录"))
            if not v_dir.endswith("/"):
                raise serializers.ValidationError(_("目录请以 '/' 结尾"))

        pattern = re.compile(r"^[a-zA-Z0-9_.*]+$")
        for f_type in attrs["file_type"]:
            if not pattern.match(f_type):
                raise serializers.ValidationError(_("文件后缀格式有误"))

            if f_type.startswith("."):
                raise serializers.ValidationError(_("文件后缀不需要使用.开头"))

        # 用户列表处理
        attrs["user_list"] = [username.strip() for username in attrs["user_list"] if username.strip() != ""]
        return attrs


class ListStrategiesSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))


class TasksSerializer(serializers.ModelSerializer):
    ip_list = ListField(_("业务机器ip"))
    preview_ip_list = ListField(_("预览地址ip列表"))
    file_path = ListField(_("文件列表"))

    class Meta:
        model = models.Tasks
        fields = "__all__"


class TaskListSerializer(GeneralSerializer):
    task_id = serializers.IntegerField(label=_("下载任务ID"))
    ip_list = ListField(_("业务机器ip"))
    file_path = ListField(_("文件列表"))
    download_status = serializers.CharField(label=_("任务状态"), max_length=16)
    filter_type = serializers.CharField(label=_("过滤类型"))
    filter_content = serializers.JSONField(label=_("过滤内容"))
    task_process_info = serializers.CharField(label=_("任务过程信息"), max_length=500)
    remark = serializers.CharField(label=_("任务创建者"), max_length=500)

    class Meta:
        model = models.Tasks
        fields = [
            "task_id",
            "ip_list",
            "file_path",
            "download_status",
            "filter_type",
            "filter_content",
            "task_process_info",
            "preview_directory",
            "preview_ip",
            "preview_ip_list",
            "preview_time_range",
            "preview_is_search_child",
            "preview_start_time",
            "preview_end_time",
            "remark",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "expiration_date",
        ]


class ExplorerListTopo(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(label=_("业务ID"))


class StrategiesTopoSerializer(serializers.Serializer):
    """
    获取拓扑序列化
    """

    bk_biz_id = serializers.IntegerField(label=_("业务ID"))
    instance_type = serializers.ChoiceField(label=_("实例类型"), choices=InstanceTypeEnum.get_choices(), required=False)
    remove_empty_nodes = serializers.BooleanField(label=_("是否删除空节点"), required=False)


class TaskPartialUpdateSerializer(serializers.Serializer):
    remark = serializers.CharField(label=_("备注"), max_length=255)

    class Meta:
        model = models.Tasks
        fields = ["remark"]

    def update(self, instance, validated_data):
        instance.remark = validated_data["remark"]
        instance.save()
        return instance


class DownloadFileSerializer(serializers.Serializer):
    target_file = serializers.CharField(label=_("加密的目标文件名"), max_length=255)

    def validate_target_file(self, value):
        return BaseCrypt().decrypt(value)


class ExtractLinksSerializer(serializers.Serializer):
    name = serializers.CharField(label=_("链路名称"))
    link_id = serializers.IntegerField(label=_("链路id"))
    link_type = serializers.CharField(label=_("链路类型"))
    created_by = serializers.CharField(label=_("创建者"))
    created_at = serializers.DateTimeField(label=_("创建时间"))

    class Meta:
        model = models.ExtractLink
        fields = ["name", "link_id", "link_type", "created_by", "created_at"]


class LinkHostsSerializer(serializers.Serializer):
    target_dir = serializers.CharField(label=_("挂载目录"), required=True)
    bk_cloud_id = serializers.IntegerField(label=_("主机云区域id"), required=True)
    ip = serializers.IPAddressField(label=_("主机ip"), required=True)


class ExtractLinkAndHostsSerializer(serializers.Serializer):
    name = serializers.CharField(label=_("链路名称"), required=True, max_length=255)
    link_type = serializers.CharField(label=_("链路类型"), required=True, max_length=20)
    operator = serializers.CharField(label=_("执行人"), required=True, max_length=255)
    op_bk_biz_id = serializers.IntegerField(label=_("执行bk_biz_id"), required=True)
    qcloud_secret_id = serializers.CharField(label=_("腾讯云SecretId"), required=False, allow_null=True, allow_blank=True)
    qcloud_secret_key = serializers.CharField(
        label=_("腾讯云SecretKey"), required=False, allow_null=True, allow_blank=True
    )
    qcloud_cos_bucket = serializers.CharField(label=_("腾讯云Cos桶名称"), required=False, allow_null=True, allow_blank=True)
    qcloud_cos_region = serializers.CharField(label=_("腾讯云Cos区域"), required=False, allow_null=True, allow_blank=True)
    is_enable = serializers.BooleanField(label=_("是否启用"), required=True)
    hosts = serializers.ListField(label=_("中转机列表"), child=LinkHostsSerializer(), required=True)
