# -*- coding: utf-8 -*-

from unittest.mock import patch
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from bk_monitor.handler import monitor
from bk_monitor.models import MonitorReportConfig
from bk_monitor.utils.metric import register_metric
from bk_monitor.utils.metric import Metric

# 公共测试常量
APP_ID = ""
APP_TOKEN = ""
MONITOR_HOST = ""
REPORT_HOST = ""
BK_USER_NAME = "admin"
BK_BIZ_ID = 2005000002

# migrate 配置
DATA_NAME_1 = "test_1"
DATA_NAME_4 = "test_4"
DATA_ID_RESPONSE_DEMO_1 = {
    "bk_data_id": 524852,
    "data_id": 524852,
    "mq_config": {
        "storage_config": {"topic": "0bkmonitor_5248520", "partition": 1},
        "cluster_config": {
            "domain_name": "kafka.service.consul",
            "port": 9092,
            "schema": None,
            "is_ssl_verify": False,
            "cluster_id": 16,
            "cluster_name": "kafka_cluster1",
            "version": None,
            "custom_option": "",
            "registered_system": "_default",
            "creator": "system",
            "create_time": 1611221280,
            "last_modify_user": "system",
            "is_default_cluster": True,
        },
        "cluster_type": "kafka",
        "auth_info": {"password": "", "username": ""},
    },
    "etl_config": "bk_standard_v2_time_series",
    "result_table_list": [
        {
            "result_table": "2005000002_log_search_4_test_1.base",
            "shipper_list": [
                {
                    "storage_config": {
                        "real_table_name": "base",
                        "database": "2005000002_log_search_4_test_1",
                        "retention_policy_name": "",
                    },
                    "cluster_config": {
                        "domain_name": "influxdb-proxy.bkmonitorv3.service.consul",
                        "port": 10203,
                        "schema": None,
                        "is_ssl_verify": False,
                        "cluster_id": 14,
                        "cluster_name": "influxdb_cluster",
                        "version": None,
                        "custom_option": "",
                        "registered_system": "_default",
                        "creator": "system",
                        "create_time": 1611221280,
                        "last_modify_user": "system",
                        "is_default_cluster": True,
                    },
                    "cluster_type": "influxdb",
                    "auth_info": {"password": "", "username": ""},
                }
            ],
            "field_list": [
                {
                    "field_name": "target",
                    "type": "string",
                    "tag": "dimension",
                    "default_value": None,
                    "is_config_by_user": True,
                    "description": "",
                    "unit": "",
                    "alias_name": "",
                    "option": {},
                },
                {
                    "field_name": "time",
                    "type": "timestamp",
                    "tag": "timestamp",
                    "default_value": "",
                    "is_config_by_user": True,
                    "description": _("数据上报时间"),
                    "unit": "",
                    "alias_name": "",
                    "option": {},
                },
            ],
            "schema_type": "free",
            "option": {},
        }
    ],
    "option": {
        "inject_local_time": True,
        "timestamp_precision": "ms",
        "flat_batch_key": "data",
        "metrics_report_path": "bkmonitorv3_ieod_production/metadata/influxdb_metrics/524852/time_series_metric",
        "disable_metric_cutter": "true",
    },
    "type_label": "time_series",
    "source_label": "custom",
    "token": "59d696b950774d6287bc8ad106e56575",
    "transfer_cluster_id": "default",
}
DATA_ID_RESPONSE_DEMO_4 = {
    "bk_data_id": 524855,
    "data_id": 524855,
    "mq_config": {
        "storage_config": {"topic": "0bkmonitor_5248550", "partition": 1},
        "cluster_config": {
            "domain_name": "kafka.service.consul",
            "port": 9092,
            "schema": None,
            "is_ssl_verify": False,
            "cluster_id": 16,
            "cluster_name": "kafka_cluster1",
            "version": None,
            "custom_option": "",
            "registered_system": "_default",
            "creator": "system",
            "create_time": 1611221280,
            "last_modify_user": "system",
            "is_default_cluster": True,
        },
        "cluster_type": "kafka",
        "auth_info": {"password": "", "username": ""},
    },
    "etl_config": "bk_standard_v2_time_series",
    "result_table_list": [
        {
            "result_table": "2005000002_log_search_log_search_4_test_4.base",
            "shipper_list": [
                {
                    "storage_config": {
                        "real_table_name": "base",
                        "database": "2005000002_log_search_log_search_4_test_4",
                        "retention_policy_name": "",
                    },
                    "cluster_config": {
                        "domain_name": "influxdb-proxy.bkmonitorv3.service.consul",
                        "port": 10203,
                        "schema": None,
                        "is_ssl_verify": False,
                        "cluster_id": 14,
                        "cluster_name": "influxdb_cluster",
                        "version": None,
                        "custom_option": "",
                        "registered_system": "_default",
                        "creator": "system",
                        "create_time": 1611221280,
                        "last_modify_user": "system",
                        "is_default_cluster": True,
                    },
                    "cluster_type": "influxdb",
                    "auth_info": {"password": "", "username": ""},
                }
            ],
            "field_list": [
                {
                    "field_name": "target",
                    "type": "string",
                    "tag": "dimension",
                    "default_value": None,
                    "is_config_by_user": True,
                    "description": "",
                    "unit": "",
                    "alias_name": "",
                    "option": {},
                },
                {
                    "field_name": "time",
                    "type": "timestamp",
                    "tag": "timestamp",
                    "default_value": "",
                    "is_config_by_user": True,
                    "description": _("数据上报时间"),
                    "unit": "",
                    "alias_name": "",
                    "option": {},
                },
            ],
            "schema_type": "free",
            "option": {},
        }
    ],
    "option": {
        "inject_local_time": True,
        "timestamp_precision": "ms",
        "flat_batch_key": "data",
        "metrics_report_path": "bkmonitorv3_ieod_production/metadata/influxdb_metrics/524855/time_series_metric",
        "disable_metric_cutter": "True",
    },
    "type_label": "time_series",
    "source_label": "custom",
    "token": "4655d514cd2c4ac79508d8ca06359d73",
    "transfer_cluster_id": "default",
}
MIGRATE_RESULT = [
    {
        "data_id": 524852,
        "data_name": "test_1",
        "bk_biz_id": 2005000002,
        "table_id": "2005000002_log_search_4_test_1.base",
        "access_token": "59d696b950774d6287bc8ad106e56575",
    },
    {
        "data_id": 524855,
        "data_name": "test_4",
        "bk_biz_id": 2005000002,
        "table_id": "2005000002_log_search_log_search_4_test_4.base",
        "access_token": "4655d514cd2c4ac79508d8ca06359d73",
    },
]

