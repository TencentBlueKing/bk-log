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
import copy

import arrow
import json
from unittest.mock import patch

from blueapps.account.models import User
from django.conf import settings
from django.test import TestCase, override_settings

from apps.log_search.models import LogIndexSet

BK_BIZ_ID = 1
SPACE_UID = "bkcc__2"
STORAGE_CLUSTER_ID = 1
SUCCESS_STATUS_CODE = 200
SOURCE_APP_CODE = "log-search-4"
SCENARIO_ID_ES = "es"
SCENARIO_ID_BKDATA = "bkdata"

OVERRIDE_MIDDLEWARE = "apps.tests.middlewares.OverrideMiddleware"

CLUSTER_INFO = [{"cluster_config": {"cluster_id": 1, "cluster_name": ""}}]

CLUSTER_INFO_WITH_AUTH = [
    {"cluster_config": {"cluster_id": 1, "cluster_name": ""}, "auth_info": {"username": "", "password": ""}}
]

CLUSTER_INFOS = {"2_bklog.test3333": {"cluster_config": {"cluster_id": 1, "cluster_name": ""}}}

MAPPING_LIST = [
    {"properties": {"date": {"type": "timestamp"}, "log": {"type": "string"}, "server_id": {"type": "long"}}}
]

CREATE_SUCCESS = {
    "result": True,
    "data": {
        "bcs_project_id": "",
        "index_set_id": 5,
        "view_roles": [],
        "bkdata_project_id": None,
        "indexes": [],
        "is_trace_log": False,
        "time_field": "abc",
        "time_field_type": "date",
        "time_field_unit": "millisecond",
        "index_set_name": "登陆日志",
        "storage_cluster_id": 1,
        "category_id": "other_rt",
        "scenario_id": "es",
        "project_id": 0,
        "space_uid": "bkcc__2",
        "bkdata_auth_url": "",
        "created_at": "2021-06-26 16:06:18+0800",
        "created_by": "admin",
        "updated_at": "2021-06-26 16:06:18+0800",
        "updated_by": "admin",
        "is_deleted": False,
        "deleted_at": None,
        "deleted_by": None,
        "collector_config_id": None,
        "source_id": None,
        "orders": 0,
        "pre_check_tag": True,
        "pre_check_msg": None,
        "is_active": True,
        "fields_snapshot": None,
        "source_app_code": settings.APP_CODE,
        "tag_ids": "",
        "is_editable": True,
    },
    "code": 0,
    "message": "",
}

DELETE_SUCCESS = {"message": "", "code": 0, "data": None, "result": True}

UPDATE_INDEX_SET = {
    "bcs_project_id": "",
    "index_set_id": 102,
    "view_roles": [],
    "bkdata_project_id": None,
    "indexes": [
        {
            "index_id": 204,
            "index_set_id": 102,
            "bk_biz_id": None,
            "bk_biz_name": None,
            "source_id": None,
            "source_name": "--",
            "result_table_id": "log_xxx",
            "time_field": "timestamp",
            "result_table_name": None,
            "apply_status": "normal",
            "apply_status_name": "正常",
        },
        {
            "index_id": 203,
            "index_set_id": 102,
            "bk_biz_id": 1,
            "bk_biz_name": None,
            "source_id": None,
            "source_name": "--",
            "result_table_id": "591_xx",
            "time_field": "timestamp",
            "result_table_name": None,
            "apply_status": "normal",
            "apply_status_name": "正常",
        },
    ],
    "is_trace_log": False,
    "time_field": "abc",
    "time_field_type": "date",
    "time_field_unit": "millisecond",
    "created_at": "2021-06-26 16:19:32+0800",
    "created_by": "admin",
    "updated_at": "2021-06-26 16:19:32+0800",
    "updated_by": "admin",
    "is_deleted": False,
    "deleted_at": None,
    "deleted_by": None,
    "index_set_name": "登陆日志",
    "project_id": 0,
    "space_uid": "bkcc__2",
    "category_id": "host",
    "collector_config_id": None,
    "scenario_id": "es",
    "storage_cluster_id": 1,
    "source_id": None,
    "orders": 0,
    "pre_check_tag": True,
    "pre_check_msg": None,
    "is_active": True,
    "fields_snapshot": "{}",
    "source_app_code": settings.APP_CODE,
    "tag_ids": "[]",
    "is_editable": True,
}

