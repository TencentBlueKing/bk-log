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
from django.test import TestCase

from apps.log_databus.handlers.storage import StorageHandler
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_extract import constants
from apps.log_extract.handlers.link import LinkHandler
from apps.log_extract.handlers.strategies import StrategiesHandler
from apps.log_extract.handlers.tasks import TasksHandler


def user_operation_record_delay(operation_record):
    print(operation_record)


CREATE_STORAGE_PARAMS = {
    "cluster_name": "test_1",
    "domain_name": "test",
    "port": 80,
    "auth_info": {"username": "test", "password": "xxx"},
    "cluster_type": "elasticsearch",
    "custom_option": {
        "bk_biz_id": 1,
        "hot_warm_config": {
            "is_enabled": False,
            "hot_attr_name": "",
            "hot_attr_value": "",
            "warm_attr_name": "",
            "warm_attr_value": "",
        },
    },
    "version": "7.1",
}

UPDATE_STORAGE_PARAMS = {
    "cluster_name": "test_1",
    "domain_name": "test",
    "port": 80,
    "auth_info": {"username": "test", "password": "xxx"},
    "schema": "https",
    "cluster_type": "elasticsearch",
    "custom_option": {
        "bk_biz_id": 1,
        "hot_warm_config": {
            "is_enabled": False,
            "hot_attr_name": "",
            "hot_attr_value": "",
            "warm_attr_name": "",
            "warm_attr_value": "",
        },
    },
    "cluster_id": 1,
}


class PermissionTest(object):
    def grant_creator_action(self, resource):
        return True


class MetaHandlerTest(object):
    @classmethod
    def get_user(cls):
        return {"operator": "admin"}

    def get_project_info(self, bk_biz_id):
        return {
            "bk_biz_id": bk_biz_id,
            "project_id": 1,
            "project_name": "test",
        }


class ExplorerHandlerTest(object):
    def get_strategies(self, bk_biz_id, ip_list):
        return {"allowed_dir_file_list": ["tmp"], "bk_os_type": "test", "operator": "admin"}

    @staticmethod
    def filter_server_access_file(allowed_dir_file_list, request_file, request_file_type="fname"):
        return True

    @staticmethod
    def get_account(bk_os_type):
        if bk_os_type != constants.WINDOWS:
            return constants.ACCOUNT["linux"]
        return constants.ACCOUNT["windows"]


def connectivity_detect_test(
    _,
    bk_biz_id,
    domain_name=None,
    port=None,
    username=None,
    password=None,
    version_info=False,
    default_auth=False,
    schema="",
):
    return {}


