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

from django.conf import settings

from apps.api.base import DataAPI

from config.domains import BCS_APIGATEWAY_ROOT
from apps.api.modules.utils import add_esb_info_before_request


def bcs_before_request(params):
    params = add_esb_info_before_request(params)
    params["Authorization"] = f"Bearer {settings.BCS_API_GATEWAY_TOKEN}"
    return params


class _BcsApi:
    MODULE = "BCS"

    def __init__(self):
        bcs_apigateway_host = settings.BCS_APIGATEWAY_HOST if settings.IS_K8S_DEPLOY_MODE else BCS_APIGATEWAY_ROOT
        self.list_cluster_by_project_id = DataAPI(
            method="GET",
            url=f"{bcs_apigateway_host}bcsapi/v4/clustermanager/v1/cluster",
            module=self.MODULE,
            description="根据项目id获取集群信息",
            header_keys=["Authorization"],
            before_request=bcs_before_request,
        )
