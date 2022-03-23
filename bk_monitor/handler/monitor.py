# -*- coding: utf-8 -*-
import logging
from typing import List, Optional

from django.utils.translation import ugettext_lazy as _

from bk_monitor.api.client import Client
from bk_monitor.constants import (
    ErrorEnum,
    NOT_EXIST_MSG,
    LABEL,
    OPTION,
    SOURCE_LABEL,
    LOGGER_NAME,
    BATCH_SIZE,
    TIME_SERIES_TYPE,
    TIME_SERIES_ETL_CONFIG,
    EVENT_ETL_CONFIG,
    EVENT_TYPE,
)
from bk_monitor.exceptions import MonitorReportRequestException, MonitorReportResultException
from bk_monitor.models import MonitorReportConfig
from bk_monitor.utils.collector import MetricCollector
from bk_monitor.utils.data_name_builder import DataNameBuilder
from bk_monitor.utils.event import EventTrigger
from bk_monitor.utils.query import CustomTable, SqlSplice

logger = logging.getLogger(LOGGER_NAME)


class BKMonitor(object):
    """BKMonitor handler 统一入口
    Attributes:
        app_id: string 应用id或者 app_code(应用code)
        app_token: String 应用token或者 app_secret
        monitor_host: String 监控esb对应地址
        report_host: String 上报地址
        bk_username: String esb接口调用者
        bk_biz_id: Int 业务id
    """

    def __init__(
        self, app_id: str, app_token: str, monitor_host: str, report_host: str, bk_username: str, bk_biz_id: int
    ):
        self._app_id = app_id
        self._app_token = app_token
        self._monitor_host = monitor_host
        self._bk_username = bk_username
        self._report_host = report_host
        self._client = Client(
            bk_app_code=self._app_id,
            bk_app_secret=self._app_token,
            bk_username=self._bk_username,
            monitor_host=self._monitor_host,
            report_host=self._report_host,
        )
        self._bk_biz_id = bk_biz_id
        self._custom_metric_instance = None

    def custom_metric(self):
        if not self._custom_metric_instance:
            self._custom_metric_instance = CustomReporter(
                client=self._client, bk_biz_id=self._bk_biz_id, app_id=self._app_id
            )
        return self._custom_metric_instance

    def build_event_trigger(self, data_name: str, event_name: str) -> "EventTrigger":
        return EventTrigger(data_name=data_name, event_name=event_name, reporter=self.custom_metric())


