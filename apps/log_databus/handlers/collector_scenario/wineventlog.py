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
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
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
                {"name": event_name, "level": ",".join(event_levels), "event_id": ",".join(event_ids)}
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
                "winlog_name": [event_log["name"] for event_log in event_logs],
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
                "es_unique_field_list": ["cloudId", "serverIp", "winEventId", "winEventChannel", "winEventRecordId"],
                "separator_node_source": "",
                "separator_node_action": "",
                "separator_node_name": "",
            },
            "fields": [
                {
                    "field_name": "__ext",
                    "field_type": "object",
                    "tag": "dimension",
                    "alias_name": "ext",
                    "description": "额外信息字段",
                    "option": {"es_type": "object", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "object"},
                },
                {
                    "field_name": "winEventApi",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "api",
                    "description": "使用的API服务，在window机器上有多套服务",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventActivityId",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "activity_id",
                    "description": "全局唯一ID，标识当前活动，同一活动的事件会是同一个ID",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventChannel",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "channel",
                    "description": "事件来源那个订阅通道，和event_logs的 name 一致",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventRecordId",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "record_id",
                    "description": "记录ID，2(32)滚动更新",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventRelatedActivityId",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "related_activity_id",
                    "description": "关联活动ID",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventOpcode",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "opcode",
                    "description": "关联的操作码",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventData",
                    "field_type": "object",
                    "tag": "dimension",
                    "alias_name": "event_data",
                    "description": "事件数据",
                    "option": build_es_option_type("object", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventId",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "event_id",
                    "description": "事件ID",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventKeywords",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "keywords",
                    "description": "关键字",
                    "option": build_es_option_type("text", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventProcessPid",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "process_pid",
                    "description": "进程ID",
                    "option": build_es_option_type("long", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventProviderGuid",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "provider_guid",
                    "description": "来源GUID",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventTask",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "task",
                    "description": "事件关联的任务 ",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventUserData",
                    "field_type": "object",
                    "tag": "dimension",
                    "alias_name": "user_data",
                    "description": "关联的用户数据 ",
                    "option": build_es_option_type("object", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventUserDomain",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "user_domain",
                    "description": "关联的用户数据 ",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventUserIdentifier",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "user_identifier",
                    "description": "当前事件关联的用户的 Windows 安全标识（Security Identifier，SID )",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventUserName",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "user_name",
                    "description": "账户名",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventUserType",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "user_type",
                    "description": "账户类型",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventVersion",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "version",
                    "description": "事件版本号",
                    "option": build_es_option_type("long", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventProcessThreadId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "process_thread_id",
                    "description": "事件线程ID",
                    "option": build_es_option_type("long", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventComputerName",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "computer_name",
                    "description": "主机名，当前活动节点的名字",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventLevel",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "level",
                    "description": "日志级别",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "winEventTimeCreated",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "time_created",
                    "description": "事件产生时间",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "iterationIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "iterationindex",
                    "description": "迭代ID",
                    "option": build_es_option_type("integer", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "cloudId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "cloudid",
                    "description": "云区域ID",
                    "option": build_es_option_type("integer", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "serverIp",
                    "field_type": "string",
                    "tag": "dimension",
                    "alias_name": "ip",
                    "description": "ip",
                    "option": build_es_option_type("keyword", es_version),
                    "flat_field": True,
                },
                {
                    "field_name": "gseIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "gseindex",
                    "description": "gse索引",
                    "option": build_es_option_type("long", es_version),
                    "flat_field": True,
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
