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
from elasticsearch5 import Elasticsearch

from apps.log_measure.exceptions import EsConnectFailException
from apps.log_measure.constants import COLUMN_DISPLAY_LIST


class ElasticHandle(object):
    def __init__(self, es_host, es_port, es_username=None, es_password=None, timeout=600):
        self.es_host = es_host
        self.es_port = es_port
        self.es_username = es_username
        self.es_password = es_password
        self.timeout = timeout
        http_auth = (self.es_username, self.es_password) if self.es_username and self.es_password else None
        self.es_client = Elasticsearch(
            [self.es_host],
            http_auth=http_auth,
            scheme="http",
            port=self.es_port,
            sniffer_timeout=600,
            verify_certs=True,
        )
        if not self.es_client.ping():
            raise EsConnectFailException()

    def get_indices_cat(
        self, index=None, bytes="b", column=COLUMN_DISPLAY_LIST
    ):  # pylint: disable=dangerous-default-value
        """
        索引统计信息
        :param index: 索引
        :param bytes: 容量单位
        :param column: 查询信息
        :return:
        """
        return self.es_client.cat.indices(index=index, format="json", bytes=bytes, h=column)
