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
from rest_framework.response import Response
from django.urls import Resolver404
from django.urls import resolve
from django.conf import settings

from apps.esb.serializers import WeWorkCreateChat
from apps.generic import APIViewSet
from apps.esb import exceptions
from apps.api import BkLogApi, TransferApi, WeWorkApi
from apps.iam.handlers.drf import ViewBusinessPermission, BusinessActionPermission, InstanceActionForDataPermission
from apps.iam.handlers.actions import _all_actions
from apps.iam.handlers.resources import _all_resources
from apps.utils.drf import list_route
from django.utils.translation import ugettext as _


class WeWorkViewSet(APIViewSet):
    @list_route(methods=["POST"], url_path="create_chat")
    def create_chat(self, request):
        """
        @api {post} /api/v1/esb_api/wework/create_chat/ 创建群聊
        @apiName create_chat
        @apiDescription 创建群聊
        @apiGroup esb_wework
        @apiParam {List} user_list 用户群员列表
        @apiParam {String} name 群名称
        @apiParamExample {Json} 请求参数
        {
            "user_list": ["admin", "xxx"]
            "name": "xxx"
        }
        """
        data = self.params_valid(WeWorkCreateChat)
        chatid = WeWorkApi.create_appchat(
            {
                "userlist": data["user_list"],
                "name": data["name"],
                "owner": request.user.username,
            }
        )["chatid"]
        WeWorkApi.send_appchat({"chatid": chatid, "msgtype": "text", "text": {"content": str(_("日志平台咨询群已创建，请@群里咨询"))}})
        return Response({"chatid": chatid})


class LogESBViewSet(APIViewSet):
    dst_call = ""
    dst_kwargs = {}

    def check_permissions(self, request):
        """
        重写rest_framework.views.APIView，目的是为了resolve对应path的view以获得对应的view的get_permissions以及has_permission方法
        """
        dst_url = "".join(self.request.path.split("esb/", 1))
        dst_url = f"/api/{dst_url.split('/api/', 1)[1]}"
        try:
            view, args, kwargs = resolve(dst_url)
        except Resolver404:
            raise exceptions.UrlNotExistError()
        dst_views_objects = view.cls(request=self.request)

        try:
            action = view.actions[self.request.method.lower()]
        except KeyError:
            raise exceptions.MethodNotAllowedError()

        dst_views_objects.action = action
        dst_views_objects.kwargs = kwargs
        dst_views_objects.args = args
        for permission in dst_views_objects.get_permissions():
            if not permission.has_permission(request, dst_views_objects):
                self.permission_denied(request, message=getattr(permission, "message", None))

        module_name = dst_views_objects.__module__
        if (
            module_name not in settings.ALLOWED_MODULES_FUNCS.keys()
            or action not in settings.ALLOWED_MODULES_FUNCS[module_name].keys()
        ):
            raise exceptions.UrlNotImplementError()

        self.dst_kwargs = kwargs
        self.dst_call = settings.ALLOWED_MODULES_FUNCS[module_name][action]

    def call(self, request):
        """
        访问esb接口
        """
        if request.method in ["GET"]:
            params = request.query_params
        else:
            params = request.data
        dst_params = self.request_params_regroup(dict(params), request.method in ["GET"])

        try:
            call_func = getattr(BkLogApi, self.dst_call)
        except AttributeError:
            raise exceptions.UrlNotImplementError

        return Response(call_func(dst_params))

    def request_params_regroup(self, query_params, method_get=True):
        """
        request_param 和 kwargs 重组
        @param {dict} query_params request请求中query_params的data转换的dict
        @param  {Boolean} method_get 是否为get请求
        @return {dict} dst_params 返回重组之后的dict
        """
        dst_params = {}
        if not method_get:
            dst_params.update(query_params)
        else:
            for tmp_key, tmp_val in query_params.items():
                dst_params[tmp_key], *_ = tmp_val

        dst_params.update(self.dst_kwargs)

        return dst_params


class MetaESBViewSet(APIViewSet):
    def get_permissions(self):
        permission_config = settings.META_ESB_FORWARD_CONFIG
        target_config = permission_config.get(self._get_dst_key())
        if not target_config:
            raise exceptions.UrlNotImplementError
        if not target_config.get("need_check_permission", True):
            return []
        if target_config.get("is_view_permission", False):
            return [ViewBusinessPermission()]
        if target_config.get("is_business_action_permission", False):
            return [BusinessActionPermission(self._get_actions(target_config.get("iam_actions")))]
        return [
            InstanceActionForDataPermission(
                target_config.get("iam_key"),
                self._get_actions(target_config.get("iam_actions")),
                _all_resources.get(target_config.get("iam_resource")),
            )
        ]

    def _get_actions(self, actions):
        return [_all_actions.get(action) for action in actions]

    def _get_dst_key(self):
        _, origin_url, *__ = self.request.path.split("meta/esb/")
        return origin_url.rstrip("/")

    def call(self, request):
        """
        @api {any} /meta/esb/$meta_call/ Meta转发接口
        @apiName meta_esb_transform
        @apiGroup Esb
        @apiDescription metaesb接口转发
        @apiParam {String} meta_call 转发的meta目标接口
        """
        if request.method in ["GET"]:
            params = request.query_params
        else:
            params = request.data
        esb_params = self.convert_params_to_esb_params(params, request.method in ["GET"])
        permission_config = settings.META_ESB_FORWARD_CONFIG

        dst_call = permission_config.get(self._get_dst_key()).get("target_call")
        if not dst_call:
            raise exceptions.UrlNotImplementError
        if dst_call == "create_es_snapshot_repository":
            return self.create_create_es_snapshot_repository(esb_params)
        try:
            call_func = getattr(TransferApi, dst_call)
        except AttributeError:
            raise exceptions.UrlNotImplementError
        return Response(call_func(esb_params))

    def convert_params_to_esb_params(self, params, is_get=True):
        dst_params = {}
        if not is_get:
            dst_params.update(params)
            return dst_params
        for temp_key, temp_value in params.items():
            dst_params[temp_key], *_ = temp_value
        return dst_params

    def create_create_es_snapshot_repository(self, params):
        if "bk_biz_id" not in params:
            raise ValueError("bk_biz_id is required")
        if "bklog" in params["snapshot_repository_name"]:
            raise ValueError("bklog is not allowed in snapshot_repository_name")
        params["snapshot_repository_name"] = f"{params['bk_biz_id']}_bklog_{params['snapshot_repository_name']}"
        return Response(TransferApi.create_es_snapshot_repository(params))
