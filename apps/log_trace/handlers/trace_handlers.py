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

from apps.log_trace.handlers.proto.proto import Proto
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler as SearchHandlerEsquery


class TraceHandler(object):
    def __init__(self, index_set_id):
        data = {"search_type": "trace"}
        search_handler_esquery = SearchHandlerEsquery(index_set_id, data)
        self._index_set_id = index_set_id
        self._proto_type = Proto.judge_trace_type(search_handler_esquery.fields().get("fields", []))

    def trace_detail(self, trace_id):
        return Proto.get_proto(self._proto_type).trace_detail(self._index_set_id, trace_id)

    def traces(self, params):
        return Proto.get_proto(self._proto_type).traces(self._index_set_id, params)

    def operations(self, service_name):
        return Proto.get_proto(self._proto_type).operations(self._index_set_id, service_name)

    def services(self):
        return Proto.get_proto(self._proto_type).services(self._index_set_id)

    def fields(self, scope: str) -> dict:
        return Proto.get_proto(self._proto_type).fields(self._index_set_id, scope)

    def search(self, data: dict) -> dict:
        return Proto.get_proto(self._proto_type).search(self._index_set_id, data)

    def trace_id(self, data: dict) -> dict:
        return Proto.get_proto(self._proto_type).trace_id(self._index_set_id, data)

    def scatter(self, data: dict):
        return Proto.get_proto(self._proto_type).scatter(self._index_set_id, data)
