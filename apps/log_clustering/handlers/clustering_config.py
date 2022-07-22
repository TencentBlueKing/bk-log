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
import json
import re

from django.utils.translation import ugettext_lazy as _

from apps.log_clustering.constants import (
    CLUSTERING_CONFIG_EXCLUDE,
    DEFAULT_CLUSTERING_FIELDS,
)
from apps.log_clustering.exceptions import (
    ClusteringConfigNotExistException,
    BkdataRegexException,
    BkdataFieldsException,
)
from apps.log_clustering.handlers.aiops.aiops_model.aiops_model_handler import AiopsModelHandler
from apps.log_clustering.handlers.pipline_service.constants import OperatorServiceEnum
from apps.log_clustering.models import ClusteringConfig
from apps.log_clustering.tasks.msg import send
from apps.log_clustering.tasks.flow import update_filter_rules, update_clustering_clean
from apps.log_databus.constants import EtlConfig
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.models import CollectorConfig
from apps.log_search.models import LogIndexSet
from apps.models import model_to_dict
from apps.utils.function import map_if
from apps.utils.local import activate_request
from apps.utils.log import logger
from apps.utils.thread import generate_request


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

    def start(self):
        from apps.log_clustering.handlers.pipline_service.aiops_service import operator_aiops_service

        pipeline_id = operator_aiops_service(self.index_set_id)
        return pipeline_id

    def update_or_create(self, params: dict):
        index_set_id = params["index_set_id"]
        log_index_set = LogIndexSet.objects.filter(index_set_id=index_set_id).first()
        collector_config_id = log_index_set.collector_config_id
        category_id = log_index_set.category_id
        log_index_set_data, *_ = log_index_set.indexes
        collector_config_name_en = ""
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if collector_config_id:
            collector_config = CollectorConfig.objects.filter(collector_config_id=collector_config_id).first()
            collector_config_name_en = (
                clustering_config.collector_config_name_en
                if clustering_config
                else collector_config.collector_config_name_en
            )
        source_rt_name = log_index_set_data["result_table_id"]
        min_members = params["min_members"]
        max_dist_list = params["max_dist_list"]
        predefined_varibles = params["predefined_varibles"]
        delimeter = params["delimeter"]
        max_log_length = params["max_log_length"]
        is_case_sensitive = params["is_case_sensitive"]
        clustering_fields = params["clustering_fields"]
        bk_biz_id = params["bk_biz_id"]
        filter_rules = params["filter_rules"]
        signature_enable = params["signature_enable"]
        from apps.log_clustering.handlers.pipline_service.aiops_service import operator_aiops_service

        if clustering_config:
            (
                change_filter_rules,
                change_model_config,
                change_clustering_fields,
                create_service,
            ) = self.check_clustering_config_update(
                clustering_config=clustering_config,
                filter_rules=filter_rules,
                min_members=min_members,
                max_dist_list=max_dist_list,
                predefined_varibles=predefined_varibles,
                delimeter=delimeter,
                max_log_length=max_log_length,
                is_case_sensitive=is_case_sensitive,
                clustering_fields=clustering_fields,
                signature_enable=signature_enable,
            )
            clustering_config.min_members = min_members
            clustering_config.max_dist_list = max_dist_list
            clustering_config.predefined_varibles = predefined_varibles
            clustering_config.delimeter = delimeter
            clustering_config.max_log_length = max_log_length
            clustering_config.is_case_sensitive = is_case_sensitive
            clustering_config.clustering_fields = clustering_fields
            clustering_config.bk_biz_id = bk_biz_id
            clustering_config.filter_rules = filter_rules
            clustering_config.signature_enable = signature_enable
            clustering_config.category_id = category_id
            clustering_config.save()

            if create_service:
                self.create_service(
                    index_set_id=index_set_id,
                    collector_config_id=collector_config_id,
                    clustering_fields=clustering_fields,
                )

            if change_filter_rules:
                # 更新filter_rule
                update_filter_rules.delay(index_set_id=index_set_id)
            if change_model_config:
                # 更新aiops model
                operator_aiops_service(index_set_id, operator=OperatorServiceEnum.UPDATE)
            if change_clustering_fields:
                # 更新flow
                update_clustering_clean.delay(index_set_id=index_set_id)

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
            signature_enable=signature_enable,
            source_rt_name=source_rt_name,
            category_id=category_id,
        )
        if signature_enable:
            self.create_service(
                index_set_id=index_set_id, clustering_fields=clustering_fields, collector_config_id=collector_config_id
            )
        return model_to_dict(clustering_config, exclude=CLUSTERING_CONFIG_EXCLUDE)

    def create_service(self, index_set_id, clustering_fields, collector_config_id=None):
        from apps.log_clustering.handlers.pipline_service.aiops_service import operator_aiops_service

        if collector_config_id:
            collector_config = CollectorConfig.objects.get(collector_config_id=collector_config_id)
            all_etl_config = collector_config.get_etl_config()
            self.pre_check_fields(
                fields=all_etl_config["fields"],
                etl_config=collector_config.etl_config,
                clustering_fields=clustering_fields,
            )
        pipeline_id = operator_aiops_service(index_set_id)
        send.delay(index_set_id=index_set_id, pipeline_id=pipeline_id)

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
                    sensitive_pattern_list.append("#{}#".format(sensitive_pattern["name"]))
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

    def change_data_stream(self, topic: str, partition: int = 1):
        """
        change_data_stream
        :param topic:
        :param partition:
        :return:
        """
        collector_handler = CollectorHandler(self.data.collector_config_id)
        if not self.data.log_bk_data_id:
            self.data.log_bk_data_id = CollectorScenario.change_data_stream(
                collector_handler.data, mq_topic=topic, mq_partition=partition
            )
            self.data.save()
        # 设置request线程变量
        activate_request(generate_request())

        collector_detail = collector_handler.retrieve(use_request=False)

        # need drop built in field
        collector_detail["fields"] = map_if(collector_detail["fields"], if_func=lambda field: not field["is_built_in"])
        from apps.log_databus.handlers.etl import EtlHandler

        etl_handler = EtlHandler.get_instance(self.data.collector_config_id)
        etl_handler.update_or_create(
            collector_detail["etl_config"],
            collector_detail["table_id"],
            collector_detail["storage_cluster_id"],
            collector_detail["retention"],
            collector_detail.get("allocation_min_days", 0),
            collector_detail["storage_replies"],
            etl_params=collector_detail["etl_params"],
            fields=collector_detail["fields"],
        )

    @staticmethod
    def check_clustering_config_update(
        clustering_config,
        filter_rules,
        min_members,
        max_dist_list,
        predefined_varibles,
        delimeter,
        max_log_length,
        is_case_sensitive,
        clustering_fields,
        signature_enable,
    ):
        """
        判断是否需要进行对应更新操作
        """
        # 此时不需要做任何更新动作
        if not signature_enable:
            return False, False, False, False
        # 此时需要创建service 而不是更新service
        if not clustering_config.signature_enable:
            return False, False, False, True
        change_filter_rules = clustering_config.filter_rules != filter_rules
        change_model_config = model_to_dict(
            clustering_config,
            fields=[
                "min_members",
                "max_dist_list",
                "predefined_varibles",
                "delimeter",
                "max_log_length",
                "is_case_sensitive",
            ],
        ) != {
            "min_members": min_members,
            "max_dist_list": max_dist_list,
            "predefined_varibles": predefined_varibles,
            "delimeter": delimeter,
            "max_log_length": max_log_length,
            "is_case_sensitive": is_case_sensitive,
        }
        change_clustering_fields = clustering_config.clustering_fields != clustering_fields

        return change_filter_rules, change_model_config, change_clustering_fields, False

    @classmethod
    def pre_check_fields(cls, fields, etl_config, clustering_fields):
        """
        判断字段是否符合要求
        """
        for field in fields:
            field_name = field.get("field_name")
            alias_name = field.get("alias_name") or field.get("field_name")
            # 正则需要符合计算平台正则要求
            if etl_config == EtlConfig.BK_LOG_REGEXP and not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9]*", field_name):
                logger.error(_("正则表达式字段名: {}不符合计算平台标准[a-zA-Z][a-zA-Z0-9]*").format(field_name))
                raise BkdataRegexException(BkdataRegexException.MESSAGE.format(field_name=field_name))
            # 存在聚类字段则允许跳出循环
            if alias_name == clustering_fields:
                break
        else:
            if clustering_fields == DEFAULT_CLUSTERING_FIELDS:
                return True
            logger.error(_("不允许删除参与日志聚类字段: {}").format(clustering_fields))
            raise ValueError(BkdataFieldsException(BkdataFieldsException.MESSAGE.format(field=clustering_fields)))

        return True
