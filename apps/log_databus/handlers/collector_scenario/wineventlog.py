from apps.log_databus.constants import LogPluginInfo
from apps.log_databus.handlers.collector_scenario import CollectorScenario


class WinEventLogScenario(CollectorScenario):

    PLUGIN_NAME = LogPluginInfo.NAME
    PLUGIN_VERSION = LogPluginInfo.VERSION

    def get_subscription_steps(self, data_id, params):
        pass

    @classmethod
    def parse_steps(cls, steps):
        pass

    @classmethod
    def get_built_in_config(cls, es_version="5.X"):
        """
        获取采集器标准字段
        """
        return {
            "option": {
                "es_unique_field_list": ["cloudId", "serverIp", "path", "gseIndex", "iterationIndex"],
                "separator_node_source": "",
                "separator_node_action": "",
                "separator_node_name": "",
            },
            "fields": [
                {
                    "field_name": "eventData",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "event_data",
                    "description": "事件数据",
                    "option": {"es_type": "integer", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "integer"},
                },
                {
                    "field_name": "serverIp",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "ip",
                    "description": "ip",
                    "option": {"es_type": "keyword", "es_include_in_all": True}
                    if es_version.startswith("5.")
                    else {"es_type": "keyword"},
                },
                {
                    "field_name": "path",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "filename",
                    "description": "日志路径",
                    "option": {"es_type": "keyword", "es_include_in_all": True}
                    if es_version.startswith("5.")
                    else {"es_type": "keyword"},
                },
                {
                    "field_name": "gseIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "gseindex",
                    "description": "gse索引",
                    "option": {"es_type": "long", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "long"},
                },
                {
                    "field_name": "iterationIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "iterationindex",
                    "description": "迭代ID",
                    "option": {"es_type": "integer", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "integer"},
                },
            ],
            "time_field": {
                "field_name": "dtEventTimeStamp",
                "field_type": "timestamp",
                "tag": "dimension",
                "alias_name": "utctime",
                "description": "数据时间",
                "option": {
                    "es_type": "date",
                    "es_include_in_all": False,
                    "es_format": "epoch_millis",
                    "time_format": "yyyy-MM-dd HH:mm:ss",
                    "time_zone": 0,
                }
                if es_version.startswith("5.")
                else {
                    "es_type": "date",
                    "es_format": "epoch_millis",
                    "time_format": "yyyy-MM-dd HH:mm:ss",
                    "time_zone": 0,
                },
            },
        }
