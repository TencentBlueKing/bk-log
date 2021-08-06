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
from django.contrib import admin
from apps.utils.admin import AppModelAdmin
from apps.log_databus.models import (
    CollectorConfig,
    StorageCapacity,
    StorageUsed,
    DataLinkConfig,
    BKDataClean,
    CleanTemplate,
    CleanStash,
)


@admin.register(CollectorConfig)
class CollectorConfigAdmin(AppModelAdmin):
    list_display = [
        "collector_config_id",
        "collector_config_name",
        "bk_app_code",
        "collector_scenario_id",
        "bk_biz_id",
        "category_id",
        "is_active",
        "bk_data_id",
        "table_id",
        "etl_config",
        "subscription_id",
        "index_set_id",
        "created_at",
        "updated_at",
        "bkdata_data_id",
    ]
    search_fields = ["collector_config_name", "etl_config", "bk_data_id"]
    readonly_fields = [
        "target_nodes",
        "target_subscription_diff",
        "bk_data_id",
        "bk_data_name",
        "table_id",
        "bkdata_data_id",
        "index_set_id",
        "etl_config",
        "task_id_list",
        "params",
        "bkdata_data_id",
    ]


@admin.register(DataLinkConfig)
class DataLinkConfigAdmin(AppModelAdmin):
    list_display = [
        "data_link_id",
        "link_group_name",
        "bk_biz_id",
        "kafka_cluster_id",
        "transfer_cluster_id",
        "es_cluster_ids",
        "is_active",
        "description",
    ]
    search_fields = ["bk_biz_id"]


@admin.register(StorageCapacity)
class StorageCapacityAdmin(AppModelAdmin):
    list_display = ["bk_biz_id", "storage_capacity", "created_at", "updated_at"]
    search_fields = ["bk_biz_id"]


@admin.register(StorageUsed)
class StorageUsedAdmin(AppModelAdmin):
    list_display = ["bk_biz_id", "storage_cluster_id", "storage_used", "updated_at"]
    search_fields = ["bk_biz_id", "storage_cluster_id"]


@admin.register(BKDataClean)
class BKDataCleanAdmin(AppModelAdmin):
    list_display = [
        "status",
        "status_en",
        "result_table_id",
        "result_table_name",
        "result_table_name_alias",
        "raw_data_id",
        "data_name",
        "data_alias",
        "data_type",
        "storage_type",
        "storage_cluster",
        "collector_config_id",
        "bk_biz_id",
        "log_index_set_id",
        "is_authorized",
    ]
    search_fields = ["result_table_id", "data_name", "collector_config_id"]


@admin.register(CleanTemplate)
class CleanTemplateAdmin(AppModelAdmin):
    list_display = ["clean_template_id", "name", "clean_type", "etl_params", "etl_fields", "bk_biz_id"]
    search_fields = ["name", "clean_type"]


@admin.register(CleanStash)
class CleanStashAdmin(AppModelAdmin):
    list_display = ["clean_stash_id", "clean_type", "etl_params", "etl_fields", "collector_config_id", "bk_biz_id"]
    search_fields = ["collector_config_id", "clean_type"]
