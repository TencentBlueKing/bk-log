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
from unittest.mock import patch
from django.test import TestCase, override_settings
from .test_collectorhandler import TestCollectorHandler
from ..log_search.test_indexset import Dummy
from ...log_databus.constants import AsyncStatus
from ...log_databus.handlers.clean import CleanHandler
from ...log_databus.handlers.collector import CollectorHandler
from ...log_databus.utils.bkdata_clean import BKDataCleanUtils
from ...log_databus.utils.clean import CleanFilterUtils
from ...log_search.models import ProjectInfo, Space

CREATE_CLEAN_STASH_PARAMS = {
    "name": "test",
    "clean_type": "bk_log_text",
    "etl_params": {"retain_original_text": True, "separator": " "},
    "etl_fields": [
        {
            "field_name": "user",
            "alias_name": "",
            "field_type": "long",
            "description": "字段描述",
            "is_analyzed": True,
            "is_dimension": True,
            "is_time": True,
            "is_delete": True,
        }
    ],
    "bk_biz_id": 0,
}

PARAMS = {
    "bk_biz_id": 0,
    "collector_config_name": "采集项名称",
    "collector_config_name_en": "test",
    "collector_scenario_id": "row",
    "category_id": "application",
    "target_object_type": "HOST",
    "target_node_type": "TOPO",
    "target_nodes": [{"bk_inst_id": 33, "bk_obj_id": "module"}],
    "data_encoding": "UTF-8",
    "bk_data_name": "abc",
    "description": "这是一个描述",
    "params": {
        "paths": ["/log/abc"],
        "conditions": {
            "type": "match",
            "match_type": "include",
            "match_content": "delete",
            "separator": "|",
            "separator_filters": [
                {"fieldindex": 1, "word": "val1", "op": "=", "logic_op": "or"},
                {"fieldindex": 2, "word": "val2", "op": "=", "logic_op": "or"},
            ],
        },
        "tail_files": True,
        "ignore_older": 1,
        "max_bytes": 1,
    },
    "storage_cluster_id": "default",
    "storage_expires": 1,
}

get_config_db_list_result = [
    {
        "status": "正常",
        "result_table_name_alias": "原始数据入库测试19",
        "data_type": "raw_data",
        "data_name": "log_tt_25",
        "storage_type": "es",
        "expire_time": "1天",
        "bk_biz_id": 706,
        "status_en": "started",
        "storage_type_alias": "未知-es",
        "created_at": "2019-02-21T20:19:37",
        "created_by": "test",
        "result_table_name": "xxxx_test19",
        "data_alias": "测试log接入",
        "raw_data_id": 1,
        "storage_cluster": "es-test",
        "result_table_id": "706_xxxx_test19",
    }
]

PROJECT_INFO = {
    "project_id": 1,
    "project_name": "test",
    "bk_biz_id": 706,
    "bk_app_code": "log-search-4",
    "time_zone": "Asia/Shanghai",
}

SPACE_INFO = {
    "space_uid": "bkcc__706",
    "bk_biz_id": 706,
    "space_type_id": "bkcc",
    "space_type_name": "业务",
    "space_id": "706",
    "space_name": "test",
}


class PermissionTest(object):
    def grant_creator_action(self, resource):
        return True


class IndexSet(object):
    index_set_id = 1
    bkdata_auth_url = "test"


