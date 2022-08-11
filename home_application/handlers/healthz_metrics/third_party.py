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
import logging

from django.utils.translation import ugettext as _

from home_application.handlers.metrics import register_healthz_metric, HealthzMetric, NamespaceData
from home_application.utils.third_party import ThirdParty, THIRD_PARTY_CHECK_API

logger = logging.getLogger()


class ThirdPartyCheck(object):
    @staticmethod
    @register_healthz_metric(namespace="third_party")
    def check() -> NamespaceData:
        namespace_data = NamespaceData(namespace="third_party", status=False, data=[])
        ping_result = ThirdPartyCheck().ping()
        namespace_data.status = [i.status for i in ping_result].count(True) == len(ping_result)
        if not namespace_data.status:
            namespace_data.message = _("周边依赖检查失败, 请查看细节")

        namespace_data.data.extend(ping_result)
        return namespace_data

    @staticmethod
    def ping():
        data = []
        for module in THIRD_PARTY_CHECK_API:
            result = ThirdParty.call_api(module)
            data.append(
                HealthzMetric(
                    status=result["status"],
                    metric_name=module,
                    metric_value=result["data"],
                    message=result["message"],
                    suggestion=result["suggestion"],
                )
            )

        check_iam_result = ThirdParty.check_iam()
        data.append(
            HealthzMetric(
                status=check_iam_result["status"],
                metric_name="iam",
                metric_value=check_iam_result["data"],
                message=check_iam_result["message"],
                suggestion=check_iam_result["suggestion"],
            )
        )

        # check esb, 只要有一个接口调成功, ESB就是正常的
        data.append(HealthzMetric(status=[i.status for i in data].count(True) > 0, metric_name="esb"))

        return data
