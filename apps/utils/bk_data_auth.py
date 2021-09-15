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
import urllib.parse
import uuid

from django.conf import settings

from apps.api import BkDataAuthApi
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import BKDATA_SUPER_TOKEN
from apps.utils.log import logger
from apps.log_esquery.permission import EsquerySearchPermissions
from apps.utils.local import get_request_username, get_request


class BkDataAuthHandler(object):
    def __init__(self, username=""):
        self.username = username or get_request_username()

    def list_authorized_rt_by_user(self):
        """
        获取用户有管理权限的RT列表
        """
        scopes = BkDataAuthApi.get_user_perm_scope(
            {"user_id": self.username, "action_id": "result_table.manage_auth", "show_admin_scopes": True}
        )
        authorized_result_tables = {scope["result_table_id"] for scope in scopes}
        return list(authorized_result_tables)

    def list_authorized_rt_by_token(self):
        """
        获取 token有权限的RT列表
        :return:
        """
        permissions = BkDataAuthApi.get_auth_token(
            {
                "token_id": settings.BKDATA_DATA_TOKEN_ID,
                "bkdata_authentication_method": "token",
                "bkdata_data_token": settings.BKDATA_DATA_TOKEN,
            }
        )["permissions"]
        authorized_result_tables = set()
        for perm in permissions:
            if perm["action_id"] != "result_table.query_data":
                continue
            if perm["status"] != "active":
                continue
            if "result_table_id" not in perm["scope"]:
                continue
            authorized_result_tables.add(perm["scope"]["result_table_id"])
        return list(authorized_result_tables)

    def filter_unauthorized_rt_by_user(self, result_tables):
        """
        过滤用户管理无权限的结果表
        :param result_tables: 待过滤的结果表列表
        :return:
        """
        if FeatureToggleObject.switch(BKDATA_SUPER_TOKEN):
            return []

        if not settings.FEATURE_TOGGLE.get("bkdata_token_auth", "off") == "on":
            return []

        try:
            req = get_request()
            auth_info = EsquerySearchPermissions.get_auth_info(req)
            if auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
                # 对白名单的app，不进行rt权限校验
                return []
        except Exception:  # pylint: disable=broad-except
            # 没有通过JWT校验
            pass

        authorized_result_tables = self.list_authorized_rt_by_user()
        unauthorized_result_tables = [rt for rt in result_tables if rt not in authorized_result_tables]
        return unauthorized_result_tables

    def filter_unauthorized_rt_by_token(self, result_tables):
        """
        过滤当前 token 未授权的结果表
        :param result_tables: 待过滤的结果表列表
        :return:
        """
        if FeatureToggleObject.switch(BKDATA_SUPER_TOKEN):
            return []

        if not settings.FEATURE_TOGGLE.get("bkdata_token_auth", "off") == "on":
            return []

        authorized_result_tables = self.list_authorized_rt_by_token()
        unauthorized_result_tables = [rt for rt in result_tables if rt not in authorized_result_tables]
        return unauthorized_result_tables

    @classmethod
    def get_auth_url(cls, result_tables, state=None):
        """
        生成数据平台鉴权页面URL
        """
        params = {
            "bk_app_code": settings.BKDATA_DATA_APP_CODE,
            "data_token_id": settings.BKDATA_DATA_TOKEN_ID,
            "scopes": ",".join(result_tables),
            "state": state or uuid.uuid4().hex,
        }
        query_string = urllib.parse.urlencode(params)

        auth_url_format = "{bkdata_url}/oauth/authorize/?{query_string}"

        return auth_url_format.format(bkdata_url=settings.BKDATA_URL, query_string=query_string)

    @classmethod
    def authorize_result_table_to_token(cls, result_tables):
        """
        将结果表授权给token
        """
        if FeatureToggleObject.switch(BKDATA_SUPER_TOKEN):
            return

        if not settings.FEATURE_TOGGLE.get("bkdata_token_auth", "off") == "on":
            return

        try:
            req = get_request()
            auth_info = EsquerySearchPermissions.get_auth_info(req)
            source_app_code = auth_info["bk_app_code"]
        except Exception:  # pylint: disable=broad-except
            # 没有通过JWT校验
            return

        # 如果API调用方是其他APP，则直接通过权限校验
        if source_app_code == settings.APP_CODE:
            return

        result = BkDataAuthApi.update_auth_token(
            {
                "token_id": settings.BKDATA_DATA_TOKEN_ID,
                "data_token_bk_app_code": settings.BKDATA_DATA_APP_CODE,
                "data_scope": {
                    "permissions": [
                        {
                            "action_id": "result_table.query_data",
                            "object_class": "result_table",
                            "scope_id_key": "result_table_id",
                            "scope_object_class": "result_table",
                            "scope": {"result_table_id": result_table_id},
                        }
                        for result_table_id in result_tables
                    ]
                },
                "reason": "Auto authorize from app => {}".format(source_app_code),
                # 过期时间一年
                "expire": 360,
            }
        )
        logger.info("[bkdata token auth] RT 自动授权结果：{}".format(result))
