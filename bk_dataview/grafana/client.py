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
import requests
from django.utils.crypto import get_random_string

from .provisioning import Datasource
from .settings import grafana_settings
from .utils import requests_curl_log

rpool = requests.Session()

API_HOST = (grafana_settings.HOST + grafana_settings.PREFIX).rstrip("/")


def get_user_by_login_or_email(username: str):
    url = f"{API_HOST}/api/users/lookup?loginOrEmail={username}"
    resp = rpool.get(url, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def create_user(username: str):
    url = f"{API_HOST}/api/admin/users/"
    # 使用proxy_auth验证, 密码随机
    password = get_random_string(12)
    data = {"name": username, "email": "", "login": username, "password": password}
    resp = rpool.post(url, json=data, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_organization_by_name(name: str):
    url = f"{API_HOST}/api/orgs/name/{name}"
    resp = rpool.get(url, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_organization_by_id(org_id: int):
    url = f"{API_HOST}/api/orgs/{org_id}"
    resp = rpool.get(url, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_all_organization():
    url = f"{API_HOST}/api/orgs/"
    resp = rpool.get(url, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def create_organization(name: str):
    url = f"{API_HOST}/api/orgs/"
    data = {"name": name}
    resp = rpool.post(url, json=data, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_org_users(org_id: int):
    url = f"{API_HOST}/api/orgs/{org_id}/users"
    resp = rpool.get(url, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def add_user_to_org(org_id: int, username: str, role: str = "Editor"):
    url = f"{API_HOST}/api/orgs/{org_id}/users"
    data = {"loginOrEmail": username, "role": role}
    resp = rpool.post(url, json=data, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def update_user_in_org(org_id: int, user_id: int, role: str = "Editor"):
    """
    更新组织中的用户
    """
    url = f"{API_HOST}/api/orgs/{org_id}/users/{user_id}"
    data = {"role": role}
    resp = rpool.patch(url, json=data, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_datasource(org_id: int, name):
    """查询数据源"""
    url = f"{API_HOST}/api/datasources/name/{name}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.get(url, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_datasource_by_id(org_id: int, id: int):
    """查询数据源"""
    url = f"{API_HOST}/api/datasources/{id}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.get(url, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def get_datasource_id(org_id: int, name):
    """查询数据源"""
    url = f"{API_HOST}/api/datasources/id/{name}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.get(url, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def create_datasource(org_id: int, ds: Datasource):
    """创建数据源"""
    url = f"{API_HOST}/api/datasources"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.post(
        url, json=ds.__dict__, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log}
    )
    return resp


def update_datasource(org_id: int, datasource_id: int, ds: Datasource):
    url = f"{API_HOST}/api/datasources/{datasource_id}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.put(
        url, json=ds.__dict__, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log}
    )
    return resp


def delete_datasource(org_id: int, datasource_id: int):
    url = f"{API_HOST}/api/datasources/{datasource_id}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.delete(url, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log})
    return resp


def update_dashboard(org_id: int, folder_id, dashboard):
    url = f"{API_HOST}/api/dashboards/db"
    data = {
        "dashboard": dashboard,
        "message": "provisioning dashboard",
        "overwrite": True,
        "folder_id": folder_id,
    }
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.post(
        url, json=data, headers=headers, auth=grafana_settings.ADMIN, hooks={"response": requests_curl_log}
    )
    return resp


def create_folder():
    pass


def search_dashboard(org_id: int, dashboard_id: int = None):
    url = f"{API_HOST}/api/search/?type=dash-db"
    if dashboard_id is not None:
        url += f"&dashboardIds={dashboard_id}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.get(url, auth=grafana_settings.ADMIN, headers=headers, hooks={"response": requests_curl_log})
    return resp


def get_dashboard_by_uid(org_id: int, dashboard_uid: int):
    url = f"{API_HOST}/api/dashboards/uid/{dashboard_uid}"
    headers = {"X-Grafana-Org-Id": str(org_id)}
    resp = rpool.get(url, auth=grafana_settings.ADMIN, headers=headers, hooks={"response": requests_curl_log})
    return resp
