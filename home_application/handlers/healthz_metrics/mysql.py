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
from home_application.handlers.metrics import register_healthz_metric, HealthzMetric, NamespaceData
from home_application.constants import MYSQL_VARIABLES, MYSQL_STATUS
from home_application.utils.mysql import MySQLClient


class MySQLMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="mysql")
    def check() -> NamespaceData:
        namespace_data = NamespaceData(namespace="mysql", status=False, data=[])
        ping_result = MySQLMetric().ping()
        namespace_data.data.append(ping_result)
        if ping_result.status:
            namespace_data.status = True
        else:
            namespace_data.message = ping_result.message
            return namespace_data

        namespace_data.data.extend(MySQLMetric().get_variables())
        namespace_data.data.extend(MySQLMetric().get_status())

        return namespace_data

    @staticmethod
    def ping():
        result = MySQLClient.get_instance().ping()
        return HealthzMetric(
            status=result["status"],
            metric_name="ping",
            metric_value=result["data"],
            message=result["message"],
            suggestion=result["suggestion"],
        )

    @staticmethod
    def get_variables():
        data = []
        for varieable_name in MYSQL_VARIABLES:
            result = MySQLClient.get_instance().show_variables(varieable_name)
            data.append(
                HealthzMetric(
                    status=result["status"],
                    metric_name=varieable_name,
                    metric_value=result["data"],
                    message=result["message"],
                )
            )

        return data

    @staticmethod
    def get_status():
        data = []
        for status_name in MYSQL_STATUS:
            result = MySQLClient.get_instance().show_status(status_name)
            data.append(
                HealthzMetric(
                    status=result["status"],
                    metric_name=status_name,
                    metric_value=result["data"],
                    message=result["message"],
                )
            )
        return data
