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
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from blueapps.account.decorators import login_exempt
import json

from apps.feature_toggle.handlers.toggle import FeatureToggleObject


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt


def home(request):
    """
    首页
    """
    toggle_list = FeatureToggleObject.toggle_list(**{"is_viewed": True})
    data = {
        # 实时日志最大长度
        "REAL_TIME_LOG_MAX_LENGTH": 20000,
        # 超过此长度删除部分日志
        "REAL_TIME_LOG_SHIFT_LENGTH": 10000,
        # 特性开关
        "FEATURE_TOGGLE": json.dumps({toggle.name: toggle.status for toggle in toggle_list}),
        "FEATURE_TOGGLE_WHITE_LIST": json.dumps(
            {
                toggle.name: toggle.biz_id_white_list
                for toggle in toggle_list
                if isinstance(toggle.biz_id_white_list, list)
            }
        ),
    }
    return render(request, settings.VUE_INDEX, data)


def bkdata_auth(request):
    """
    鉴权页面
    """
    return render(request, "auth.html")


@login_exempt
def contact(request):
    """
    联系我们
    """
    return JsonResponse({"data": "login_exempt"})


@login_exempt
def healthz(request):
    return JsonResponse({"server_up": 1})
