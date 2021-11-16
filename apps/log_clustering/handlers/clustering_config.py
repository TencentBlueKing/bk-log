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
import json

from django.db.transaction import atomic

from apps.api import BkDataDatabusApi
from apps.log_clustering.constants import (
    CLUSTERING_CONFIG_EXCLUDE,
    DEFAULT_CLUSTERING_FIELDS,
)
from apps.log_clustering.exceptions import ClusteringConfigNotExistException
from apps.log_clustering.handlers.aiops.aiops_model.aiops_model_handler import AiopsModelHandler
from apps.log_clustering.models import ClusteringConfig
from apps.log_databus.constants import BKDATA_ES_TYPE_MAP
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import CollectorConfig
from apps.models import model_to_dict
from apps.utils.function import map_if


class ClusteringConfigHandler(object):
    def __init__(self, index_set_id=None, collector_config_id=None):
        self.index_set_id = index_set_id
        self.data = None
        if index_set_id:
            try:
                self.data = ClusteringConfig.objects.get(index_set_id=self.index_set_id)
            except ClusteringConfig.DoesNotExist:
                raise ClusteringConfigNotExistException()
        if collector_config_id:
            try:
                self.data = ClusteringConfig.objects.get(collector_config_id=collector_config_id)
            except ClusteringConfig.DoesNotExist:
                raise ClusteringConfigNotExistException()

    def retrieve(self):
        return model_to_dict(self.data, exclude=CLUSTERING_CONFIG_EXCLUDE)

    def update_or_create(self, params: dict):
        index_set_id = params["index_set_id"]
        collector_config_id = params["collector_config_id"]
        collector_config_name_en = params["collector_config_name_en"]
        min_members = params["min_members"]
        max_dist_list = params["max_dist_list"]
        predefined_varibles = params["predefined_varibles"]
        delimeter = params["delimeter"]
        max_log_length = params["max_log_length"]
        is_case_sensitive = params["is_case_sensitive"]
        clustering_fields = params["clustering_fields"]
        bk_biz_id = params["bk_biz_id"]
        filter_rules = params["filter_rules"]
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if clustering_config:
            clustering_config.collector_config_id = collector_config_id
            clustering_config.collector_config_name_en = collector_config_name_en
            clustering_config.min_members = min_members
            clustering_config.max_dist_list = max_dist_list
            clustering_config.predefined_varibles = predefined_varibles
            clustering_config.delimeter = delimeter
            clustering_config.max_log_length = max_log_length
            clustering_config.is_case_sensitive = is_case_sensitive
            clustering_config.clustering_fields = clustering_fields
            clustering_config.bk_biz_id = bk_biz_id
            clustering_config.filter_rules = filter_rules
            clustering_config.save()
            return model_to_dict(clustering_config, exclude=CLUSTERING_CONFIG_EXCLUDE)
        clustering_config = ClusteringConfig.objects.create(
            collector_config_id=collector_config_id,
            collector_config_name_en=collector_config_name_en,
            min_members=min_members,
            max_dist_list=max_dist_list,
            predefined_varibles=predefined_varibles,
            delimeter=delimeter,
            max_log_length=max_log_length,
            is_case_sensitive=is_case_sensitive,
            clustering_fields=clustering_fields,
            bk_biz_id=bk_biz_id,
            filter_rules=filter_rules,
            index_set_id=index_set_id,
        )
        return model_to_dict(clustering_config, exclude=CLUSTERING_CONFIG_EXCLUDE)

    def preview(
        self, input_data, min_members, max_dist_list, predefined_varibles, delimeter, max_log_length, is_case_sensitive
    ):
        aiops_experiments_debug_result = AiopsModelHandler().aiops_experiments_debug(
            input_data=input_data,
            clustering_field=DEFAULT_CLUSTERING_FIELDS,
            min_members=min_members,
            max_dist_list=max_dist_list,
            predefined_varibles=predefined_varibles,
            delimeter=delimeter,
            max_log_length=max_log_length,
            is_case_sensitive=is_case_sensitive,
        )
        return self._deal_preview(aiops_experiments_debug_result)

    @classmethod
    def _deal_preview(cls, aiops_experiments_debug_result):
        result = []
        for predict_output_data in aiops_experiments_debug_result["predict_output_data"]:
            pattern = cls._deal_pattern(json.loads(predict_output_data["pattern"]))
            token_with_regex = cls._deal_token_with_regex(json.loads(predict_output_data["token_with_regex"]))
            result.append({"patterns": pattern, "token_with_regex": token_with_regex})
        return result

    @classmethod
    def _deal_pattern(cls, pattern_result: dict):
        result = []
        for sensitivity, pattern_result in pattern_result.items():
            sensitive_pattern_list = []
            for sensitive_pattern in pattern_result:
                if isinstance(sensitive_pattern, dict):
                    sensitive_pattern_list.append("[$({})]".format(sensitive_pattern["name"]))
                    continue
                sensitive_pattern_list.append(sensitive_pattern)
            result.append({"sensitivity": sensitivity, "pattern": " ".join(sensitive_pattern_list)})
        return result

    @classmethod
    def _deal_token_with_regex(cls, token_with_regex_result: list):
        result = {}
        for token_with_regex in token_with_regex_result:
            if isinstance(token_with_regex, dict):
                result[token_with_regex["name"]] = token_with_regex["regex"]
        return result

    def collector_config_reset(self, clustering_config: ClusteringConfig):
        # todo need reset collector_config
        # collector_config = CollectorConfig.objects.get(collector_config_id=clustering_config.collector_config_id)
        pass

    def sync_bkdata_etl(self):
        """
        must at change_data_stream before apply
        :return:
        """
        collector_config = CollectorConfig.objects.get(collector_config_id=self.data.collector_config_id)
        etl_config = collector_config.get_etl_config()
        self.create_or_update_bkdata_etl(etl_config["fields"], etl_config["etl_params"])

    @atomic
    def create_or_update_bkdata_etl(self, fields, etl_params):
        self.data.etl_fields = fields
        self.data.etl_params = etl_params
        self.data.save()

        collector_config = CollectorConfig.objects.get(collector_config_id=self.data.collector_config_id)
        _, table_id = collector_config.table_id.split(".")
        etl_storage = EtlStorage.get_instance(etl_config=collector_config.etl_config)

        # 获取清洗配置
        collector_scenario = CollectorScenario.get_instance(
            collector_scenario_id=collector_config.collector_scenario_id
        )
        built_in_config = collector_scenario.get_built_in_config()
        time_field = built_in_config.get("time_field")
        fields_config = etl_storage.get_result_table_config(fields, etl_params, built_in_config).get("field_list", [])
        bkdata_json_config = etl_storage.get_bkdata_etl_config(fields, etl_params, built_in_config)
        params = {
            "raw_data_id": self.data.bkdata_data_id,
            "result_table_name": table_id,
            "result_table_name_alias": table_id,
            "clean_config_name": collector_config.collector_config_name,
            "description": collector_config.description,
            "bk_biz_id": collector_config.bk_biz_id,
            "fields": [
                {
                    "field_name": field.get("field_name")
                    if field.get("field_name") != time_field.get("field_name")
                    else time_field.get("alias_name"),
                    "field_type": BKDATA_ES_TYPE_MAP.get(field.get("option").get("es_type"), "string"),
                    "field_alias": field.get("description") if field.get("description") else field.get("field_name"),
                    "is_dimension": field.get("tag", "dimension") == "dimension",
                    "field_index": index,
                }
                for index, field in enumerate(fields_config, 1)
            ],
            "json_config": json.dumps(bkdata_json_config),
        }
        if not self.data.bkdata_etl_processing_id:
            result = BkDataDatabusApi.databus_cleans_post(params)
            self.data.bkdata_etl_processing_id = result["processing_id"]
            self.data.bkdata_etl_result_table_id = result["result_table_id"]
            self.data.save()
            return

        params.update({"processing_id": self.data.bkdata_etl_processing_id})
        BkDataDatabusApi.databus_cleans_put(params)

    def change_data_stream(self, topic: str, partition: int = 1):
        """
        change_data_stream
        :param topic:
        :param partition:
        :return:
        """
        collector_handler = CollectorHandler(self.data.collector_config_id)
        self.data.log_bk_data_id = CollectorScenario.change_data_stream(
            collector_handler.data, mq_topic=topic, mq_partition=partition
        )
        self.data.save()
        collector_detail = collector_handler.retrieve()

        # need drop built in field
        collector_detail["fields"] = map_if(collector_detail["fields"], if_func=lambda field: not field["is_built_in"])
        from apps.log_databus.handlers.etl import EtlHandler

        EtlHandler(self.data.collector_config_id).update_or_create(
            collector_detail["etl_config"],
            collector_detail["table_id"],
            collector_detail["storage_cluster_id"],
            collector_detail["retention"],
            collector_detail["allocation_min_days"],
            collector_detail["storage_replies"],
            etl_params=collector_detail["etl_params"],
            fields=collector_detail["fields"],
        )
