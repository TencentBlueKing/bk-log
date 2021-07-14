# -*- coding: utf-8 -*-
from django.contrib import admin

from bk_monitor.models import MonitorReportConfig


@admin.register(MonitorReportConfig)
class AuditRecordAdmin(admin.ModelAdmin):
    list_display = ["data_id", "data_name", "bk_biz_id", "table_id", "access_token", "id"]
    search_fields = ["data_name"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_list_display_links(self, request, list_display):
        return None
