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
from enum import Enum
from typing import Tuple

from .settings import grafana_settings


class GrafanaPermission(Enum):
    View = 1
    Edit = 2
    Admin = 4


class GrafanaRole(Enum):
    Viewer = 1
    Editor = 2
    Admin = 3

    def __str__(self):
        return self.name

    def __gt__(self, role: "GrafanaRole") -> bool:
        return self.value > role.value

    def __eq__(self, role: "GrafanaRole") -> bool:
        if not isinstance(role, self.__class__):
            return False
        return self.value == role.value


class BasePermission:
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        raise NotImplementedError(".has_permission() must be overridden.")


class AllowAny(BasePermission):
    """"""

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        return True, GrafanaRole[grafana_settings.DEFAULT_ROLE]


class IsAuthenticated(BasePermission):
    """"""

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        return bool(request.user and request.user.is_authenticated), GrafanaRole[grafana_settings.DEFAULT_ROLE]
