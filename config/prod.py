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

import importlib
import os

from config import RUN_VER
from config.env import load_settings

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 正式环境
RUN_MODE = "PRODUCT"

# CSRF
CSRF_COOKIE_NAME = "bklog_csrftoken"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")

# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')


# 正式环境数据库可以在这里配置
# 默认 default 请不要修改，如果使用了外部数据库，请联系【蓝鲸助手】授权
# DATABASES.update(
#     {
#         # 外部数据库授权，请联系 【蓝鲸助手】
#         'external_db': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': '',  # 外部数据库名
#             'USER': '',  # 外部数据库用户
#             'PASSWORD': '',  # 外部数据库密码
#             'HOST': '',  # 外部数据库主机
#             'PORT': '',  # 外部数据库端口
#         },
#     }
# )

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
BK_IAM_SYSTEM_NAME = "日志平台"

BK_IAM_INNER_HOST = os.getenv("BK_IAM_HOST", os.getenv("BK_IAM_V3_INNER_HOST", "http://iam.service.consul"))

BK_IAM_RESOURCE_API_HOST = os.getenv("BKAPP_IAM_RESOURCE_API_HOST", "{}{}".format(BK_PAAS_INNER_HOST, SITE_URL))

# 权限中心 SaaS host
BK_IAM_APP_CODE = os.getenv("BK_IAM_V3_APP_CODE", "bk_iam")
BK_IAM_SAAS_HOST = os.environ.get("BK_IAM_V3_SAAS_HOST", BK_PAAS_HOST + "/o/{}/".format(BK_IAM_APP_CODE))

# 加载各个版本特殊配置
env_settings = load_settings()
for _setting in env_settings.keys():
    if _setting == _setting.upper():
        locals()[_setting] = env_settings.get(_setting)
