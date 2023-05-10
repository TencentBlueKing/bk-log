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
from django.utils.translation import ugettext as _
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import IS_AUTO_DEPLOY_PLUGIN
from apps.utils.log import logger
from apps.log_databus.handlers.collector_scenario.base import CollectorScenario
from apps.log_databus.constants import LogPluginInfo


class RedisSlowLogCollectorScenario(CollectorScenario):
    """
    Redis 慢日志采集
    """

    PLUGIN_NAME = LogPluginInfo.NAME
    PLUGIN_VERSION = LogPluginInfo.VERSION
    CONFIG_NAME = "bkunifylogbeat_redis_slowlog"

    def get_subscription_steps(self, data_id, params, collector_config_id=None):
        """
        params内包含的参数
        params.redis_host: 采集目标, list
            redis_hosts = ["host1:port1", "host2:port2"]
        params.redis_password: redis密码, str
            redis_password = "password"
        params.redis_password_file: redis密码文件, str
        """

        local_params = {
            "hosts": params.get("redis_hosts", []),
            "password": params.get("redis_password", ""),
            "password_file": params.get("redis_password_file", ""),
        }
        local_params = self._add_ext_labels(local_params, params, collector_config_id)
        local_params = self._add_ext_meta(local_params, params)
        steps = [
            {
                "id": self.PLUGIN_NAME,  # 这里的ID不能随意变更，需要同步修改解析的逻辑(parse_steps)
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
        """
        try:
            for step in steps:
                if step["id"] == cls.PLUGIN_NAME:
                    config = step["params"]["context"]
                    break
            else:
                config = steps[0]["params"]["context"]

            local, *_ = config["local"]
            return {"redis_hosts": local["hosts"]}
        except (IndexError, KeyError, ValueError) as e:
            logger.exception(f"parse step config failed config => {steps}，error => {e}")
            return {"redis_hosts": []}

    @classmethod
    def get_built_in_config(cls, es_version="5.X"):
        """
        获取采集器标准字段
        """
        return {
            "option": {
                "es_unique_field_list": ["cloudId", "serverIp", "gseIndex", "iterationIndex", "bk_host_id"],
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
