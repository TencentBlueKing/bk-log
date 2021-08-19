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
import os

from django.apps.config import AppConfig
from django.conf import settings
from django.contrib.auth.signals import user_logged_in

try:
    from blueapps.utils.esbclient import get_client_by_user
except Exception:  # pylint: disable=broad-except
    pass


class ApiConfig(AppConfig):
    name = "apps.log_search"
    verbose_name = "LOG_SEARCH"

    def ready(self):
        self.init_bklog_api()
        self.sync_package_version()
        self.check_feature()
        return True

    @classmethod
    def init_bklog_api(cls):
        if not settings.BKAPP_IS_BKLOG_API:
            return
        user_logged_in.disconnect(dispatch_uid="update_last_login")

    def sync_package_version(self):
        """
        同步SaaS和后台包的版本号到数据库中
        """
        # 企业版需判断返回具体版本号
        if settings.RUN_VER != "open":
            return
        from apps.log_search.models import GlobalConfig

        try:
            with open(os.path.join(settings.PROJECT_ROOT, "VERSION"), encoding="utf-8") as fd:
                version = fd.read().strip()
        except Exception:  # pylint: disable=broad-except
            version = ""

        if settings.BKAPP_IS_BKLOG_API:
            config_id = "BACKEND_VERSION"
        else:
            config_id = "SAAS_VERSION"

        # 更新配置
        try:
            config = GlobalConfig.objects.filter(config_id=config_id).first()
            if not config:
                GlobalConfig.objects.create(config_id=config_id, configs=version)
                return

            if config.configs == version:
                return

            # 更新版本
            config.configs = version
            config.save()
        except Exception:  # pylint: disable=broad-except
            pass

    def check_feature(self):
        # 企业版需判断是否部署数据平台、监控
        if settings.RUN_VER != "open":
            return
        client = get_client_by_user(user_or_username=settings.SYSTEM_USE_API_ACCOUNT)
        bk_apps = client.bk_paas.get_app_info()
        if bk_apps["result"]:
            bk_apps = [item["bk_app_code"] for item in bk_apps["data"]]
            # 是否部署监控SaaS
            for menu in settings.MENUS:
                if menu["id"] == "monitor":
                    monitor_menu = menu
                    break

            monitor_menu["feature"] = "off"
            # settings.FEATURE_TOGGLE["monitor"] = "off"

            if settings.SAAS_MONITOR in bk_apps:
                monitor_menu["feature"] = "on"
                settings.FEATURE_TOGGLE["monitor_report"] = "on"
            elif "bk_monitor" in bk_apps:
                monitor_menu["feature"] = "on"
                settings.SAAS_MONITOR = "bk_monitor"
                settings.FEATURE_TOGGLE["monitor_report"] = "on"

            if not settings.MONITOR_URL:
                # 监控域名
                settings.MONITOR_URL = f"{os.getenv('BK_PAAS_HOST', '')}/o/{settings.SAAS_MONITOR}"

            # 是否部署数据平台SaaS
            settings.FEATURE_TOGGLE["scenario_bkdata"] = "on" if settings.SAAS_BKDATA in bk_apps else "off"
