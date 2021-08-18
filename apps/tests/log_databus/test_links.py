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
from apps.log_databus.handlers.link import DataLinkHandler

TRANSFER_CLUSTERS = [
    {"cluster_id": "default", "domain_name": "test", "port": 80},
    {"cluster_id": "default", "domain_name": "test", "port": 80},
    {"cluster_id": "default1", "domain_name": "test1", "port": 80},
]

CLUSTERS = [
    {
        "cluster_config": {
            "registered_system": "_default",
            "cluster_id": "default",
            "cluster_name": "default1",
            "domain_name": "test",
            "port": 80,
        }
    }
]

TRANSFER_CLUSTERS_RES = [
    {"cluster_id": "default", "cluster_name": "default", "domain_name": "test", "port": 80},
    {"cluster_id": "default1", "cluster_name": "default1", "domain_name": "test1", "port": 80},
]

CLUSTERS_RES = [{"cluster_id": "default", "cluster_name": "default1", "domain_name": "test", "port": 80}]


class TestLinks(TestCase):
    @patch("apps.api.TransferApi.list_transfer_cluster", lambda: TRANSFER_CLUSTERS)
    @patch("apps.api.TransferApi.get_cluster_info", lambda _: CLUSTERS)
    @override_settings(TABLE_ID_PREFIX="")
    def test_get_cluster_list(self):
        self.assertEqual(DataLinkHandler.get_cluster_list("transfer"), TRANSFER_CLUSTERS_RES)
        self.assertEqual(DataLinkHandler.get_cluster_list("kafka"), CLUSTERS_RES)
        self.assertEqual(DataLinkHandler.get_cluster_list("es"), CLUSTERS_RES)
