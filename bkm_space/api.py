# -*- coding: utf-8 -*-
import abc
from typing import List, Union

from django.conf import settings
from django.utils.module_loading import import_string

from bkm_space.define import Space, SpaceTypeEnum


class AbstractSpaceApi(metaclass=abc.ABCMeta):
    """
    空间相关的接口实现
    """

    @classmethod
    def get_space_detail(cls, space_uid: str = "", id: int = 0) -> Union[None, Space]:
        """
        查看具体空间实例详情
        :param space_uid: 空间唯一标识
        :param id: 空间自增ID
        """
        # TODO: 需实现该接口
        raise NotImplementedError

    @classmethod
    def list_spaces(cls) -> List[Space]:
        """
        查询空间列表
        """
        raise NotImplementedError

    @classmethod
    def get_related_space(cls, space_uid: str, related_space_type: str) -> Union[None, Space]:
        """
        查询空间关联的资源对应空间。 如果类型和关联类型一致，则返回自己。
        """
        # 不在资源定义中的类型，直接返回
        if related_space_type not in SpaceTypeEnum._value2member_map_:
            return None

        space = cls.get_space_detail(space_uid)
        if space is None:
            return None
        space_type, _ = cls.parse_space_uid(space_uid)
        # 如果类型和关联类型一致，则返回自己。
        if space_type == related_space_type:
            return space

        related_space_list = space.extend["resources"]
        for r_space in related_space_list:
            if r_space["resource_type"] == related_space_type:
                return cls.get_space_detail(cls.gen_space_uid(related_space_type, r_space["resource_id"]))

    @classmethod
    def gen_space_uid(cls, space_type: str, space_id: str) -> str:
        return f"{space_type}__{space_id}"

    @classmethod
    def parse_space_uid(cls, space_uid: str) -> tuple:
        """
        将 空间唯一标识 解析为 空间类型 和 空间ID
        :param space_uid: 空间唯一标识
        :return: 二元组 space_type, space_id
        """
        parsed_data = space_uid.split("__", 1)
        if len(parsed_data) != 2:
            raise ValueError("invalid space_uid format")
        space_type, space_id = parsed_data
        return space_type, space_id


class SpaceApiProxy(object):
    def __init__(self):
        self._api = None

    def __getattr__(self, action):
        if self._api is None:
            self.init_api()
        func = getattr(self._api, action)
        return func

    def init_api(self):
        api_class = getattr(settings, "BKM_SPACE_API_CLASS", "bkm_space.api.AbstractSpaceApi")
        self._api = import_string(api_class)


SpaceApi: AbstractSpaceApi = SpaceApiProxy()
