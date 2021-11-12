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
from django.conf import settings
from django.db.transaction import atomic

from apps.api import TransferApi, BcsCcApi
from apps.log_bcs.exceptions import ApplyConfigForBcsException
from apps.log_bcs.models import BcsClusterInfo
from apps.log_bcs.utils.k8s import version_cmp_greater
from apps.utils.log import logger
from apps.utils.template import render


class BcsHandler:
    TEMPLATES_PATH = "apps/log_bcs/templates/"
    BKLOG_CRD = "crd.yaml.tpl"
    BKLOG_DEPLOYMENT = "deployment.yaml.tpl"

    # BKLOG_CRD must first
    APPLY_CONFIG = [BKLOG_CRD, BKLOG_DEPLOYMENT]

    # crd k8s new version
    CRD_K8S_NEW_VERSION = "v1.16"

    def render_context(self, cluster_id) -> dict:
        host_path = settings.BCS_BKLOG_HOST_PATH.rstrip("/")
        return {
            "namespace": settings.BCS_BKLOG_NAMESPACE,
            "host_path": settings.BCS_BKLOG_HOST_PATH,
            "gse_endpoint": "/".join([host_path, settings.BCS_GSE_ENDPONIT]),
            "is_old_version": self.is_old_k8s_version(cluster_id),
            "bkunifylogbeat_image": settings.BCS_BKUNIFYLOGBEAT_IMAGE,
            "bk_log_sidecar_image": settings.BCS_BK_LOG_SIDECAR_IMAGE,
        }

    def render(self, target_config: str, cluster_id: str):
        config_path = "".join([self.TEMPLATES_PATH, target_config])
        return render(config_path, self.render_context(cluster_id))

    def is_old_k8s_version(self, cluster_id: str) -> bool:
        cluster_k8s_version = BcsCcApi.get_cluster_config_by_cluster_id({"cluster_id": cluster_id})["version"]
        return version_cmp_greater(self.CRD_K8S_NEW_VERSION, cluster_k8s_version)

    def apply_bklog_for_bcs(self, cluster_id: str, namespace: str):
        for apply_config in self.APPLY_CONFIG:
            apply_config_content = self.render(apply_config, cluster_id)
            if not TransferApi.apply_yaml_to_bcs_cluster(
                {"cluster_id": cluster_id, "namespace": namespace, "yaml_content": apply_config_content}
            ):
                logger.error(
                    f"[bcs] apply bklog config [{apply_config}] failed apply_config_content [{apply_config_content}]"
                )
                raise ApplyConfigForBcsException
            logger.info(f"[bcs] apply bklog config [{apply_config}] success")

    @atomic
    def register_bklog_to_bcs(self, cluster_id, project_id, bk_biz_id):
        """
        - register cluster to metadata
        - record bcs cluster to bklog database
        - apply bklog log collector config to bcs cluster
        """
        self.register_cluster_to_metadata(bk_biz_id, project_id, cluster_id)
        BcsClusterInfo.active_bcs_cluster(cluster_id, bk_biz_id, project_id)
        self.apply_bklog_for_bcs(cluster_id, settings.BCS_BKLOG_NAMESPACE)

    def register_cluster_to_metadata(self, bk_biz_id, project_id, cluster_id):
        if self.cluster_exists(cluster_id, bk_biz_id):
            logger.info(f"[bcs] cluster => [{cluster_id}] bk_biz_id => [{bk_biz_id}] has exist in metadata")
            return
        TransferApi.register_bcs_cluster({"bk_biz_id": bk_biz_id, "cluster_id": cluster_id, "project_id": project_id})
        logger.info(f"[bcs] register cluster => [{cluster_id}] bk_biz_id => [{bk_biz_id}]to metadata")

    def cluster_exists(self, cluster_id, bk_biz_id) -> bool:
        metadata_bcs_clusters = self.list_metadata_bcs_cluster(bk_biz_id)
        return any([cluster["cluster_id"] == cluster_id for cluster in metadata_bcs_clusters])

    def list_metadata_bcs_cluster(self, bk_biz_id) -> list:
        return TransferApi.list_bcs_cluster_info({"bk_biz_id": bk_biz_id})

    def list_bcs_cluster(self, bk_biz_id=None) -> list:
        open_log_bcs_clusters = set(BcsClusterInfo.objects.values_list("cluster_id", flat=True))
        bcs_clusters = BcsCcApi.list_cluster()
        bcs_projects = BcsCcApi.list_project()["results"]
        bcs_project_name_map = {p["project_id"]: p["project_name"] for p in bcs_projects}
        bcs_areas = BcsCcApi.list_area()["results"]
        bcs_area_name_map = {area["id"]: area["chinese_name"] for area in bcs_areas}
        if bk_biz_id:
            bcs_projects = [p for p in bcs_projects if str(p["cc_app_id"]) == str(bk_biz_id)]
        bcs_project_ids = {p["project_id"] for p in bcs_projects}
        return [
            {
                "area_name": bcs_area_name_map.get(cluster["area_id"], cluster["area_id"]),
                "project_name": bcs_project_name_map.get(cluster["project_id"], cluster["project_id"]),
                "project_id": cluster["project_id"],
                "cluster_id": cluster["cluster_id"],
                # "disable": cluster["disable"],
                "environment": cluster["environment"],
                "status": cluster["status"],
                "has_open_log": cluster["cluster_id"] in open_log_bcs_clusters,
            }
            for cluster in bcs_clusters
            if cluster["project_id"] in bcs_project_ids
        ]
