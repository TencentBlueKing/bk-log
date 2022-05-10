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
from __future__ import unicode_literals

import os

# Create your views here.

BKPAAS_ENGINE_REGION = os.environ.get("BKPAAS_ENGINE_REGION")
# 注意，如果是迁移的旧应用，并且 AppID 中包含下划线(_)，这里的 BKPAAS_ENGINE_APP_NAME 需要将下划线替换成 "0us0"
# 即 BKPAAS_ENGINE_APP_NAME = os.environ.get('BKPAAS_ENGINE_APP_NAME').replace("_", "0us0")
BKPAAS_ENGINE_APP_NAME = os.environ.get("BKPAAS_ENGINE_APP_NAME")
FLOWER_URL = "http://{}-{}-flower".format(BKPAAS_ENGINE_REGION, BKPAAS_ENGINE_APP_NAME)

try:
    from revproxy.views import ProxyView
except ImportError:
    pass
else:

    class FlowerProxy(ProxyView):
        upstream = FLOWER_URL
