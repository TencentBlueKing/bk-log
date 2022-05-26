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

from apps.log_clustering.models import ClusteringConfig
from apps.log_measure.events import NOTIFY_EVENT
from apps.log_search.handlers.search.aggs_handlers import AggsViewAdapter
from apps.utils.local import set_local_param


@task(ignore_result=True)
def send(index_set_id):
    clustering_config = ClusteringConfig.objects.get(index_set_id=index_set_id)
    doc_count = get_doc_count(index_set_id=index_set_id, bk_biz_id=clustering_config.bk_biz_id)
    msg = _("有新聚类创建，请关注！索引集id: {}, 创建者: {}, 过去一天的数据量doc_count为: {}").format(
        index_set_id, clustering_config.created_by, doc_count
    )
    NOTIFY_EVENT(
        content=f"{msg}",
        dimensions={"index_set_id": clustering_config.index_set_id, "msg_type": "clustering_config"},
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
