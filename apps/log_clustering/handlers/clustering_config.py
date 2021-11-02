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
from apps.log_clustering.constants import CLUSTERING_CONFIG_EXCLUDE
from apps.log_clustering.exceptions import ClusteringConfigNotExistException
from apps.log_clustering.models import ClusteringConfig
from apps.models import model_to_dict


class ClusteringConfigHandler(object):
    def __init__(self, index_set_id=None):
        self.index_set_id = index_set_id
        self.data = None
        if index_set_id:
            try:
                self.data = ClusteringConfig.objects.get(index_set_id=self.index_set_id)
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
