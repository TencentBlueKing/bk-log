# -*- coding: utf-8 -*-
import typing
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bkm_ipchooser import constants, exceptions
from bkm_space.utils import space_uid_to_bk_biz_id


class PaginationSer(serializers.Serializer):
    start = serializers.IntegerField(help_text=_("数据起始位置"), required=False, default=0)
    page_size = serializers.IntegerField(
        help_text=_("拉取数据数量，不传或传 `-1` 表示拉取所有"),
        required=False,
        min_value=constants.CommonEnum.PAGE_RETURN_ALL_FLAG.value,
        max_value=500,
        default=constants.CommonEnum.PAGE_RETURN_ALL_FLAG.value,
    )


class ScopeSer(serializers.Serializer):
    scope_type = serializers.ChoiceField(help_text=_("资源范围类型"), choices=constants.ScopeType.list_choices())
    scope_id = serializers.CharField(help_text=_("资源范围ID"), min_length=1)
    # 最终只会使用 bk_biz_id
    bk_biz_id = serializers.IntegerField(help_text=_("业务 ID"), required=False)

    def validate(self, attrs):
        if attrs["scope_type"] == constants.ScopeType.SPACE.value:
            attrs["bk_biz_id"] = space_uid_to_bk_biz_id(attrs["scope_id"])
        else:
            attrs["bk_biz_id"] = int(attrs["scope_id"])
        return attrs


class TreeNodeSer(serializers.Serializer):
    object_id = serializers.CharField(help_text=_("节点类型ID"))
    instance_id = serializers.IntegerField(help_text=_("节点实例ID"))
    meta = ScopeSer(help_text=_("Meta元数据"), required=False)


class HostSearchConditionSer(serializers.Serializer):
    ip = serializers.IPAddressField(label=_("内网IP"), required=False, protocol="ipv4")
    ipv6 = serializers.IPAddressField(label=_("内网IPv6"), required=False, protocol="ipv6")
    os_type = serializers.ChoiceField(label=_("操作系统类型"), required=False, choices=constants.OS_CHOICES)
    host_name = serializers.CharField(label=_("主机名称"), required=False, min_length=1)
    content = serializers.CharField(label=_("模糊搜索内容（支持同时对`主机IP`/`主机名`/`操作系统`进行模糊搜索"), required=False, min_length=1)


class ScopeSelectorBaseSer(serializers.Serializer):
    all_scope = serializers.BooleanField(help_text=_("是否获取所有资源范围的拓扑结构，默认为 `false`"), required=False, default=False)
    scope_list = serializers.ListField(help_text=_("要获取拓扑结构的资源范围数组"), child=ScopeSer(), default=[], required=False)


class QueryHostsBaseSer(ScopeSelectorBaseSer, PaginationSer):
    search_condition = HostSearchConditionSer(required=False)

    # k-v 查找上线前临时兼容的模糊查询字段
    search_content = serializers.CharField(label=_("模糊搜索内容"), required=False)

    # 适配原代码风格
    conditions = serializers.ListField(label=_("搜索条件"), required=False, child=serializers.DictField())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        search_cond_map: typing.Dict[str, str] = {
            "ip": "inner_ip",
            "inner_ipv6": "inner_ipv6",
            "os_type": "os_type",
            "host_name": "bk_host_name",
            "cloud_name": "query",
            "alive": "status",
            "content": "query",
        }

        conditions = []
        search_condition: typing.Dict[str, str] = attrs.get("search_condition", {})
        # k-v 查找上线前临时兼容的模糊查询字段
        if "search_content" in attrs:
            for fuzzy_field in constants.CommonEnum.DEFAULT_HOST_FUZZY_SEARCH_FIELDS.value:
                conditions.append({"field": fuzzy_field, "operator": "contains", "value": attrs["search_content"]})

        for key, val in search_condition.items():
            cond_key: str = search_cond_map[key]
            if key == "cloud_name":
                # 云区域名暂时只支持模糊搜索
                conditions.append({"key": cond_key, "value": val, "fuzzy_search_fields": ["bk_cloud_id"]})
            elif key == "content":
                conditions.append(
                    {
                        "key": cond_key,
                        "value": val,
                        "fuzzy_search_fields": constants.CommonEnum.DEFAULT_HOST_FUZZY_SEARCH_FIELDS.value
                        + ["os_type"],
                    }
                )
            elif key == "alive":
                # 转为数据库可识别的 Agent 状态
                if val == constants.AgentStatusType.ALIVE.value:
                    cond_vals: typing.List[str] = [constants.ProcStateType.RUNNING]
                else:
                    cond_vals: typing.List[str] = list(
                        set(constants.PROC_STATE_TUPLE) - {constants.ProcStateType.RUNNING}
                    )
                conditions.append({"key": cond_key, "value": cond_vals})
            else:
                conditions.append({"key": cond_key, "value": [val]})
        # 回写查询条件
        attrs["conditions"] = conditions
        return attrs


class HostInfoWithMetaSer(serializers.Serializer):
    meta = ScopeSer(help_text=_("Meta元数据"), required=False)
    cloud_id = serializers.IntegerField(help_text=_("云区域 ID"), required=False)
    ip = serializers.IPAddressField(help_text=_("IPv4 协议下的主机IP"), required=False, protocol="ipv4")
    host_id = serializers.IntegerField(help_text=_("主机 ID，优先取 `host_id`，否则取 `ip` + `cloud_id`"), required=False)

    def validate(self, attrs):
        if not ("host_id" in attrs or ("ip" in attrs and "cloud_id" in attrs)):
            raise exceptions.SerValidationError(_("参数校验失败: 请传入 host_id 或者 cloud_id + ip"))
        return attrs
