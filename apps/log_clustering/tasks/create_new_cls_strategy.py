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

from celery.task import task

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import BKDATA_CLUSTERING_TOGGLE
from apps.log_clustering.constants import StrategiesType, DEFAULT_METRIC
from apps.log_clustering.handlers.clustering_monitor import ClusteringMonitorHandler
from apps.log_clustering.models import ClusteringConfig


@task(ignore_result=True)
def create_new_cls_strategy(index_set_id):
    if not FeatureToggleObject.switch(BKDATA_CLUSTERING_TOGGLE):
        return
    conf = FeatureToggleObject.toggle(BKDATA_CLUSTERING_TOGGLE).feature_config
    bk_biz_id = conf.get("bk_biz_id")
    clustering_monitor_handler = ClusteringMonitorHandler(index_set_id=index_set_id, bk_biz_id=bk_biz_id)
    clustering_config = ClusteringConfig.objects.get(index_set_id=index_set_id)
    table_id = clustering_config.after_treat_flow["judge_new_class"]["result_table_id"]
    clustering_monitor_handler.save_strategy(
        table_id=table_id, metric=DEFAULT_METRIC, strategy_type=StrategiesType.NEW_CLS_strategy
    )
