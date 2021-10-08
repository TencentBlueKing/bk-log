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
import json

from . import BaseHandler
from .. import models


class DBHandler(BaseHandler):
    def handle_user(self, request, username: str):
        pass

    def handle_org(self, request, org_name: str, username: str):
        pass

    def handle_datasources(self, request, org_name: str, org_id: int, ds_list: int, provisioning):
        created = list(
            models.DataSource.objects.filter(org_id=org_id, name__in=[ds.name for ds in ds_list]).values_list(
                "name", flat=True
            )
        )

        want_create = []
        for ds in ds_list:
            if ds.name in created:
                continue
            _ds = models.DataSource(
                org_id=org_id,
                name=ds.name,
                type=ds.type,
                url=ds.url,
                access=ds.access,
                is_default=ds.isDefault,
                database=ds.database,
                with_credentials=ds.withCredentials,
                version=ds.version,
                json_data=json.dumps(ds.jsonData),
            )
            want_create.append(_ds)

        if len(want_create) > 0:
            models.DataSource.objects.bulk_create(want_create)

    def handle_dashboards(self, request, org_name: str, org_id: int):
        pass