NOT_EDITABLE_RETURN = {
    "result": False,
    "code": "3600001",
    "data": None,
    "message": "索引集登陆日志禁止编辑（3600001）",
    "errors": None,
}

INDEX_SET_LISTS = {
    "total": 1,
    "list": [
        {
            "index_set_id": 31,
            "view_roles": [],
            "bkdata_project_id": None,
            "bcs_project_id": "",
            "indexes": [
                {
                    "index_id": 62,
                    "index_set_id": 31,
                    "bk_biz_id": None,
                    "bk_biz_name": None,
                    "source_id": None,
                    "source_name": "--",
                    "result_table_id": "log_xxx",
                    "time_field": "timestamp",
                    "result_table_name": None,
                    "apply_status": "normal",
                    "apply_status_name": "正常",
                },
                {
                    "index_id": 61,
                    "index_set_id": 31,
                    "bk_biz_id": 1,
                    "bk_biz_name": None,
                    "source_id": None,
                    "source_name": "--",
                    "result_table_id": "591_xx",
                    "time_field": "timestamp",
                    "result_table_name": None,
                    "apply_status": "normal",
                    "apply_status_name": "正常",
                },
            ],
            "is_trace_log": False,
            "time_field": "abc",
            "time_field_type": "date",
            "time_field_unit": "millisecond",
            "created_at": "2021-06-26 16:11:58+0800",
            "created_by": "admin",
            "updated_at": "2021-06-26 16:11:58+0800",
            "updated_by": "admin",
            "is_deleted": False,
            "deleted_at": None,
            "deleted_by": None,
            "index_set_name": "登陆日志",
            "project_id": 0,
            "space_uid": "bkcc__2",
            "category_id": "other_rt",
            "collector_config_id": None,
            "scenario_id": "es",
            "storage_cluster_id": 1,
            "source_id": None,
            "orders": 0,
            "pre_check_tag": True,
            "pre_check_msg": None,
            "is_active": True,
            "fields_snapshot": "{}",
            "source_app_code": settings.APP_CODE,
            "tag_ids": "[]",
            "category_name": "其他",
            "scenario_name": "第三方ES",
            "storage_cluster_name": "",
            "apply_status": "normal",
            "apply_status_name": "正常",
            "bk_biz_id": 2,
            "permission": {},
            "is_editable": True,
        }
    ],
}

TOKEN_PERMISSIONS = {
    "permissions": [
        {
            "status": "active",
            "data_token_id": 592,
            "scope_id_key": "result_table_id",
            "updated_by": "admin",
            "created_at": "2020-04-26 17:35:50",
            "description": None,
            "scope_name_key": "result_table_name",
            "updated_at": "2020-04-26 17:35:50",
            "created_by": "admin",
            "scope_display": {"result_table_name": "2_test_table_1"},
            "scope": {
                "result_table_name": "2_test_table_1",
                "result_table_id": "2_test_table_1",
                "description": "测试表1",
            },
            "object_class": "result_table",
            "id": 4297,
            "scope_object_class": "result_table",
            "action_id": "result_table.query_data",
        }
    ]
}

SYSC_AUTH_STATUS_RESULT = [
    {
        "index_id": 154,
        "index_set_id": 135,
        "bk_biz_id": None,
        "bk_biz_name": None,
        "source_id": None,
        "source_name": "--",
        "result_table_id": "log_xxx",
        "time_field": "timestamp",
        "result_table_name": None,
        "apply_status": "normal",
        "apply_status_name": "正常",
    },
    {
        "index_id": 153,
        "index_set_id": 135,
        "bk_biz_id": 1,
        "bk_biz_name": None,
        "source_id": None,
        "source_name": "--",
        "result_table_id": "591_xx",
        "time_field": "timestamp",
        "result_table_name": None,
        "apply_status": "normal",
        "apply_status_name": "正常",
    },
]

