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
from django.db.transaction import atomic

from apps.log_clustering.constants import (
    DEFAULT_SCENARIO,
    DEFAULT_LABEL,
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
    DEFAULT_PATTERN_MONITOR_MSG,
    DEFAULT_PATTERN_RECOVER_MSG,
    DEFAULT_METRIC,
    DEFAULT_CLUSTERING_ITEM_NAME,
)
from apps.log_clustering.exceptions import ClusteringIndexSetNotExistException
from apps.api import MonitorApi
from apps.log_clustering.models import SignatureStrategySettings, ClusteringConfig
from apps.log_clustering.utils.monitor import MonitorUtils
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
        self.log_index_set_data, *_ = self.index_set.indexes

    def update_strategies(self, pattern_level, actions):
        result = True
        operators = []
        for action in actions:
            strategy_id = None
            operator_msg = ""
            operator_result = True
            try:
                if action["action"] == ActionEnum.CREATE.value:
                    strategy_id = self.save_strategy(
                        pattern_level=pattern_level, signature=action["signature"], pattern=action["pattern"]
                    )["id"]
                if action["action"] == ActionEnum.DELETE.value:
                    strategy_id = action.get("strategy_id")
                    self.delete_strategy(strategy_id=strategy_id)
            except Exception as e:  # pylint:disable=broad-except
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

    @atomic
    def save_strategy(
        self,
        pattern_level="",
        signature="",
        table_id=None,
        pattern="",
        metric="",
        strategy_type=StrategiesType.NORMAL_STRATEGY,
    ):
        signature_strategy_settings = SignatureStrategySettings.objects.create(
            **{
                "signature": signature,
                "index_set_id": self.index_set_id,
                "strategy_id": None,
                "bk_biz_id": self.bk_biz_id,
                "pattern_level": pattern_level,
                "strategy_type": strategy_type,
            }
        )
        name = self._generate_name(
            index_set_name=self.index_set.index_set_name,
            strategy_type=strategy_type,
            signature_setting_id=signature_strategy_settings.id,
        )
        notice_template = DEFAULT_PATTERN_MONITOR_MSG
        recover_template = DEFAULT_PATTERN_RECOVER_MSG
        item_name = self._generate_item_name(strategy_type=strategy_type, pattern=pattern)

        query_config = self._generate_query_config(
            index_set_id=self.index_set_id,
            pattern_level=pattern_level,
            table_id=table_id or self.log_index_set_data["result_table_id"],
            metric=metric,
            signature=signature,
            strategy_type=strategy_type,
        )

        labels = DEFAULT_LABEL
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            labels += [f"LogClustering/NewLog/{self.index_set_id}"]
        else:
            labels += [f"LogClustering/NewClass/{self.index_set_id}"]

        strategy = MonitorApi.save_alarm_strategy_v2(
            params={
                "bk_biz_id": self.bk_biz_id,
                "scenario": DEFAULT_SCENARIO,
                "name": name,
                "labels": labels,
                "is_enabled": True,
                "items": [
                    {
                        "name": item_name,
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
                                log_index_set_id=self.index_set_id, bk_biz_id=self.bk_biz_id,
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
        signature_strategy_settings.strategy_id = strategy_id
        signature_strategy_settings.save()
        return strategy

    def delete_strategy(self, strategy_id):
        MonitorApi.delete_alarm_strategy_v2(params={"bk_biz_id": self.bk_biz_id, "ids": [strategy_id]})
        SignatureStrategySettings.objects.filter(strategy_id=strategy_id).delete()
        return strategy_id

    @classmethod
    def _generate_item_name(cls, strategy_type=StrategiesType.NORMAL_STRATEGY, pattern=""):
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            return f"pattern: {pattern}"
        if strategy_type == StrategiesType.NEW_CLS_strategy:
            return DEFAULT_CLUSTERING_ITEM_NAME

    @classmethod
    def _generate_query_config(
        cls,
        index_set_id,
        table_id,
        pattern_level="",
        metric="",
        signature="",
        strategy_type=StrategiesType.NORMAL_STRATEGY,
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
                    "query_string": '{}_{}: "{}"'.format(AGGS_FIELD_PREFIX, pattern_level, signature),
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
                    "agg_interval": 60 * 5,  # 新类告警聚类周期固定为5min
                    "agg_dimension": [],
                    "agg_condition": [{"key": "sensitivity", "method": "eq", "value": ["dist_09"], "condition": "and"}],
                    "metric_field": metric,
                    "unit": "",
                    "time_field": DEFAULT_TIME_FIELD,
                    "name": table_id,
                }
            ]
        return query_config

    @classmethod
    def _generate_name(cls, index_set_name, strategy_type=StrategiesType.NORMAL_STRATEGY, signature_setting_id=None):
        if strategy_type == StrategiesType.NORMAL_STRATEGY:
            return "{}_#{}".format(index_set_name, signature_setting_id)
        if strategy_type == StrategiesType.NEW_CLS_strategy:
            return _("{}_日志聚类24H新类告警").format(index_set_name)

    def update_new_cls_strategy(self, action, strategy_id=""):
        if action == ActionEnum.CREATE.value:
            strategy = self.create_new_cls_strategy()
            return strategy["id"]
        if action == ActionEnum.DELETE.value:
            strategy_id = self.delete_strategy(strategy_id=strategy_id)
            return strategy_id

    def create_new_cls_strategy(self):
        clustering_config = ClusteringConfig.objects.get(index_set_id=self.index_set_id)
        table_id = clustering_config.new_cls_pattern_rt
        return self.save_strategy(
            table_id=table_id, metric=DEFAULT_METRIC, strategy_type=StrategiesType.NEW_CLS_strategy
        )
