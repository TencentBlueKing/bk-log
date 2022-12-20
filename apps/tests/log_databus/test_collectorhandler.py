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
import copy
from unittest.mock import patch

from django.test import TestCase

from apps.exceptions import ApiResultError
from apps.log_databus.constants import LogPluginInfo
from apps.log_databus.handlers.collector import CollectorHandler

BK_DATA_ID = 1
BK_DATA_NAME = "2_log_test_collector"
TABLE_ID = "2_log.test_table"
SUBSCRIPTION_ID = 2
TASK_ID = 3
NEW_TASK_ID = 4
LAST_TASK_ID = 5
PARAMS = {
    "bk_biz_id": 706,
    "collector_config_name": "采集项名称",
    "collector_config_name_en": "test_collector",
    "collector_scenario_id": "row",
    "category_id": "application",
    "target_object_type": "HOST",
    "target_node_type": "TOPO",
    "target_nodes": [{"bk_inst_id": 33, "bk_obj_id": "module"}],
    "data_encoding": "UTF-8",
    "bk_data_name": "abc",
    "description": "这是一个描述",
    "params": {
        "paths": ["/log/abc"],
        "conditions": {
            "type": "match",
            "match_type": "include",
            "match_content": "delete",
            "separator": "|",
            "separator_filters": [
                {"fieldindex": 1, "word": "val1", "op": "=", "logic_op": "or"},
                {"fieldindex": 2, "word": "val2", "op": "=", "logic_op": "or"},
            ],
        },
        "tail_files": True,
        "ignore_older": 1,
        "max_bytes": 1,
    },
    "storage_cluster_id": "default",
    "storage_expires": 1,
}

PART_FAILED_INSTANCE_DATA = {
    "instances": [
        {
            "status": "FAILED",
            "host_statuses": [
                {"status": "UNKNOWN", "version": "3.0.10", "name": "unifytlogc"},
                {"status": "UNKNOWN", "version": "3.0.10", "name": "unifytlogc"},
            ],
            "running_task": None,
            "instance_id": "host|instance|host|127.0.0.1-0-0",
            "create_time": "2019-09-19T20:32:19.957883",
            "instance_info": {
                "host": {
                    "bk_host_name": "rbtnode1",
                    "bk_supplier_account": "0",
                    "bk_cloud_id": [
                        {
                            "bk_obj_name": "",
                            "id": "0",
                            "bk_obj_id": "plat",
                            "bk_obj_icon": "",
                            "bk_inst_id": 0,
                            "bk_inst_name": "default area",
                        }
                    ],
                    "bk_host_innerip": "127.0.0.1",
                },
                "service": {},
            },
        },
        {
            "status": "SUCCESS",
            "host_statuses": [
                {"status": "RUNNING", "version": "3.0.10", "name": "unifytlogc"},
                {"status": "RUNNING", "version": "3.0.10", "name": "unifytlogc"},
            ],
            "running_task": None,
            "instance_id": "host|instance|host|127.0.0.1-0-0",
            "create_time": "2019-09-19T20:32:19.957883",
            "instance_info": {
                "host": {
                    "bk_host_name": "rbtnode1",
                    "bk_supplier_account": "0",
                    "bk_cloud_id": [
                        {
                            "bk_obj_name": "",
                            "id": "0",
                            "bk_obj_id": "plat",
                            "bk_obj_icon": "",
                            "bk_inst_id": 0,
                            "bk_inst_name": "default area",
                        }
                    ],
                    "bk_host_innerip": "127.0.0.1",
                },
                "service": {},
            },
        },
    ],
    "subscription_id": SUBSCRIPTION_ID,
}

CONFIG_DATA = {
    "data_id_config": {"option": {"encoding": "encoding data"}, "data_name": "data name"},
    "result_table_config": "",
    "subscription_config": [
        {
            "steps": [
                {
                    "config": {"plugin_name": LogPluginInfo.NAME, "plugin_version": LogPluginInfo.VERSION},
                    "type": "PLUGIN",
                    "id": LogPluginInfo.NAME,
                    "params": {
                        "context": {
                            "dataid": BK_DATA_ID,
                            "local": [
                                {
                                    "paths": ["testlogic_op"],
                                    "delimiter": "|",
                                    "filters": [
                                        {"conditions": [{"index": 1, "key": "val1", "op": "="}]},
                                        {"conditions": [{"index": 1, "key": "val1", "op": "="}]},
                                    ],
                                    "encoding": "UTF-8",
                                }
                            ],
                        }
                    },
                }
            ]
        }
    ],
}


class CCModuleTest(object):
    """
    mock CCApi.search_module
    """

    def bulk_request(self, params=None):
        return []


class CCBizHostsTest(object):
    """
    mock CCApi.list_biz_hosts
    """

    def bulk_request(self, params=None):
        return []


