from apps.log_databus.handlers.collector_plugin import CollectorPluginHandler
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.serializers import CollectorEtlStorageSerializer


class TransferCollectorPluginHandler(CollectorPluginHandler):
    def _build_plugin_etl_template(self, params: dict) -> dict:
        params["etl_template"].update(
            {
                "retention": self.collector_plugin.retention,
                "table_id": self.collector_plugin.collector_plugin_name_en,
                "etl_config": self.collector_plugin.etl_config,
                "storage_cluster_id": self.collector_plugin.storage_cluster_id,
                "allocation_min_days": self.collector_plugin.allocation_min_days,
                "storage_replies": self.collector_plugin.storage_replies,
            }
        )
        serializer = CollectorEtlStorageSerializer(data=params["etl_template"])
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def _create_instance_etl_storage(self, params: dict) -> None:
        etl_config = {
            "etl_config": params.get("etl_config"),
            "table_id": params.get("table_id"),
            "etl_params": params.get("etl_params"),
            "fields": params.get("fields"),
            "storage_cluster_id": params.get("storage_cluster_id"),
            "retention": params.get("retention"),
            "allocation_min_days": params.get("allocation_min_days"),
            "storage_replies": params.get("storage_replies"),
        }
        EtlHandler(self.collector_config_id).update_or_create(**etl_config)
