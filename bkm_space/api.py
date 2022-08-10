# -*- coding: utf-8 -*-
import abc
from typing import List, Union

from django.conf import settings
from django.utils.module_loading import import_string

from bkm_space.define import Space


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


SpaceApi = SpaceApiProxy()