RETRIEVE_LIST = {
    "bcs_project_id": "",
    "index_set_id": 63,
    "view_roles": [],
    "bkdata_project_id": None,
    "indexes": [
        {
            "index_id": 126,
            "index_set_id": 63,
            "bk_biz_id": None,
            "bk_biz_name": None,
            "source_id": None,
            "source_name": "--",
            "result_table_id": "log_xxx",
            "time_field": "timestamp",
            "result_table_name": None,
            "apply_status": "normal",
            "apply_status_name": "正常",
        },
        {
            "index_id": 125,
            "index_set_id": 63,
            "bk_biz_id": 1,
            "bk_biz_name": None,
            "source_id": None,
            "source_name": "--",
            "result_table_id": "591_xx",
            "time_field": "timestamp",
            "result_table_name": None,
            "apply_status": "normal",
            "apply_status_name": "正常",
        },
    ],
    "is_trace_log": False,
    "time_field": "abc",
    "time_field_type": "date",
    "time_field_unit": "millisecond",
    "source_name": "--",
    "created_at": "2021-06-26 16:15:41+0800",
    "created_by": "admin",
    "updated_at": "2021-06-26 16:15:41+0800",
    "updated_by": "admin",
    "is_deleted": False,
    "deleted_at": None,
    "deleted_by": None,
    "index_set_name": "登陆日志",
    "project_id": 0,
    "space_uid": "bkcc__2",
    "category_id": "other_rt",
    "collector_config_id": None,
    "scenario_id": "es",
    "storage_cluster_id": 1,
    "source_id": None,
    "orders": 0,
    "pre_check_tag": True,
    "pre_check_msg": None,
    "is_active": True,
    "fields_snapshot": "{}",
    "source_app_code": settings.APP_CODE,
    "tag_ids": "[]",
    "is_editable": True,
}


class Dummy(dict):
    def __getitem__(self, item):
        return {}