@patch("apps.iam.handlers.drf.BusinessActionPermission.has_permission", return_value=True)
@patch("apps.log_search.tasks.mapping.sync_single_index_set_mapping_snapshot.delay", return_value=None)
@patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id", return_value=None)
@patch("apps.iam.handlers.drf.InstanceActionPermission.has_permission", return_value=True)
@patch("apps.iam.handlers.drf.ViewBusinessPermission.has_permission", return_value=True)
@patch("apps.iam.handlers.permission.Permission.batch_is_allowed", return_value=Dummy())
@patch("apps.decorators.user_operation_record.delay", return_value=None)
@patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id.delay", return_value=None)
@patch("apps.log_databus.tasks.bkdata.sync_clean.delay", return_value=None)
# @patch("django.core.cache.cache", FakeCache())
class TestClean(TestCase):
    def test_create_clean_stash(self, *args, **kwargs):
        collector_config_id, create_stash_result = self._create_clean_stash()
        self.assertEqual(create_stash_result["clean_type"], CREATE_CLEAN_STASH_PARAMS["clean_type"])
        self.assertEqual(create_stash_result["etl_params"], CREATE_CLEAN_STASH_PARAMS["etl_params"])
        self.assertEqual(create_stash_result["etl_fields"], CREATE_CLEAN_STASH_PARAMS["etl_fields"])
        self.assertEqual(create_stash_result["bk_biz_id"], CREATE_CLEAN_STASH_PARAMS["bk_biz_id"])
        self.assertEqual(create_stash_result["collector_config_id"], collector_config_id)

    def test_get_stash(self, *args, **kwargs):
        collector_config_id, _ = self._create_clean_stash()
        get_stash_result = CollectorHandler(collector_config_id=collector_config_id).get_clean_stash()
        self.assertEqual(get_stash_result["clean_type"], CREATE_CLEAN_STASH_PARAMS["clean_type"])
        self.assertEqual(get_stash_result["etl_params"], CREATE_CLEAN_STASH_PARAMS["etl_params"])
        self.assertEqual(get_stash_result["etl_fields"], CREATE_CLEAN_STASH_PARAMS["etl_fields"])
        self.assertEqual(get_stash_result["bk_biz_id"], CREATE_CLEAN_STASH_PARAMS["bk_biz_id"])
        self.assertEqual(get_stash_result["collector_config_id"], collector_config_id)

    @patch("apps.feature_toggle.handlers.toggle.FeatureToggleObject.switch", return_value=True)
    def test_list_clean(self, *args, **kwargs):
        self.test_refresh()
        clean_list = CleanFilterUtils(bk_biz_id=706).filter(page=1, pagesize=1, keyword="", etl_config="")
        self.assertEqual(clean_list["total"], 1)
        clean_list_keyword_one = CleanFilterUtils(bk_biz_id=706).filter(
            page=1, pagesize=1, keyword="test", etl_config=""
        )
        print(clean_list_keyword_one)
        self.assertEqual(clean_list_keyword_one["total"], 1)
        clean_list_keyword_none = CleanFilterUtils(bk_biz_id=706).filter(
            page=1, pagesize=1, keyword="test2", etl_config=""
        )
        self.assertEqual(clean_list_keyword_none["total"], 0)
        clean_list_etl_config_one = CleanFilterUtils(bk_biz_id=706).filter(
            page=1, pagesize=1, keyword="test", etl_config="bkdata_clean"
        )
        self.assertEqual(clean_list_etl_config_one["total"], 1)
        clean_list_etl_config_none = CleanFilterUtils(bk_biz_id=706).filter(
            page=1, pagesize=1, keyword="test", etl_config="bk_log_text"
        )
        self.assertEqual(clean_list_etl_config_none["total"], 0)

    @patch("apps.api.BkDataDatabusApi.get_config_db_list", lambda params: get_config_db_list_result)
    @patch("apps.log_search.handlers.index_set.IndexSetHandler.create", return_value=IndexSet)
    @patch("apps.log_search.handlers.index_set.IndexSetHandler.delete", return_value=IndexSet)
    def test_refresh(self, *args, **kwargs):
        self._init_project_info()
        _, create_collector_result = TestCollectorHandler.create()
        collector_config_id = create_collector_result["collector_config_id"]
        self.collector = CollectorHandler(collector_config_id=collector_config_id)
        result_table_names = CleanHandler(collector_config_id=collector_config_id).refresh(
            raw_data_id=self.collector.data.bk_data_id, bk_biz_id=self.collector.data.bk_biz_id
        )
        self.assertEqual([result_table_name for result_table_name in result_table_names], ["xxxx_test19"])

    @override_settings(CACHES={"default": {"BACKEND": "apps.tests.log_esquery.test_qos.FakeCache"}})
    def test_sync(self, *args, **kwargs):
        self.assertEqual(CleanHandler.sync(bk_biz_id=706, polling=False), AsyncStatus.RUNNING)
        self.assertEqual(CleanHandler.sync(bk_biz_id=706, polling=True), AsyncStatus.RUNNING)
        BKDataCleanUtils.unlock_sync_clean(bk_biz_id=706)
        self.assertEqual(CleanHandler.sync(bk_biz_id=706, polling=True), AsyncStatus.DONE)

    @classmethod
    def _create_clean_stash(cls):
        _, create_collector_result = TestCollectorHandler.create()
        collector_config_id = create_collector_result["collector_config_id"]
        create_stash_result = CollectorHandler(collector_config_id=collector_config_id).create_clean_stash(
            CREATE_CLEAN_STASH_PARAMS
        )
        return collector_config_id, create_stash_result

    @classmethod
    def _init_project_info(cls):
        ProjectInfo.objects.create(**PROJECT_INFO)
        Space.objects.create(**SPACE_INFO)
