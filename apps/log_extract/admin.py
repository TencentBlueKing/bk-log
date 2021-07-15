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
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import TextInput
from django import forms

from apps.utils.admin import AppModelAdmin
from apps.log_extract.constants import ExtractLinkType
from apps.log_extract.models import Strategies, Tasks, ExtractLink, ExtractLinkHost


@admin.register(Strategies)
class StrategiesAdmin(AppModelAdmin):
    list_display = ["strategy_id", "bk_biz_id", "strategy_name", "operator", "created_at", "created_by"]
    search_fields = ["bk_biz_id", "strategy_name"]
    readonly_fields = ["user_list", "modules", "visible_dir", "file_type"]


@admin.register(Tasks)
class TasksAdmin(AppModelAdmin):
    list_display = [
        "task_id",
        "bk_biz_id",
        "download_status",
        "pipeline_id",
        "total_elapsed",
        "download_file_detail",
        "created_at",
        "created_by",
    ]
    search_fields = ["bk_biz_id", "task_id"]
    readonly_fields = [
        "ip_list",
        "file_path",
        "filter_content",
        "pipeline_components_id",
        "ex_data",
        "total_elapsed",
        "ip_num",
        "download_file_detail",
    ]


class HostInline(admin.TabularInline):
    model = ExtractLinkHost
    extra = 1


class ExtractLinkAdminForm(forms.ModelForm):
    link_type = forms.ChoiceField(label=_("链路类型"), choices=ExtractLinkType.get_choices())

    class Meta:
        model = ExtractLink
        if settings.FEATURE_TOGGLE["extract_cos"] == "on":
            fields = (
                "name",
                "link_type",
                "operator",
                "op_bk_biz_id",
                "qcloud_cos_bucket",
                "qcloud_cos_region",
                "qcloud_secret_key",
                "qcloud_secret_id",
                "is_enable",
            )
        else:
            fields = (
                "name",
                "link_type",
                "operator",
                "op_bk_biz_id",
                "is_enable",
            )


@admin.register(ExtractLink)
class ExtractLinkAdmin(AppModelAdmin):
    inlines = [HostInline]
    formfield_overrides = {models.TextField: {"widget": TextInput(attrs={"class": "vTextField"})}}
    list_display = ["name"]
    form = ExtractLinkAdminForm
