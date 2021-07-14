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
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.log_extract.models import Strategies
from apps.log_extract.handlers.explorer import ExplorerHandler
from apps.utils.local import activate_request

BK_BIZ_ID = 215
USER = "admin"

STRATEGIES_LIST = [
    [
        {
            "strategy_name": "test1-1",
            "user_list": [USER],
            "visible_dir": ["/data/logs/linux/"],
            "file_type": ["linux1"],
            "select_type": "topo",
            "modules": [
                {"bk_inst_id": 2000000991, "bk_inst_name": "linux01", "bk_obj_id": "module", "bk_biz_id": "215"}
            ],
            "bk_biz_id": BK_BIZ_ID,
            "operator": USER,
        },
        {
            "strategy_name": "test1-2",
            "user_list": [USER],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "topo",
            "modules": [{"bk_inst_id": 2000001069, "bk_inst_name": "windows", "bk_obj_id": "set", "bk_biz_id": "215"}],
            "visible_dir": ["/data/logs/windows/"],
            "file_type": ["windows"],
            "operator": USER,
        },
        {
            "strategy_name": "test1-3",
            "user_list": [USER],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "topo",
            "modules": [
                {"bk_inst_id": 2000000944, "bk_inst_name": "linux02", "bk_obj_id": "set", "bk_biz_id": "215"},
                {"bk_inst_id": 2000001068, "bk_inst_name": "中转服务器", "bk_obj_id": "set", "bk_biz_id": "215"},
            ],
            "visible_dir": ["/data/"],
            "file_type": ["linux2", "linux3"],
            "operator": USER,
        },
    ],
    [
        {
            "strategy_name": "test2-1",
            "user_list": [USER, "bcac"],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "topo",
            "modules": [{"bk_inst_id": 215, "bk_inst_name": "功夫西游", "bk_obj_id": "biz", "bk_biz_id": 215}],
            "visible_dir": ["/data/logs/"],
            "file_type": ["tar"],
            "operator": USER,
        },
        {
            "strategy_name": "test2-2",
            "user_list": ["jajj", "bcac"],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "topo",
            "modules": [{"bk_inst_id": 215, "bk_inst_name": "功夫西游", "bk_obj_id": "biz", "bk_biz_id": 215}],
            "visible_dir": ["/data/logs/log2/"],
            "file_type": ["txt"],
            "operator": USER,
        },
        {
            "strategy_name": "test2-3",
            "user_list": [USER, "jajj"],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "topo",
            "modules": [{"bk_inst_id": 215, "bk_inst_name": "功夫西游", "bk_obj_id": "biz", "bk_biz_id": 215}],
            "visible_dir": ["/data/logs/log1/"],
            "file_type": ["log", "txt"],
            "operator": USER,
        },
    ],
]

