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
from django.test import TestCase, override_settings

from apps.log_search.models import Space
from apps.log_databus.exceptions import CollectorConfigNotExistException
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.constants import LogPluginInfo, WorkLoadType
from apps.exceptions import ApiRequestError, ApiResultError
from bkm_space.define import SpaceTypeEnum
from .test_collectorhandler import TestCollectorHandler, get_data_id
from ...log_databus.serializers import CollectorCreateSerializer
from ...utils.drf import custom_params_valid

BK_DATA_ID = 1
BK_DATA_NAME = "2_log_test_collector"
TABLE_ID = "2_log.test_collector"
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
DELETE_MSG = {"result": True}
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
                    "bk_host_id": 1,
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
                    "bk_host_id": 1,
                },
                "service": {},
            },
        },
    ],
    "subscription_id": SUBSCRIPTION_ID,
}

FAILED_INSTANCE_DATA = {
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
        }
    ],
    "subscription_id": SUBSCRIPTION_ID,
}

SUCCESS_INSTANCE_DATA = {
    "instances": [
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
        }
    ],
    "subscription_id": SUBSCRIPTION_ID,
}

RUNNING_INSTANCE_DATA = {
    "instances": [
        {
            "status": "RUNNING",
            "host_statuses": [
                {"status": "PENDING", "version": "3.0.10", "name": "unifytlogc"},
                {"status": "PENDING", "version": "3.0.10", "name": "unifytlogc"},
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
        }
    ],
    "subscription_id": SUBSCRIPTION_ID,
}

INSTANCE_DATA_RETURN = {
    "FAILED": [
        {
            "status": "FAILED",
            "ip": "127.0.0.1",
            "bk_cloud_id": 0,
            "instance_id": "host|instance|host|127.0.0.1-0-0",
            "instance_name": "127.0.0.1",
            "plugin_version": "3.0.10",
            "bk_supplier_id": "0",
            "create_time": "2019-09-19T20:32:19.957883",
        }
    ],
    "SUCCESS": [
        {
            "status": "SUCCESS",
            "ip": "127.0.0.1",
            "bk_cloud_id": 0,
            "instance_id": "host|instance|host|127.0.0.1-0-0",
            "instance_name": "127.0.0.1",
            "plugin_version": "3.0.10",
            "bk_supplier_id": "0",
            "create_time": "2019-09-19T20:32:19.957883",
        }
    ],
}
STATUS_DATA = [PART_FAILED_INSTANCE_DATA]
STATUS_DATA_RETURN = [
    {
        "status": "FAILED",
        "status_name": "失败",
        "ip": "127.0.0.1",
        "cloud_id": 0,
        "instance_id": "host|instance|host|127.0.0.1-0-0",
        "instance_name": "127.0.0.1",
        "plugin_name": "unifytlogc",
        "plugin_version": "3.0.10",
        "bk_supplier_id": "0",
        "create_time": "2019-09-19T20:32:19.957883",
        "host_id": 1,
        "ipv6": "",
        "host_name": "rbtnode1",
    },
    {
        "status": "SUCCESS",
        "status_name": "正常",
        "ip": "127.0.0.1",
        "cloud_id": 0,
        "ipv6": "",
        "host_name": "rbtnode1",
        "instance_id": "host|instance|host|127.0.0.1-0-0",
        "instance_name": "127.0.0.1",
        "plugin_name": "unifytlogc",
        "plugin_version": "3.0.10",
        "bk_supplier_id": "0",
        "create_time": "2019-09-19T20:32:19.957883",
        "host_id": 1,
    },
]
TOPO_TREE = [
    {
        "host_count": 0,
        "default": 0,
        "bk_obj_name": "业务",
        "bk_obj_id": "biz",
        "service_instance_count": 0,
        "child": [
            {
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "test",
                "bk_obj_id": "test",
                "service_instance_count": 0,
                "child": [],
                "service_template_id": 0,
                "bk_inst_id": 4,
                "bk_inst_name": "test",
            }
        ],
        "service_template_id": 0,
        "bk_inst_id": 4,
        "bk_inst_name": "日志平台-测试1",
    }
]
TOPO_TREE_RETURN = {
    "biz|4": {
        "host_count": 0,
        "default": 0,
        "bk_obj_name": "业务",
        "bk_obj_id": "biz",
        "service_instance_count": 0,
        "child": [
            {
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "test",
                "bk_obj_id": "test",
                "service_instance_count": 0,
                "child": [],
                "service_template_id": 0,
                "bk_inst_id": 4,
                "bk_inst_name": "test",
                "node_link": ["biz|4", "test|4"],
            }
        ],
        "service_template_id": 0,
        "bk_inst_id": 4,
        "bk_inst_name": "日志平台-测试1",
        "node_link": ["biz|4"],
    },
    "test|4": {
        "host_count": 0,
        "default": 0,
        "bk_obj_name": "test",
        "bk_obj_id": "test",
        "service_instance_count": 0,
        "child": [],
        "service_template_id": 0,
        "bk_inst_id": 4,
        "bk_inst_name": "test",
        "node_link": ["biz|4", "test|4"],
    },
}
SEARCH_HOST_DATA = {
    "count": 3,
    "info": [
        {
            "host": {
                "bk_cpu": 8,
                "bk_isp_name": "1",
                "bk_os_name": "linux centos",
                "bk_province_name": "440000",
                "bk_host_id": 1,
                "import_from": "2",
                "bk_os_version": "7.4.1708",
                "bk_disk": 639,
                "operator": "",
                "docker_server_version": "1.12.4",
                "create_time": "2019-05-17T12:40:29.212+08:00",
                "bk_mem": 32012,
                "bk_host_name": "VM_1_10_centos",
                "last_time": "2019-09-11T11:27:37.318+08:00",
                "bk_host_innerip": "127.0.0.1",
                "bk_comment": "",
                "docker_client_version": "1.12.4",
                "bk_os_bit": "64-bit",
                "bk_outer_mac": "",
                "bk_asset_id": "",
                "bk_service_term": "null",
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
                "bk_sla": "null",
                "bk_cpu_mhz": 2499,
                "bk_host_outerip": "",
                "bk_state_name": "CN",
                "bk_os_type": "1",
                "bk_mac": "52:54:00:0a:ac:26",
                "bk_bak_operator": "",
                "bk_supplier_account": "0",
                "bk_sn": "",
                "bk_cpu_module": "Intel(R) Xeon(R) Gold 61xx CPU",
            },
            "set": [],
            "biz": [
                {
                    "bk_biz_id": 2,
                    "language": "1",
                    "life_cycle": "2",
                    "bk_biz_developer": "",
                    "bk_biz_maintainer": "admin,jx",
                    "bk_biz_tester": "",
                    "time_zone": "Asia/Shanghai",
                    "default": 0,
                    "create_time": "2019-05-17T12:38:29.549+08:00",
                    "bk_biz_productor": "admin",
                    "bk_supplier_account": "0",
                    "operator": "",
                    "bk_biz_name": "蓝鲸",
                    "last_time": "2019-09-29T10:28:37.748+08:00",
                    "bk_supplier_id": 0,
                }
            ],
            "module": [],
        },
        {
            "host": {
                "bk_cpu": 8,
                "bk_isp_name": "2",
                "bk_os_name": "linux centos",
                "bk_province_name": "440000",
                "bk_host_id": 2,
                "import_from": "2",
                "bk_os_version": "7.4.1708",
                "bk_disk": 147,
                "operator": "",
                "docker_server_version": "",
                "create_time": "2019-05-17T12:40:33.671+08:00",
                "bk_mem": 32012,
                "bk_host_name": "VM_1_11_centos",
                "last_time": "2019-05-17T15:53:41.676+08:00",
                "bk_host_innerip": "127.0.0.1",
                "bk_comment": "",
                "docker_client_version": "",
                "bk_os_bit": "64-bit",
                "bk_outer_mac": "",
                "bk_asset_id": "",
                "bk_service_term": "null",
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
                "bk_sla": "null",
                "bk_cpu_mhz": 1999,
                "bk_host_outerip": "",
                "bk_state_name": "CN",
                "bk_os_type": "1",
                "bk_mac": "52:54:00:f8:42:96",
                "bk_bak_operator": "",
                "bk_supplier_account": "0",
                "bk_sn": "",
                "bk_cpu_module": "AMD EPYC Processor",
            },
            "set": [],
            "biz": [
                {
                    "bk_biz_id": 2,
                    "language": "1",
                    "life_cycle": "2",
                    "bk_biz_developer": "",
                    "bk_biz_maintainer": "admin,jx",
                    "bk_biz_tester": "",
                    "time_zone": "Asia/Shanghai",
                    "default": 0,
                    "create_time": "2019-05-17T12:38:29.549+08:00",
                    "bk_biz_productor": "admin",
                    "bk_supplier_account": "0",
                    "operator": "",
                    "bk_biz_name": "蓝鲸",
                    "last_time": "2019-09-29T10:28:37.748+08:00",
                    "bk_supplier_id": 0,
                }
            ],
            "module": [],
        },
        {
            "host": {
                "bk_cpu": 8,
                "bk_isp_name": "3",
                "bk_os_name": "linux centos",
                "bk_province_name": "440000",
                "bk_host_id": 3,
                "import_from": "2",
                "bk_os_version": "7.4.1708",
                "bk_disk": 639,
                "operator": "",
                "docker_server_version": "1.12.4",
                "create_time": "2019-05-17T12:40:37.473+08:00",
                "bk_mem": 32012,
                "bk_host_name": "rbtnode1",
                "last_time": "2019-09-11T11:26:43.887+08:00",
                "bk_host_innerip": "127.0.0.1",
                "bk_comment": "",
                "docker_client_version": "1.12.4",
                "bk_os_bit": "64-bit",
                "bk_outer_mac": "",
                "bk_asset_id": "",
                "bk_service_term": "null",
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
                "bk_sla": "null",
                "bk_cpu_mhz": 1999,
                "bk_host_outerip": "",
                "bk_state_name": "CN",
                "bk_os_type": "1",
                "bk_mac": "52:54:00:f2:b3:a6",
                "bk_bak_operator": "",
                "bk_supplier_account": "0",
                "bk_sn": "",
                "bk_cpu_module": "AMD EPYC Processor",
            },
            "set": [],
            "biz": [
                {
                    "bk_biz_id": 2,
                    "language": "1",
                    "life_cycle": "2",
                    "bk_biz_developer": "",
                    "bk_biz_maintainer": "admin,jx",
                    "bk_biz_tester": "",
                    "time_zone": "Asia/Shanghai",
                    "default": 0,
                    "create_time": "2019-05-17T12:38:29.549+08:00",
                    "bk_biz_productor": "admin",
                    "bk_supplier_account": "0",
                    "operator": "",
                    "bk_biz_name": "蓝鲸",
                    "last_time": "2019-09-29T10:28:37.748+08:00",
                    "bk_supplier_id": 0,
                }
            ],
            "module": [],
        },
    ],
}
TASK_DETAIL_DATA = {
    "status": "FAILED",
    "task_id": 24626,
    "finish_time": "null",
    "start_time": "2019-09-19 15:07:13",
    "instance_id": "host|instance|host|127.0.0.1-0-0",
    "pipeline_id": "0242b9eebb0b355aa4f9d6e41acd8d68",
    "create_time": "2019-09-19 15:07:13",
    "steps": [
        {
            "status": "FAILED",
            "target_hosts": [
                {
                    "status": "FAILED",
                    "pipeline_id": "cf9b9eb54bf33e1799294e9ce2e2d3ba",
                    "create_time": "2019-09-19 15:07:13",
                    "finish_time": "null",
                    "start_time": "2019-09-19 15:07:14",
                    "node_name": "[unifytlogc] 下发插件配置 0:127.0.0.1",
                    "sub_steps": [
                        {
                            "status": "SUCCESS",
                            "inputs": {"status": "UNKNOWN", "host_status_id": 105981, "_loop": 0},
                            "log": "",
                            "index": 0,
                            "finish_time": "2019-09-19 15:07:14",
                            "start_time": "2019-09-19 15:07:14",
                            "node_name": "更新插件部署状态",
                            "pipeline_id": "efe41658ac4d3c0b99dafa134f8e6549",
                            "create_time": "2019-09-19 15:07:13",
                            "ex_data": "null",
                        },
                        {
                            "status": "SUCCESS",
                            "inputs": {
                                "file_params": [],
                                "host_status_id": 105981,
                                "_loop": 0,
                                "ip_list": [{"ip": "127.0.0.1", "bk_supplier_id": "0", "bk_cloud_id": "0"}],
                                "config_instance_ids": [],
                                "job_client": {"username": "admin", "bk_biz_id": "2", "os_type": "linux"},
                                "subscription_step_id": 46813,
                            },
                            "log": "[2019-09-19 15:07:14 INFO] JobPushMultipleConfigFileService called with params",
                            "index": 1,
                            "finish_time": "2019-09-19 15:07:17",
                            "start_time": "2019-09-19 15:07:14",
                            "node_name": "渲染并下发配置",
                            "pipeline_id": "327b1793e3c3300ba683bbfe57985aa6",
                            "create_time": "2019-09-19 15:07:13",
                            "ex_data": "null",
                        },
                        {
                            "status": "FAILED",
                            "inputs": {
                                "control": {
                                    "stop_cmd": "./stop.sh unifytlogc",
                                    "health_cmd": "./unifytlogc -z",
                                    "reload_cmd": "./reload.sh unifytlogc",
                                    "start_cmd": "./start.sh unifytlogc",
                                    "version_cmd": "./unifytlogc -v",
                                    "kill_cmd": "./stop.sh unifytlogc",
                                    "restart_cmd": "./restart.sh unifytlogc",
                                },
                                "exe_name": "null",
                                "_loop": 0,
                                "setup_path": "/usr/local/gse/plugins/bin",
                                "pid_path": "/var/run/gse/unifytlogc.pid",
                                "proc_name": "unifytlogc",
                                "hosts": [{"ip": "127.0.0.1", "bk_cloud_id": 0, "bk_supplier_id": 0}],
                                "gse_client": {"username": "admin", "os_type": "linux"},
                            },
                            "log": "[2019-09-19 15:07:17 INFO] GSE register process success",
                            "index": 2,
                            "finish_time": "2019-09-19 15:07:25",
                            "start_time": "2019-09-19 15:07:17",
                            "node_name": "重载插件进程",
                            "pipeline_id": "ecb56b3d98473b7f858919d776c2d58e",
                            "create_time": "2019-09-19 15:07:13",
                            "ex_data": "以下主机操作进程失败：127.0.0.1",
                        },
                        {
                            "status": "PENDING",
                            "inputs": "null",
                            "log": "",
                            "index": 3,
                            "finish_time": "null",
                            "outputs": "null",
                            "start_time": "null",
                            "node_name": "更新插件部署状态",
                            "pipeline_id": "aaf49227ba8736169ff8fafa5e7cfe42",
                            "create_time": "null",
                            "ex_data": "null",
                        },
                    ],
                }
            ],
            "finish_time": "null",
            "start_time": "2019-09-19 15:07:13",
            "node_name": "[unifytlogc] 下发插件配置",
            "pipeline_id": "1c5278d835503842b2270e7554b145e0",
            "create_time": "2019-09-19 15:07:13",
            "action": "INSTALL",
            "type": "PLUGIN",
            "id": "unifytlogc",
            "extra_info": {},
        }
    ],
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
            "bk_host_id": 1,
        },
        "service": {},
    },
}

