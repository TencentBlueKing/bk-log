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
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.log_measure.constants import COLLECTOR_IMPORT_PATHS
from apps.log_measure.utils.metric import MetricUtils
from apps.utils.drf import list_route
from bk_monitor.utils.collector import MetricCollector


class StatisticViewSet(APIViewSet):
    @list_route(methods=["GET"], url_path="statistic")
    def get_statistic(self, request):
        namespace = request.GET.get("namespace")
        namespaces = self.get_list_obj(namespace)
        data_name = request.GET.get("data_name")
        data_names = self.get_list_obj(data_name)
        data = MetricCollector(collector_import_paths=COLLECTOR_IMPORT_PATHS).collect(
            namespaces=namespaces, time_filter_enable=False, data_names=data_names
        )
        metric_datas = [j.__dict__ for i in data for j in i["metrics"]]
        MetricUtils.del_instance()
        return Response(metric_datas)

    @staticmethod
    def get_list_obj(obj_str):
        return obj_str.split(",") if obj_str else obj_str
