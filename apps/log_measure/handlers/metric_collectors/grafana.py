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
from json import decoder

from django.utils.translation import ugettext as _

from bk_dataview.grafana import client as grafana_client
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric


class GrafanaMetricCollector(object):
    @staticmethod
    @register_metric(
        "grafana_dashboard", description=_("Grafana 仪表盘"), data_name="metric", time_filter=TimeFilterEnum.MINUTE60
    )
    def grafana_dashboard():
        metrics = []
        all_organization = grafana_client.get_all_organization().json()
        for org in all_organization:
            org_name = org["name"]
            if not org_name.isdigit():
                continue
            if int(org_name) not in MetricUtils.get_instance().biz_info:
                continue

            try:
                dashboards = grafana_client.search_dashboard(org_id=org["id"]).json()
            except decoder.JSONDecodeError:
                return metrics

            metrics.append(
                # 各个业务下的仪表盘数
                Metric(
                    metric_name="count",
                    metric_value=len(dashboards),
                    dimensions={
                        "bk_biz_id": int(org_name),
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(org_name),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )
            # 各个仪表盘的视图数
            panel_count = defaultdict(int)
            # 仪表盘id->name转换关系
            dashboard_id_to_name_dict = dict()
            for dashboard in dashboards:
                dashboard_id_to_name_dict[dashboard["uid"]] = dashboard["title"]
                dashboard_info = (
                    grafana_client.get_dashboard_by_uid(org_id=org["id"], dashboard_uid=dashboard["uid"])
                    .json()
                    .get("dashboard", {})
                )
                for panel in dashboard_info.get("panels", []):
                    if panel["type"] == "row":
                        # 如果是行类型，需要统计嵌套数量
                        panel_count[dashboard["uid"]] += len(panel.get("panels", []))
                    else:
                        panel_count[dashboard["uid"]] += 1

            for dashboard_id in panel_count:
                metrics.append(
                    # 各个业务各个dashboard下的视图数
                    Metric(
                        metric_name="panel_count",
                        metric_value=panel_count[dashboard_id],
                        dimensions={
                            "bk_biz_id": int(org_name),
                            "bk_biz_name": MetricUtils.get_instance().get_biz_name(org_name),
                            "dashboard_id": dashboard_id,
                            "dashboard_name": dashboard_id_to_name_dict[dashboard_id],
                        },
                        timestamp=MetricUtils.get_instance().report_ts,
                    )
                )
            metrics.append(
                # 各个业务仪表盘试图总数
                Metric(
                    metric_name="panel_total",
                    metric_value=sum(panel_count.values()),
                    dimensions={
                        "bk_biz_id": int(org_name),
                        "bk_biz_name": MetricUtils.get_instance().get_biz_name(org_name),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )

        return metrics