class TestUserOperationRecord(TestCase):
    @patch("apps.decorators.user_operation_record.delay", user_operation_record_delay)
    @patch("apps.api.TransferApi.create_cluster_info", lambda _: 1)
    @patch("apps.log_databus.handlers.storage.Permission", PermissionTest)
    @patch("apps.log_databus.handlers.storage.get_request_username", lambda: "admin")
    def test_create_storage(self):
        StorageHandler().create(params=CREATE_STORAGE_PARAMS)

    @patch("apps.decorators.user_operation_record.delay", user_operation_record_delay)
    @patch("apps.api.TransferApi.get_cluster_info", lambda _: [{"cluster_config": {"custom_option": {"bk_biz_id": 1}}}])
    @patch(
        "apps.log_databus.handlers.storage.StorageHandler.connectivity_detect", connectivity_detect_test,
    )
    @patch("apps.api.TransferApi.modify_cluster_info", lambda _: {"auth_info": {"password": ""}})
    @patch("apps.log_databus.handlers.storage.get_request_username", lambda: "admin")
    def test_update_storage(self):
        StorageHandler(cluster_id=1).update(params=UPDATE_STORAGE_PARAMS)

    def test_start_export(self):
        pass

    @patch("apps.decorators.user_operation_record.delay", user_operation_record_delay)
    @patch("apps.log_extract.handlers.strategies.MetaHandler", MetaHandlerTest)
    @patch("apps.log_audit.handlers.auth.get_request_username", lambda: "admin")
    def test_log_extract_strategy(self):
        StrategiesHandler().update_or_create(
            "test_1",
            user_list=["samuel"],
            bk_biz_id=1,
            select_type="test",
            modules="test",
            visible_dir="/log",
            file_type="log",
            operator="admin",
        )
        # print(create_data)
        StrategiesHandler(strategy_id=1).update_or_create(
            "test_1",
            user_list=["samuel"],
            bk_biz_id=1,
            select_type="test",
            modules="test",
            visible_dir="/var/log",
            file_type="log",
            operator="admin",
        )
        # print(update_data)
        StrategiesHandler(strategy_id=1).delete_strategies()

    @patch("apps.decorators.user_operation_record.delay", user_operation_record_delay)
    def test_log_extract_links(self):
        LinkHandler().create_or_update(
            name="test",
            link_type="common",
            operator="admin",
            op_bk_biz_id=1,
            is_enable=True,
            qcloud_secret_id="",
            qcloud_secret_key="",
            qcloud_cos_bucket="",
            qcloud_cos_region="",
            hosts=[{"target_dir": "var", "bk_cloud_id": "1", "ip": "127.0.0.1"}],
        )
        LinkHandler(link_id=1).create_or_update(
            name="test",
            link_type="common",
            operator="admin",
            op_bk_biz_id=1,
            is_enable=True,
            qcloud_secret_id="",
            qcloud_secret_key="",
            qcloud_cos_bucket="",
            qcloud_cos_region="",
            hosts=[],
        )
        LinkHandler(link_id=1).destroy()

    @patch("apps.decorators.user_operation_record.delay", user_operation_record_delay)
    @patch("apps.log_extract.handlers.tasks.ExplorerHandler", ExplorerHandlerTest)
    def test_create_log_extract_tasks(self):
        TasksHandler().create(
            bk_biz_id=1,
            ip_list=[{"bk_cloud_id": 1, "ip": "127.0.0.1"}],
            request_file_list=["tmp"],
            filter_type="test",
            remark="",
            filter_content="",
            preview_directory="",
            preview_ip="127.0.0.1",
            preview_time_range="",
            preview_is_search_child=True,
            link_id=1,
            preview_start_time="",
            preview_end_time="",
        )

    @patch("apps.decorators.user_operation_record.delay", user_operation_record_delay)
    @patch("apps.log_search.handlers.index_set.BkDataIndexSetHandler.pre_create", lambda _: {})
    @patch("apps.log_search.handlers.index_set.BkDataIndexSetHandler.post_create", lambda _, b: {})
    @patch("apps.log_search.handlers.index_set.BkDataIndexSetHandler.pre_update", lambda _: {})
    @patch("apps.log_search.handlers.index_set.BkDataIndexSetHandler.post_update", lambda _, b: {})
    @patch("apps.log_search.handlers.index_set.get_request_username", lambda: "admin")
    def test_replace_index_set(self):
        IndexSetHandler.replace(
            index_set_name="test_1",
            scenario_id="bkdata",
            view_roles=[],
            indexes=[
                {
                    "bk_biz_id": "215",
                    "result_table_id": "215_bcs_file_log_bGSQ",
                    "time_field": "",
                    "time_format": "微秒（microsecond）",
                    "fields": "",
                }
            ],
            bk_app_code="bk-log-4",
            space_uid="bkcc__2",
        )

        IndexSetHandler.replace(
            index_set_name="test_1",
            scenario_id="bkdata",
            view_roles=[],
            indexes=[
                {
                    "bk_biz_id": "215",
                    "result_table_id": "215_bcs_file_log_bGSQ",
                    "time_field": "",
                    "time_format": "微秒（microsecond）",
                    "fields": "",
                }
            ],
            bk_app_code="bk-log-4",
            space_uid="bkcc__2",
        )
