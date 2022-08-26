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
import arrow
from celery.task import task

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import BKDATA_CLUSTERING_TOGGLE
from apps.log_clustering.exceptions import ClusteringClosedException
from apps.log_clustering.models import ClusteringConfig
from apps.log_measure.events import NOTIFY_EVENT
from apps.log_search.handlers.search.aggs_handlers import AggsViewAdapter
from apps.log_search.models import LogIndexSet, Space
from apps.utils.local import set_local_param


@task(ignore_result=True)
def send(index_set_id):
    clustering_config = ClusteringConfig.objects.get(index_set_id=index_set_id)
    log_index_set = LogIndexSet.objects.get(index_set_id=index_set_id)
    doc_count = get_doc_count(index_set_id=index_set_id, bk_biz_id=clustering_config.bk_biz_id)
    space = Space.objects.get(bk_biz_id=clustering_config.bk_biz_id)

    if not FeatureToggleObject.switch(BKDATA_CLUSTERING_TOGGLE):
        raise ClusteringClosedException()
    conf = FeatureToggleObject.toggle(BKDATA_CLUSTERING_TOGGLE).feature_config

    if doc_count > conf.get("auto_approve_doc_count", 0):
        # 千万级别的需要人工审批
        msg = _("[待审批] 有新聚类创建，请关注！索引集id: {}, 索引集名称: {}, 业务id: {}, 业务名称: {}, 创建者: {}, 过去一天的数据量doc_count={}").format(
            index_set_id,
            log_index_set.index_set_name,
            clustering_config.bk_biz_id,
            space.space_name,
            clustering_config.created_by,
            doc_count,
        )
    else:
        from apps.log_clustering.handlers.pipline_service.aiops_service import operator_aiops_service

        pipeline_id = operator_aiops_service(index_set_id)
        msg = _(
            "[自动接入] 有新聚类创建，请关注！索引集id: {}, 索引集名称: {}, 业务id: {}, 业务名称: {}, 创建者: {}, 过去一天的数据量doc_count={}，任务ID: {}"
        ).format(
            index_set_id,
            log_index_set.index_set_name,
            clustering_config.bk_biz_id,
            space.space_name,
            clustering_config.created_by,
            doc_count,
            pipeline_id,
        )

    NOTIFY_EVENT(
        content=f"{msg}", dimensions={"index_set_id": clustering_config.index_set_id, "msg_type": "clustering_config"},
    )


def get_doc_count(index_set_id, bk_biz_id):
    set_local_param("time_zone", settings.TIME_ZONE)
    now = arrow.now()
    aggs_result = AggsViewAdapter().date_histogram(
        index_set_id=index_set_id,
        query_data={
            "bk_biz_id": bk_biz_id,
            "addition": [],
            "host_scopes": {"modules": [], "ips": "", "target_nodes": [], "target_node_type": ""},
            "start_time": now.shift(days=-1).format(),
            "end_time": now.format("YYYY-MM-DD HH:mm:ss"),
            "time_range": "customized",
            "keyword": "*",
            "begin": 0,
            "size": 500,
            "fields": [],
            "interval": "1d",
        },
    )
    doc_count = 0
    for bucket in aggs_result["aggs"]["group_by_histogram"]["buckets"]:
        doc_count += bucket["doc_count"]

    return doc_count
