# -*- coding: utf-8 -*-
from rest_framework import permissions


class SuperuserWritePermission(permissions.BasePermission):
    """
    超级管理员写权限
    """

    def check_permission(self, request):
        if request.method in permissions.SAFE_METHODS:
            # 安全方法无需校验
            return True
        user = request.user
        return user and user.is_superuser

    def has_permission(self, request, view):
        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.check_permission(request)