HOST_TOPO_INFO_LINUX01 = {
    "topo": [
        {
            "bk_set_id": 2000000943,
            "module": [{"bk_module_name": "linux", "bk_module_id": 2000000991}],
            "bk_set_name": "linux01",
        }
    ],
    "host": {"bk_os_type": None, "bk_host_id": 2000006651, "bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
}
HOST_TOPO_INFO_LINUX02 = {
    "topo": [
        {
            "bk_set_id": 2000000944,
            "module": [{"bk_module_name": "linux", "bk_module_id": 2000000992}],
            "bk_set_name": "linux02",
        }
    ],
    "host": {"bk_os_type": "1", "bk_host_id": 2000000102, "bk_cloud_id": 0, "bk_host_innerip": "1.1.1.2"},
}
HOST_TOPO_INFO_WINDOWS = {
    "topo": [
        {
            "bk_set_id": 2000001069,
            "module": [{"bk_module_name": "windows", "bk_module_id": 2000001134}],
            "bk_set_name": "windows",
        }
    ],
    "host": {"bk_os_type": "2", "bk_host_id": 2000000101, "bk_cloud_id": 0, "bk_host_innerip": "1.1.1.3"},
}
HOST_TOPO_INFO_TEMPORARY = {
    "topo": [
        {
            "bk_set_id": 2000001068,
            "module": [{"bk_module_name": "中转", "bk_module_id": 2000001135}],
            "bk_set_name": "中转服务器",
        }
    ],
    "host": {"bk_os_type": None, "bk_host_id": 2000006652, "bk_cloud_id": 0, "bk_host_innerip": "1.1.1.4"},
}
# 主机topo信息
TOPO_SET = {
    "1.1.1.1": HOST_TOPO_INFO_LINUX01,
    "1.1.1.2": HOST_TOPO_INFO_LINUX02,
    "1.1.1.3": HOST_TOPO_INFO_WINDOWS,
    "1.1.1.4": HOST_TOPO_INFO_TEMPORARY,
}
IP_SET = {
    "linux01_linux": "1.1.1.1",  # linux
    "linux02_linux": "1.1.1.2",  # linux
    "windows_windows": "1.1.1.3",  # windows
    "temporary_temporary": "1.1.1.4",  # linux
}
# 每条策略对应可访问的文件目录及后缀
ALLOWED_DIR_FILE_LIST = {
    IP_SET["windows_windows"]: [
        {"file_path": "/data/logs/windows/", "file_type": {".windows"}, "operator": USER},
        {"file_path": "/data/logs/", "file_type": {".tar"}, "operator": USER},
        {"file_path": "/data/logs/log1/", "file_type": {".log", ".txt"}, "operator": USER},
    ],
    IP_SET["linux02_linux"]: [
        {"file_path": "/data/", "file_type": {".linux2", ".linux3"}, "operator": USER},
        {"file_path": "/data/logs/", "file_type": {".tar"}, "operator": USER},
        {"file_path": "/data/logs/log1/", "file_type": {".log", ".txt"}, "operator": USER},
    ],
}
# 用户请求浏览的目录列表（多个列表用于循环，实际用户一次只能请求一个目录）
REQUEST_DIR_DICT = {
    IP_SET["windows_windows"]: ["/data/logs/", "/data/logs/windows/"],
    IP_SET["linux02_linux"]: ["/data/", "/data/logs/log1/"],
}

# 可浏览的目录及文件后缀
ALLOWED_FILE_DICT = {
    IP_SET["windows_windows"]: [
        {"file_type": {"\\.tar"}, "file_path": "/data/logs/"},
        {"file_type": {"\\.tar", "\\.windows"}, "file_path": "/data/logs/windows/"},
    ],
    IP_SET["linux02_linux"]: [
        {"file_type": {"\\.linux2", "\\.linux3"}, "file_path": "/data/"},
        {"file_type": {"\\.linux2", "\\.linux3", "\\.log", "\\.txt", "\\.tar"}, "file_path": "/data/logs/log1/"},
    ],
}

# 浏览策略请求集
STRATEGIES_REQUESTS = [
    {"bk_biz_id": 215, "ip_list": ",".join([IP_SET["linux01_linux"], IP_SET["temporary_temporary"]])},
    {"bk_biz_id": 215, "ip_list": ",".join([IP_SET["linux01_linux"], IP_SET["linux02_linux"]])},
]
# 浏览策略相应result集
STRATEGIES_RESULTS = [{"result": False}, {"result": True, "data": {}}]
ALLOWED_DIR_FILE_LIST_INTERSECTION = {
    IP_SET["windows_windows"]: [
        {"file_path": "/data/logs/windows/", "file_type": {".windows"}, "operator": USER},
        {"file_path": "/data/logs/", "file_type": {".tar"}, "operator": USER},
        {"file_path": "/data/logs/log1/", "file_type": {".log", ".txt"}, "operator": USER},
    ],
    IP_SET["linux02_linux"]: [
        {"file_path": "/data/logs/", "file_type": {".tar"}, "operator": USER},
        {"file_path": "/data/logs/log1/", "file_type": {".log", ".txt"}, "operator": USER},
    ],
}
# 浏览策略相应data集
STRATEGIES_DATA = [
    "",
]
# 浏览文件请求集
EXPLORER_REQUESTS = []

EXPLORER_RESULTS = []
BASE_URL = "/api/v1/log_extract/explorer"

BIZ_TOTAL_TOP = [
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
                "child": [],
                "bk_inst_id": 2000000942,
                "bk_inst_name": "空闲机池",
                "children": [],
                "bk_biz_id": 215,
                "id": "2",
                "name": "空闲机池",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_inst_id": 2000000991,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "4",
                        "name": "linux",
                    }
                ],
                "bk_inst_id": 2000000943,
                "bk_inst_name": "linux01",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_inst_id": 2000000991,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "4",
                        "name": "linux",
                    }
                ],
                "bk_biz_id": 215,
                "id": "3",
                "name": "linux01",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_inst_id": 2000000992,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "7",
                        "name": "linux",
                    }
                ],
                "bk_inst_id": 2000000944,
                "bk_inst_name": "linux02",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_inst_id": 2000000992,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "7",
                        "name": "linux",
                    }
                ],
                "bk_biz_id": 215,
                "id": "6",
                "name": "linux02",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_inst_id": 2000001134,
                        "bk_inst_name": "windows",
                        "children": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "10",
                        "name": "windows",
                    }
                ],
                "bk_inst_id": 2000001069,
                "bk_inst_name": "windows",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_inst_id": 2000001134,
                        "bk_inst_name": "windows",
                        "children": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "10",
                        "name": "windows",
                    }
                ],
                "bk_biz_id": 215,
                "id": "9",
                "name": "windows",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_inst_id": 2000001135,
                        "bk_inst_name": "中转",
                        "children": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "13",
                        "name": "中转",
                    }
                ],
                "bk_inst_id": 2000001068,
                "bk_inst_name": "中转服务器",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_inst_id": 2000001135,
                        "bk_inst_name": "中转",
                        "children": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "13",
                        "name": "中转",
                    }
                ],
                "bk_biz_id": 215,
                "id": "12",
                "name": "中转服务器",
            },
        ],
        "bk_inst_id": 215,
        "bk_inst_name": "功夫西游",
        "children": [
            {
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "集群",
                "bk_obj_id": "set",
                "child": [],
                "bk_inst_id": 2000000942,
                "bk_inst_name": "空闲机池",
                "children": [],
                "bk_biz_id": 215,
                "id": "2",
                "name": "空闲机池",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_inst_id": 2000000991,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "4",
                        "name": "linux",
                    }
                ],
                "bk_inst_id": 2000000943,
                "bk_inst_name": "linux01",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_inst_id": 2000000991,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.1",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "5",
                                "name": "1.1.1.1",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "4",
                        "name": "linux",
                    }
                ],
                "bk_biz_id": 215,
                "id": "3",
                "name": "linux01",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_inst_id": 2000000992,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "7",
                        "name": "linux",
                    }
                ],
                "bk_inst_id": 2000000944,
                "bk_inst_name": "linux02",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_inst_id": 2000000992,
                        "bk_inst_name": "linux",
                        "children": [
                            {
                                "ip": "1.1.1.2",
                                "os_type": "1",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "8",
                                "name": "1.1.1.2",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "7",
                        "name": "linux",
                    }
                ],
                "bk_biz_id": 215,
                "id": "6",
                "name": "linux02",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_inst_id": 2000001134,
                        "bk_inst_name": "windows",
                        "children": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "10",
                        "name": "windows",
                    }
                ],
                "bk_inst_id": 2000001069,
                "bk_inst_name": "windows",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_inst_id": 2000001134,
                        "bk_inst_name": "windows",
                        "children": [
                            {
                                "ip": "1.1.1.3",
                                "os_type": "2",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "11",
                                "name": "1.1.1.3",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "10",
                        "name": "windows",
                    }
                ],
                "bk_biz_id": 215,
                "id": "9",
                "name": "windows",
            },
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
                        "child": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_inst_id": 2000001135,
                        "bk_inst_name": "中转",
                        "children": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "13",
                        "name": "中转",
                    }
                ],
                "bk_inst_id": 2000001068,
                "bk_inst_name": "中转服务器",
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "模块",
                        "bk_obj_id": "module",
                        "child": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_inst_id": 2000001135,
                        "bk_inst_name": "中转",
                        "children": [
                            {
                                "ip": "1.1.1.4",
                                "os_type": "",
                                "children": [],
                                "bk_biz_id": 215,
                                "id": "14",
                                "name": "1.1.1.4",
                            }
                        ],
                        "bk_biz_id": 215,
                        "id": "13",
                        "name": "中转",
                    }
                ],
                "bk_biz_id": 215,
                "id": "12",
                "name": "中转服务器",
            },
        ],
        "bk_biz_id": 215,
        "id": "1",
        "name": "功夫西游",
    }
]


