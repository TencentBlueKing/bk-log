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
import copy
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings

from apps.exceptions import ValidationError
from apps.log_databus.models import CollectorConfig
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.etl import EtlHandler
from apps.log_databus.serializers import CollectorEtlStorageSerializer
from apps.log_databus.constants import ETL_DELIMITER_DELETE, ETL_DELIMITER_END, ETL_DELIMITER_IGNORE
from apps.log_search.constants import FieldBuiltInEnum, FieldDateFormatEnum
from apps.utils.db import array_group

# 采集相关
COLLECTOR_CONFIG_ID = 1
BK_DATA_ID = 11
SUBSCRIPTION_ID = 12
TASK_ID = 13
COLLECTOR_CONFIG = {
    "collector_config_name": "采集项名称",
    "collector_scenario_id": "row",
    "bk_biz_id": 706,
    "category_id": "application",
    "target_object_type": "HOST",
    "target_node_type": "TOPO",
    "target_nodes": [
        {"id": 12},
        {"bk_inst_id": 33, "bk_obj_id": "module"},
        {"ip": "127.0.0.1", "bk_cloud_id": 0, "bk_supplier_id": 0},
    ],
    "target_subscription_diff": [],
    "description": "这是一个描述",
    "is_active": True,
    "subscription_id": SUBSCRIPTION_ID,
}

# 清洗相关
CLUSTER_INFO = {"cluster_config": {"version": "7.2"}}

TABLE_ID = "2_log.test_table"
ETL_CONFIG = "bk_log_text"
ETL_PARAMS = {}

ETL_CONFIG_JSON = "bk_log_json"
ETL_PARAMS_JSON = {"retain_original_text": True}

ETL_CONFIG_DELIMITER = "bk_log_delimiter"
ETL_PARAMS_DELIMITER = {"separator": "|", "retain_original_text": True}
ETL_DELIMITER_CONTENT = 'val1|{"key": "val"}||val4|other message'

# SDK只返回需要的字段
ETL_DELIMITER_PREVIEW_SDK = {
    "key1": "val1",
    "key2": '{"key": "val"}',
    "key3": "",
    "key4": "val4",
    "key5": "other message",
}
# 用户预览结果
ETL_DELIMITER_PREVIEW = []
for index, val in enumerate(ETL_DELIMITER_CONTENT.split("|")):
    ETL_DELIMITER_PREVIEW.append({"field_index": index + 1, "field_name": "", "value": val})

# 用户配置的字段信息
FIELDS_DELIMITER = [
    {
        "field_index": 1,
        "field_name": "key1",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    },
    {
        "field_index": 2,
        "field_name": "key2",
        "field_type": "object",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    },
    {
        "field_index": 5,
        "field_name": "",
        "field_type": "",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": True,
    },
]
# 根据FIELDS_DELIMITER需要生成的META.RT.separator_field_list
ETL_DELIMITER_META_FIELDS = [
    "key1",
    "key2",
    ETL_DELIMITER_IGNORE,
    ETL_DELIMITER_IGNORE,
    ETL_DELIMITER_DELETE,
    ETL_DELIMITER_END,
]

# 给前端需要返回有配置或删除的字段
ETL_DELIMITER_RESULT = {
    1: {"field_name": "key1", "field_type": "string", "is_delete": False},
    2: {"field_name": "key2", "field_type": "object", "is_delete": False},
    5: {"field_name": "", "field_type": "", "is_delete": True},
}

# 正则
ETL_CONFIG_REGEXP = "bk_log_regexp"
ETL_PARAMS_REGEXP = {
    "separator_regexp": "(?P<request_ip>[\\d\\.]+)[^[]+\\[(?P<request_time>[^]]+)\\]",
    "retain_original_text": True,
}
ETL_REGEXP_CONTENT = '127.0.0.1 - - [30/Nov/2019:21:07:10 +0800] "GET /api/v3/object/statistics HTTP/1.0" "200"'
FIELDS_REGEXP = [
    {
        "field_name": "request_ip",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    },
    {
        "field_name": "request_time",
        "field_type": "string",
        "alias_name": "",
        "is_time": True,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
        "option": {"time_zone": 8, "time_format": "dd/MMM/yyyy:HH:mm:ss Z"},
    },
]