TASK_STATUS_DATA = [
    {
        "status": "FAILED",
        "task_id": 24516,
        "finish_time": None,
        "start_time": "2019-09-17 19:23:03",
        "instance_id": "host|instance|host|127.0.0.1-0-0",
        "pipeline_id": "b087abf3072b3a85a4b00e7a1c3d90c2",
        "create_time": "2019-09-17 19:23:02",
        "steps": [
            {
                "status": "FAILED",
                "target_hosts": [
                    {
                        "status": "FAILED",
                        "pipeline_id": "ca20fc59e7a138258f4e22beff18aaec",
                        "create_time": "2019-09-17 19:23:02",
                        "finish_time": None,
                        "start_time": "2019-09-17 19:23:04",
                        "node_name": "[unifytlogc] 下发插件配置 0:127.0.0.1",
                        "sub_steps": [
                            {
                                "status": "SUCCESS",
                                "pipeline_id": "82fbf2706772353b8f59aa61f9084022",
                                "create_time": "2019-09-17 19:23:02",
                                "index": 0,
                                "finish_time": "2019-09-17 19:23:04",
                                "start_time": "2019-09-17 19:23:04",
                                "node_name": "更新插件部署状态",
                            },
                            {
                                "status": "SUCCESS",
                                "pipeline_id": "5d42f91ef09438729c67fa3add82778a",
                                "create_time": "2019-09-17 19:23:02",
                                "index": 1,
                                "finish_time": "2019-09-17 19:23:07",
                                "start_time": "2019-09-17 19:23:04",
                                "node_name": "渲染并下发配置",
                            },
                            {
                                "status": "FAILED",
                                "pipeline_id": "da862b51b1c43a2f8876f6c3e311d779",
                                "create_time": "2019-09-17 19:23:02",
                                "index": 2,
                                "finish_time": "2019-09-17 19:23:16",
                                "start_time": "2019-09-17 19:23:07",
                                "node_name": "重载插件进程",
                            },
                            {
                                "status": "PENDING",
                                "pipeline_id": "9ac0acd362ac388cb1e1cf34635c5991",
                                "create_time": None,
                                "index": 3,
                                "finish_time": None,
                                "start_time": None,
                                "node_name": "更新插件部署状态",
                            },
                        ],
                    }
                ],
                "finish_time": None,
                "start_time": "2019-09-17 19:23:03",
                "node_name": "[unifytlogc] 下发插件配置",
                "pipeline_id": "874164bdd0a7355fb939533d34d063e3",
                "create_time": "2019-09-17 19:23:02",
                "action": "INSTALL",
                "type": "PLUGIN",
                "id": "unifytlogc",
                "extra_info": {},
            }
        ],
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
                "bk_host_id": 1,
            },
            "service": {},
        },
    }
]
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
FAILED_SUBSCRIPTION_STATUS = [{"instance_id": "xxx", "status": "FAILED"}]


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


