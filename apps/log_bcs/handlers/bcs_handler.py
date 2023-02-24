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

from apps.utils.log import logger
from apps.api import BcsCcApi, BcsApi
from apps.log_search.models import Space
from bkm_space.define import SpaceTypeEnum


class BcsHandler:
    @classmethod
    def list_bcs_shared_cluster_namespace(cls, bcs_cluster_id):
        namespaces = BcsCcApi.list_shared_clusters_ns({"cluster_id": bcs_cluster_id, "desire_all_data": "1"})
        project_id_to_ns = {}
        for ns in namespaces.get("results", []):
            project_id_to_ns.setdefault(ns["project_id"], []).append(ns["name"])
        return project_id_to_ns

    @classmethod
    def list_bcs_cluster(cls, bk_biz_id=None) -> list:
        if bk_biz_id is None:
            logger.warning("[forbidden]query bcs cluster, but not bk_biz_id")
            return []

        space = Space.objects.get(bk_biz_id=bk_biz_id)
        if space.space_type_id == SpaceTypeEnum.BKCC.value:
            clusters = BcsApi.list_cluster_by_project_id({"businessID": bk_biz_id})
        elif space.space_type_id == SpaceTypeEnum.BCS.value:
            clusters = BcsApi.list_cluster_by_project_id({"projectID": space.space_id})
        elif space.space_type_id == SpaceTypeEnum.BKCI.value and space.space_code:
            clusters = BcsApi.list_cluster_by_project_id({"projectID": space.space_code})
        else:
            clusters = []

        result = []

        for cluster in clusters:
            result.append(
                {
                    "project_id": cluster["projectID"],
                    "cluster_id": cluster["clusterID"],
                    "cluster_name": cluster["clusterName"],
                    "region": cluster["region"],
                    "environment": cluster["environment"],
                    "status": cluster["status"],
                    "engine_type": cluster["engineType"],
                    "is_shared": cluster["is_shared"],
                }
            )
        return result
