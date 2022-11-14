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
from bkm_space.utils import space_uid_to_bk_biz_id

"""
DRF 插件
"""
from functools import wraps  # noqa
from typing import List, Callable  # noqa

from django.conf import settings  # noqa
from rest_framework import permissions  # noqa

from iam import Resource  # noqa
from . import Permission  # noqa
from .actions import ActionMeta, ActionEnum  # noqa
from .resources import ResourceEnum, ResourceMeta  # noqa
from ..exceptions import NotHaveInstanceIdError  # noqa


class IAMPermission(permissions.BasePermission):
    def __init__(self, actions: List[ActionMeta], resources: List[Resource] = None):
        self.actions = actions
        self.resources = resources or []

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # 跳过权限校验
        if settings.IGNORE_IAM_PERMISSION:
            return True

        if not self.actions:
            return True

        client = Permission()
        for action in self.actions:
            client.is_allowed(
                action=action, resources=self.resources, raise_exception=True,
            )
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # 跳过权限校验
        if settings.IGNORE_IAM_PERMISSION:
            return True
        return self.has_permission(request, view)


class BusinessActionPermission(IAMPermission):
    """
    关联业务的动作权限检查
    """

    def __init__(self, actions: List[ActionMeta]):
        super(BusinessActionPermission, self).__init__(actions)

    @classmethod
    def fetch_biz_id_by_request(cls, request):
        bk_biz_id = request.data.get("bk_biz_id", 0) or request.query_params.get("bk_biz_id", 0)
        return bk_biz_id

    def has_permission(self, request, view):
        bk_biz_id = self.fetch_biz_id_by_request(request)
        if not bk_biz_id:
            return True
        self.resources = [ResourceEnum.BUSINESS.create_instance(bk_biz_id)]
        return super(BusinessActionPermission, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # 先查询对象中有没有业务ID相关属性
        bk_biz_id = None
        if hasattr(obj, "space_uid"):
            bk_biz_id = space_uid_to_bk_biz_id(obj.space_uid)
        elif hasattr(obj, "bk_biz_id"):
            bk_biz_id = obj.bk_biz_id
        if bk_biz_id:
            self.resources = [ResourceEnum.BUSINESS.create_instance(bk_biz_id)]
            return super(BusinessActionPermission, self).has_object_permission(request, view, obj)
        # 没有就尝试取请求的业务ID
        return self.has_permission(request, view)


class ViewBusinessPermission(BusinessActionPermission):
    """
    业务访问权限检查
    """

    def __init__(self):
        super(ViewBusinessPermission, self).__init__([ActionEnum.VIEW_BUSINESS])


class InstanceActionPermission(IAMPermission):
    """
    关联其他资源的权限检查
    """

    def __init__(self, actions: List[ActionMeta], resource_meta: ResourceMeta):
        self.resource_meta = resource_meta
        super(InstanceActionPermission, self).__init__(actions)

    def has_permission(self, request, view):
        # 跳过权限校验
        if settings.IGNORE_IAM_PERMISSION:
            return True
        instance_id = view.kwargs[self.get_look_url_kwarg(view)]
        resource = self.resource_meta.create_instance(instance_id)
        self.resources = [resource]
        return super(InstanceActionPermission, self).has_permission(request, view)

    def get_look_url_kwarg(self, view):
        # Perform the lookup filtering.
        lookup_url_kwarg = view.lookup_url_kwarg or view.lookup_field

        assert lookup_url_kwarg in view.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )
        return lookup_url_kwarg


class InstanceActionForDataPermission(InstanceActionPermission):
    def __init__(
        self, iam_instance_id_key, *args, get_instance_id: Callable = lambda _id: _id,
    ):
        self.iam_instance_id_key = iam_instance_id_key
        self.get_instance_id = get_instance_id
        super(InstanceActionForDataPermission, self).__init__(*args)

    def has_permission(self, request, view):
        if request.method == "GET":
            data = request.query_params
        else:
            data = request.data
        instance_id = data.get(self.iam_instance_id_key) or view.kwargs.get(self.get_look_url_kwarg(view))
        if instance_id is None:
            raise NotHaveInstanceIdError
        resource = self.resource_meta.create_instance(self.get_instance_id(instance_id))
        self.resources = [resource]
        return super(InstanceActionPermission, self).has_permission(request, view)


def insert_permission_field(
    actions: List[ActionMeta],
    resource_meta: ResourceMeta,
    id_field: Callable = lambda item: item["id"],
    data_field: Callable = lambda data_list: data_list,
    always_allowed: Callable = lambda item: False,
    many: bool = True,
):
    """
    数据返回后，插入权限相关字段
    :param actions: 动作列表
    :param resource_meta: 资源类型
    :param id_field: 从结果集获取ID字段的方式
    :param data_field: 从response.data中获取结果集的方式
    :param always_allowed: 满足一定条件进行权限豁免
    :param many: 是否为列表数据
    """

    def wrapper(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            response = view_func(*args, **kwargs)

            result_list = data_field(response.data)
            if not many:
                result_list = [result_list]

            resources = []
            for item in result_list:
                if not id_field(item):
                    continue
                attribute = {}
                if "bk_biz_id" in item:
                    attribute["bk_biz_id"] = item["bk_biz_id"]
                if "space_uid" in item:
                    attribute["space_uid"] = item["space_uid"]

                resources.append(
                    [resource_meta.create_simple_instance(instance_id=id_field(item), attribute=attribute)]
                )

            if not resources:
                return response

            if settings.IGNORE_IAM_PERMISSION:
                for item in result_list:
                    item.setdefault("permission", {})
                    item["permission"].update({action.id: True for action in actions})
                return response

            permission_result = Permission().batch_is_allowed(actions, resources)

            for item in result_list:
                origin_instance_id = id_field(item)
                if not origin_instance_id:
                    # 如果拿不到实例ID，则不处理
                    continue
                instance_id = str(origin_instance_id)
                item.setdefault("permission", {})
                item["permission"].update(permission_result[instance_id])

                if always_allowed(item):
                    # 权限豁免
                    for action_id in item["permission"]:
                        item["permission"][action_id] = True

            return response

        return wrapped_view

    return wrapper