BK_BIZ_ID = -200
SPACE_ID = "1ce0ae294d63478ea46a2a1772acd8a7"
SPACE_UID = "bcs__{}".format(SPACE_ID)
BCS_CLUSTER_ID = "BCS-K8S-10000"
PROJECTS = [
    {
        "approval_status": 2,
        "approval_time": "2021-01-01T00:00:00+08:00",
        "approver": "",
        "bg_id": 1,
        "bg_name": "test-bg",
        "cc_app_id": 0,
        "center_id": 1,
        "center_name": "test-center-name",
        "created_at": "2021-01-01T00:00:00+08:00",
        "creator": "admin",
        "data_id": 0,
        "deploy_type": "[0]",
        "dept_id": 1,
        "dept_name": "test-dept-name",
        "description": "testproject",
        "english_name": "testproject",
        "extra": {},
        "is_offlined": False,
        "is_secrecy": False,
        "kind": 0,
        "logo_addr": "",
        "project_id": "1ce0ae294d63478ea46a2a1772acd8a7",
        "project_name": "testproject",
        "project_type": 1,
        "remark": "",
        "updated_at": "2021-01-01T00:00:00+08:00",
        "updater": "",
        "use_bk": False,
    }
]


PROJECT_CLUSTER_LIST = [
    {
        "clusterID": BCS_CLUSTER_ID,
        "clusterName": "公共集群测试",
        "federationClusterID": "",
        "provider": "provider",
        "region": "ap-region",
        "vpcID": "vpc-123",
        "projectID": "1ce0ae294d63478ea46a2a1772acd8a7",
        "businessID": "2",
        "environment": "stag",
        "engineType": "k8s",
        "isExclusive": True,
        "clusterType": "single",
        "labels": {},
        "creator": "admin",
        "createTime": "2021-01-01T00:00:00+08:00",
        "updateTime": "2021-01-01T00:00:00+08:00",
        "bcsAddons": {},
        "extraAddons": {},
        "systemID": "cls-system-id",
        "manageType": "INDEPENDENT_CLUSTER",
        "status": "RUNNING",
        "is_shared": True,
    }
]


