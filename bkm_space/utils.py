# -*- coding: utf-8 -*-
from typing import Tuple, Union, Dict, List

from bkm_space import api
from bkm_space.define import SpaceTypeEnum


def space_uid_to_bk_biz_id(space_uid: str, id: int = None) -> int:
    """
    空间唯一标识 转换为 业务ID
    规则：空间类型为业务的，直接返回业务ID；空间类型为其他，则返回空间自增ID的相反数
    :param space_uid: 空间唯一标识
    :param id: 空间自增ID
    """
    try:
        space_type, space_id = parse_space_uid(space_uid)
    except ValueError:
        return 0

    if space_type == SpaceTypeEnum.BKCC.value:
        # 遇到业务空间直接转换
        return int(space_id)

    if id is not None:
        # 如果有传自增ID，就直接使用自增ID，对其取相反数，得到负数的业务ID
        return -id

    # 如果没有提供自增ID，非业务空间则通过API查询
    space = api.SpaceApi.get_space_detail(space_uid=space_uid)

    if not space:
        return 0

    return -int(space.id)


def bk_biz_id_to_space_uid(bk_biz_id: Union[str, int]) -> str:
    """
    业务ID 转换为 空间唯一标识
    :param bk_biz_id: CMDB 业务ID
    :return:
    """
    if isinstance(bk_biz_id, (str, int)):
        bk_biz_id = int(bk_biz_id)
    else:
        return ""

    if bk_biz_id >= 0:
        return api.SpaceApi.gen_space_uid(SpaceTypeEnum.BKCC.value, bk_biz_id)

    space = api.SpaceApi.get_space_detail(id=-bk_biz_id)

    if not space:
        return ""

    return space.space_uid


def parse_space_uid(space_uid: str) -> Tuple[str, str]:
    return api.SpaceApi.parse_space_uid(space_uid)


def _inject_space_field_recursive(data: Union[Dict, List], max_depth, depth=0):
    """
    递归注入空间参数
    """
    if max_depth != -1 and depth > max_depth:
        return

    if isinstance(data, Dict):
        if "space_uid" in data and isinstance(data["space_uid"], str) and "bk_biz_id" not in data:
            # 传了 space_uid 的，补充 bk_biz_id
            bk_biz_id = space_uid_to_bk_biz_id(data["space_uid"])
            if bk_biz_id:
                data["bk_biz_id"] = bk_biz_id
        elif "space_uid" not in data and "bk_biz_id" in data and isinstance(data["bk_biz_id"], (str, int)):
            # 传了 bk_biz_id 的，补充 space_uid
            space_uid = bk_biz_id_to_space_uid(data["bk_biz_id"])
            if space_uid:
                data["space_uid"] = space_uid

        for key in data:
            _inject_space_field_recursive(data[key], max_depth, depth + 1)

    elif isinstance(data, List):
        for param in data:
            _inject_space_field_recursive(param, max_depth, depth + 1)


def inject_space_field(data: Union[Dict, List], max_depth=5):
    """
    注入空间参数
    """
    _inject_space_field_recursive(data, max_depth)
    return data


def is_bcs_space(space_uid: str) -> bool:
    """判断是否是bcs类型的空间 ."""
    if not space_uid:
        return False
    space_type, _ = parse_space_uid(space_uid)
    return space_type == SpaceTypeEnum.BCS.value
