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
from django.utils.translation import ugettext_lazy as _


def patch_home_panels(home_config):
    panels = [
        {
            "datasource": None,
            "fieldConfig": {"defaults": {"custom": {}}, "overrides": []},
            "gridPos": {"h": 4, "w": 24, "x": 0, "y": 0},
            "id": 2,
            "options": {
                "content": "<br>\n<br>\n<br>\n<div><H1>Welcome {} </H1></div>".format(_("欢迎使用仪表盘")),
                "mode": "html",
            },
            "pluginVersion": "7.1.0",
            "targets": [],
            "timeFrom": None,
            "timeShift": None,
            "title": "",
            "transparent": True,
            "type": "text",
        },
        {
            "datasource": None,
            "fieldConfig": {"defaults": {"custom": {}}, "overrides": []},
            "folderId": None,
            "gridPos": {"h": 24, "w": 8, "x": 0, "y": 4},
            "headings": True,
            "id": 7,
            "limit": 15,
            "pluginVersion": "7.2.0-beta1",
            "query": "",
            "recent": False,
            "search": True,
            "starred": False,
            "tags": [],
            "targets": [],
            "timeFrom": None,
            "timeShift": None,
            "title": _("所有仪表盘"),
            "type": "dashlist",
        },
        {
            "datasource": None,
            "fieldConfig": {"defaults": {"custom": {}}, "overrides": []},
            "gridPos": {"h": 24, "w": 8, "x": 8, "y": 4},
            "headings": True,
            "id": 6,
            "limit": 15,
            "pluginVersion": "7.2.0-beta1",
            "query": "",
            "recent": True,
            "search": False,
            "starred": True,
            "tags": [],
            "targets": [],
            "timeFrom": None,
            "timeShift": None,
            "title": _("收藏和最近查看的仪表盘"),
            "type": "dashlist",
        },
        {
            "datasource": None,
            "fieldConfig": {"defaults": {"custom": {}}, "overrides": []},
            "gridPos": {"h": 24, "w": 8, "x": 16, "y": 4},
            "id": 3,
            "options": {
                "content": """
<br>
<div>
    <a href="{}dashboard/new"><H3>{}</H3></a>
</div>
<br>
<div>
    <a href="{}dashboards/folder/new"><H3>{}</H3></a>
</div>
<br>
<div>
    <a href="{}dashboard/import"><H3>{}</H3></a>
</div>
<br><br><br><br>
<div>
    <a href="{}" target="_blank">{}</a>
</div>
                """.format(
                    settings.GRAFANA["PREFIX"],
                    _("还没有仪表盘？快速创建您的仪表盘吧！"),
                    settings.GRAFANA["PREFIX"],
                    _("为方便管理仪表盘，可以创建目录。"),
                    settings.GRAFANA["PREFIX"],
                    _("本地有仪表盘配置文件，直接导入即可。"),
                    settings.BK_DOC_URL,
                    _("更多使用方法查看产品文档"),
                ),
                "mode": "html",
            },
            "pluginVersion": "7.1.0",
            "targets": [],
            "timeFrom": None,
            "timeShift": None,
            "title": _("仪表盘使用指引"),
            "type": "text",
        },
    ]

    home_config["dashboard"]["panels"] = panels
    return home_config