TABLE_STR = "test_table"
STORAGE_CLUSTER_ID = 2
RETENTION_TIME = 30
ALLOCATION_MIN_DAYS = 7
HOT_WARM_CONFIG = {
    "is_enabled": True,
    "hot_attr_name": "temperature",
    "hot_attr_value": "hot",
    "warm_attr_name": "temperature",
    "warm_attr_value": "warm",
}
# 不可以与内置字段重复
FIELDS_ERROR_BUILT = [
    {
        "field_name": "ip",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    }
]

# 整形不可以分词
FIELDS_ERROR_ANALYZED = [
    {
        "field_name": "key1",
        "field_type": "int",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": True,
        "is_dimension": False,
        "is_delete": False,
    }
]

# 时间格式与类型冲突
FIELDS_ERROR_TIME_FORMAT = [
    {
        "field_name": "key1",
        "field_type": "int",
        "alias_name": "",
        "is_time": True,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
        "option": {"time_zone": 0, "time_format": "yyyy-MM-DD hh:mm:ss"},
    }
]

# 时间字段不可分词
FIELDS_ERROR_TIME_ANALYZED = [
    {
        "field_name": "key1",
        "field_type": "string",
        "alias_name": "",
        "is_time": True,
        "is_analyzed": True,
        "is_dimension": True,
        "is_delete": False,
        "option": {"time_zone": 0, "format": "yyyy-MM-DD hh:mm:ss"},
    }
]

# 不存在有效字段
FIELDS_ERROR_INVALID = [
    {
        "field_name": "ip",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": True,
    }
]

# 分隔符未带field_index
FIELDS_INDEX_INVALID = [
    {
        "field_name": "ip",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    }
]

# 删除字段判断
FIELDS_DELETE = [
    {
        "field_name": "ip",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": True,
    },
    {
        "field_name": "key1",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    },
]

# 正常字段清洗
FIELDS = [
    {
        "field_name": "ip",
        "field_type": "string",
        "alias_name": "key1",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": False,
        "is_delete": False,
    },
    {
        "field_name": "key2",
        "field_type": "string",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": True,
        "is_dimension": False,
        "is_delete": False,
    },
    {
        "field_name": "key3",
        "field_type": "int",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
    },
    {
        "field_name": "time1",
        "field_type": "string",
        "alias_name": "",
        "is_time": True,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": False,
        "option": {"time_zone": 0, "time_format": "yyyy-MM-DD hh:mm:ss"},
    },
    {
        "field_name": "delete1",
        "field_type": "int",
        "alias_name": "",
        "is_time": False,
        "is_analyzed": False,
        "is_dimension": True,
        "is_delete": True,
    },
]
# 时间字段的来源直接设为非维度
FIELDS_NOT_ES_DOC_VALUES_KEYS = ["key1", "time1"]
FIELDS_TIME_FIELD_ALIAS_NAME = "time1"
FIELDS_VAILD_NUM = 4
FIELDS_TIME_FIELD_OPTION = {
    "time_zone": 0,
    "format": "yyyy-MM-DD hh:mm:ss",
    "real_path": f"{EtlStorage.separator_node_name}.time1",
}

VIEW_ROLES = [1]
ETL_PARAMS = {
    "table_id": TABLE_ID,
    "etl_config": ETL_CONFIG,
    "etl_params": ETL_PARAMS,
    "fields": FIELDS,
    "storage_cluster_id": STORAGE_CLUSTER_ID,
    "retention": RETENTION_TIME,
    "view_roles": VIEW_ROLES,
}
LOG_INDEX_DATA = {
    "index_set_name": "索引集名称",
    "project_id": 111,
    "source_id": 2,
    "scenario_id": "es",
    "view_roles": [2],
    "bkdata_project_id": 11,
}