SHARED_CLUSTERS_NS = {
    "count": 2,
    "results": [
        {
            "cluster_id": BCS_CLUSTER_ID,
            "created_at": "2021-01-01T00:00:00+08:00",
            "creator": "admin",
            "description": "",
            "env_type": "dev",
            "has_image_secret": False,
            "id": 2,
            "name": "test-cluster-share-test1",
            "project_id": "1ce0ae294d63478ea46a2a1772acd8a7",
            "status": "",
            "updated_at": "2021-01-01T00:00:00+08:00",
        },
        {
            "cluster_id": BCS_CLUSTER_ID,
            "created_at": "2021-01-01T00:00:00+08:00",
            "creator": "admin",
            "description": "",
            "env_type": "dev",
            "has_image_secret": False,
            "id": 3,
            "name": "test-cluster-share-test2",
            "project_id": "1ce0ae294d63478ea46a2a1772acd8a7",
            "status": "",
            "updated_at": "2021-01-01T00:00:00+08:00",
        },
    ],
}


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


@patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id.delay", return_value=None)
class TestCollector(TestCase):
    def setUp(self) -> None:
        Space.objects.create(
            space_uid=SPACE_UID,
            bk_biz_id=BK_BIZ_ID,
            space_type_id=SpaceTypeEnum.BCS.value,
            space_type_name="容器项目",
            space_id=SPACE_ID,
            space_name="测试容器日志项目",
            space_code="testproject",
        )

    @patch(
        "apps.api.TransferApi.get_data_id",
        get_data_id,
    )
    @patch(
        "apps.api.TransferApi.get_result_table",
        lambda x: {"result_table_id": TABLE_ID} if x["table_id"] == TABLE_ID else {},
    )
    @patch("apps.api.TransferApi.create_data_id", lambda _: {"bk_data_id": BK_DATA_ID})
    @patch("apps.api.TransferApi.create_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.NodeApi.create_subscription", lambda _: {"subscription_id": SUBSCRIPTION_ID})
    @patch("apps.api.NodeApi.subscription_statistic", subscription_statistic)
    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": TASK_ID})
    @patch("apps.api.NodeApi.switch_subscription", lambda _: {})
    @patch("apps.api.NodeApi.check_subscription_task_ready", lambda _: True)
    @patch("apps.api.TransferApi.modify_data_id", lambda _: {"bk_data_id": BK_DATA_ID})
    @patch("apps.api.CCApi.search_module", CCModuleTest())
    @patch("apps.api.CCApi.list_biz_hosts", CCBizHostsTest())
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    @patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id.delay", return_value=None)
    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_create(self, *args, **kwargs):
        params = copy.deepcopy(PARAMS)
        params = custom_params_valid(serializer=CollectorCreateSerializer, params=params)

        params["params"]["conditions"]["type"] = "separator"
        result = CollectorHandler().update_or_create(params)
        self.assertEqual(result["bk_data_id"], BK_DATA_ID)
        self.assertEqual(result["collector_config_name"], params["collector_config_name"])
        self.assertEqual(result["subscription_id"], SUBSCRIPTION_ID)
        self.assertEqual(result["task_id_list"], [str(TASK_ID)])
        self._test_retrieve(result["collector_config_id"])
        self._test_update(result["collector_config_id"])
        self._test_run_subscription_task(result["collector_config_id"])
        self._test_start(result["collector_config_id"])
        self._test_retry_target_nodes(result["collector_config_id"])
        self._test_delete_subscription(result["collector_config_id"])
        self._test_get_target_mapping(result["collector_config_id"])
        self._test_get_subscription_status(result["collector_config_id"])
        self._test_get_subscription_task_detail(result["collector_config_id"])
        self._test_get_subscription_task_status(result["collector_config_id"])
        self._test_stop(result["collector_config_id"])
        self._test_destroy(result["collector_config_id"])

    @patch(
        "apps.api.TransferApi.get_data_id",
        get_data_id,
    )
    @patch(
        "apps.api.TransferApi.get_result_table",
        lambda x: {"result_table_id": TABLE_ID} if x["table_id"] == TABLE_ID else {},
    )
    @patch("apps.api.TransferApi.modify_data_id", lambda _: {"bk_data_id": BK_DATA_ID})
    @patch("apps.api.TransferApi.modify_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.NodeApi.update_subscription_info", lambda _: {"subscription_id": SUBSCRIPTION_ID})
    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": NEW_TASK_ID})
    def _test_update(self, collector_config_id, *args, **kwargs):
        params = copy.deepcopy(PARAMS)
        params["collector_config_id"] = collector_config_id

        new_collector_config_name = "新的名字"
        params["collector_config_name"] = new_collector_config_name

        params["target_nodes"] = [{"bk_inst_id": 34, "bk_obj_id": "module", "ip": "127.0.0.1", "bk_cloud_id": 1}]
        with self.assertRaises(CollectorConfigNotExistException):
            CollectorHandler(collector_config_id=9999)

        collector = CollectorHandler(collector_config_id=collector_config_id)
        result = collector.update_or_create(params)
        self.assertEqual(result["collector_config_name"], new_collector_config_name)

        self.assertListEqual(
            collector.data.target_subscription_diff,
            [
                {"type": "add", "bk_inst_id": 34, "bk_obj_id": "module"},
                {"type": "delete", "bk_inst_id": 33, "bk_obj_id": "module"},
            ],
        )

    @patch("apps.utils.thread.MultiExecuteFunc.append")
    @patch("apps.utils.thread.MultiExecuteFunc.run")
    @patch("apps.api.CCApi.search_biz_inst_topo", lambda _: [])
    @patch("apps.api.CCApi.search_set", CCSetTest())
    def _test_retrieve(self, collector_config_id, mock_run, mock_append):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        mock_append.return_value = ""
        mock_run.return_value = CONFIG_DATA
        result = collector.retrieve()

        self.assertEqual(result.get("data_encoding"), "UTF-8")
        self.assertIsNone(result.get("storage_cluster_id"))
        self.assertIsNone(result.get("retention"))
        self.assertEqual(result.get("collector_config_id"), collector_config_id)
        self.assertEqual(result.get("collector_scenario_id"), "row")

    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": LAST_TASK_ID})
    def _test_run_subscription_task(self, collector_config_id):
        target_nodes = [{"ip": "127.0.0.1", "bk_cloud_id": 0}]

        # 指定订阅节点
        collector1 = CollectorHandler(collector_config_id=collector_config_id)
        task_id_one = copy.deepcopy(collector1.data.task_id_list)
        task_id_one.append(str(LAST_TASK_ID))
        result1 = collector1._run_subscription_task(nodes=target_nodes)
        self.assertEqual(result1, task_id_one)

    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": 6})
    def _test_start(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        result = collector.start()
        self.assertEqual(result, ["6"])

    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": 7})
    def _test_stop(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        result = collector.stop()
        self.assertEqual(result, ["7"])

    @patch("apps.api.NodeApi.retry_subscription", lambda _: {"task_id": 8})
    def _test_retry_target_nodes(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        task_id_list = copy.deepcopy(collector.data.task_id_list)
        task_id_list.append("8")
        params = {"instance_id_list": [{"instance_id": "xxx"}]}
        result = collector.retry_instances(params)
        self.assertEqual(result, task_id_list)

    @patch("apps.api.NodeApi.delete_subscription", lambda _: DELETE_MSG)
    def _test_delete_subscription(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        result = collector._delete_subscription()
        self.assertTrue(result.get("result"))

    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": 8})
    @patch("apps.api.NodeApi.delete_subscription", lambda _: DELETE_MSG)
    def _test_destroy(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        collector.destroy()

        with self.assertRaises(CollectorConfigNotExistException):
            CollectorHandler(collector_config_id=collector_config_id)

    def test_format_subscription_instance_status(self, *args, **kwargs):
        result = CollectorHandler.format_subscription_instance_status(PART_FAILED_INSTANCE_DATA)
        self.assertEqual(result, STATUS_DATA_RETURN)

    @patch("apps.api.CCApi.search_biz_inst_topo", lambda _: TOPO_TREE)
    @patch("apps.api.NodeApi.get_subscription_instance_status", lambda _: STATUS_DATA)
    def _test_get_subscription_status(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)

        # 采集目标是HOST-INSTANCE
        collector.data.target_node_type = "INSTANCE"
        result = collector.get_subscription_status()
        self.assertFalse(result["contents"][0]["is_label"])
        self.assertEqual(result["contents"][0]["bk_obj_name"], "主机")
        self.assertEqual(result["contents"][0]["node_path"], "主机")
        self.assertEqual(result["contents"][0]["bk_obj_id"], "host")

        # 如果采集目标是HOST-TOPO
        collector.data.target_node_type = "TOPO"
        result2 = collector.get_subscription_status()
        self.assertFalse(result2["contents"][0]["is_label"])
        self.assertEqual(result2["contents"][0]["bk_obj_id"], "module")
        self.assertEqual(result2["contents"][0]["bk_inst_id"], 34)

    def test_get_node_mapping(self, *args, **kwargs):
        result = CollectorHandler().get_node_mapping(TOPO_TREE)
        self.assertEqual(result, TOPO_TREE_RETURN)

    def _test_get_target_mapping(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        collector.data.target_subscription_diff = [
            {"type": "add", "bk_inst_id": 2, "bk_obj_id": "biz"},
            {"type": "add", "bk_inst_id": 3, "bk_obj_id": "module"},
            {"type": "delete", "bk_inst_id": 4, "bk_obj_id": "set"},
            {"type": "modify", "bk_inst_id": 5, "bk_obj_id": "module"},
        ]
        result = collector.get_target_mapping()
        self.assertEqual({"module|5": "modify", "set|4": "delete", "module|3": "add", "biz|2": "add"}, result)

    @patch("apps.api.NodeApi.get_subscription_instance_status", lambda _: [PART_FAILED_INSTANCE_DATA])
    def _test_get_part_failed_subscription_status(self, collector_config_id):
        result = CollectorHandler().get_subscription_status_by_list([collector_config_id])
        self.assertEqual(
            result,
            [
                {
                    "collector_id": collector_config_id,
                    "subscription_id": SUBSCRIPTION_ID,
                    "status": "",
                    "status_name": "",
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "pending": 0,
                }
            ],
        )

    @patch("apps.api.NodeApi.get_subscription_instance_status", lambda _: [FAILED_INSTANCE_DATA])
    def _test_get_failed_subscription_status(self, collector_config_id):
        result = CollectorHandler().get_subscription_status_by_list([collector_config_id])
        self.assertEqual(
            result,
            [
                {
                    "collector_id": collector_config_id,
                    "subscription_id": 2,
                    "status": "",
                    "status_name": "",
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "pending": 0,
                }
            ],
        )

    @patch("apps.api.NodeApi.get_subscription_instance_status", lambda _: [SUCCESS_INSTANCE_DATA])
    def _test_get_success_subscription_status(self, collector_config_id):
        result = CollectorHandler().get_subscription_status_by_list([collector_config_id])
        self.assertEqual(
            result,
            [
                {
                    "collector_id": collector_config_id,
                    "subscription_id": 2,
                    "status": "",
                    "status_name": "正常",
                    "total": 1,
                    "success": 1,
                    "failed": 0,
                    "pending": 0,
                }
            ],
        )

    @patch("apps.api.NodeApi.get_subscription_instance_status", lambda _: [RUNNING_INSTANCE_DATA])
    def _test_get_running_subscription_status(self, collector_config_id):
        result = CollectorHandler().get_subscription_status_by_list([collector_config_id])
        self.assertEqual(
            result,
            [
                {
                    "collector_id": collector_config_id,
                    "subscription_id": 2,
                    "status": "RUNNING",
                    "status_name": "部署中",
                    "total": 1,
                    "success": 0,
                    "failed": 0,
                    "pending": 1,
                }
            ],
        )

    @patch("apps.api.NodeApi.get_subscription_task_detail", lambda _: TASK_DETAIL_DATA)
    def _test_get_subscription_task_detail(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)
        result = collector.get_subscription_task_detail("host|instance|host|127.0.0.1-0-0", task_id="24626")
        for i in ["unifytlogc", "下发插件配置", "更新插件部署状态", "渲染并下发配置", "重载插件进程"]:
            self.assertIn(i, result["log_detail"])
        self.assertEqual(result.get("log_result").get("status"), "FAILED")
        self.assertEqual(result.get("log_result").get("task_id"), 24626)
        self.assertEqual(result.get("log_result").get("instance_id"), "host|instance|host|127.0.0.1-0-0")

    def test_get_instance_log(self, *args, **kwargs):
        result = CollectorHandler.get_instance_log(TASK_DETAIL_DATA)
        result2 = CollectorHandler.get_instance_log({"steps": []})

        self.assertEqual(result, "[unifytlogc] 下发插件配置-重载插件进程")
        self.assertEqual(result2, "")

    @patch("apps.decorators.user_operation_record.delay", return_value=True)
    @patch("apps.api.NodeApi.switch_subscription", lambda _: {})
    @patch("apps.api.NodeApi.subscription_statistic", subscription_statistic)
    def test_format_task_instance_status(self, *args, **kwargs):
        _, create_result = TestCollectorHandler.create()
        collector_config_id = create_result["collector_config_id"]
        result = CollectorHandler(collector_config_id=collector_config_id).format_task_instance_status(
            [TASK_DETAIL_DATA]
        )
        self.assertEqual(result[0]["status"], "FAILED")
        self.assertEqual(result[0]["ip"], "127.0.0.1")
        self.assertEqual(result[0]["log"], "[unifytlogc] 下发插件配置-重载插件进程")
        self.assertEqual(result[0]["instance_id"], "host|instance|host|127.0.0.1-0-0")
        self.assertEqual(result[0]["instance_name"], "127.0.0.1")
        self.assertEqual(result[0]["task_id"], 24626)

    @patch("apps.api.CCApi.search_biz_inst_topo", lambda _: TOPO_TREE)
    @patch("apps.api.NodeApi.get_subscription_task_status", lambda _: [TASK_DETAIL_DATA])
    def _test_get_subscription_task_status(self, collector_config_id):
        collector = CollectorHandler(collector_config_id=collector_config_id)

        # 采集目标是HOST-TOPO
        result = collector.get_subscription_task_status(collector.data.task_id_list)
        self.assertTrue(result["contents"][0]["is_label"])
        self.assertEqual(result["contents"][0]["label_name"], "add")
        self.assertEqual(result["contents"][0]["bk_obj_id"], "module")
        self.assertEqual(result["contents"][0]["bk_inst_id"], 34)

        # 采集目标是HOST-INSTANCE
        collector.data.target_node_type = "INSTANCE"
        result2 = collector.get_subscription_task_status(collector.data.task_id_list)
        self.assertFalse(result2["contents"][0]["is_label"])
        self.assertEqual(result2["contents"][0]["bk_obj_name"], "主机")
        self.assertEqual(result2["contents"][0]["node_path"], "主机")
        self.assertEqual(result2["contents"][0]["bk_obj_id"], "host")

    def test_check_task_ready_exception(self, *args, **kwargs):
        self.assertEqual(CollectorHandler._check_task_ready_exception(ApiRequestError("test1", 111)), True)
        self.assertEqual(
            CollectorHandler._check_task_ready_exception(ApiResultError("test2", code=1306201, errors="test2")), True
        )
        with self.assertRaises(BaseException):
            CollectorHandler._check_task_ready_exception(ApiResultError("test2", code=111, errors="test2"))

        with self.assertRaises(BaseException):
            CollectorHandler._check_task_ready_exception(BaseException())

    @patch("apps.api.TransferApi.create_data_id", lambda _: {"bk_data_id": BK_DATA_ID})
    @patch(
        "apps.api.TransferApi.get_data_id",
        get_data_id,
    )
    @patch(
        "apps.api.TransferApi.get_result_table",
        lambda x: {"result_table_id": TABLE_ID} if x["table_id"] == TABLE_ID else {},
    )
    @patch("apps.api.TransferApi.create_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.NodeApi.create_subscription", lambda _: {"subscription_id": SUBSCRIPTION_ID})
    @patch("apps.api.NodeApi.subscription_statistic", subscription_statistic)
    @patch("apps.api.NodeApi.run_subscription_task", lambda _: {"task_id": TASK_ID})
    @patch("apps.api.NodeApi.switch_subscription", lambda _: {})
    @patch("apps.api.NodeApi.check_subscription_task_ready", lambda _: True)
    @patch("apps.api.TransferApi.modify_data_id", lambda _: {"bk_data_id": BK_DATA_ID})
    @patch("apps.api.CCApi.search_module", CCModuleTest())
    @patch("apps.api.CCApi.list_biz_hosts", CCBizHostsTest())
    @patch("apps.decorators.user_operation_record.delay", return_value=None)
    @patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id.delay", return_value=None)
    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_pre_check(self, *args, **kwargs):
        params = copy.deepcopy(PARAMS)
        result = CollectorHandler().pre_check(
            params={"bk_biz_id": params["bk_biz_id"], "collector_config_name_en": params["collector_config_name_en"]}
        )
        self.assertEqual(result["allowed"], True)

        params = custom_params_valid(serializer=CollectorCreateSerializer, params=params)
        params["params"]["conditions"]["type"] = "separator"
        CollectorHandler().update_or_create(params)

        # 测试collector_config_name_en同名
        params = copy.deepcopy(PARAMS)
        result = CollectorHandler().pre_check(
            params={"bk_biz_id": params["bk_biz_id"], "collector_config_name_en": params["collector_config_name_en"]}
        )
        self.assertEqual(result["allowed"], False)

        result = CollectorHandler().pre_check(
            params={"bk_biz_id": params["bk_biz_id"], "collector_config_name_en": "1"}
        )
        self.assertEqual(result["allowed"], True)

    @patch("apps.api.BcsApi.list_cluster_by_project_id", lambda _: PROJECT_CLUSTER_LIST)
    @patch("apps.api.BcsCcApi.list_project", lambda _: PROJECTS)
    @patch("apps.api.BcsCcApi.list_shared_clusters_ns", lambda _: SHARED_CLUSTERS_NS)
    def test_validate_container_config_yaml(self, *args, **kwargs):

        yaml_config = """
---
encoding: UTF-8
labelSelector:
  matchLabels:
    app.kubernetes.io/component: api-support
    app.kubernetes.io/instance: bk-apigateway
    app.kubernetes.io/name: bk-apigateway
logConfigType: std_log_config
namespaceSelector:
  any: false
  matchNames:
  - test-cluster-share-test1
  - test-cluster-share-test2
---
encoding: UTF-8
labelSelector:
  matchLabels:
    app.kubernetes.io/instance: bkmonitor
    app.kubernetes.io/name: influxdb-proxy
logConfigType: container_log_config
path:
  - /var/log/influxdb-proxy.log
  - /var/log/influxdb.log
namespaceSelector:
  any: false
  matchNames:
  - test-cluster-share-test1
  - test-cluster-share-test2
        """
        result = CollectorHandler().validate_container_config_yaml(
            bk_biz_id=BK_BIZ_ID, bcs_cluster_id=BCS_CLUSTER_ID, yaml_config=yaml_config
        )
        self.assertTrue(result["parse_status"])

    @patch("apps.api.BcsApi.list_cluster_by_project_id", lambda _: PROJECT_CLUSTER_LIST)
    @patch("apps.api.BcsCcApi.list_project", lambda _: PROJECTS)
    def test_list_bcs_clusters(self, *args, **kwargs):
        clusters = CollectorHandler().list_bcs_clusters(BK_BIZ_ID)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(BCS_CLUSTER_ID, clusters[0]["id"])

    def test_list_workload_type(self, *args, **kwargs):
        workload_type_list = CollectorHandler().list_workload_type()
        self.assertEqual(
            workload_type_list,
            [WorkLoadType.DEPLOYMENT, WorkLoadType.JOB, WorkLoadType.DAEMON_SET, WorkLoadType.STATEFUL_SET],
        )

    @patch("apps.api.BcsApi.list_cluster_by_project_id", lambda _: PROJECT_CLUSTER_LIST)
    @patch("apps.api.BcsCcApi.list_project", lambda _: PROJECTS)
    @patch("apps.api.BcsCcApi.list_shared_clusters_ns", lambda _: SHARED_CLUSTERS_NS)
    def test_list_namespace(self, *args, **kwargs):
        expect_namespace_list = {"test-cluster-share-test1", "test-cluster-share-test2"}

        result = CollectorHandler().list_namespace(bk_biz_id=BK_BIZ_ID, bcs_cluster_id=BCS_CLUSTER_ID)
        result_ns = {r["id"] for r in result}
        self.assertSetEqual(expect_namespace_list, result_ns)
