# -*- coding: utf-8 -*-
DATA_META = {"scope_type": "biz", "scope_id": 2, "bk_biz_id": 2}

API_TOPO_TREES_REQUEST = {"all_scope": False, "scope_list": [{"scope_type": "biz", "scope_id": "2"}]}

API_TOPO_TREES_RESPONSE = {
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
        {
            "instance_id": 2,
            "instance_name": "蓝鲸",
            "object_id": "biz",
            "object_name": "业务",
            "meta": DATA_META,
            "child": [
                {
                    "instance_id": 144,
                    "instance_name": "mark测试",
                    "object_id": "set",
                    "object_name": "集群",
                    "meta": DATA_META,
                    "child": [
                        {
                            "instance_id": 281,
                            "instance_name": "空闲机模块",
                            "object_id": "module",
                            "object_name": "模块",
                            "meta": DATA_META,
                            "child": [],
                            "count": 4,
                        }
                    ],
                    "count": 4,
                },
                {
                    "instance_id": 2,
                    "instance_name": "空闲机池",
                    "objectId": "set",
                    "object_name": "集群",
                    "meta": DATA_META,
                    "child": [
                        {
                            "instance_id": 3,
                            "instance_name": "空闲机",
                            "object_id": "module",
                            "object_name": "模块",
                            "child": [],
                            "meta": DATA_META,
                            "count": 92,
                        }
                    ],
                    "count": 92,
                },
            ],
            "count": 96,
        }
    ],
    "request_id": "226d141055aa98f724a03cdce843cae1",
}

API_TOPO_QUERY_PATH_REQUEST = {"node_list": [{"meta": DATA_META, "object_id": "set", "instance_id": "144"}]}

API_TOPO_QUERY_PATH_RESPONSE = {
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
        [
            {"meta": DATA_META, "instance_id": 2, "instance_name": "蓝鲸", "objectId": "biz", "object_name": "业务"},
            {
                "meta": DATA_META,
                "instance_id": 144,
                "instance_name": "mark测试",
                "object_id": "set",
                "object_name": "集群",
            },
        ]
    ],
    "request_id": "c13b9418f45d3af0",
}

API_TOPO_QUERY_HOSTS_REQUEST = {"node_list": API_TOPO_QUERY_PATH_REQUEST["node_list"], "start": 0, "page_size": 20}

API_TOPO_QUERY_HOSTS_RESPONSE = {
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": {
        "start": 0,
        "page_size": 10,
        "total": 1,
        "data": [
            {
                "meta": DATA_META,
                "host_id": 355675,
                "ip": "127.0.0.1",
                "ipv6": "",
                "host_name": "",
                "alive": 0,
                "cloud_area": {"id": 2, "name": "ababababa"},
                "biz": {"id": 2, "name": "蓝鲸"},
                "os_name": "",
            }
        ],
    },
    "requestId": "97af493eb8c3a027478b098a02e3870a",
}


API_TOPO_QUERY_HOST_ID_INFOS_REQUEST = API_TOPO_QUERY_HOSTS_REQUEST

API_TOPO_QUERY_HOST_ID_INFOS_RESPONSE = {
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": {"start": 0, "pageSize": -1, "total": 1, "data": [{"meta": DATA_META, "host_id": 355675}]},
    "request_id": "b96a0c97063469d8ac8ddceef64e73bc",
}


API_TOPO_AGENT_STATISTICS_REQUEST = API_TOPO_QUERY_PATH_REQUEST

API_TOPO_AGENT_STATISTICS_RESPONSE = {
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": [
        {
            "node": {"meta": DATA_META, "instance_id": 2, "object_id": "biz"},
            "agent_statistics": {"alive_count": 100, "no_alive_count": 200, "total_count": 300},
            "host_num": 300,
        }
    ],
    "request_id": "c17ae1b76dc47a86",
}


API_HOST_CHECK_REQUEST = {
    "scope_list": API_TOPO_TREES_REQUEST["scope_list"],
    "ip_list": ["0:127.0.0.1"],
    "ipv6_list": ["0:A:A:A:A:A:A"],
    "key_list": ["11111", "hahaha"],
}

API_HOST_CHECK_RESPONSE = {
    "success": True,
    "code": 0,
    "error_msg": "成功",
    "data": API_TOPO_QUERY_HOSTS_RESPONSE["data"],
    "request_id": "c17ae1b76dc47a86",
}


API_HOST_DETAILS_REQUEST = {
    "scope_list": API_TOPO_TREES_REQUEST["scope_list"],
    "host_list": [{"host_id": 1, "meta": DATA_META}, {"ip": "127.0.0.1", "cloud_id": 0, "meta": DATA_META}],
}

API_HOST_DETAILS_RESPONSE = API_HOST_CHECK_RESPONSE
