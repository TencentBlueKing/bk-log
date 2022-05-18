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

from home_application.handlers.metrics import register_healthz_metric, HealthzMetric
from home_application.utils.third_party import ThirdParty, THIRD_PARTY_CHECK_API

logger = logging.getLogger()


class ThirdPartyCheck(object):
    @staticmethod
    @register_healthz_metric(namespace="ThirdParty", description=_("周边依赖健康检查"))
    def third_party():
        data = []
        for module in THIRD_PARTY_CHECK_API:
            status = ThirdParty.call_api(module)
            data.append(HealthzMetric(status=status, metric_name=module, metric_value=status, dimensions={}))

        # check paas
        paas_status = False
        if ThirdParty.check_paas():
            paas_status = True
        data.append(HealthzMetric(status=paas_status, metric_name="paas", metric_value=paas_status, dimensions={}))

        # check esb, 只要有一个接口调成功, ESB就是正常的
        esb_status = False
        if [i.status for i in data].count(True):
            esb_status = True
        data.append(HealthzMetric(status=esb_status, metric_name="esb", metric_value=esb_status, dimensions={}))

        return data
