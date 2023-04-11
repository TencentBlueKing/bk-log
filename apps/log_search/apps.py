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
import os

from django.apps.config import AppConfig
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_migrate

from apps.iam import Permission
from apps.utils.local import activate_request
from apps.utils.log import logger
from apps.utils.thread import generate_request
from iam.contrib.iam_migration.migrator import IAMMigrator

try:
    from blueapps.utils.esbclient import get_client_by_user
except Exception:  # pylint: disable=broad-except
    pass


def migrate_iam(sender, **kwargs):
    if Permission.get_iam_client().in_compatibility_mode():
        # 存量部署存在V1的操作时，需要跑该配置将V1操作改名，避免与新名称发生冲突
        IAMMigrator("legacy.json").migrate()
    IAMMigrator("initial.json").migrate()


class ApiConfig(AppConfig):
    name = "apps.log_search"
    verbose_name = "LOG_SEARCH"

    def ready(self):
        self.init_bklog_api()
        self.sync_package_version()
        self.check_feature()
        post_migrate.connect(migrate_iam, sender=self)
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

        if settings.BKAPP_IS_BKLOG_API:
            config_id = "BACKEND_VERSION"
        else:
            config_id = "SAAS_VERSION"

        # 更新配置
        try:
            config = GlobalConfig.objects.filter(config_id=config_id).first()
            if not config:
                GlobalConfig.objects.create(config_id=config_id, configs=settings.VERSION)
                return

            if config.configs == settings.VERSION:
                return

            # 更新版本
            config.configs = settings.VERSION
            config.save()
        except Exception:  # pylint: disable=broad-except
            pass

    def check_feature(self):
        # 企业版需判断是否部署数据平台、监控
        if settings.RUN_VER != "open":
            return

        is_deploy_monitor = False
        is_deploy_bkdata = False
        if settings.IS_K8S_DEPLOY_MODE:
            activate_request(generate_request())
            from apps.api import BKPAASApi

            uni_apps_query_by_id_part_params = {"format": "bk_std_json", "include_deploy_info": True}

            def uni_apps_is_exist(query_result):
                if not bool(query_result and query_result[0]):
                    return False

                # 如果是第三方应用，没有部署信息，直接判断为已部署
                deploy_info = query_result[0].get("deploy_info", {})
                if not deploy_info:
                    return True

                # v3的应用需要继续判断部署状态
                return deploy_info.get("prod", {}).get("deployed", False)

            try:
                result = BKPAASApi.uni_apps_query_by_id(
                    {"id": settings.SAAS_MONITOR, **uni_apps_query_by_id_part_params}
                )
                is_deploy_monitor = uni_apps_is_exist(result)

                result = BKPAASApi.uni_apps_query_by_id(
                    {"id": settings.SAAS_BKDATA, **uni_apps_query_by_id_part_params}
                )
                is_deploy_bkdata = uni_apps_is_exist(result)
            except Exception as e:  # pylint: disable=broad-except
                # 忽略这个API请求的错误, 避免错误导致整个APP启动失败
                # 错误情况下，记录下日志，同时认为对应的APP未部署
                logger.exception(e)
        else:
            client = get_client_by_user(user_or_username=settings.SYSTEM_USE_API_ACCOUNT)
            bk_apps = client.bk_paas.get_app_info()
            if bk_apps["result"]:
                bk_apps = [item["bk_app_code"] for item in bk_apps["data"]]

                is_deploy_monitor = bool(settings.SAAS_MONITOR in bk_apps)
                is_deploy_bkdata = bool(settings.SAAS_BKDATA in bk_apps)

        # 是否部署监控SaaS
        for menu in settings.MENUS:
            if menu["id"] == "monitor":
                menu["feature"] = "on" if is_deploy_monitor else "off"
                break

        settings.FEATURE_TOGGLE["monitor_report"] = "on" if is_deploy_monitor else "off"
        settings.FEATURE_TOGGLE["scenario_bkdata"] = "on" if is_deploy_bkdata else "off"

        if not settings.MONITOR_URL:
            # 监控域名
            settings.MONITOR_URL = f"{os.getenv('BK_PAAS_HOST', '')}/o/{settings.SAAS_MONITOR}"
