# Generated by Django 3.2.15 on 2023-01-09 10:13
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

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_clustering", "0015_alter_clusteringconfig_after_treat_flow_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClusteringSubscription",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_by", models.CharField(default="", max_length=32, verbose_name="创建者")),
                ("updated_by", models.CharField(blank=True, default="", max_length=32, verbose_name="修改者")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="删除时间")),
                ("deleted_by", models.CharField(blank=True, max_length=32, null=True, verbose_name="删除者")),
                (
                    "subscription_type",
                    models.CharField(
                        choices=[("email", "邮件"), ("wechat", "企业微信")],
                        default="wechat",
                        max_length=64,
                        verbose_name="订阅类型",
                    ),
                ),
                ("space_uid", models.CharField(db_index=True, max_length=64, verbose_name="空间ID")),
                ("index_set_id", models.IntegerField(db_index=True, verbose_name="索引集id")),
                ("title", models.TextField(verbose_name="标题")),
                ("receivers", models.JSONField(verbose_name="接收人")),
                ("managers", models.JSONField(verbose_name="管理员")),
                ("frequency", models.JSONField(verbose_name="发送频率")),
                (
                    "pattern_level",
                    models.CharField(
                        choices=[
                            ("01", "LEVEL_01"),
                            ("03", "LEVEL_03"),
                            ("05", "LEVEL_05"),
                            ("07", "LEVEL_07"),
                            ("09", "LEVEL_09"),
                        ],
                        default="05",
                        max_length=64,
                        verbose_name="敏感度",
                    ),
                ),
                ("log_display_count", models.IntegerField(default=5, verbose_name="日志条数")),
                (
                    "log_col_show_type",
                    models.CharField(
                        choices=[("pattern", "PATTERN模式"), ("log", "采样日志")],
                        default="pattern",
                        max_length=64,
                        verbose_name="日志列显示",
                    ),
                ),
                ("group_by", models.JSONField(blank=True, default=[], null=True, verbose_name="统计维度")),
                (
                    "year_on_year_hour",
                    models.IntegerField(
                        choices=[
                            (0, "不比对"),
                            (1, "1小时前"),
                            (2, "2小时前"),
                            (3, "3小时前"),
                            (6, "6小时前"),
                            (12, "12小时前"),
                            (24, "24小时前"),
                        ],
                        default=0,
                        verbose_name="同比",
                    ),
                ),
                (
                    "year_on_year_change",
                    models.CharField(
                        choices=[("all", "所有"), ("rise", "上升"), ("decline", "下降")],
                        default="all",
                        max_length=64,
                        verbose_name="同比变化",
                    ),
                ),
                ("query_string", models.TextField(blank=True, default="*", null=True, verbose_name="查询语句")),
                ("addition", models.JSONField(blank=True, default=[], null=True, verbose_name="查询条件")),
                ("host_scopes", models.JSONField(blank=True, default={}, null=True, verbose_name="主机范围")),
                ("is_show_new_pattern", models.BooleanField(default=True, verbose_name="是否只要新类")),
                ("is_enabled", models.BooleanField(default=True, verbose_name="是否启用")),
                ("last_run_at", models.DateTimeField(blank=True, null=True, verbose_name="最后运行时间")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
            ],
            options={
                "verbose_name": "日志聚类订阅",
                "verbose_name_plural": "日志聚类订阅",
            },
        ),
    ]
