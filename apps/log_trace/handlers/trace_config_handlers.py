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
from apps.log_search.models import LogIndexSet
from apps.log_search.exceptions import IndexTraceProjectIDException
from apps.utils.function import ignored
from bk_dataview.grafana import client
from bk_dataview.grafana.settings import grafana_settings


class TraceConfigHandlers(object):
    def __init__(self):
        pass

    @classmethod
    def get_user_trace_index_set(cls, project_id, bk_biz_id, request, scenarios=None):
        if not project_id:
            raise IndexTraceProjectIDException()
        index_set_ids = LogIndexSet.objects.filter(project_id=project_id).values_list("index_set_id", flat=True)
        index_sets = LogIndexSet.get_index_set(index_set_ids, scenarios, is_trace_log=True)
        with ignored(Exception):
            cls.refresh_grafana(bk_biz_id, request)
        return index_sets

    @classmethod
    def refresh_grafana(cls, bk_biz_id, request):
        grafana_handler = grafana_settings.BACKEND_CLASS()
        from apps.grafana.provisioning import TraceProvisioning

        trace_provisioning = TraceProvisioning()
        org_id = cls.get_grafana_org_id(bk_biz_id)
        ds_list = trace_provisioning.datasources(request, bk_biz_id, org_id)
        grafana_handler.handle_datasources(request, bk_biz_id, org_id, ds_list, trace_provisioning)

    @staticmethod
    def get_grafana_org_id(org_name):
        resp = client.get_organization_by_name(org_name)
        if resp.status_code == 200:
            _org = resp.json()
            return _org["id"]

        if resp.status_code == 404:
            resp = client.create_organization(org_name)
            _org = resp.json()
            return _org["orgId"]
