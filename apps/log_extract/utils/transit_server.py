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
from dataclasses import dataclass
from django.conf import settings

from apps.api import CCApi


def get_bk_host_id_by_ipv6(bk_cloud_id: int, ip: str) -> int:
    """
    根据 ipv6 获取 bk_host_id
    :param bk_cloud_id: 云区域ID
    :param ip: ipv6
    :return: bk_host_id
    """
    bk_host_id = 0
    if not settings.ENABLE_DHCP:
        return bk_host_id

    # 因为不知道ip是v4还是v6的IP, 所以都查一次
    params = {
        "bk_biz_id": settings.BLUEKING_BK_BIZ_ID,
        "fields": ["bk_host_id"],
        "host_property_filter": {
            "condition": "OR",
            "rules": [
                {
                    "condition": "AND",
                    "rules": [
                        {
                            "field": "bk_cloud_id",
                            "operator": "equal",
                            "value": bk_cloud_id,
                        },
                        {
                            "field": "bk_host_innerip",
                            "operator": "equal",
                            "value": ip,
                        },
                    ],
                },
                {
                    "condition": "AND",
                    "rules": [
                        {
                            "field": "bk_cloud_id",
                            "operator": "equal",
                            "value": bk_cloud_id,
                        },
                        {
                            "field": "bk_host_innerip_v6",
                            "operator": "equal",
                            "value": ip,
                        },
                    ],
                },
            ],
        },
        "page": {"limit": 1, "start": 0},
        "no_request": True,
    }
    result = CCApi.list_biz_hosts(params)
    if not result or not result["info"]:
        return bk_host_id

    return result["info"][0]["bk_host_id"]


@dataclass
class TransitServer(object):
    ip: str
    target_dir: str
    bk_cloud_id: int

    def __post_init__(self):
        self.bk_host_id = get_bk_host_id_by_ipv6(bk_cloud_id=self.bk_cloud_id, ip=self.ip)
