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
from ..provisioning import DATASOURCE_NEED_CREATE


logger = logging.getLogger(__name__)


class APIHandler(BaseHandler):
    def handle_user(self, request, username: str):
        pass

    def handle_org(self, request, org_name: str, username: str):
        pass

    def handle_datasources(self, request, org_name: str, org_id: int, ds_list: list, provisioning):
        """API不能批量处理多个数据源"""
        for datasource in ds_list:
            if datasource.is_delete:
                resp = client.delete_datasource(org_id, datasource.id)
                if resp.status_code == 200:
                    logger.info("delete provision datasource success, %s", resp)
                    continue
                logger.info("delete provision datasource failed, %s", resp)
                continue

            if datasource.id != DATASOURCE_NEED_CREATE:
                resp = client.get_datasource_by_id(org_id, datasource.id)
                if resp.status_code == 200:
                    result = resp.json()
                    datasource.version = result["version"] + 1
                    resp = client.update_datasource(org_id, result["id"], datasource)
                    if resp.status_code == 200:
                        logger.info("update provision datasource success, %s", resp)
                continue

            resp = client.get_datasource(org_id, datasource.name)
            if resp.status_code == 200:
                result = resp.json()
                datasource.version = result["version"] + 1
                resp = client.update_datasource(org_id, result["id"], datasource)
                datasource.id = result["id"]
                if resp.status_code == 200:
                    provisioning.datasource_callback(request, org_name, org_id, datasource, True, "")
                    logger.info("update provision datasource success, %s", resp)
                continue

            if resp.status_code == 404:
                resp = client.create_datasource(org_id, datasource)
                # 412 code 代表已经存在
                if resp.status_code == 200:
                    logger.info("create provision datasource success, %s", resp)
                    datasource.id = resp.json()["id"]
                    provisioning.datasource_callback(request, org_name, org_id, datasource, True, "")
                    continue
                logger.info("create provision datasource fail, %s", resp)

    def handle_dashboards(self, request, org_name: str, org_id: int, db_list):
        pass
