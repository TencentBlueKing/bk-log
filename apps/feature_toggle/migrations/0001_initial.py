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


from django.db import migrations, models
import django_jsonfield_backport.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FeatureToggle",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="创建时间")),
                ("created_by", models.CharField(default="", max_length=32, verbose_name="创建者")),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name="更新时间")),
                ("updated_by", models.CharField(blank=True, default="", max_length=32, verbose_name="修改者")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="删除时间")),
                ("deleted_by", models.CharField(blank=True, max_length=32, null=True, verbose_name="删除者")),
                ("name", models.CharField(max_length=64, unique=True, verbose_name="特性开关name")),
                ("alias", models.CharField(blank=True, max_length=64, null=True, verbose_name="特性开关别名")),
                ("status", models.CharField(default="off", max_length=32, verbose_name="特性开关status")),
                ("description", models.TextField(blank=True, null=True, verbose_name="特性开关描述")),
                ("is_viewed", models.BooleanField(default=True, verbose_name="是否在前端展示")),
                (
                    "feature_config",
                    django_jsonfield_backport.models.JSONField(blank=True, null=True, verbose_name="特性开关配置"),
                ),
                (
                    "biz_id_white_list",
                    django_jsonfield_backport.models.JSONField(blank=True, null=True, verbose_name="业务白名单"),
                ),
            ],
            options={
                "verbose_name": "日志平台特性开关",
                "verbose_name_plural": "41_日志平台特性开关",
            },
        ),
    ]
