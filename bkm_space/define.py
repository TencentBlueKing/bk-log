# -*- coding: utf-8 -*-
from enum import Enum
from typing import Union

from dataclasses import dataclass, asdict, fields


class SpaceTypeEnum(Enum):
    """
    空间类型枚举
    """

    BKCC = "bkcc"  # CMDB 业务


@dataclass
class Space:
    """
    空间格式
    """

    to_dict = asdict

    id: int
    space_type_id: str
    space_id: str
    space_name: str
    status: str
    space_code: Union[None, str]
    space_uid: str
    type_name: Union[None, str]

    @classmethod
    def from_dict(cls, data):
        init_fields = {f.name for f in fields(cls) if f.init}
        filtered_data = {k: data.pop(k, None) for k in init_fields}
        instance = cls(**filtered_data)
        setattr(instance, "extend", data)
        return instance
