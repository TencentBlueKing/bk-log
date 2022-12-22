# -*- coding: utf-8 -*-
import abc
from collections import namedtuple
from enum import Enum
from typing import Dict, List, Tuple, Any

from django.utils.translation import ugettext_lazy as _


def tuple_choices(tupl):
    """从django-model的choices转换到namedtuple"""
    return [(t, t) for t in tupl]


def dict_to_namedtuple(dic):
    """从dict转换到namedtuple"""
    return namedtuple("AttrStore", list(dic.keys()))(**dic)


def choices_to_namedtuple(choices):
    """从django-model的choices转换到namedtuple"""
    return dict_to_namedtuple(dict(choices))


class EnhanceEnum(Enum):
    """增强枚举类，提供常用的枚举值列举方法"""

    @classmethod
    @abc.abstractmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        """
        获取枚举成员与释义的映射关系
        :return:
        """
        raise NotImplementedError

    @classmethod
    def list_member_values(cls) -> List[Any]:
        """
        获取所有的枚举成员值
        :return:
        """
        member_values = []
        for member in cls._member_names_:
            member_values.append(cls._member_map_[member].value)
        return member_values

    @classmethod
    def get_member_value__alias_map(cls) -> Dict[Any, str]:
        """
        获取枚举成员值与释义的映射关系，缓存计算结果
        :return:
        """
        member_value__alias_map = {}
        member__alias_map = cls._get_member__alias_map()

        for member, alias in member__alias_map.items():
            if type(member) is not cls:
                raise ValueError(f"except member type -> {cls}, but got -> {type(member)}")
            member_value__alias_map[member.value] = alias

        return member_value__alias_map

    @classmethod
    def list_choices(cls) -> List[Tuple[Any, Any]]:
        """
        获取可选项列表，一般用于序列化器、model的choices选项
        :return:
        """
        return list(cls.get_member_value__alias_map().items())


class CommonEnum(EnhanceEnum):
    SEP = ":"
    PAGE_RETURN_ALL_FLAG = -1
    DEFAULT_HOST_FUZZY_SEARCH_FIELDS = [
        "bk_host_innerip",
        "bk_host_innerip_v6",
        "bk_host_name",
        "bk_os_type",
        "bk_os_name",
    ]
    DEFAULT_HOST_FIELDS = [
        "bk_host_id",
        "bk_cloud_id",
        "bk_host_innerip",
        "bk_host_innerip_v6",
        "bk_host_name",
        "bk_os_type",
        "bk_os_name",
        "bk_agent_id",
        "bk_cloud_vendor",
        "bk_mem",
        "bk_disk",
        "bk_cpu",
        "bk_cpu_architecture",
        "bk_cpu_module",
        "operator",
    ]
    DEFAULT_SET_FIELDS = [
        "bk_set_id",
        "bk_set_name",
        "set_template_id",
    ]
    DEFAULT_MODULE_FIELDS = [
        "bk_module_id",
        "bk_module_name",
        "service_template_id",
    ]
    SIMPLE_HOST_FIELDS = [
        "bk_host_id",
        "bk_cloud_id",
        "bk_host_innerip",
        "bk_host_innerip_v6",
        "bk_host_name",
        "bk_os_type",
        "bk_os_name",
    ]
    FETCH_HOST_COUNT_FIELDS = ["bk_host_id"]

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {
            cls.SEP: _("字段分隔符"),
            cls.PAGE_RETURN_ALL_FLAG: _("全量返回标志"),
            cls.DEFAULT_HOST_FUZZY_SEARCH_FIELDS: _("默认模糊查询字段"),
            cls.DEFAULT_HOST_FIELDS: _("主机列表默认返回字段"),
            cls.DEFAULT_SET_FIELDS: _("集群列表默认返回字段"),
            cls.DEFAULT_MODULE_FIELDS: _("模块列表默认返回字段"),
            cls.SIMPLE_HOST_FIELDS: _("主机列表简单返回字段"),
            cls.FETCH_HOST_COUNT_FIELDS: _("查询只为了统计主机数量限定返回bk_host_id减少请求时间"),
        }


class ScopeType(EnhanceEnum):
    """作用域类型"""

    BIZ = "biz"
    SPACE = "space"

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {cls.BIZ: _("业务"), cls.SPACE: _("空间")}


class ObjectType(EnhanceEnum):
    """CMDB 拓扑节点类型"""

    BIZ = "biz"
    SET = "set"
    MODULE = "module"
    HOST = "host"

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {cls.BIZ: _("业务"), cls.SET: _("集群"), cls.MODULE: _("模块"), cls.HOST: _("主机")}


class AgentStatusType(EnhanceEnum):
    """对外展示的 Agent 状态"""

    ALIVE = 1
    NO_ALIVE = 0

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {cls.ALIVE: _("存活"), cls.NO_ALIVE: _("未存活")}


class TemplateType(EnhanceEnum):
    """模板类型"""

    SERVICE_TEMPLATE = "SERVICE_TEMPLATE"
    SET_TEMPLATE = "SET_TEMPLATE"

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {cls.SERVICE_TEMPLATE: _("服务模版"), cls.SET_TEMPLATE: _("集群模版")}


class TimeEnum(EnhanceEnum):
    """时间枚举"""

    SECOND = 1
    MINUTE = SECOND * 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    WEEK = DAY * 7

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {
            cls.SECOND: _("秒"),
            cls.MINUTE: _("分钟"),
            cls.HOUR: _("小时"),
            cls.DAY: _("天"),
            cls.WEEK: _("周"),
        }


PROC_STATE_TUPLE = ("RUNNING", "UNKNOWN", "TERMINATED", "NOT_INSTALLED", "UNREGISTER", "REMOVED", "MANUAL_STOP")
PROC_STATE_CHOICES = tuple_choices(PROC_STATE_TUPLE)
ProcStateType = choices_to_namedtuple(PROC_STATE_CHOICES)

OS_TUPLE = ("LINUX", "WINDOWS", "AIX", "SOLARIS")
OS_CHOICES = tuple_choices(OS_TUPLE)
OsType = choices_to_namedtuple(OS_CHOICES)
OS_CHN = {os_type: os_type if os_type == OsType.AIX else os_type.capitalize() for os_type in OS_TUPLE}
BK_OS_TYPE = {"LINUX": "1", "WINDOWS": "2", "AIX": "3", "SOLARIS": "5"}

# 默认云区域ID
DEFAULT_CLOUD = 0
DEFAULT_CLOUD_NAME = _("直连区域")