class TestEtl(TestCase):
    def test_etl_time(self):
        formsts = FieldDateFormatEnum.get_choices_list_dict()
        for format in formsts:
            try:
                etl_time = EtlHandler().etl_time(format["id"], 8, format["description"])
            except Exception as e:  # pylint: disable=broad-except
                etl_time = {"epoch_millis": "exception:" + str(e)}
            print(f'[{format["id"]}][{format["name"]}] {format["description"]} => {etl_time}')
            self.assertEqual(etl_time["epoch_millis"], "1136185445000")

    def test_etl_param(self):
        etl_param = {
            "table_id": TABLE_ID,
            "etl_config": ETL_CONFIG_JSON,
            "etl_params": ETL_PARAMS_JSON,
            "fields": FIELDS,
            "storage_cluster_id": STORAGE_CLUSTER_ID,
            "retention": RETENTION_TIME,
            "view_roles": VIEW_ROLES,
        }

        with self.assertRaises(ValidationError):
            etl_param["fields"] = FIELDS_ERROR_BUILT
            CollectorEtlStorageSerializer().validate(etl_param)

        with self.assertRaises(ValidationError):
            etl_param["fields"] = FIELDS_ERROR_ANALYZED
            CollectorEtlStorageSerializer().validate(etl_param)

        with self.assertRaises(ValidationError):
            etl_param["fields"] = FIELDS_ERROR_TIME_FORMAT
            CollectorEtlStorageSerializer().validate(etl_param)

        with self.assertRaises(ValidationError):
            etl_param["fields"] = FIELDS_ERROR_TIME_ANALYZED
            CollectorEtlStorageSerializer().validate(etl_param)

        with self.assertRaises(ValidationError):
            etl_param["fields"] = FIELDS_ERROR_INVALID
            CollectorEtlStorageSerializer().validate(etl_param)

        with self.assertRaises(ValidationError):
            etl_param["etl_config"] = ETL_CONFIG_DELIMITER
            etl_param["fields"] = FIELDS_INDEX_INVALID
            CollectorEtlStorageSerializer().validate(etl_param)

        etl_param["etl_config"] = ETL_CONFIG_JSON
        etl_param["fields"] = FIELDS_DELETE
        CollectorEtlStorageSerializer().validate(etl_param)
        return True

    @patch("apps.api.TransferApi.create_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.modify_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.get_cluster_info", lambda _: [CLUSTER_INFO])
    @patch("apps.log_databus.handlers.etl.EtlHandler._update_or_create_index_set")
    def test_bk_log_text(self, mock_index_set):
        collector_config = CollectorConfig.objects.create(**COLLECTOR_CONFIG)
        mock_index_set.return_value = LOG_INDEX_DATA

        # 直接入库
        etl_storage = EtlStorage.get_instance(ETL_CONFIG)
        result = etl_storage.update_or_create_result_table(
            collector_config,
            table_id=TABLE_ID,
            storage_cluster_id=STORAGE_CLUSTER_ID,
            retention=RETENTION_TIME,
            allocation_min_days=ALLOCATION_MIN_DAYS,
            storage_replies=1,
            fields=FIELDS,
            etl_params=ETL_PARAMS,
            hot_warm_config=HOT_WARM_CONFIG,
        )
        doc_values_nums = [item for item in result["params"]["field_list"] if "es_doc_values" in item["option"]]
        self.assertEqual(result["params"]["time_alias_name"], "utctime")
        self.assertEqual(len(doc_values_nums), 0, "直接入库不需要设置任何doc_values")
        self.assertTrue("es_doc_values" not in result["params"]["time_option"], "time_option必须设置且不可设置doc_values")

        etl_config = etl_storage.parse_result_table_config(result["params"])
        self.assertIsInstance(etl_config["etl_params"]["es_unique_field_list"], list)
        self.assertEqual(etl_config["etl_params"]["separator_node_action"], "")
        return True

    @patch("apps.api.TransferApi.create_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.modify_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.get_cluster_info", lambda _: [CLUSTER_INFO])
    @patch("apps.log_databus.handlers.etl.EtlHandler._update_or_create_index_set")
    def test_bk_log_json(self, mock_index_set):
        """
        JSON清洗
        """
        collector_config = CollectorConfig.objects.create(**COLLECTOR_CONFIG)
        mock_index_set.return_value = LOG_INDEX_DATA

        etl_storage = EtlStorage.get_instance(ETL_CONFIG_JSON)
        result = etl_storage.update_or_create_result_table(
            collector_config,
            table_id=TABLE_ID,
            storage_cluster_id=STORAGE_CLUSTER_ID,
            retention=RETENTION_TIME,
            allocation_min_days=ALLOCATION_MIN_DAYS,
            storage_replies=1,
            fields=FIELDS,
            etl_params=ETL_PARAMS_JSON,
            hot_warm_config=HOT_WARM_CONFIG,
        )
        built_in_keys = FieldBuiltInEnum.get_choices()
        fields_not_doc_values = []
        fields_user = {}
        for item in result["params"]["field_list"]:
            # 用户清洗字段
            if item["field_name"].lower() not in built_in_keys:
                if "es_doc_values" in item["option"]:
                    fields_not_doc_values.append(item["field_name"])
                source_field = item["alias_name"] if item.get("alias_name") else item["field_name"]
                fields_user[source_field] = item
        self.assertEqual(fields_not_doc_values, FIELDS_NOT_ES_DOC_VALUES_KEYS)
        self.assertEqual(len(fields_user), FIELDS_VAILD_NUM, "清洗字段数不一致")
        # 时间字段
        self.assertEqual(fields_user["time1"]["option"]["es_type"], "keyword")
        self.assertEqual(result["params"]["time_alias_name"], "time1")
        self.assertTrue("es_doc_values" not in result["params"]["time_option"], "time_option必须设置且不可设置doc_values")
        # option
        self.assertEqual(result["params"]["option"]["separator_fields_remove"], "delete1")

        # 字段解析
        etl_param = copy.deepcopy(result["params"])
        etl_config = etl_storage.parse_result_table_config(etl_param)

        self.assertIsInstance(etl_config["etl_params"]["es_unique_field_list"], list)
        self.assertEqual(etl_config["etl_params"]["separator_node_action"], "json")

        etl_fields = array_group(etl_config["fields"], "field_name", True)
        self.assertEqual(etl_fields["ip"]["alias_name"], "key1")
        self.assertTrue(etl_fields["key2"]["is_analyzed"])
        self.assertTrue(etl_fields["key3"]["is_dimension"])
        self.assertEqual(etl_fields["time1"]["option"]["es_type"], "date")
        self.assertTrue(etl_fields["time1"]["is_time"])
        self.assertTrue(etl_fields["time1"]["is_dimension"])
        self.assertTrue(etl_fields["delete1"]["is_delete"])
        return True

    @patch("apps.api.TransferApi.create_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.modify_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.get_cluster_info", lambda _: [CLUSTER_INFO])
    @patch("apps.log_databus.handlers.etl_storage.utils.transfer.preview")
    @patch("apps.log_databus.handlers.etl.EtlHandler._update_or_create_index_set")
    def test_bk_log_regexp(self, mock_index_set, mock_preview):
        """
        正则清洗
        """
        collector_config = CollectorConfig.objects.create(**COLLECTOR_CONFIG)
        mock_index_set.return_value = LOG_INDEX_DATA

        mock_preview.return_value = {"request_time": "30/Nov/2019:21:07:10 +0800", "request_ip": "127.0.0.1"}

        etl_storage = EtlStorage.get_instance(ETL_CONFIG_REGEXP)
        # 预览
        settings.ENVIRONMENT = "stag"
        etl_preview = etl_storage.etl_preview(ETL_REGEXP_CONTENT, ETL_PARAMS_REGEXP)
        self.assertEqual(etl_preview[0]["field_name"], "request_ip")

        # 清洗
        result = etl_storage.update_or_create_result_table(
            collector_config,
            table_id=TABLE_ID,
            storage_cluster_id=STORAGE_CLUSTER_ID,
            retention=RETENTION_TIME,
            allocation_min_days=ALLOCATION_MIN_DAYS,
            fields=FIELDS_REGEXP,
            storage_replies=1,
            etl_params=ETL_PARAMS_REGEXP,
            hot_warm_config=HOT_WARM_CONFIG,
        )
        built_in_keys = FieldBuiltInEnum.get_choices()
        fields_not_doc_values = []
        fields_user = {}
        for item in result["params"]["field_list"]:
            # 用户清洗字段
            if item["field_name"].lower() not in built_in_keys:
                if "es_doc_values" in item["option"]:
                    fields_not_doc_values.append(item["field_name"])
                source_field = item["alias_name"] if item.get("alias_name") else item["field_name"]
                fields_user[source_field] = item
        # 时间字段
        self.assertEqual(fields_user["request_ip"]["option"]["es_type"], "keyword")
        self.assertEqual(result["params"]["time_alias_name"], "request_time")
        self.assertTrue("es_doc_values" not in result["params"]["time_option"], "time_option必须设置且不可设置doc_values")

        # 字段解析
        etl_param = copy.deepcopy(result["params"])
        etl_config = etl_storage.parse_result_table_config(etl_param)

        etl_fields = array_group(etl_config["fields"], "field_name", True)
        self.assertEqual(etl_fields["request_time"]["option"]["es_type"], "date")
        return True

    @patch("apps.api.TransferApi.create_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.modify_result_table", lambda _: {"table_id": TABLE_ID})
    @patch("apps.api.TransferApi.get_cluster_info", lambda _: [CLUSTER_INFO])
    @patch("apps.log_databus.handlers.etl_storage.utils.transfer.preview")
    @patch("apps.log_databus.handlers.etl.EtlHandler._update_or_create_index_set")
    def test_bk_log_delimiter(self, mock_index_set, mock_preview):
        """
        分隔符清洗
        """
        collector_config = CollectorConfig.objects.create(**COLLECTOR_CONFIG)
        mock_index_set.return_value = LOG_INDEX_DATA
        mock_preview.return_value = ETL_DELIMITER_PREVIEW_SDK

        etl_storage = EtlStorage.get_instance(ETL_CONFIG_DELIMITER)
        # 预览
        settings.ENVIRONMENT = "stag"
        etl_preview = etl_storage.etl_preview(ETL_DELIMITER_CONTENT, ETL_PARAMS_DELIMITER)
        self.assertEqual(etl_preview, ETL_DELIMITER_PREVIEW)

        # 清洗
        result = etl_storage.update_or_create_result_table(
            collector_config,
            table_id=TABLE_ID,
            storage_cluster_id=STORAGE_CLUSTER_ID,
            retention=RETENTION_TIME,
            allocation_min_days=ALLOCATION_MIN_DAYS,
            fields=FIELDS_DELIMITER,
            storage_replies=1,
            etl_params=ETL_PARAMS_DELIMITER,
            hot_warm_config=HOT_WARM_CONFIG,
        )

        # 字段解析
        etl_param = copy.deepcopy(result["params"])
        etl_config = etl_storage.parse_result_table_config(etl_param)
        user_fields = list(filter(lambda x: not x.get("is_built_in", False), etl_config["fields"]))

        # 比较用户字段
        self.assertEqual(len(user_fields), 3)
        for field in user_fields:
            etl_field = ETL_DELIMITER_RESULT.get(field["field_index"], False)
            if not etl_field:
                self.assertTrue(etl_field, f"ETL结果异常: 第{field['field_index']}列不存在")
            self.assertEqual(field["field_name"], etl_field["field_name"])
            self.assertEqual(field["field_type"], etl_field["field_type"])
            self.assertEqual(field["is_delete"], etl_field["is_delete"])

        # 比较 META信息
        self.assertEqual(etl_config["etl_params"]["separator_field_list"], ETL_DELIMITER_META_FIELDS)

        return True
