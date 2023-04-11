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

"""
权限中心模块
"""
from django.utils.translation import ugettext_lazy as _  # noqa

from apps.api.modules.utils import add_esb_info_before_request  # noqa
from config.domains import IAM_APIGATEWAY_ROOT_V2  # noqa
from apps.api.base import DataAPI  # noqa


class _IAMApi(object):
    MODULE = _("IAM权限中心")

    def __init__(self):
        self.batch_instance = DataAPI(
            method="POST",
            url=IAM_APIGATEWAY_ROOT_V2 + "authorization/batch_instance/",
            module=self.MODULE,
            description="批量资源实例授权/回收",
            default_return_value=None,
            before_request=add_esb_info_before_request,
        )
        self.batch_path = DataAPI(
            method="POST",
            url=IAM_APIGATEWAY_ROOT_V2 + "authorization/batch_path/",
            module=self.MODULE,
            description="批量资源拓扑授权/回收",
            default_return_value=None,
            before_request=add_esb_info_before_request,
        )
        self.share_system_info = DataAPI(
            method="GET",
            url=IAM_APIGATEWAY_ROOT_V2 + "share/systems/{system_id}/",
            module=self.MODULE,
            url_keys=["system_id"],
            description="系统共享信息",
            default_return_value=None,
            before_request=add_esb_info_before_request,
        )


IAMApi = _IAMApi()
