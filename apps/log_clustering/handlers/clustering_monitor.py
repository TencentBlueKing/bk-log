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
from apps.log_clustering.constants import (
    DEFAULT_SCENARIO,
    DEFAULT_LABELS,
    DEFAULT_NO_DATA_CONFIG,
    DEFAULT_EXPRESSION,
    DEFAULT_DATA_SOURCE_LABEL,
    DEFAULT_DATA_TYPE_LABEL,
    AGGS_FIELD_PREFIX,
    DEFAULT_AGG_INTERVAL,
    DEFAULT_TIME_FIELD,
    DEFAULT_ALGORITHMS,
    DEFAULT_DETECTS,
    DEFAULT_ACTION_TYPE,
    DEFAULT_ACTION_CONFIG,
    ActionEnum,
    StrategiesType,
    DEFAULT_DATA_SOURCE_LABEL_BKDATA,
    DEFAULT_DATA_TYPE_LABEL_BKDATA,
    DEFAULT_AGG_METHOD_BKDATA,
)
from apps.log_clustering.exceptions import ClusteringIndexSetNotExistException
from apps.api import MonitorApi
from apps.log_clustering.models import SignatureStrategySettings
from apps.log_clustering.utils.monitor import MonitorUtils
from apps.log_databus.models import CollectorConfig
from apps.log_search.models import LogIndexSet


