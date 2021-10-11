from apps.log_databus.constants import LogPluginInfo
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.collector_scenario.utils import build_es_option_type
from apps.utils.log import logger


class WinEventLogScenario(CollectorScenario):
    PLUGIN_NAME = LogPluginInfo.NAME
    PLUGIN_VERSION = LogPluginInfo.VERSION
    CONFIG_NAME = "bkunifylogbeat_winlog"

    def get_subscription_steps(self, data_id, params):
        event_names = params.get("winlog_name", [])
        event_ids = params.get("winlog_event_id", [])
        event_levels = params.get("winlog_level", [])
        local_params = {
            "event_logs": [
                {"event_name": event_name, "level": ",".join(event_levels), "event_id": ",".join(event_ids)}
                for event_name in event_names
            ]
        }
        return [
            {
                "id": self.PLUGIN_NAME,
                "type": "PLUGIN",
                "config": {
                    "plugin_name": self.PLUGIN_NAME,
                    "plugin_version": self.PLUGIN_VERSION,
                    "config_templates": [{"name": f"{self.CONFIG_NAME}.conf", "version": "latest"}],
                },
                "params": {
                    "context": {
                        "dataid": data_id,
                        "local": [local_params],
                    }
                },
            }
        ]

    @classmethod
    def parse_steps(cls, steps):
        try:
            step, *_ = steps
            config = step["params"]["context"]
            local, *_ = config["local"]
            event_logs = local["event_logs"]
            first_event, *_ = event_logs
            return {
                "winlog_name": [event_log["event_name"] for event_log in event_logs],
                "winlog_level": first_event["level"].split(","),
                "winlog_event_id": first_event["event_id"].split(","),
            }
        except (IndexError, KeyError, ValueError) as e:
            logger.exception(f"parse step config failed config => {steps}，error => {e}")
            return {"winlog_name": [], "winlog_level": [], "winlog_event_id": []}

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
                    "field_type": "object",
                    "tag": "dimension",
                    "alias_name": "event_data",
                    "description": "事件数据",
                    "option": build_es_option_type("object", es_version),
                },
                {
                    "field_name": "eventId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "event_id",
                    "description": "事件ID",
                    "option": build_es_option_type("integer", es_version),
                },
                {
                    "field_name": "keywords",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "keywords",
                    "description": "关键字",
                    "option": build_es_option_type("text", es_version),
                },
                {
                    "field_name": "level",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "level",
                    "description": "级别",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "logName",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "log_name",
                    "description": "日志名称",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "processId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "process_id",
                    "description": "进程ID",
                    "option": build_es_option_type("integer", es_version),
                },
                {
                    "field_name": "providerGuid",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "provider_guid",
                    "description": "来源GUID",
                    "option": build_es_option_type("integer", es_version),
                },
                {
                    "field_name": "recordNumber",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "record_number",
                    "description": "记录编号",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "sourceName",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "source_name",
                    "description": "来源",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "task",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "task",
                    "description": "任务类型",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "threadId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "thread_id",
                    "description": "线程ID",
                    "option": build_es_option_type("integer", es_version),
                },
                {
                    "field_name": "computerName",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "computer_name",
                    "description": "计算机",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "iterationIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "iterationindex",
                    "description": "迭代ID",
                    "option": build_es_option_type("integer", es_version),
                },
                {
                    "field_name": "cloudId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "cloudid",
                    "description": "云区域ID",
                    "option": build_es_option_type("integer", es_version),
                },
                {
                    "field_name": "serverIp",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "ip",
                    "description": "ip",
                    "option": build_es_option_type("keyword", es_version),
                },
                {
                    "field_name": "gseIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "gseindex",
                    "description": "gse索引",
                    "option": build_es_option_type("long", es_version),
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
