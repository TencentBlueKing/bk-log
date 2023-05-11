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
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import IS_AUTO_DEPLOY_PLUGIN
from apps.utils.log import logger
from apps.log_databus.handlers.collector_scenario.base import CollectorScenario
from apps.log_databus.handlers.collector_scenario.utils import deal_collector_scenario_param
from apps.log_databus.constants import LogPluginInfo
from django.utils.translation import ugettext as _


class SectionCollectorScenario(CollectorScenario):
    """
    段日志采集
    """

    PLUGIN_NAME = LogPluginInfo.NAME
    PLUGIN_VERSION = LogPluginInfo.VERSION

    def get_subscription_steps(self, data_id, params, collector_config_id=None):
        """
        获取订阅步骤
        :param data_id: 数据源ID
        :param params: 同创建采集项的请求参数
        :param collector_config_id: 采集配置ID
        {
            "paths": ["/log/abc"],
            "conditions": {
                "type": "match",
                "match_type": "include",
                "match_content": "delete",
                "separator": "|",
                "separator_filters": [
                    {
                        "fieldindex": 1,
                        "word": "",
                        "op": "=",
                        "logic_op": "and"
                    }
                ]
            },
        }
        :return: steps
        """
        filters, params = deal_collector_scenario_param(params)
        local_params = {
            "filters": filters,
            "multiline_pattern": params["multiline_pattern"],
            "multiline_max_lines": params["multiline_max_lines"],
            "multiline_timeout": params["multiline_timeout"],
        }

        local_params = self._deal_text_public_params(local_params, params, collector_config_id)
        steps = [
            {
                "id": self.PLUGIN_NAME,  # 这里的ID不能随意变更，需要同步修改解析的逻辑(parse_steps)
                "type": "PLUGIN",
                "config": {
                    "plugin_name": self.PLUGIN_NAME,
                    "plugin_version": self.PLUGIN_VERSION,
                    "config_templates": [{"name": f"{self.PLUGIN_NAME}.conf", "version": "latest"}],
                },
                "params": {"context": {"dataid": data_id, "local": [local_params]}},
            },
        ]

        if FeatureToggleObject.switch(IS_AUTO_DEPLOY_PLUGIN):
            steps.insert(
                0,
                # 增加前置检测步骤，如果采集器不存在，则尝试安装
                {
                    "id": f"main:{self.PLUGIN_NAME}",
                    "type": "PLUGIN",
                    "config": {
                        "job_type": "MAIN_INSTALL_PLUGIN",
                        "check_and_skip": True,
                        "is_version_sensitive": False,
                        "plugin_name": self.PLUGIN_NAME,
                        "plugin_version": self.PLUGIN_VERSION,
                        "config_templates": [
                            {"name": f"{self.PLUGIN_NAME}.conf", "version": "latest", "is_main": True}
                        ],
                    },
                    "params": {"context": {}},
                },
            )
        return steps

    @classmethod
    def parse_steps(cls, steps):
        """
        解析订阅步骤至参数，
        :param steps: 订阅步骤
        [
            {
                "config": {
                    "config_templates": [
                        {
                            "version": "7.0.11",
                            "name": "bklogbeat.conf"
                        }
                    ],
                    "plugin_name": "bklogbeat",
                    "plugin_version": "7.0.11"
                },
                "type": "PLUGIN",
                "id": "bklogbeat",
                "params": {
                    "context": {
                        "dataid": 123,
                        "local": {
                            "paths": [],
                            "encoding": "utf-8",
                            "filters": [{
                                "fieldindex": 1,
                                "word": "",
                                "op": "=",
                            }],
                            "delimiter": "|"
                        }
                    }
                }
            }
        ]
        :return:
        """
        try:
            for step in steps:
                if step["id"] == cls.PLUGIN_NAME:
                    config = step["params"]["context"]
                    break
            else:
                config = steps[0]["params"]["context"]

            try:
                separator_filters = []
                # 如果是逻辑或，会拆成多个配置下发
                logic_op = "and" if len(config["local"][0]["filters"]) <= 1 else "or"
                for filter_item in config["local"][0]["filters"]:
                    for condition_item in filter_item["conditions"]:
                        separator_filters.append(
                            {
                                "fieldindex": condition_item["index"],
                                "word": condition_item["key"],
                                "op": condition_item["op"],
                                "logic_op": logic_op,
                            }
                        )
            except (IndexError, KeyError, ValueError):
                separator_filters = []

            match_content = ""
            if separator_filters and separator_filters[0]["fieldindex"] == "-1":
                _type = "match"
                match_content = separator_filters[0].get("word", "")
                separator_filters = []
            elif not separator_filters:
                _type = "match"
            else:
                _type = "separator"

            params = {
                "paths": config["local"][0]["paths"],
                "conditions": {
                    "separator": config["local"][0]["delimiter"],
                    "separator_filters": separator_filters,
                    "type": _type,
                    "match_type": "include",  # 目前只支持include
                    "match_content": match_content,
                },
                "multiline_pattern": config["local"][0]["multiline_pattern"],
                "multiline_max_lines": config["local"][0]["multiline_max_lines"],
                "multiline_timeout": config["local"][0]["multiline_timeout"],
                "encoding": config["local"][0]["encoding"],
            }
        except (IndexError, KeyError, ValueError) as e:
            logger.exception(f"解析订阅步骤失败，参数:{steps}，错误:{e}")
            params = {
                "paths": [],
                "conditions": {
                    "type": "match",
                    "match_type": "include",
                    "match_content": "",
                    "separator": "",
                    "separator_filters": [],
                },
                "multiline_pattern": "",
                "multiline_max_lines": "",
                "multiline_timeout": "",
            }
        return params

    @classmethod
    def get_built_in_config(cls, es_version="5.X"):
        """
        获取采集器标准字段
        """
        return {
            "option": {
                "es_unique_field_list": ["cloudId", "serverIp", "path", "gseIndex", "iterationIndex", "bk_host_id"],
                "separator_node_source": "",
                "separator_node_action": "",
                "separator_node_name": "",
            },
            "fields": [
                {
                    "field_name": "bk_host_id",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "bk_host_id",
                    "description": "主机ID",
                    "option": {"es_type": "integer", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "integer"},
                },
                {
                    "field_name": "__ext",
                    "field_type": "object",
                    "tag": "dimension",
                    "alias_name": "ext",
                    "description": _("额外信息字段"),
                    "option": {"es_type": "object", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "object"},
                },
                {
                    "field_name": "cloudId",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "cloudid",
                    "description": _("云区域ID"),
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
                    "description": _("日志路径"),
                    "option": {"es_type": "keyword", "es_include_in_all": True}
                    if es_version.startswith("5.")
                    else {"es_type": "keyword"},
                },
                {
                    "field_name": "gseIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "gseindex",
                    "description": _("gse索引"),
                    "option": {"es_type": "long", "es_include_in_all": False}
                    if es_version.startswith("5.")
                    else {"es_type": "long"},
                },
                {
                    "field_name": "iterationIndex",
                    "field_type": "float",
                    "tag": "dimension",
                    "alias_name": "iterationindex",
                    "description": _("迭代ID"),
                    "flat_field": True,
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
                "description": _("数据时间"),
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
