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
from typing import Tuple

from apps.iam import Permission, ActionEnum, ResourceEnum
from bk_dataview.grafana.permissions import BasePermission, GrafanaRole


class BizPermission(BasePermission):
    """
    业务权限
    """

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        if request.user.is_superuser:
            return True, GrafanaRole.Admin

        bk_biz_id = int(org_name)
        permission = Permission()

        resources = [ResourceEnum.BUSINESS.create_instance(bk_biz_id)]

        if permission.is_allowed(action=ActionEnum.MANAGE_DASHBOARD, resources=resources):
            return True, GrafanaRole.Editor

        # permission.is_allowed(action=ActionEnum.VIEW_DASHBOARD, resources=resources, raise_exception=True)
        # 不在校验查看仪表盘权限 通过索引集权限去过滤
        return True, GrafanaRole.Editor


class ExplorePermission(BasePermission):
    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        return True, GrafanaRole.Viewer