class ClusteringMonitorHandler(object):
    def __init__(self, index_set_id, bk_biz_id: int):
        self.index_set_id = index_set_id
        self.bk_biz_id = bk_biz_id
        self.index_set = LogIndexSet.objects.filter(index_set_id=self.index_set_id).first()
        if not self.index_set:
            raise ClusteringIndexSetNotExistException(
                ClusteringIndexSetNotExistException.MESSAGE.format(index_set_id=self.index_set_id)
            )
        self.collector_config = CollectorConfig.objects.get(collector_config_id=self.index_set.collector_config_id)
        if not self.collector_config:
            raise ClusteringIndexSetNotExistException(
                ClusteringIndexSetNotExistException.MESSAGE.format(index_set_id=self.index_set_id)
            )

    def update_strategies(self, log_level, actions):
        result = True
        operators = []
        for action in actions:
            strategy_id = None
            operator_msg = ""
            operator_result = True
            try:
                if action["action"] == ActionEnum.CREATE.value:
                    strategy_id = self.save_strategy(
                        log_level=log_level, signature=action["signature"], pattern=action["pattern"]
                    )["id"]
                if action["action"] == ActionEnum.DELETE.value:
                    strategy_id = action.get("strategy_id")
                    self.delete_strategy(strategy_id=strategy_id)
            except Exception as e:  # pylint:disable=bare-except
                operator_result = False
                operator_msg = str(e)
                result = False
            finally:
                operators.append(
                    {
                        "signature": action["signature"],
                        "strategy_id": strategy_id,
                        "operator_result": operator_result,
                        "operator_msg": operator_msg,
                    }
                )
        return {"result": result, "operators": operators}

    def save_strategy(
        self,
        log_level="",
        signature="",
        table_id=None,
        pattern="",
        metric="",
        strategy_type=StrategiesType.NORMAL_STRATEGY,
    ):
        name = self._generate_name(
            index_set_name=self.index_set.index_set_name, signature=signature, strategy_type=strategy_type
        )
        notice_template = self._generate_notice_template(
            index_set_name=self.index_set.index_set_name,
            signature=signature,
            pattern=pattern,
            strategy_type=strategy_type,
        )
        recover_template = self._generate_recover_template(
            index_set_name=self.index_set.index_set_name,
            signature=signature,
            pattern=pattern,
            strategy_type=strategy_type,
        )
        query_config = self._generate_query_config(
            index_set_id=self.index_set_id,
            log_level=log_level,
            table_id=table_id or self.collector_config.table_id,
            metric=metric,
            signature=signature,
            strategy_type=strategy_type,
        )
        strategy = MonitorApi.save_alarm_strategy_v2(
            params={
                "bk_biz_id": self.bk_biz_id,
                "scenario": DEFAULT_SCENARIO,
                "name": name,
                "labels": DEFAULT_LABELS,
                "is_enabled": True,
                "items": [
                    {
                        "name": name,
                        "no_data_config": DEFAULT_NO_DATA_CONFIG,
                        "target": [[]],
                        "expression": DEFAULT_EXPRESSION,
                        "origin_sql": "",
                        "query_configs": query_config,
                        "algorithms": DEFAULT_ALGORITHMS,
                    }
                ],
                "detects": DEFAULT_DETECTS,
                "actions": [
                    {
                        "type": DEFAULT_ACTION_TYPE,
                        "config": DEFAULT_ACTION_CONFIG,
                        "notice_group_ids": [
                            MonitorUtils.get_or_create_notice_group(
                                collector_config_id=self.collector_config.collector_config_id,
                                log_index_set_id=self.index_set_id,
                                bk_biz_id=self.bk_biz_id,
                            )
                        ],
                        "notice_template": {
                            "anomaly_template": notice_template,
                            "recovery_template": recover_template,
                        },
                    }
                ],
            }
        )
        strategy_id = strategy["id"]
        SignatureStrategySettings.objects.create(
            **{
                "signature": signature,
                "index_set_id": self.index_set_id,
                "strategy_id": strategy_id,
                "bk_biz_id": self.bk_biz_id,
            }
        )
        return strategy

    def delete_strategy(self, strategy_id):
        MonitorApi.delete_alarm_strategy_v2(params={"bk_biz_id": self.bk_biz_id, "ids": [strategy_id]})
        SignatureStrategySettings.objects.filter(strategy_id=strategy_id).delete()
        return strategy_id

    @classmethod
    def _generate_notice_template(
        cls, index_set_name, signature, pattern="", strategy_type=StrategiesType.NORMAL_STRATEGY
    ):
        notice_template = ""
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            notice_template = """{{{{content.level}}}}
                {{{{content.begin_time}}}}
                {{{{content.time}}}}
                {{{{content.duration}}}}
                {{{{strategy.name}}}}日志聚类pattern告警
                索引集名称:{index_set_name}
                signature:{signature}
                pattern:{pattern}
                {{{{alarm.detail_url}}}}""".format(
                index_set_name=index_set_name, signature=signature, pattern=pattern
            )
        if strategy_type == StrategiesType.NEW_CLS_strategy:
            notice_template = """{{{{content.level}}}}
                {{{{content.begin_time}}}}
                {{{{content.time}}}}
                {{{{content.duration}}}}
                {{{{strategy.name}}}}日志聚类新类告警
                索引集名称:{index_set_name}
                signature:{{{{alarm.dimensions["dimension_name"].display_value}}}}
                {{{{alarm.detail_url}}}}""".format(
                index_set_name=index_set_name
            )
        return notice_template

    @classmethod
    def _generate_recover_template(
        cls, index_set_name, signature, pattern="", strategy_type=StrategiesType.NORMAL_STRATEGY
    ):
        recover_template = ""
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            recover_template = """{{{{content.level}}}}
                {{{{content.begin_time}}}}
                {{{{content.time}}}}
                {{{{content.duration}}}}
                {{{{strategy.name}}}}日志聚类pattern告警恢复
                索引集名称:{index_set_name}
                signature:{signature}
                pattern:{pattern}
                {{{{alarm.detail_url}}}}""".format(
                index_set_name=index_set_name, signature=signature, pattern=pattern
            )
        if strategy_type == StrategiesType.NEW_CLS_strategy:
            recover_template = """{{{{content.level}}}}
                {{{{content.begin_time}}}}
                {{{{content.time}}}}
                {{{{content.duration}}}}
                {{{{strategy.name}}}}日志聚类新类告警恢复
                索引集名称:{index_set_name}
                signature:{{{{alarm.dimensions["dimension_name"].display_value}}}}
                {{{{alarm.detail_url}}}}""".format(
                index_set_name=index_set_name
            )
        return recover_template

    @classmethod
    def _generate_query_config(
        cls, index_set_id, table_id, log_level="", metric="", signature="", strategy_type=StrategiesType.NORMAL_STRATEGY
    ):
        query_config = []
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            query_config = [
                {
                    "data_source_label": DEFAULT_DATA_SOURCE_LABEL,
                    "data_type_label": DEFAULT_DATA_TYPE_LABEL,
                    "alias": DEFAULT_EXPRESSION,
                    "metric_id": "bk_log_search.index_set.{}".format(index_set_id),
                    "functions": [],
                    "query_string": '{}_{}: "{}"'.format(AGGS_FIELD_PREFIX, log_level, signature),
                    "result_table_id": table_id,
                    "index_set_id": index_set_id,
                    "agg_interval": DEFAULT_AGG_INTERVAL,
                    "agg_dimension": [],
                    "agg_condition": [],
                    "time_field": DEFAULT_TIME_FIELD,
                    "name": table_id,
                }
            ]
        if strategy_type == StrategiesType.NEW_CLS_strategy:
            query_config = [
                {
                    "data_source_label": DEFAULT_DATA_SOURCE_LABEL_BKDATA,
                    "data_type_label": DEFAULT_DATA_TYPE_LABEL_BKDATA,
                    "alias": DEFAULT_EXPRESSION,
                    "metric_id": "bk_data.{table_id}.{metric}".format(table_id=table_id, metric=metric),
                    "functions": [],
                    "result_table_id": table_id,
                    "agg_method": DEFAULT_AGG_METHOD_BKDATA,
                    "agg_interval": DEFAULT_AGG_INTERVAL,
                    "agg_dimension": [metric],
                    "agg_condition": [],
                    "metric_field": metric,
                    "unit": "",
                    "time_field": DEFAULT_TIME_FIELD,
                    "name": table_id,
                }
            ]
        return query_config

    @classmethod
    def _generate_name(cls, index_set_name, signature="", strategy_type=StrategiesType.NORMAL_STRATEGY):
        name = ""
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            name = "{}_signature_{}".format(index_set_name, signature)
        if strategy_type == StrategiesType.NEW_CLS_strategy:
            name = "{}_new_cls".format(index_set_name)
        return name