class CustomReporter(object):
    """
    bk_monitor_sdk 采集，上报，查询，初始化可调用的方法
    Attributes：
        bk_biz_id: Int 业务id
        client: Client 通用Client 类型
        app_id: string 应用id或者 app_code(应用code)
    """

    def __init__(self, client: Client, bk_biz_id: int, app_id: str):
        self.bk_biz_id = bk_biz_id
        self.app_id = app_id
        self._client = client

    def migrate(self, data_name_list: list):
        """
        初始化数据源相关配置
        """
        for data_name_obj in data_name_list:
            # data_name是否合法验证
            data_name = data_name_obj["name"]
            custom_report_type = data_name_obj["custom_report_type"]
            if not data_name:
                logger.exception(_("数据源名称不能为空"))
                raise MonitorReportRequestException(ErrorEnum.PARAMS_VERIFY_ERROR, "name can not be empty")

            try:
                bk_monitor_config = MonitorReportConfig.objects.get(data_name=data_name)
            except MonitorReportConfig.DoesNotExist:
                bk_monitor_config = MonitorReportConfig.objects.create(
                    **{"data_name": data_name, "bk_biz_id": self.bk_biz_id}
                )

            # 判断data_id table_ud access_token 是否已有记录 如果均有 则不需要进行对应查找
            if bk_monitor_config.data_id and bk_monitor_config.table_id and bk_monitor_config.access_token:
                logger.info(f"complete report_config data_name -> {data_name}")
                continue

            data_name_builder = DataNameBuilder(data_name, self.bk_biz_id, data_name_prefix=self.app_id)
            ok, data = self._get_data_id(data_name_builder)
            if not ok:
                self._client.create_data_id(
                    {
                        "data_name": data_name_builder.name,
                        "etl_config": TIME_SERIES_ETL_CONFIG
                        if custom_report_type == TIME_SERIES_TYPE
                        else EVENT_ETL_CONFIG,
                        "type_label": custom_report_type,
                        "source_label": SOURCE_LABEL,
                        "option": OPTION,
                    }
                )
                ok, data = self._get_data_id(data_name_builder)
                if not ok:
                    logger.error(_(f"data_id已创建却无法获取相关信息， 建议联系管理员处理 data_name -> {data_name}"))
                    raise MonitorReportResultException(
                        ErrorEnum.CALL_GET_DATA_ID_RESPONSE_ERROR, _("data_id已创建却无法获取相关信息， 建议联系管理员处理")
                    )

            bk_monitor_config.table_id = data["table_id"]
            bk_monitor_config.data_id = data["data_id"]
            bk_monitor_config.access_token = data["access_token"]
            bk_monitor_config.custom_report_type = custom_report_type

            if custom_report_type == EVENT_TYPE:
                # 判断是否已经创建event_group
                if not bk_monitor_config.table_id:
                    result = self._client.create_event_group(
                        {
                            "bk_data_id": bk_monitor_config.data_id,
                            "bk_biz_id": self.bk_biz_id,
                            "event_group_name": data_name_builder.time_series_group_name,
                            "label": LABEL,
                            "event_info_list": [],
                        }
                    )
                    bk_monitor_config.table_id = result["table_id"]
            if custom_report_type == TIME_SERIES_TYPE:
                # 判断是否已经创建time_series_group
                if not bk_monitor_config.table_id:
                    self._client.create_time_series_group(
                        {
                            "bk_data_id": bk_monitor_config.data_id,
                            "bk_biz_id": self.bk_biz_id,
                            "time_series_group_name": data_name_builder.time_series_group_name,
                            "label": LABEL,
                            "table_id": data_name_builder.table_id,
                        }
                    )
                    bk_monitor_config.table_id = data_name_builder.table_id

            bk_monitor_config.save()
            logger.info(f"create report config successful data_name -> {data_name}")

        # 维护data_id 是否enable
        self._enable_data_id([data_name_obj["name"] for data_name_obj in data_name_list])
        logger.info("enable data_id successful")

    def report(self, collector_import_paths: list = None, namespaces: list = None):
        """
        将已通过 register_metric 注册的对应metric收集发送给监控，可在tasks 任务中增加对应任务即可
        Attributes:
            collector_import_paths: list 动态引用文件列表
            namespaces: 允许上报namespace列表
        """

        data = MetricCollector(collector_import_paths=collector_import_paths).collect(namespaces=namespaces)

        for key, val in data.items():
            if not self._report_params_verity(key, val):
                continue
            try:
                monitor_report_config = MonitorReportConfig.objects.get(data_name=key, is_enable=True)
            except MonitorReportConfig.DoesNotExist:
                logger.info(_("f{key} data_name初始化异常，请检查"))
                continue

            try:
                chunks = [val[i : i + BATCH_SIZE] for i in range(0, len(val), BATCH_SIZE)]
                for chunk in chunks:
                    self._client.custom_report(
                        {
                            "data_id": monitor_report_config.data_id,
                            "access_token": monitor_report_config.access_token,
                            "data": chunk,
                        }
                    )
            except Exception as e:  # pylint: disable=broad-except
                logger.warning(f"custom_report error: {e}")

    def trigger_event(self, data_name: str, event: dict):
        if not data_name:
            logger.error("[bk_monitor] data_name is empty")
            return

        try:
            monitor_report_config = MonitorReportConfig.objects.get(data_name=data_name, is_enable=True)
        except MonitorReportConfig.DoesNotExist:
            logger.error("[bk_monitor] data_name init failed please check")
            return
        try:
            self._client.custom_report(
                {
                    "data_id": monitor_report_config.data_id,
                    "access_token": monitor_report_config.access_token,
                    "data": [event],
                }
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(f"custom_report event error: {e}")

    def query(
        self,
        data_name: str,
        fields: list,
        where_conditions: Optional[List[str]] = None,
        group_by_conditions: Optional[List[str]] = None,
    ):
        """
        获取对应fields及对应addition返回结果集合
        Attributes：
            data_name: String 数据源名称
            fields: list 字段集合
            where_conditions：list where条件集合
            group_by_conditions: list group by 条件集合
        """
        table_id = CustomTable(data_name=data_name).table_id
        sql_slice = SqlSplice(fields, table_id)
        sql_slice.add_where_conditions(where_conditions)
        sql_slice.add_group_by_conditions(group_by_conditions)
        return self._client.get_ts_data(data={"sql": sql_slice.format_sql()})

    def _report_params_verity(self, key, val):
        """
        report 参数验证
        """
        if not key:
            logger.info(_(f"{key} data对应数据源为空，请检查数据源"))
            return False

        if not val:
            logger.info(_(f"{val} 数据源采集的数据为空"))
            return False

        return True

    def _get_data_id(self, data_name_builder):
        try:
            result = self._client.get_data_id({"data_name": data_name_builder.name})
        except MonitorReportResultException as e:
            if NOT_EXIST_MSG not in e.message:
                raise
            return False, {}

        data_id = result["data_id"]
        access_token = result["token"]
        table_id = None
        if result.get("result_table_list"):
            table_id = result["result_table_list"][0]["result_table"]
        return True, {"data_id": data_id, "access_token": access_token, "table_id": table_id}

    def _enable_data_id(self, data_name_list: list):
        monitor_report_configs = MonitorReportConfig.objects.all()
        for monitor_report_config in monitor_report_configs:
            if monitor_report_config.data_name in data_name_list and not monitor_report_config.is_enable:
                self._client.modify_data_id({"data_id": monitor_report_config.data_id, "is_enable": True})
                monitor_report_config.is_enable = True
                monitor_report_config.save()
                continue
            if monitor_report_config.data_name not in data_name_list and monitor_report_config.is_enable:
                self._client.modify_data_id({"data_id": monitor_report_config.data_id, "is_enable": False})
                monitor_report_config.is_enable = False
                monitor_report_config.save()
                continue


class BKMonitorModel(object):
    """
    对外提供data_name查询对应配置
    Attributes：
        data_name: String 数据源名称
    """

    def __init__(self, data_name: str):
        self._data_name = data_name
        try:
            self.monitor_report_config = MonitorReportConfig.objects.get(data_name=self._data_name, is_enable=True)
        except MonitorReportConfig.DoesNotExist:
            self.monitor_report_config = None

    @property
    def config(self):
        if not self.monitor_report_config:
            return {}
        else:
            return {
                "data_id": self.monitor_report_config.data_id,
                "data_name": self.monitor_report_config.data_name,
                "bk_biz_id": self.monitor_report_config.bk_biz_id,
                "table_id": self.monitor_report_config.table_id,
                "access_token": self.monitor_report_config.access_token,
                "is_enable": self.monitor_report_config.is_enable,
            }
