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

import json
import logging
import sys
from unittest.mock import patch

import arrow
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils.translation import ugettext_lazy as _
from django_fakeredis import FakeRedis

from apps.iam.handlers import permission
from apps.log_databus.models import CollectorConfig
from apps.log_databus.views import collector_views

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()

BK_APP_CODE = "bk_log_search"
BK_BIZ_ID = 2
COLLECTOR_CONFIG_ID = 231
COLLECTOR_SCENARIO_ID_ROW = "row"
COLLECTOR_SCENARIO_ID_SECTION = "section"
SUCCESS_STATUS_CODE = 200

PARAMS = {"bk_biz_id": BK_BIZ_ID, "page": 1, "pagesize": 2, "keyword": ""}

OVERRIDE_MIDDLEWARE = "apps.tests.middlewares.OverrideMiddleware"

CLUSTER_INFOS = {
    "2_bklog.test3333": {"cluster_config": {"cluster_id": 1, "cluster_name": ""}, "storage_config": {"retention": 7}}
}

FAKE_CACHE = CLUSTER_INFOS

BATCH_IS_ALLOWED = {"231": {"search_log": True}}

SCENARIOS = [
    {
        "collector_scenario_id": COLLECTOR_SCENARIO_ID_ROW,
        "collector_scenario_name": _("行日志"),
        "is_active": True,
        "config": {
            "paths": {
                "field_type": "list",
                "field_name": "paths",
                "field_alias": _("日志路径"),
                "required": True,
                "option": {},
            },
            "conditions": {
                "field_type": "dict",
                "field_name": "conditions",
                "field_alias": _("过滤方式"),
                "required": False,
                "option": {"choices": ["match", "separator"]},
            },
        },
    },
    {
        "collector_scenario_id": COLLECTOR_SCENARIO_ID_SECTION,
        "collector_scenario_name": _("段日志"),
        "is_active": False,
        "config": {
            "paths": {
                "field_type": "list",
                "field_name": "paths",
                "field_alias": _("日志路径"),
                "required": True,
                "option": {},
            },
            "conditions": {
                "field_type": "dict",
                "field_name": "conditions",
                "field_alias": _("过滤方式"),
                "required": False,
                "option": {"choices": ["match"]},
            },
        },
    },
]

COLLECTORS_LIST = {
    "result": True,
    "data": {
        "total": 1,
        "list": [
            {
                "add_pod_label": False,
                "bcs_cluster_id": None,
                "environment": None,
                "extra_labels": None,
                "collector_config_id": 231,
                "collector_scenario_name": "行日志文件",
                "collector_plugin_id": None,
                "category_name": "操作系统",
                "target_nodes": [{"bk_inst_id": 52, "bk_obj_id": "module"}],
                "task_id_list": ["1331697"],
                "target_subscription_diff": {},
                "created_at": "2021-06-26 15:55:08+0800",
                "created_by": "",
                "updated_at": "2021-06-26 15:55:08+0800",
                "updated_by": "",
                "is_deleted": False,
                "deleted_at": None,
                "deleted_by": None,
                "custom_type": "log",
                "custom_name": "容器日志上报",
                "collector_config_name": "test3333",
                "bk_app_code": "bk_log_search",
                "collector_scenario_id": "row",
                "bk_biz_id": 2,
                "bkdata_biz_id": None,
                "category_id": "os",
                "target_object_type": "HOST",
                "target_node_type": "TOPO",
                "description": "test3333",
                "is_active": True,
                "data_link_id": None,
                "bk_data_id": 1500586,
                "bk_data_name": None,
                "table_id": "test3333",
                "bkbase_table_id": None,
                "processing_id": None,
                "etl_processor": "transfer",
                "etl_config": None,
                "subscription_id": 2103,
                "bkdata_data_id": None,
                "index_set_id": None,
                "data_encoding": None,
                "params": "{}",
                "itsm_ticket_sn": None,
                "itsm_ticket_status": "not_apply",
                "log_group_id": None,
                "can_use_independent_es_cluster": True,
                "collector_package_count": 10,
                "collector_output_format": None,
                "collector_config_overlay": None,
                "storage_shards_nums": None,
                "storage_shards_size": None,
                "storage_replies": 1,
                "bkdata_data_id_sync_times": 0,
                "collector_config_name_en": "",
                "storage_cluster_id": 1,
                "rule_id": 0,
                "storage_cluster_name": "",
                "table_id_prefix": "2_bklog_",
                "is_search": False,
                "permission": {"search_log": True},
                "create_clean_able": True,
                "bkdata_index_set_ids": [],
                "retention": 7,
                "is_display": True,
                "yaml_config_enabled": False,
                "yaml_config": "",
            }
        ],
    },
    "code": 0,
    "message": "",
}