# report 配置
NAMESPACE = "test1"
METRIC_NAME = "test_metric_1"
METRIC_VALUE = 1
DIMENSIONS = {"dimension": 1}
CURRENT_TIMESTAMP = 1617223184.0

# query 配置
WHERE_CONDITIONS = ["a>1", "b>1"]
GROUP_BY_CONDITIONS = ["data", "minute1"]
QUERY_RESULT = {
    "list": [{"time": 1617223184000, "test1_test_metric_1": 1, "dimension": 1}],
    "totalRecords": 1,
    "timetaken": 0.005821943283081055,
    "device": "influxdb",
}


def get_data_id(self, data):
    if DATA_NAME_1 in data["data_name"]:
        return DATA_ID_RESPONSE_DEMO_1
    elif DATA_NAME_4 in data["data_name"]:
        return DATA_ID_RESPONSE_DEMO_4


def modify_data_id(self, data):
    return True


@register_metric(namespace=NAMESPACE, data_name=DATA_NAME_4)
def test_collect_metric():
    return [
        Metric(metric_name=METRIC_NAME, metric_value=METRIC_VALUE, dimensions=DIMENSIONS, timestamp=CURRENT_TIMESTAMP)
    ]


def custom_report(self, data):
    return


def get_ts_data(self, data):
    return QUERY_RESULT


class TestBkMonitor(TestCase):
    monitor_object = monitor.BKMonitor(
        app_id=APP_ID,
        app_token=APP_TOKEN,
        monitor_host=MONITOR_HOST,
        report_host=REPORT_HOST,
        bk_username=BK_USER_NAME,
        bk_biz_id=BK_BIZ_ID,
    )

    @patch("bk_monitor.api.client.Client.get_data_id", get_data_id)
    @patch("bk_monitor.api.client.Client.modify_data_id", modify_data_id)
    def test_migrate(self):
        self.monitor_object.custom_metric().migrate(data_name_list=[DATA_NAME_1])
        self.monitor_object.custom_metric().migrate(data_name_list=[DATA_NAME_4], data_name_prefix="log-search")
        monitor_report_config = [
            obj
            for obj in MonitorReportConfig.objects.all().values(
                "data_id", "data_name", "bk_biz_id", "table_id", "access_token"
            )
        ]
        self.assertEqual(monitor_report_config, MIGRATE_RESULT)

    @patch("bk_monitor.api.client.Client.custom_report", custom_report)
    def test_report(self):
        self.test_migrate()
        self.monitor_object.custom_metric().report()

    @patch("bk_monitor.api.client.Client.get_ts_data", get_ts_data)
    def test_query(self):
        self.test_migrate()
        self.assertEqual(
            self.monitor_object.custom_metric().query(
                data_name=DATA_NAME_4,
                fields=[f"{NAMESPACE}_{METRIC_NAME}"],
                # where_conditions=WHERE_CONDITIONS,
                # group_by_conditions=GROUP_BY_CONDITIONS,
            ),
            QUERY_RESULT,
        )
