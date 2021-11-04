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
"""
context_processor for common(setting)

除setting外的其他context_processor内容，均采用组件的方式(string)
"""
import datetime  # noqa
from django.utils import translation  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa
from django.conf import settings  # noqa

from blueapps.account.conf import ConfFixture  # noqa


def mysetting(request):
    return {
        "gettext": _,
        "_": _,
        "LANGUAGES": settings.LANGUAGES,
        # 基础信息
        "RUN_MODE": settings.RUN_MODE,
        "ENVIRONMENT": settings.ENVIRONMENT,
        "APP_CODE": settings.APP_CODE,
        "SITE_URL": settings.SITE_URL,
        "AJAX_URL_PREFIX": settings.SITE_URL + "api/v1/",
        "RUN_VER_DISPLAY": settings.RUN_VER_DISPLAY,
        # 远程静态资源url
        "REMOTE_STATIC_URL": settings.REMOTE_STATIC_URL,
        # 静态资源
        "STATIC_URL": settings.STATIC_URL,
        "STATIC_VERSION": settings.STATIC_VERSION,
        "BK_STATIC_URL": settings.STATIC_URL + "dist",
        # 登录跳转链接
        "LOGIN_URL": ConfFixture.LOGIN_URL,
        "LOGIN_SERVICE_URL": ConfFixture.LOGIN_URL,
        # 'LOGOUT_URL': settings.LOGOUT_URL,
        "BK_PAAS_HOST": "%s/app/list/" % settings.BK_PAAS_HOST,
        "BK_PLAT_HOST": settings.BK_PAAS_HOST,
        "BK_CC_HOST": settings.BK_CC_HOST,
        # 数据平台跳转URL
        "BKDATA_URL": settings.BKDATA_URL,
        # 监控URL
        "MONITOR_URL": settings.MONITOR_URL,
        # 日志采集接入指引
        "COLLECTOR_GUIDE_URL": settings.COLLECTOR_GUIDE_URL,
        # 当前页面，主要为了login_required做跳转用
        "APP_PATH": request.get_full_path(),
        "NOW": datetime.datetime.now(),
        "RUN_VER": settings.RUN_VER,
        "TITLE": settings.HEADER_CONFIG["en"] if translation.get_language() == "en" else settings.HEADER_CONFIG["zh"],
        "TITLE_MENU": settings.TITLE_MENU_CONFIG["en"]
        if translation.get_language() == "en"
        else settings.TITLE_MENU_CONFIG["zh"],
        "BK_DOC_URL": settings.BK_DOC_URL,
        "BK_DOC_QUERY_URL": settings.BK_DOC_QUERY_URL,
        "BK_FAQ_URL": settings.BK_FAQ_URL,
        "BK_HOT_WARM_CONFIG_URL": settings.BK_HOT_WARM_CONFIG_URL,
        "BIZ_ACCESS_URL": settings.BIZ_ACCESS_URL,
        "DEMO_BIZ_ID": settings.DEMO_BIZ_ID,
        "ES_STORAGE_CAPACITY": settings.ES_STORAGE_CAPACITY,
        "TAM_AEGIS_KEY": settings.TAM_AEGIS_KEY,
        "BK_LOGIN_URL": f"{settings.BK_PAAS_HOST}/api/c/compapi/v2/usermanage/fs_list_users/",
        "MENU_LOGO_URL": f"{settings.STATIC_URL}{settings.MENU_LOGO_URL}",
        "BK_DOC_DATA_URL": settings.BK_DOC_DATA_URL,
    }
