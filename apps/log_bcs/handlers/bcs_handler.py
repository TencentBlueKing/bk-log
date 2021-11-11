from django.conf import settings
from django.db.transaction import atomic

from apps.api import TransferApi, BcsCcApi
from apps.log_bcs.exceptions import ApplyConfigForBcsException
from apps.utils.log import logger
from apps.utils.template import render


class BcsHandler:
    TEMPLATES_PATH = "apps/log_bcs/templates/"
    BKLOG_CRD = "crd.yaml.tpl"
    BKLOG_DEPLOYMENT = "deployment.yaml.tpl"

    APPLY_CONFIG = [BKLOG_CRD, BKLOG_DEPLOYMENT]

    def render_context(self) -> dict:
        return {
            "namespace": settings.BCS_BKLOG_NAMESPACE,
            "host_path": settings.BCS_BKLOG_HOST_PATH,
            "gse_endpoint": settings.BCS_GSE_ENDPONIT,
        }

    def render(self, target_config: str):
        config_path = "".join(self.TEMPLATES_PATH, target_config)
        return render(config_path, self.render_context())

    def apply_bklog_for_bcs(self, cluster_id: str, namespace: str):
        for apply_config in self.APPLY_CONFIG:
            apply_config_content = self.render(apply_config)
            if TransferApi.apply_yaml_to_bcs_cluster(
                {"cluster_id": cluster_id, "namespace": namespace, "yaml_content": apply_config_content}
            ):
                logger.error(
                    f"[bcs] apply bklog config [{apply_config}] failed apply_config_content [{apply_config_content}]"
                )
                raise ApplyConfigForBcsException
            logger.info(f"[bcs] apply bklog config [{apply_config}] success")

    @atomic
    def register_bklog_for_bcs(self, cluster_id, project_id, bk_biz_id):
        self.register_cluster_to_metadata(bk_biz_id, project_id, cluster_id)

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
        return TransferApi.list_metadata_bcs_cluster({"bk_biz_id": bk_biz_id})

    def list_bcs_cluster(self, bk_biz_id=None) -> list:
        bcs_clusters = BcsCcApi.list_cluster()
        if bk_biz_id:
            pass
        return bcs_clusters
