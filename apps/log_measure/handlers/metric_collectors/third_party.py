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
from collections import defaultdict
from django.utils.translation import ugettext as _

from apps.api import TransferApi
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class ThirdPartyMetricCollector(object):
    @staticmethod
    @register_metric("third_party_es", description=_("第三方ES"), data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def third_party_es():
        clusters = TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True})
        groups = defaultdict(int)
        for cluster in clusters:
            if cluster["cluster_config"]["registered_system"] == "_default":
                continue
            bk_biz_id = cluster["cluster_config"]["custom_option"]["bk_biz_id"]
            if not bk_biz_id:
                continue
            groups[bk_biz_id] += 1

        metrics = [
            Metric(
                metric_name="count",
                metric_value=count,
                dimensions={
                    "bk_biz_id": bk_biz_id,
                    "bk_biz_name": MetricUtils.get_instance().get_biz_name(bk_biz_id),
                },
                timestamp=MetricUtils.get_instance().report_ts,
            )
            for bk_biz_id, count in groups.items()
        ]

        return metrics
