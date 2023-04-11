# -*- coding=utf-8 -*-
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
数据平台后端权限管理模块
"""
from django.utils.translation import ugettext_lazy as _  # noqa

from apps.api.base import DataAPI  # noqa
from apps.api.modules.utils import add_esb_info_before_request_for_bkdata_user  # noqa
from config.domains import AUTH_APIGATEWAY_ROOT  # noqa


class _BkDataAuthApi:

    MODULE = _("数据平台鉴权模块")

    def __init__(self):
        self.check_user_perm = DataAPI(
            method="POST",
            url=AUTH_APIGATEWAY_ROOT + "users/{user_id}/check/",
            module=self.MODULE,
            url_keys=["user_id"],
            description="检查用户是否具有指定权限",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.get_user_perm_scope = DataAPI(
            method="GET",
            url=AUTH_APIGATEWAY_ROOT + "users/{user_id}/scopes/",
            module=self.MODULE,
            url_keys=["user_id"],
            description="检查用户是否具有指定权限",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.get_auth_token = DataAPI(
            method="GET",
            url=AUTH_APIGATEWAY_ROOT + "tokens/{token_id}/",
            module=self.MODULE,
            url_keys=["token_id"],
            description="get auth token details",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.update_auth_token = DataAPI(
            method="PUT",
            url=AUTH_APIGATEWAY_ROOT + "tokens/{token_id}/",
            module=self.MODULE,
            url_keys=["token_id"],
            description="update auth token",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
        self.add_project_data = DataAPI(
            method="POST",
            url=AUTH_APIGATEWAY_ROOT + "projects/{project_id}/data/add/",
            module=self.MODULE,
            url_keys=["project_id"],
            description="添加项目数据",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )

        self.add_cluster_group = DataAPI(
            method="POST",
            url=AUTH_APIGATEWAY_ROOT + "projects/{project_id}/cluster_group/",
            module=self.MODULE,
            url_keys=["project_id"],
            description="申请资源组",
            default_return_value=None,
            before_request=add_esb_info_before_request_for_bkdata_user,
            after_request=None,
        )
