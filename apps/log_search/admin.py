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
from django.contrib import admin
from apps.utils.admin import AppModelAdmin
from apps.log_search.models import (
    ProjectInfo,
    LogIndexSet,
    LogIndexSetData,
    UserIndexSetConfig,
    ResourceChange,
    AccessSourceConfig,
    GlobalConfig,
    UserIndexSetSearchHistory,
    AsyncTask,
    EmailTemplate,
    UserMetaConf,
    Space,
    SpaceType,
)


@admin.register(ProjectInfo)
class ProjectInfoAdmin(AppModelAdmin):
    list_display = [
        "project_id",
        "project_name",
        "bk_biz_id",
        "bk_app_code",
        "time_zone",
        "description",
        "created_at",
        "created_by",
        "is_deleted",
    ]
    search_fields = ["project_id", "bk_biz_id", "project_name", "bk_app_code"]


@admin.register(SpaceType)
class SpaceTypeAdmin(AppModelAdmin):
    list_display = [
        "type_id",
        "type_name",
    ]
    search_fields = [
        "type_id",
        "type_name",
    ]


@admin.register(Space)
class SpaceAdmin(AppModelAdmin):
    list_display = [
        "id",
        "space_uid",
        "bk_biz_id",
        "space_type_id",
        "space_type_name",
        "space_id",
        "space_name",
        "space_code",
    ]
    search_fields = [
        "id",
        "space_uid",
        "bk_biz_id",
        "space_type_id",
        "space_type_name",
        "space_id",
        "space_name",
        "space_code",
    ]


@admin.register(AccessSourceConfig)
class AccessSourceConfigAdmin(AppModelAdmin):
    list_display = ["source_id", "source_name", "scenario_id", "space_uid", "properties"]
    search_fields = ["source_id", "source_name", "scenario_id", "space_uid"]


@admin.register(LogIndexSet)
class LogIndexSetAdmin(AppModelAdmin):
    list_display = [
        "index_set_id",
        "index_set_name",
        "space_uid",
        "category_id",
        "bkdata_project_id",
        "scenario_id",
        "source_id",
        "orders",
        "view_roles",
        "is_active",
        "is_deleted",
        "created_at",
        "created_by",
        "source_app_code",
        "list_operate",
    ]
    search_fields = ["index_set_id", "index_set_name", "space_uid", "scenario_id"]
    readonly_fields = ["bkdata_project_id", "collector_config_id", "pre_check_msg", "fields_snapshot", "tag_ids"]


@admin.register(LogIndexSetData)
class LogIndexSetDataAdmin(AppModelAdmin):
    list_display = [
        "index_id",
        "index_set_id",
        "bk_biz_id",
        "result_table_id",
        "result_table_name",
        "time_field",
        "apply_status",
        "is_deleted",
        "created_at",
        "created_by",
        "list_operate",
    ]
    search_fields = ["index_set_id", "bk_biz_id", "result_table_id"]


@admin.register(ResourceChange)
class ResourceChangeAdmin(AppModelAdmin):
    list_display = [
        "space_uid",
        "change_type",
        "group_id",
        "resource_id",
        "resource_scope_id",
        "created_by",
        "created_at",
        "sync_status",
        "sync_time",
    ]
    search_fields = ["sync_status", "index_set_id"]


@admin.register(GlobalConfig)
class GlobalConfigAdmin(AppModelAdmin):
    list_display = ["config_id", "configs"]
    search_fields = ["config_id", "configs"]


@admin.register(UserIndexSetConfig)
class UserIndexSetConfigAdmin(AppModelAdmin):
    list_display = ["index_set_id", "display_fields", "sort_list", "created_by", "created_at"]
    search_fields = ["index_set_id", "created_by"]


@admin.register(UserIndexSetSearchHistory)
class UserIndexSetSearchHistoryAdmin(AppModelAdmin):
    list_display = ["index_set_id", "params", "created_by", "created_at", "duration"]
    search_fields = ["index_set_id", "created_by"]


@admin.register(AsyncTask)
class AsyncTaskAdmin(AppModelAdmin):
    list_display = [
        "request_param",
        "sorted_param",
        "scenario_id",
        "index_set_id",
        "result",
        "failed_reason",
        "file_name",
        "file_size",
        "download_url",
        "is_clean",
        "created_by",
        "created_at",
        "export_status",
        "start_time",
        "end_time",
        "export_type",
        "bk_biz_id",
        "completed_at",
    ]
    search_fields = ["scenario_id", "request_param", "download_url", "file_name"]


@admin.register(EmailTemplate)
class EmailTemplateAdmin(AppModelAdmin):
    list_display = ["name", "path"]

    search_fields = ["name"]


@admin.register(UserMetaConf)
class UserMetaConfAdmin(AppModelAdmin):
    list_display = ["username", "conf", "type"]
    search_fields = ["username"]
