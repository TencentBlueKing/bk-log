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

from apps.grafana.constants import TRACE_DATASOURCE_TYPE
from apps.grafana.model import TraceDatasourceMap
from apps.log_search.handlers.meta import MetaHandler
from apps.log_search.models import LogIndexSet
from apps.utils.db import array_hash
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
        trace_index_sets = LogIndexSet.objects.filter(is_trace_log=True, project_id=project_info["project_id"]).values(
            "index_set_name", "index_set_id"
        )
        datasource_maps = TraceDatasourceMap.objects.filter(bk_biz_id=org_name).values("datasource_id", "index_set_id")
        datasource_map_hash = array_hash(datasource_maps, "index_set_id", "datasource_id")
        trace_index_set_hash = array_hash(trace_index_sets, "index_set_id", "index_set_name")
        trace_index_set_ids = {trace_index_set["index_set_id"] for trace_index_set in trace_index_sets}
        map_index_set_ids = {datasource_map["index_set_id"] for datasource_map in datasource_maps}
        need_create_datasource = trace_index_set_ids - map_index_set_ids
        need_delete_datasource = map_index_set_ids - trace_index_set_ids
        need_update_datasource = map_index_set_ids & trace_index_set_ids
        result = []
        for index_set_id in need_create_datasource:
            result.append(
                Datasource(
                    name=trace_index_set_hash[index_set_id],
                    type=TRACE_DATASOURCE_TYPE,
                    access="direct",
                    isDefault=False,
                    url="proxy/trace/{}".format(index_set_id),
                    jsonData={"index_set_id": index_set_id},
                    orgId=org_id,
                )
            )

        for index_set_id in need_delete_datasource:
            result.append(Datasource(id=datasource_map_hash[index_set_id], is_delete=True, type="", name="", url=""))

        for index_set_id in need_update_datasource:
            result.append(
                Datasource(
                    name=trace_index_set_hash[index_set_id],
                    type=TRACE_DATASOURCE_TYPE,
                    access="direct",
                    isDefault=False,
                    url="proxy/trace/{}".format(index_set_id),
                    jsonData={"index_set_id": index_set_id},
                    orgId=org_id,
                    id=datasource_map_hash[index_set_id],
                )
            )
        return result

    def datasource_callback(
        self, request, org_name: str, org_id: int, datasource: Datasource, status: bool, content: str
    ):
        if datasource.type == TRACE_DATASOURCE_TYPE:
            TraceDatasourceMap.objects.update_or_create(
                bk_biz_id=org_name,
                index_set_id=datasource.jsonData["index_set_id"],
                datasource_id=datasource.id,
            )

    def dashboards(self, request, org_name, org_id) -> list:
        return []
