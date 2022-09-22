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
import importlib

__author__ = u"蓝鲸智云"
__copyright__ = "Copyright © 2012-2019 Tencent BlueKing. All Rights Reserved."
__all__ = ["celery_app", "ENVIRONMENT", "RUN_VER", "APP_CODE", "SECRET_KEY", "BK_URL", "BASE_DIR"]

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app


def get_env_or_raise(*keys):
    """Get an environment variable, if it does not exist, raise an exception"""
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    raise RuntimeError(
        ('Environment variable "{}" not found, you must set this variable to run this application.').format(keys)
    )


# SaaS运行版本，如非必要请勿修改
RUN_VER = os.environ.get("BKPAAS_ENGINE_REGION", "open")

APP_CODE = get_env_or_raise("APP_ID", "BKPAAS_APP_ID")
# 应用用于调用云 API 的 Secret
SECRET_KEY = get_env_or_raise("APP_TOKEN", "BKPAAS_APP_SECRET")


# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if "BKPAAS_ENVIRONMENT" in os.environ:
    ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT", "dev")
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get("BK_ENV", "development")
    ENVIRONMENT = {
        "development": "dev",
        "testing": "stag",
        "production": "prod",
    }.get(PAAS_V2_ENVIRONMENT)


# 蓝鲸平台URL
BK_URL = os.getenv("BKPAAS_URL", None)  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# read VERSION file
try:
    VERSION = open(os.path.join(BASE_DIR, "VERSION"), "r", encoding="utf-8").read().strip()
except:  # noqa
    VERSION = "Unknown version"