class CCSetTest(object):
    """
    mock CCApi.list_biz_hosts
    """

    def bulk_request(self, params=None):
        return []


class CCBizHostsFilterTest(object):
    """
    mock CCApi.list_biz_hosts
    """

    def bulk_request(self, params=None):
        return [
            {
                "bk_os_name": "",
                "bk_host_id": 2000006651,
                "bk_cloud_id": 0,
                "bk_supplier_account": "tencent",
                "bk_host_innerip": "127.0.0.2",
                "bk_os_type": "1",
            },
        ]


FILTER_ILLEGAL_IPS_BIZ_ID = 215
FILTER_ILLEGAL_IPS_IP_LIST = ["127.0.0.1"]


def subscription_statistic(params):
    return [
        {
            "subscription_id": SUBSCRIPTION_ID,
            "status": [
                {"status": "SUCCESS", "count": 0},
                {"status": "PENDING", "count": 0},
                {"status": "FAILED", "count": 0},
                {"status": "RUNNING", "count": 0},
            ],
            "versions": [],
            "instances": 0,
        }
    ]


def get_data_id(x):
    if x["data_name"] != BK_DATA_NAME:
        raise ApiResultError()
    return {"data_name": BK_DATA_NAME, "bk_data_id": BK_DATA_ID}


@patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id.delay", return_value=None)
class TestCollectorHandler(TestCase):
    @staticmethod
    @patch(
        "apps.api.TransferApi.get_data_id", get_data_id,
    )
    @patch(
        "apps.api.TransferApi.get_result_table",
        lambda x: {"result_table_id": TABLE_ID} if x["table_id"] == TABLE_ID else {},
    )
    @patch("apps.api.TransferApi.create_data_id", lambda _: {"bk_data_id": BK_DATA_ID})
    @patch("apps.api.NodeApi.create_subscription", lambda _: {"subscription_id": SUBSCRIPTION_ID})
    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": TASK_ID})
    def create(params=None, *args, **kwargs):
        """
        创建 CollectorHandler实例对象，并创建一个采集配置
        """

        if params:
            result = CollectorHandler().update_or_create(params=params)
        else:
            params = copy.deepcopy(PARAMS)
            params["params"]["conditions"]["type"] = "separator"
            result = CollectorHandler().update_or_create(params=params)
        return params, result

    @patch("apps.api.NodeApi.switch_subscription", lambda _: {})
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    @patch("apps.api.NodeApi.subscription_statistic", subscription_statistic)
    def test_update_or_create(self, *args, **kwargs):
        """
        测试'创建采集配置'函数 CollectorHandler.update_or_create
        """
        params, result = self.create()

        self.assertEqual(result["bk_data_id"], BK_DATA_ID)
        self.assertEqual(result["collector_config_name"], params["collector_config_name"])
        self.assertEqual(result["subscription_id"], SUBSCRIPTION_ID)
        self.assertEqual(result["task_id_list"], [str(TASK_ID)])

    @patch("apps.utils.thread.MultiExecuteFunc.append")
    @patch("apps.utils.thread.MultiExecuteFunc.run")
    @patch("apps.api.NodeApi.switch_subscription", lambda _: {})
    @patch("apps.api.CCApi.search_biz_inst_topo", lambda _: [])
    @patch("apps.api.CCApi.search_module", CCModuleTest())
    @patch("apps.api.CCApi.search_set", CCSetTest())
    @patch("apps.api.CCApi.list_biz_hosts", CCBizHostsTest())
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    def test_retrieve(self, mock_run, mock_append, *args, **kwargs):
        """
        测试'获取采集配置'函数 CollectorHandler.retrieve
        """
        _, result = self.create()

        mock_append.return_value = ""
        mock_run.return_value = CONFIG_DATA

        collector_config_id = result["collector_config_id"]
        collector = CollectorHandler(collector_config_id=collector_config_id)

        res = collector.retrieve()

        self.assertEqual(res.get("data_encoding"), "UTF-8")
        self.assertIsNone(res.get("storage_cluster_id"))
        self.assertIsNone(res.get("retention"))
        self.assertEqual(res.get("collector_config_id"), collector_config_id)
        self.assertEqual(res.get("collector_scenario_id"), "row")

    @patch("apps.api.CCApi.list_biz_hosts", CCBizHostsFilterTest())
    def test_filter_illegal_ips(self, *args, **kwargs):
        self.assertEqual(
            CollectorHandler._filter_illegal_ip_and_host_id(
                bk_biz_id=FILTER_ILLEGAL_IPS_BIZ_ID, ips=FILTER_ILLEGAL_IPS_IP_LIST
            )[0],
            ["127.0.0.1"],
        )