class TestCollectorViewSetAPI(TestCase):
    """
    测试 CollectorViewSet中的接口
    """

    @patch("apps.api.TransferApi.get_result_table_storage", lambda _: CLUSTER_INFOS)
    @patch("apps.log_databus.views.collector_views.CollectorViewSet.get_permissions", lambda _: [])
    @patch("apps.utils.cache.caches_one_hour", lambda _: FAKE_CACHE)
    @patch.object(collector_views.CollectorViewSet, "get_permissions", lambda _: [])
    @patch.object(permission.Permission, "batch_is_allowed", lambda _, actions, resources: BATCH_IS_ALLOWED)
    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    @FakeRedis("apps.utils.cache.cache")
    def test_list_collector(self):
        """
        测试 api.v1.databus.collectors
        """
        # 测试数据库添加一条CollectorConfig数据
        self.maxDiff = 500000
        CollectorConfig.objects.create(
            collector_config_id=COLLECTOR_CONFIG_ID,
            collector_config_name="test3333",
            bk_app_code=BK_APP_CODE,
            collector_scenario_id=COLLECTOR_SCENARIO_ID_ROW,
            bk_biz_id=BK_BIZ_ID,
            category_id="os",
            target_object_type="HOST",
            target_node_type="TOPO",
            target_nodes=[{"bk_inst_id": 52, "bk_obj_id": "module"}],
            target_subscription_diff={},
            description="test3333",
            is_active=True,
            bk_data_id=1500586,
            table_id="2_bklog.test3333",
            subscription_id=2103,
            task_id_list=["1331697"],
        )

        # 取到created_at和updated_at
        collector_config = CollectorConfig.objects.get(collector_config_id=COLLECTOR_CONFIG_ID)
        created_at = (
            arrow.get(collector_config.created_at).to(settings.TIME_ZONE).strftime(settings.BKDATA_DATETIME_FORMAT)
        )
        updated_at = (
            arrow.get(collector_config.updated_at).to(settings.TIME_ZONE).strftime(settings.BKDATA_DATETIME_FORMAT)
        )
        COLLECTORS_LIST["data"]["list"][0].update({"created_at": created_at})
        COLLECTORS_LIST["data"]["list"][0].update({"updated_at": updated_at})
        path = "/api/v1/databus/collectors/"

        data = PARAMS

        response = self.client.get(path=path, data=data)

        content = json.loads(response.content)

        logger.info(" {func_name}:{content}".format(func_name=sys._getframe().f_code.co_name, content=content))

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)
        self.assertEqual(content, COLLECTORS_LIST)

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_list_scenarios(self):
        """
        测试接口 api.v1.databus.collectors.scenarios
        """
        path = "/api/v1/databus/collectors/scenarios/"

        response = self.client.get(path=path)

        content = json.loads(response.content)

        logger.info(" {func_name}:{content}".format(func_name=sys._getframe().f_code.co_name, content=content))

        self.assertEqual(response.status_code, SUCCESS_STATUS_CODE)

        self.assertEqual(content["data"], SCENARIOS)
