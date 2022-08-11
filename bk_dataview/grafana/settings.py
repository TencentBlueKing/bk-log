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
from django.conf import settings
from django.utils.module_loading import import_string

# 默认配置
DEFAULTS = {
    "HOST": "http://127.0.0.1:3000",
    "PREFIX": "/",
    "ADMIN": ("admin", "admin"),
    "AUTHENTICATION_CLASSES": ["bk_dataview.grafana.authentication.SessionAuthentication"],
    "PERMISSION_CLASSES": ["bk_dataview.grafana.permissions.IsAuthenticated"],
    "PROVISIONING_CLASSES": ["bk_dataview.grafana.provisioning.SimpleProvisioning"],
    "PROVISIONING_PATH": "",
    "DEFAULT_ROLE": "Editor",
    "CODE_INJECTIONS": {
        "<head>": """<head>
<style>
      .sidemenu {{
        display: none !important;
      }}
      .navbar-page-btn .gicon-dashboard {{
        display: none !important;
      }}
      .navbar .navbar-buttons--tv {{
        display: none !important;
      }}
    .css-1jrggg2 {{
          left: 0 !important;
      }}
      .css-9nwlx8 {{
        display: none;
      }}
</style>
{}
<script>""".format(
            """<script src="http://cdn-go.cn/aegis/aegis-sdk/latest/aegis.min.js?_bid=3977"></script>"""
            if settings.TAM_AEGIS_KEY
            else ""
        )
        + f"""window.ageisId = "{settings.TAM_AEGIS_KEY}";"""
        + """
setTimeout(function(){
    if(window.ageisId) {
        const aegis = new Aegis({
            id: window.ageisId, // 项目ID
            uin: window.grafanaBootData ? (window.grafanaBootData.user ? window.grafanaBootData.user.name : "dev") : "dev",
            reportApiSpeed: true, // 接口测速
            reportAssetSpeed: true, // 静态资源测速
            pagePerformance: true, // 页面测速
            onError: true, // 当前实例是否需要进行错误监听，获取错误日志
            delay: 1000, // 上报节流时间，在该时间段内的上报将会合并到一个上报请求中
            repeat: 5, // 重复上报次数，对于同一个错误超过多少次不上报
            offlineLog: false, // 是否使用离线日志
            restfulApiList: [], // 当开启了接口测速，且项目中有些接口采用了 restful 规范，需要在该配置中列出，帮助 Aegis 识别哪些接口是同一条接
            spa: true
        })
    }
},5000);
var _wr = function(type) {
    var orig = history[type];
    return function() {
        var rv = orig.apply(this, arguments);
        var e = new Event(type);
        e.arguments = arguments;
        window.dispatchEvent(e);
        return rv;
    };
};
   history.pushState = _wr('pushState');
   history.replaceState = _wr('replaceState');
  ["popstate", "replaceState", "pushState"].forEach(function(eventName) {
    window.addEventListener(eventName, function() {
      window.parent.postMessage({ pathname: this.location.pathname }, "*");
    });
  });
   window.addEventListener('message', function(e) {
        if(e && e.data ) {
        var dom = null;
        switch(e.data) {
            case 'create':
            dom = document.querySelector('.sidemenu__top .sidemenu-item:nth-child(2) .dropdown-menu li:nth-child(2) a');
            break;
            case 'folder':
            dom = document.querySelector('.sidemenu__top .sidemenu-item:nth-child(2) .dropdown-menu li:nth-child(3) a');
            break;
            case 'import':
            dom = document.querySelector('.sidemenu__top .sidemenu-item:nth-child(2) .dropdown-menu li:nth-child(4) a');
            break;
        }
        dom && dom.click()
        }
    })
</script>
        """
    },
    "BACKEND_CLASS": "bk_dataview.grafana.backends.api.APIHandler",
}

IMPORT_STRINGS = ["AUTHENTICATION_CLASSES", "PERMISSION_CLASSES", "PROVISIONING_CLASSES", "BACKEND_CLASS"]

APP_LABEL = "grafana"


class GrafanaSettings:
    def __init__(self, defaults=None, import_strings=None):
        self.user_settings = getattr(settings, "GRAFANA", {})
        self.defaults = defaults
        self.import_strings = import_strings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Grafana setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(item) for item in val]
        return val


grafana_settings = GrafanaSettings(DEFAULTS, IMPORT_STRINGS)
