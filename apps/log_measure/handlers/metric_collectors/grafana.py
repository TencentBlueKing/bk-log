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
                Metric(
                    metric_name="count",
                    metric_value=len(dashboards),
                    dimensions={
                        "target_bk_biz_id": int(org_name),
                        "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(org_name),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )

            panel_count = 0
            for dashboard in dashboards:
                dashboard_info = (
                    grafana_client.get_dashboard_by_uid(org_id=org["id"], dashboard_uid=dashboard["uid"])
                    .json()
                    .get("dashboard", {})
                )
                for panel in dashboard_info.get("panels", []):
                    if panel["type"] == "row":
                        # 如果是行类型，需要统计嵌套数量
                        panel_count += len(panel.get("panels", []))
                    else:
                        panel_count += 1

            metrics.append(
                Metric(
                    metric_name="panel_count",
                    metric_value=panel_count,
                    dimensions={
                        "target_bk_biz_id": int(org_name),
                        "target_bk_biz_name": MetricUtils.get_instance().get_biz_name(org_name),
                    },
                    timestamp=MetricUtils.get_instance().report_ts,
                )
            )

        return metrics
