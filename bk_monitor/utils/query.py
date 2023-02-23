# -*- coding: utf-8 -*
from django.utils.translation import ugettext_lazy as _

from bk_monitor.models import MonitorReportConfig
from bk_monitor.exceptions import GetTsDataException
from bk_monitor.constants import ErrorEnum


class SqlSplice(object):
    """
    get_ts_data sql 拼接类
    """

    def __init__(self, fields, table_name):
        self.fields = fields
        self.table_name = table_name
        self.where_conditions = []
        self.group_by_conditions = []

    def add_where_conditions(self, where_conditions):
        if not where_conditions:
            return
        self.where_conditions.extend(where_conditions)

    def add_group_by_conditions(self, group_by_conditions):
        if not group_by_conditions:
            return
        self.group_by_conditions.extend(group_by_conditions)

    def format_sql(self):
        sql = f"select {', '.join(self.fields)} from {self.table_name}"
        if self.where_conditions:
            sql = f"{sql} where {' AND '.join(self.where_conditions)}"
        if self.group_by_conditions:
            sql = f"{sql} group by {', '.join(self.group_by_conditions)}"
        return sql


class CustomTable(object):
    """
    从监控相关接口获取历史数据
    """

    def __init__(self, data_name):
        self.data_name = data_name

    @property
    def table_id(self):
        try:
            monitor_report_config = MonitorReportConfig.objects.get(data_name=self.data_name, is_enable=True)
        except MonitorReportConfig.DoesNotExist:
            raise GetTsDataException(
                ErrorEnum.TABLE_ID_NOT_EXIST, _("{data_name} data_name 不存在，请先初始化").format(data_name=self.data_name)
            )

        return monitor_report_config.table_id
