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
from typing import List

from django.conf import settings
from django.utils.translation import ugettext as _

from apps.log_search.handlers.meta import MetaHandler
from apps.log_search.models import LogIndexSet
from bk_dataview.grafana.provisioning import BaseProvisioning, Datasource


class Provisioning(BaseProvisioning):
    def datasources(self, request, org_name, org_id) -> list:
        return [
            Datasource(
                name=_("日志平台-时序数据"),
                type="bk_log_datasource",
                access="direct",
                isDefault=True,
                version=1,
                jsonData={"baseUrl": "/{}api/v1/".format(settings.SITE_URL)},
                url="",
                orgId=org_id,
            )
        ]

    def dashboards(self, request, org_name, org_id) -> list:
        return []


class TraceProvisioning(BaseProvisioning):
    def datasources(self, request, org_name: str, org_id: int) -> List[Datasource]:
        project_info = MetaHandler.get_project_info(org_name)
        qs = LogIndexSet.objects.filter(is_trace_log=True, project_id=project_info["project_id"])
        return [
            Datasource(
                name=trace.index_set_name,
                type="jaeger",
                access="direct",
                isDefault=False,
                url="proxy{}trace/{}".format(settings.SITE_URL, trace.index_set_id),
                orgId=org_id,
            )
            for trace in qs
        ]

    def dashboards(self, request, org_name, org_id) -> list:
        return []