@patch("apps.iam.handlers.drf.BusinessActionPermission.has_permission", return_value=True)
@patch("apps.log_search.tasks.mapping.sync_single_index_set_mapping_snapshot.delay", return_value=None)
@patch("apps.log_databus.tasks.bkdata.async_create_bkdata_data_id", return_value=None)
@patch("apps.iam.handlers.drf.InstanceActionPermission.has_permission", return_value=True)
@patch("apps.iam.handlers.drf.ViewBusinessPermission.has_permission", return_value=True)
@patch("apps.iam.handlers.permission.Permission.batch_is_allowed", return_value=Dummy())
@patch("apps.decorators.user_operation_record.delay", return_value=None)
class TestIndexSet(TestCase):
    def setUp(self) -> None:
        if User.objects.filter(username="admin").exists():
            return
        User.objects.create_superuser(username="admin")

    @staticmethod
    def sync_index_id(index_sets, ids):
        for index, i_s in enumerate(index_sets["indexes"]):
            i_s["index_id"] = ids[index]

    @staticmethod
    def sync_indexes(index_sets, **kwargs):
        for i_s in index_sets["indexes"]:
            for key, value in kwargs.items():
                i_s[key] = value

    @staticmethod
    def sync_params(index_set, **kwargs):
        for key, value in kwargs.items():
            index_set[key] = value

    @patch("apps.log_search.tasks.mapping.sync_index_set_mapping_snapshot.delay", return_value=None)
    @patch("apps.utils.bk_data_auth.BkDataAuthHandler.filter_unauthorized_rt_by_user", return_value=[])
    @patch(
        "apps.utils.bk_data_auth.BkDataAuthHandler.list_authorized_rt_by_token", return_value=["591_xx", "log_xxx"],
    )
    @patch("apps.api.TransferApi.get_cluster_info", return_value=CLUSTER_INFO_WITH_AUTH)
    @patch("apps.api.BkLogApi.mapping", return_value=MAPPING_LIST)
    @patch("apps.api.TransferApi.get_result_table_storage", lambda _: CLUSTER_INFOS)
    @patch("apps.api.BkDataAuthApi.get_auth_token", return_value=TOKEN_PERMISSIONS)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_sync_auth_status(self, *args, **kwargs):
        """
        测试API [POST] sync_auth_status
        """
        data = {
            "index_set_name": "登陆日志",
            "space_uid": SPACE_UID,
            "storage_cluster_id": STORAGE_CLUSTER_ID,
            "result_table_id": "591_xx",
            "category_id": "other_rt",
            "scenario_id": SCENARIO_ID_BKDATA,
            "view_roles": [],
            "indexes": [
                {"bk_biz_id": BK_BIZ_ID, "result_table_id": "591_xx", "time_field": "timestamp"},
                {"bk_biz_id": None, "result_table_id": "log_xxx", "time_field": "timestamp"},
            ],
            "is_trace_log": "0",
            "time_field": "abc",
            "time_field_type": "date",
            "time_field_unit": "millisecond",
        }

        path = "/api/v1/index_set/"

        self.client.post(path=path, data=json.dumps(data), content_type="application/json")

        index_set = LogIndexSet.objects.all().first()
        index_set_id = index_set.index_set_id
        index_ids = [i["index_id"] for i in index_set.indexes]

        path = "/api/v1/index_set/" + str(index_set_id) + "/sync_auth_status/"

        response = self.client.post(path=path)
        content = json.loads(response.content)

        for index, item in enumerate(SYSC_AUTH_STATUS_RESULT):
            item["index_set_id"] = index_set_id
            item["index_id"] = index_ids[index]

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.assertEqual(content["data"], SYSC_AUTH_STATUS_RESULT)

    @patch("apps.api.TransferApi.get_cluster_info", return_value=CLUSTER_INFO)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_list_index_set(self, *args, **kwargs):
        """
        测试 索引集-列表 api.v1.index_set
        """
        # 插入一条索引集记录
        self.do_create_index_set(self)

        # 取到插入数据的一些字段
        index_set = LogIndexSet.objects.all().first()

        index_set_id = index_set.index_set_id
        storage_cluster_id = index_set.storage_cluster_id
        created_at = arrow.get(index_set.created_at).to(settings.TIME_ZONE).strftime(settings.BKDATA_DATETIME_FORMAT)
        updated_at = arrow.get(index_set.updated_at).to(settings.TIME_ZONE).strftime(settings.BKDATA_DATETIME_FORMAT)
        index_ids = [i["index_id"] for i in index_set.indexes]

        path = "/api/v1/index_set/"
        data = {"space_uid": SPACE_UID, "storage_cluster_id": storage_cluster_id, "page": 1, "pagesize": 2}

        response = self.client.get(path=path, data=data)
        content = json.loads(response.content)

        # 同步测试数据库中一些实时和自增的字段
        self.sync_index_id(INDEX_SET_LISTS["list"][0], index_ids)
        self.sync_indexes(INDEX_SET_LISTS["list"][0], index_set_id=index_set_id)
        self.sync_params(
            INDEX_SET_LISTS["list"][0], index_set_id=index_set_id, created_at=created_at, updated_at=updated_at
        )

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        data = content["data"]
        self.maxDiff = 100000

        self.assertEqual(data, INDEX_SET_LISTS)

    @patch("apps.log_search.tasks.mapping.sync_index_set_mapping_snapshot.delay", return_value=None)
    # @patch("apps.log_search.handlers.index_set.LogIndexSetDataHandler.post_add_log.delay", return_value=True)
    @patch("apps.api.TransferApi.get_cluster_info", return_value=CLUSTER_INFO_WITH_AUTH)
    @patch("apps.log_search.models.LogIndexSetData.objects.filter", return_value=[])
    @patch("apps.api.BkLogApi.mapping", return_value=MAPPING_LIST)
    @patch("apps.api.TransferApi.get_result_table_storage", lambda _: CLUSTER_INFOS)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def do_create_index_set(self, *args, **kwargs):
        """
        添加一条索引集数据
        """
        data = {
            "index_set_name": "登陆日志",
            "space_uid": SPACE_UID,
            "storage_cluster_id": STORAGE_CLUSTER_ID,
            "result_table_id": "591_xx",
            "category_id": "other_rt",
            "scenario_id": SCENARIO_ID_ES,
            "view_roles": [],
            "indexes": [
                {"bk_biz_id": BK_BIZ_ID, "result_table_id": "591_xx", "time_field": "timestamp"},
                {"bk_biz_id": None, "result_table_id": "log_xxx", "time_field": "timestamp"},
            ],
            "is_trace_log": "0",
            "time_field": "abc",
            "time_field_type": "date",
            "time_field_unit": "millisecond",
        }

        path = "/api/v1/index_set/"

        response = self.client.post(path=path, data=json.dumps(data), content_type="application/json")
        return response

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_create_index_set(self, *args, **kwargs):
        """
        测试API [POST] create_index_set
        """

        response = self.do_create_index_set(self)

        content = json.loads(response.content)

        index_set_id = content["data"]["index_set_id"]
        created_at = content["data"]["created_at"]
        updated_at = content["data"]["updated_at"]

        CREATE_SUCCESS["data"].update(
            {"index_set_id": index_set_id, "created_at": created_at, "updated_at": updated_at}
        )
        self.maxDiff = 100000
        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.assertEqual(content, CREATE_SUCCESS)

    @patch("apps.log_search.tasks.mapping.sync_index_set_mapping_snapshot.delay", return_value=None)
    @patch("apps.api.BkLogApi.mapping", return_value=MAPPING_LIST)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_update_index_set(self, *args, **kwargs):
        """
        测试API [POST] update_index_set
        """
        # 插入一条索引集记录
        self.do_create_index_set(self)

        # 获取插入索引集的一些信息
        index_set = LogIndexSet.objects.all().first()
        index_set_id = index_set.index_set_id
        space_uid = index_set.space_uid
        storage_cluster_id = index_set.storage_cluster_id
        scenario_id = index_set.scenario_id
        index_ids = [i["index_id"] for i in index_set.indexes]

        data = {
            "space_uid": space_uid,
            "scenario_id": scenario_id,
            "index_set_name": "登陆日志",
            "view_roles": [],
            "storage_cluster_id": storage_cluster_id,
            "category_id": "host",
            "indexes": [
                {"bk_biz_id": BK_BIZ_ID, "result_table_id": "591_xx", "time_field": "timestamp"},
                {"bk_biz_id": None, "result_table_id": "log_xxx", "time_field": "timestamp"},
            ],
            "time_field": "abc",
            "time_field_type": "date",
            "time_field_unit": "millisecond",
        }

        path = "/api/v1/index_set/" + str(index_set_id) + "/"

        response = self.client.patch(path=path, data=json.dumps(data), content_type="application/json")

        content = json.loads(response.content)

        created_at = content["data"]["created_at"]
        updated_at = content["data"]["updated_at"]

        # 同步测试数据库中一些实时和自增的字段
        self.sync_indexes(UPDATE_INDEX_SET, index_set_id=index_set_id)
        self.sync_index_id(UPDATE_INDEX_SET, index_ids)
        self.sync_params(UPDATE_INDEX_SET, index_set_id=index_set_id, created_at=created_at, updated_at=updated_at)

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.maxDiff = 1000000
        self.assertEqual(content["data"], UPDATE_INDEX_SET)

        # 测试不可编辑字段 为True下仍可以编辑
        index_set.is_editable = False
        index_set.save()
        response = self.client.patch(path=path, data=json.dumps(data), content_type="application/json")
        content = json.loads(response.content)
        created_at = content["data"]["created_at"]
        updated_at = content["data"]["updated_at"]

        check_data = copy.deepcopy(UPDATE_INDEX_SET)
        self.sync_params(
            check_data, index_set_id=index_set_id, created_at=created_at, updated_at=updated_at, is_editable=False
        )
        self.assertEqual(json.loads(response.content)["data"], check_data)

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_delete_index_set(self, *args):
        """
        测试API [DELETE] delete_index_set
        """

        # 插入一条索引集记录
        self.do_create_index_set(self)

        # 获取插入索引集的id
        index_set = LogIndexSet.objects.all().first()
        index_set_id = index_set.index_set_id

        path = "/api/v1/index_set/"
        path += str(index_set_id) + "/"

        response = self.client.delete(path=path)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.assertEqual(content, DELETE_SUCCESS)

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_retrieve_index_set(self, *args):
        """
        测试API [GET] retrieve_index_set
        """
        # 插入一条索引集记录
        self.do_create_index_set(self)

        # 获取一些自增的字段，以更新到验证数据中
        index_set = LogIndexSet.objects.all().first()
        index_set_id = index_set.index_set_id
        index_ids = [i["index_id"] for i in index_set.indexes]
        created_at = arrow.get(index_set.created_at).to(settings.TIME_ZONE).strftime(settings.BKDATA_DATETIME_FORMAT)
        updated_at = arrow.get(index_set.updated_at).to(settings.TIME_ZONE).strftime(settings.BKDATA_DATETIME_FORMAT)

        path = "/api/v1/index_set/" + str(index_set_id) + "/"

        response = self.client.get(path=path)
        content = json.loads(response.content)

        # 同步测试数据库中一些实时和自增的字段
        self.sync_index_id(RETRIEVE_LIST, index_ids)
        self.sync_indexes(RETRIEVE_LIST, index_set_id=index_set_id)
        self.sync_params(RETRIEVE_LIST, index_set_id=index_set_id, created_at=created_at, updated_at=updated_at)

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.maxDiff = 100000
        self.assertEqual(content["data"], RETRIEVE_LIST)
