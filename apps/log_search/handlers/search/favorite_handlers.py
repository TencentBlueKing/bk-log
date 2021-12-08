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
from apps.log_databus.constants import TargetNodeTypeEnum
from apps.log_search.constants import DEFAULT_BK_CLOUD_ID
from apps.log_search.models import FavoriteSearch, UserIndexSetSearchHistory
from apps.utils.db import array_group


class FavoriteHandlers(object):

    SEARCH_HISTORY_TYPE = "favorite"

    def __init__(self, favorite_search_id=None):
        self.favorite_search_id = favorite_search_id

    def favorite_search(self, project_id):
        favorite_search_objs = (
            FavoriteSearch.objects.filter(project_id=project_id)
            .order_by("-created_at")
            .values("id", "search_history_id", "description")
        )
        search_history_ids = list(
            map(lambda search_history_obj: search_history_obj["search_history_id"], favorite_search_objs)
        )
        search_history_objs = UserIndexSetSearchHistory.objects.filter(id__in=search_history_ids).values(
            "params", "index_set_id", "id"
        )
        search_history_objs = array_group(search_history_objs, "id")
        return [
            {
                "favorite_search_id": favorite_obj["id"],
                "favorite_description": favorite_obj["description"],
                "index_set_id": search_history_objs[favorite_obj["search_history_id"]][0]["index_set_id"],
                "params": search_history_objs[favorite_obj["search_history_id"]][0]["params"],
                "query_string": self._generate_query_string(
                    search_history_objs[favorite_obj["search_history_id"]][0]["params"]
                ),
            }
            for favorite_obj in favorite_search_objs
        ]

    @classmethod
    def create(cls, project_id, index_set_id, host_scopes, addition, keyword, description):
        params = {"host_scopes": host_scopes, "addition": addition, "keyword": keyword}
        search_history_obj = UserIndexSetSearchHistory.objects.create(
            index_set_id=index_set_id, params=params, search_type=cls.SEARCH_HISTORY_TYPE
        )
        return FavoriteSearch.objects.create(
            project_id=project_id, search_history_id=search_history_obj.id, description=description
        )

    def delete(self):
        favorite_search = FavoriteSearch.objects.get(id=self.favorite_search_id)
        UserIndexSetSearchHistory.objects.filter(id=favorite_search.search_history_id).delete()
        favorite_search.delete()

    @staticmethod
    def _generate_query_string(params):
        key_word = params.get("keyword", "")
        if key_word is None:
            key_word = ""
        query_string = key_word
        host_scopes = params.get("host_scopes", {})
        target_nodes = host_scopes.get("target_nodes", {})

        if target_nodes:
            if host_scopes["target_node_type"] == TargetNodeTypeEnum.INSTANCE.value:
                query_string += " AND ({})".format(
                    ",".join([f"{target_node['bk_cloud_id']}:{target_node['ip']}" for target_node in target_nodes])
                )
            else:
                first_node, *_ = target_nodes
                target_list = [str(target_node["bk_inst_id"]) for target_node in target_nodes]
                query_string += f" AND ({first_node['bk_obj_id']}:" + ",".join(target_list) + ")"

        if host_scopes.get("modules"):
            modules_list = [str(_module["bk_inst_id"]) for _module in host_scopes["modules"]]
            query_string += " ADN (modules:" + ",".join(modules_list) + ")"
            host_scopes["target_node_type"] = TargetNodeTypeEnum.TOPO.value
            host_scopes["target_nodes"] = host_scopes["modules"]

        if host_scopes.get("ips"):
            query_string += " AND (ips:" + host_scopes["ips"] + ")"
            host_scopes["target_node_type"] = TargetNodeTypeEnum.INSTANCE.value
            host_scopes["target_nodes"] = [
                {"ip": ip, "bk_cloud_id": DEFAULT_BK_CLOUD_ID} for ip in host_scopes["ips"].split(",")
            ]

        additions = params.get("addition", [])
        if additions:
            query_string += (
                " AND ("
                + " AND ".join(
                    [f'{addition["field"]} {addition["operator"]} {addition["value"]}' for addition in additions]
                )
                + ")"
            )
        return query_string
