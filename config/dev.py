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
from config import RUN_VER
from config.env import load_settings
import sys
from django.utils.translation import ugettext_lazy as _


if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = "DEVELOP"

# APP本地静态资源目录
STATIC_URL = "/static/"

# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# Celery 消息队列设置 RabbitMQ
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# Celery 消息队列设置 Redis
BROKER_URL = "redis://localhost:6379/0"

DEBUG = True

# 本地开发数据库设置
# USE FOLLOWING SQL TO CREATE THE DATABASE NAMED APP_CODE
# SQL: CREATE DATABASE `log-search-v2` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; # noqa: E501
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": APP_CODE,
        "USER": "root",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    },
}

# Test

if "test" in sys.argv:
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": APP_CODE}

# 该配置需要等待SITE_URL被patch掉才能正确配置，因此放在patch逻辑后面
GRAFANA = {
    "HOST": os.getenv("BKAPP_GRAFANA_URL", ""),
    "PREFIX": "{}grafana/".format(os.getenv("BKAPP_GRAFANA_PREFIX", SITE_URL)),
    "ADMIN": (os.getenv("BKAPP_GRAFANA_ADMIN_USERNAME", "admin"), os.getenv("BKAPP_GRAFANA_ADMIN_PASSWORD", "admin")),
    "PROVISIONING_CLASSES": ["apps.grafana.provisioning.Provisioning", "apps.grafana.provisioning.TraceProvisioning"],
    "PERMISSION_CLASSES": ["apps.grafana.permissions.BizPermission"],
}


# ==============================================================================
# IAM
# ==============================================================================
BK_IAM_SYSTEM_ID = "bk_log_search"
BK_IAM_SYSTEM_NAME = _("日志平台")

BK_IAM_INNER_HOST = os.getenv("BK_IAM_HOST", os.getenv("BK_IAM_V3_INNER_HOST", "http://iam.service.consul"))

BK_IAM_RESOURCE_API_HOST = os.getenv("BKAPP_IAM_RESOURCE_API_HOST", f"{BK_PAAS_HOST}/o/{APP_CODE}/")

# 权限中心 SaaS host
BK_IAM_APP_CODE = os.getenv("BK_IAM_V3_APP_CODE", "bk_iam")
BK_IAM_SAAS_HOST = os.environ.get("BK_IAM_V3_SAAS_HOST", f"{BK_PAAS_HOST}/o/{BK_IAM_APP_CODE}/")

BK_IAM_RESOURCE_API_HOST = os.getenv("BKAPP_IAM_RESOURCE_API_HOST", "{}{}".format(BK_PAAS_INNER_HOST, SITE_URL))


# 加载各个版本特殊配置
env_settings = load_settings()
for _setting in env_settings.keys():
    if _setting == _setting.upper():
        locals()[_setting] = env_settings.get(_setting)

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from config.local_settings import *  # noqa
except ImportError:
    pass
