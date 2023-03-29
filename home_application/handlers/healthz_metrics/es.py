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
import time
import logging

from socket import gaierror

from django.utils.translation import ugettext as _

from apps.log_measure.exceptions import EsConnectFailException
from apps.log_measure.utils.metric import MetricUtils
from apps.log_databus.constants import VisibleEnum
from home_application.handlers.metrics import register_healthz_metric, HealthzMetric, NamespaceData

logger = logging.getLogger()


class ESMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="es")
    def check():
        namespace_data = NamespaceData(namespace="es", status=False, data=[])
        ping_result = ESMetric().ping()
        namespace_data.data.extend(ping_result)
        if not ping_result:
            namespace_data.status = True
            namespace_data.message = _("没有公共ES集群")
            return namespace_data
        namespace_data.status = [i.status for i in ping_result].count(True) == len(ping_result)
        if not namespace_data.status:
            namespace_data.message = _("查看详情")
        namespace_data.data.extend(ping_result)

        return namespace_data

    @staticmethod
    def ping():
        data = []
        try:
            clusters = MetricUtils.get_instance().list_cluster_info()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Failed to get es clusters, err: {e}")
            data.append(HealthzMetric(status=False, metric_name="ping", message=str(e)))
            return data

        for cluster in clusters:
            if (
                cluster.get("cluster_config", {})
                .get("custom_option", {})
                .get("visible_config", {})
                .get("visible_type", "")
                != VisibleEnum.ALL_BIZ.value
            ):
                continue
            cluster_name = cluster.get("cluster_config").get("cluster_name", "")
            result = HealthzMetric(status=False, metric_name="ping")
            start_time = time.time()
            try:
                es_client = MetricUtils.get_instance().get_es_client(cluster_info=cluster)
                if es_client:
                    result.status = True
                    result.dimensions = {"cluster_name": cluster_name}
            except (EsConnectFailException, gaierror) as e:
                logger.error(f"failed to get es client, err: {e}")
                result.message = str(e)
                result.suggestion = _("确认ES集群[{cluster_name}]是否可用").format(cluster_name=cluster_name)

            spend_time = time.time() - start_time
            result.metric_value = "{}ms".format(int(spend_time * 1000))

            data.append(result)
        return data
