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
"""

from django.test import TestCase
from unittest.mock import patch

from apps.log_search.handlers.biz import BizHandler

BIZ_INST_TOPO = [
    {
        "host_count": 0,
        "default": 0,
        "bk_obj_name": "业务",
        "bk_obj_id": "biz",
        "child": [
            {
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "集群",
                "bk_obj_id": "set",
                "child": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [],
                        "bk_inst_id": 2000000991,
                        "bk_inst_name": "linux",
                    }
                ],
                "bk_inst_id": 2000000943,
                "bk_inst_name": "linux01",
            }
        ],
        "bk_inst_id": 215,
        "bk_inst_name": "功夫西游",
    }
]

INNER_MODULES = {
    "bk_set_id": 2000000942,
    "module": [
        {"default": 3, "bk_module_name": "待回收", "bk_module_id": 2000000990, "host_apply_enabled": False},
        {"default": 2, "bk_module_name": "故障机", "bk_module_id": 2000000989, "host_apply_enabled": False},
        {"default": 1, "bk_module_name": "空闲机", "bk_module_id": 2000000988, "host_apply_enabled": False},
    ],
    "bk_set_name": "空闲机池",
}

BK_BIZ_ID = 215

NODE_LIST = [{"bk_biz_id": 215, "bk_inst_id": 2000000991, "bk_inst_name": "linux", "bk_obj_id": "module"}]

GET_NODE_PATH = {
    (215, "module", 2000000991): {
        "bk_obj_id": "module",
        "bk_inst_id": 2000000991,
        "bk_inst_name": "linux",
        "bk_biz_id": 215,
        "node_path": "功夫西游/linux01/linux",
    }
}

HOST_LIST = [
    {
        "topo": [
            {
                "bk_set_id": 2000001069,
                "module": [{"bk_module_name": "windows", "bk_module_id": 2000001134}],
                "bk_set_name": "windows",
            }
        ],
        "host": {
            "bk_os_name": "",
            "bk_host_id": 2000000101,
            "bk_cloud_id": 0,
            "bk_supplier_account": "tencent",
            "bk_host_innerip": "127.0.0.1",
            "bk_os_type": "2",
        },
    },
    {
        "topo": [
            {
                "bk_set_id": 2000001069,
                "module": [{"bk_module_name": "windows", "bk_module_id": 2000001134}],
                "bk_set_name": "windows",
            }
        ],
        "host": {
            "bk_os_name": "",
            "bk_host_id": 2000000101,
            "bk_cloud_id": 0,
            "bk_supplier_account": "tencent",
            "bk_host_innerip": "",
            "bk_os_type": "2",
        },
    },
    {
        "topo": [
            {
                "bk_set_id": 2000001069,
                "module": [{"bk_module_name": "windows", "bk_module_id": 2000001134}],
                "bk_set_name": "windows",
            }
        ],
        "host": {
            "bk_os_name": "",
            "bk_host_id": 2000000101,
            "bk_cloud_id": 0,
            "bk_supplier_account": "tencent",
            "bk_host_innerip": "127.0.0.1,127.0.0.2",
            "bk_os_type": "2",
        },
    },
]

DST_HOST_LIST = [
    {
        "topo": [
            {
                "bk_set_id": 2000001069,
                "module": [{"bk_module_name": "windows", "bk_module_id": 2000001134}],
                "bk_set_name": "windows",
            }
        ],
        "host": {
            "bk_os_name": "",
            "bk_host_id": 2000000101,
            "bk_cloud_id": 0,
            "bk_supplier_account": "tencent",
            "bk_host_innerip": "127.0.0.1",
            "bk_os_type": "2",
        },
    },
    {
        "topo": [
            {
                "bk_set_id": 2000001069,
                "module": [{"bk_module_name": "windows", "bk_module_id": 2000001134}],
                "bk_set_name": "windows",
            }
        ],
        "host": {
            "bk_os_name": "",
            "bk_host_id": 2000000101,
            "bk_cloud_id": 0,
            "bk_supplier_account": "tencent",
            "bk_host_innerip": "127.0.0.1",
            "bk_os_type": "2",
        },
    },
]


class TestBiz(TestCase):
    def setUp(self) -> None:
        self.biz_handler = BizHandler(bk_biz_id=BK_BIZ_ID)

    @patch("apps.api.CCApi.search_biz_inst_topo", lambda _: BIZ_INST_TOPO)
    @patch("apps.api.CCApi.get_biz_internal_module", lambda _: INNER_MODULES)
    def test_get_node_path(self):
        result = self.biz_handler.get_node_path(node_list=NODE_LIST)
        self.assertEqual(result, GET_NODE_PATH)
