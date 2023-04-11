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

from collections import namedtuple

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

DYNAMIC_GROUP_ID_LIST = ["11c290dc-66e8-11ec-84ba-1e84cfcf753a", "fb40d723-66e7-11ec-84ba-1e84cfcf753a"]
DYNAMIC_GROUP_LIST = [
    {
        "bk_biz_id": 2,
        "id": DYNAMIC_GROUP_ID_LIST[0],
        "name": "test_dynamic_group_set",
        "bk_obj_id": "set",
        "info": {
            "condition": [
                {
                    "bk_obj_id": "set",
                    "condition": [{"field": "bk_set_name", "operator": "$in", "value": ["空闲机池", "蓝鲸平台"]}],
                }
            ]
        },
        "create_user": "admin",
        "modify_user": "admin",
        "create_time": "2021-12-27T07:39:05.805Z",
        "last_time": "2021-12-28T09:04:56.386Z",
    },
    {
        "bk_biz_id": 2,
        "id": DYNAMIC_GROUP_ID_LIST[1],
        "name": "test_dynamic_group_host",
        "bk_obj_id": "host",
        "info": {
            "condition": [
                {
                    "bk_obj_id": "host",
                    "condition": [{"field": "bk_host_innerip", "operator": "$in", "value": ["127.0.0.1", "127.0.0.1"]}],
                }
            ]
        },
        "create_user": "admin",
        "modify_user": "admin",
        "create_time": "2021-12-27T07:38:28.045Z",
        "last_time": "2021-12-29T02:52:31.947Z",
    },
]
DYNAMIC_GROUP_TO_INSTANCE = {
    "fb40d723-66e7-11ec-84ba-1e84cfcf753a": [
        {"bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0, "bk_supplier_account": "0"},
        {"bk_host_innerip": "127.0.0.2", "bk_cloud_id": 0, "bk_supplier_account": "0"},
    ],
    "11c290dc-66e8-11ec-84ba-1e84cfcf753a": [
        {"bk_set_id": 2, "bk_set_name": "空闲机池"},
        {"bk_set_id": 3, "bk_set_name": "蓝鲸平台"},
    ],
}
DYNAMIC_GROUP_TO_INSTANCE_RETURN = {
    "fb40d723-66e7-11ec-84ba-1e84cfcf753a": [
        {"ip": "127.0.0.1", "bk_cloud_id": 0, "bk_supplier_id": "0"},
        {"ip": "127.0.0.2", "bk_cloud_id": 0, "bk_supplier_id": "0"},
    ],
    "11c290dc-66e8-11ec-84ba-1e84cfcf753a": [
        {"bk_inst_id": 2, "bk_obj_id": "set", "bk_set_name": "空闲机池"},
        {"bk_inst_id": 3, "bk_obj_id": "set", "bk_set_name": "蓝鲸平台"},
    ],
}


class NodeInstance:
    bk_obj_id = NODE_LIST[0]["bk_obj_id"]
    bk_inst_id = NODE_LIST[0]["bk_inst_id"]
    bk_biz_id = NODE_LIST[0]["bk_biz_id"]
    bk_inst_name = NODE_LIST[0]["bk_inst_name"]


class HostInstance:
    bk_host_id = HOST_LIST[0]["host"]["bk_host_id"]
    host = HOST_LIST[0]["host"]


NODE_INSTANCE_INFO = (NodeInstance.bk_obj_id, NodeInstance.bk_inst_id)
NODE = namedtuple("Node", ["bk_biz_id", "bk_obj_id", "bk_inst_id", "bk_inst_name"])
NODE_INSTANCE = NODE(NodeInstance.bk_biz_id, NodeInstance.bk_obj_id, NodeInstance.bk_inst_id, NodeInstance.bk_inst_name)
NODE_NAME = "{}|{}".format(str(NodeInstance.bk_obj_id), str(NodeInstance.bk_inst_id))
NODE_MAPPING = {NODE_NAME: {"node_link": [NODE_NAME], "bk_inst_name": NodeInstance.bk_inst_name}}

HOST_LIST_AGENT = [HostInstance.host]
HOST_DETAILS = [{"bk_host_id": HostInstance.bk_host_id}]

AGENT_STATUS = [{"ip": "127.0.0.1", "plat_id": "0", "status": True}]
AGENT_STATUS_RESULT = {
    "bk_obj_id": NodeInstance.bk_obj_id,
    "bk_inst_id": NodeInstance.bk_inst_id,
    "bk_inst_name": NodeInstance.bk_inst_name,
    "count": len(HOST_LIST_AGENT),
    "agent_error_count": 0,
    "bk_biz_id": NodeInstance.bk_biz_id,
    "node_path": NodeInstance.bk_inst_name,
}


class ExecDynamicGroup(object):
    """
    mock CCApi.execute_dynamic_group
    """

    def bulk_request(self, params=None):
        dynamic_group_id = params["id"]
        return DYNAMIC_GROUP_TO_INSTANCE.get(dynamic_group_id, [])


class SearchDynamicGroup(object):
    """
    mock CCApi.search_dynamic_group
    """

    def bulk_request(self, params=None):
        return DYNAMIC_GROUP_LIST


class TestBiz(TestCase):
    def setUp(self) -> None:
        self.biz_handler = BizHandler(bk_biz_id=BK_BIZ_ID)

    @patch("apps.api.CCApi.search_biz_inst_topo", lambda _: BIZ_INST_TOPO)
    @patch("apps.api.CCApi.get_biz_internal_module", lambda _: INNER_MODULES)
    def test_get_node_path(self):
        result = self.biz_handler.get_node_path(node_list=NODE_LIST)
        self.assertEqual(result, GET_NODE_PATH)

    @patch("apps.api.CCApi.execute_dynamic_group", ExecDynamicGroup())
    def test_get_dynamic_group(self):
        result = self.biz_handler.get_dynamic_group(dynamic_group_id_list=DYNAMIC_GROUP_ID_LIST)
        self.assertEqual(result, DYNAMIC_GROUP_TO_INSTANCE_RETURN)

    @patch("apps.api.CCApi.search_dynamic_group", SearchDynamicGroup())
    def test_list_dynamic_group(self):
        result = self.biz_handler.list_dynamic_group()
        self.assertEqual(result["list"], DYNAMIC_GROUP_LIST)

    @patch("apps.api.CCApi.list_biz_hosts.bulk_request", lambda _: HOST_DETAILS)
    def test_batch_get_hosts_by_inst_id(self):
        result = self.biz_handler.batch_get_hosts_by_inst_id(NODE_INSTANCE_INFO)
        self.assertEqual(result, HOST_DETAILS)

    @patch("apps.api.GseApi.get_agent_status", lambda _: AGENT_STATUS)
    def test_batch_get_agent_status(self):
        result = self.biz_handler.batch_get_agent_status((HOST_LIST_AGENT, NODE_INSTANCE, NODE_MAPPING))
        self.assertEqual(result, AGENT_STATUS_RESULT)
