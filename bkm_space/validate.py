# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from bkm_space.api import SpaceApi
from bkm_space.define import SpaceTypeEnum
from bkm_space.errors import NoRelatedResourceError
from bkm_space.utils import bk_biz_id_to_space_uid


def validate_bk_biz_id(bk_biz_id: int) -> int:
    """
    注入业务id校验
    :return:
    """
    # 业务id为正数，表示空间类型是bkcc，可以调用cmdb相关接口
    bk_biz_id = int(bk_biz_id)
    if bk_biz_id > 0:
        return bk_biz_id
    # 业务id为负数，需要获取空间关联的业务id替换
    space_uid = bk_biz_id_to_space_uid(bk_biz_id)
    space = SpaceApi.get_related_space(space_uid, SpaceTypeEnum.BKCC.value)
    if space:
        return space.bk_biz_id
    # 无业务关联的空间，不允许查询cmdb相关接口
    # 当前抛出异常
    raise NoRelatedResourceError(f"当前空间{space_uid}无关联{SpaceTypeEnum.BKCC.value}资源")