class User:
    def __init__(self):
        self.username = USER


class Request:
    def __init__(self):
        self.user = User()


class TestExplorer(TestCase):
    def setUp(self):
        activate_request(Request())
        self.explorer = ExplorerHandler()

    @staticmethod
    def setting_strategy(setting_index_list):
        for index, strategies in enumerate(STRATEGIES_LIST):
            # 配置策略
            if index not in setting_index_list:
                continue
            for strategy in strategies:
                # StrategiesHandler().update_or_create(**strategy)
                Strategies.objects.create(**strategy)

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    def test_get_allowed_dir_file_list(self, *args, **kwargs):
        """
        测试获取可访问的目录及目录下可访问的文件后缀
        """
        # 遍历每组测试样例
        self.setting_strategy([0, 1])
        strategies = self.explorer.get_user_strategies(BK_BIZ_ID, USER)
        strategies = sorted(strategies, key=lambda x: x["strategy_id"])
        allowed_strategies = {}
        for host_topo in [HOST_TOPO_INFO_WINDOWS, HOST_TOPO_INFO_LINUX02]:
            ip = host_topo["host"]["bk_host_innerip"]
            allowed_dir_file_list = self.explorer.get_allowed_dir_file_list(strategies, host_topo["topo"])
            [item.pop("strategy_name") for item in allowed_dir_file_list]
            self.assertEqual(allowed_dir_file_list, ALLOWED_DIR_FILE_LIST[ip])
            if not allowed_strategies.get(ip):
                allowed_strategies[ip] = allowed_dir_file_list
            else:
                allowed_strategies[ip].extend(allowed_dir_file_list)
        return allowed_strategies

    def test_get_intersection_strategies(self, *args, **kwargs):
        allowed_strategies = self.test_get_allowed_dir_file_list()
        result = []
        for ip, ip_allowed_strategies in allowed_strategies.items():
            result = self.explorer.get_intersection_strategies(result, ip_allowed_strategies)
            [item.pop("strategy_name") for item in result if "strategy_name" in item]
            self.assertEqual(result, ALLOWED_DIR_FILE_LIST_INTERSECTION[ip])

    def test_get_search_params(self, *args, **kwargs):
        """
        测试文件列表的搜索参数，search_params作为FileSearchService组件的参数执行文件浏览脚本
        """
        allowed_strategies = self.test_get_allowed_dir_file_list()
        for ip, allowed_dir_file_list in allowed_strategies.items():
            for index, request_dir in enumerate(REQUEST_DIR_DICT[ip]):
                search_params = self.explorer.get_search_params(allowed_dir_file_list, request_dir)
                self.assertEqual(search_params, ALLOWED_FILE_DICT[ip][index])

    @override_settings(MIDDLEWARE=("apps.tests.middlewares.OverrideMiddleware",))
    @patch("apps.log_extract.handlers.explorer.get_request_username")
    @patch("apps.log_extract.handlers.explorer.ExplorerHandler.search_biz_inst_topo")
    def test_list_accessible_topo(self, total_topo, get_request_username):
        strategy = {
            "strategy_name": "test1-2",
            "user_list": [USER],
            "bk_biz_id": BK_BIZ_ID,
            "select_type": "module",
            "modules": [{"bk_inst_id": 0, "bk_inst_name": "windows", "bk_obj_id": "module", "bk_biz_id": "215"}],
            "visible_dir": ["/data/logs/windows/"],
            "file_type": ["windows"],
            "operator": USER,
        }
        Strategies.objects.create(**strategy)
        request_path = BASE_URL + "/topo/"
        get_request_username.return_value = USER
        total_topo.return_value = BIZ_TOTAL_TOP
        response = self.client.get(request_path, data={"bk_biz_id": str(BK_BIZ_ID)})
        import json

        content = json.loads(response.content)
        self.assertDictEqual(
            content["data"][0],
            {
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "业务",
                "bk_obj_id": "biz",
                "child": [],
                "children": [
                    {
                        "host_count": 0,
                        "default": 0,
                        "bk_obj_name": "集群",
                        "bk_obj_id": "set",
                        "child": [],
                        "children": [
                            {
                                "host_count": 0,
                                "default": 0,
                                "bk_obj_name": "模块",
                                "bk_obj_id": "module",
                                "child": [
                                    {
                                        "ip": "1.1.1.3",
                                        "os_type": "2",
                                        "children": [],
                                        "bk_biz_id": 215,
                                        "id": "11",
                                        "name": "1.1.1.3",
                                    }
                                ],
                                "bk_inst_id": 2000001134,
                                "bk_inst_name": "windows",
                                "children": [
                                    {
                                        "ip": "1.1.1.3",
                                        "os_type": "2",
                                        "children": [],
                                        "bk_biz_id": 215,
                                        "id": "11",
                                        "name": "1.1.1.3",
                                    }
                                ],
                                "bk_biz_id": 215,
                                "id": "10",
                                "name": "windows",
                            }
                        ],
                        "bk_inst_id": 2000001069,
                        "bk_inst_name": "windows",
                        "bk_biz_id": 215,
                        "id": "9",
                        "name": "windows",
                    }
                ],
                "bk_inst_id": 215,
                "bk_inst_name": "功夫西游",
                "bk_biz_id": 215,
                "id": "1",
                "name": "功夫西游",
            },
        )
