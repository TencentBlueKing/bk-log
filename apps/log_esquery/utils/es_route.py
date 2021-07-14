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
from apps.api import BkLogApi
from apps.log_search.models import Scenario


class EsRoute:
    def __init__(self, indices=None, storage_cluster_id=None, scenario_id=None, raise_exception=True):
        self._indices = indices
        self._cluster_id = storage_cluster_id
        self._scenario_id = scenario_id
        self._raise_exception = raise_exception

    def cat_indices(self):
        if self._scenario_id in [Scenario.BKDATA]:
            return self._get_bkdata_indices()
        target_index = self._get_index_target(self._indices)
        url = f"_cat/indices/{target_index}?bytes=b"
        result = self._query(url)
        return result

    def _get_bkdata_indices(self):
        index_list = self._indices.split(",")
        ret = []
        for _index in index_list:
            target_index = self._get_index_target(_index)
            url = f"_cat/indices/{target_index}?bytes=b"
            result = self._bkdata_query(_index, url)
            ret.extend(result.get(_index, []))
        return ret

    def _bkdata_query(self, index, url):
        return BkLogApi.es_route(
            {"indices": index, "scenario_id": self._scenario_id, "url": url}, raise_exception=self._raise_exception
        )

    def cluster_stats(self):
        url = "_cluster/stats"
        return self._query(url)

    def cluster_nodes_stats(self):
        url = "_nodes/stats"
        return self._query(url)

    def _query(self, url):
        return BkLogApi.es_route(
            {
                "indices": self._indices if self._indices else "",
                "scenario_id": self._scenario_id,
                "storage_cluster_id": self._cluster_id if self._cluster_id is not None else 0,
                "url": url,
            },
            raise_exception=self._raise_exception,
        )

    def _get_index_target(self, index: str):
        if index is None or index == "":
            return ""
        index_list: list = index.split(",")
        new_index_list: list = []
        for _index in index_list:
            if not _index.endswith("*"):
                _index = _index + "_*"
            new_index_list.append(_index)
        ret = ",".join(new_index_list)
        return ret.replace(".", "_")
