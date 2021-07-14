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
import logging

from .. import client
from . import BaseHandler

_ORG_DATASOURCES_CACHE = {}

logger = logging.getLogger(__name__)


class APIHandler(BaseHandler):
    def handle_user(self, request, username: str):
        pass

    def handle_org(self, request, org_name: str, username: str):
        pass

    def handle_datasources(self, request, org_name: str, org_id: int, ds_list: list):
        """API不能批量处理多个数据源"""
        _ORG_DATASOURCES_CACHE.setdefault(org_name, {})

        for ds in ds_list:
            if ds.name in _ORG_DATASOURCES_CACHE[org_name]:
                continue

            resp = client.get_datasource(org_id, ds.name)
            if resp.status_code == 200:
                result = resp.json()
                ds.version = result["version"] + 1
                resp = client.update_datasource(org_id, result["id"], ds)
                if resp.status_code == 200:
                    _ORG_DATASOURCES_CACHE[org_name][ds.name] = ds
                    logger.info("update provision datasource success, %s", resp)
                    return

            if resp.status_code == 404:
                resp = client.create_datasource(org_id, ds)
                # 412 code 代表已经存在
                if resp.status_code == 200:
                    _ORG_DATASOURCES_CACHE[org_name][ds.name] = ds

                logger.info("create provision datasource success, %s", resp)

    def handle_dashboards(self, request, org_name: str, org_id: int, db_list):
        pass
