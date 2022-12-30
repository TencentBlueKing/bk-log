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

from django.db import migrations
from apps.feature_toggle.plugins.constants import USER_GUIDE_CONFIG


def forwards_func(apps, schema_editor):
    feature_toggle = apps.get_model("feature_toggle", "FeatureToggle")
    feature_toggle.objects.update_or_create(
        name=USER_GUIDE_CONFIG,
        defaults={
            "alias": None,
            "status": "on",
            "description": "",
            "is_viewed": False,
            "feature_config": {
                "default": {
                    "step_list": [
                        {"title": "业务选择框", "target": "#bizSelectorGuide", "content": "业务选择框的位置全部换到左侧导航"},
                        {"title": "管理能力增强", "target": "#manageMenuGuide", "content": "日志提取任务挪到管理；增加数据存储、使用等状态管理"},
                    ]
                }
            },
            "biz_id_white_list": None,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("feature_toggle", "0005_merge_20220409_2322"),
    ]

    operations = [migrations.RunPython(forwards_func)]
