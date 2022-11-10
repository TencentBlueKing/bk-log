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
from django.utils.translation import ugettext as _

from apps.api import BkDataDataFlowApi
from apps.utils import ChoicesEnum

DEFAULT_TIME_FIELD = "timestamp"
DEFAULT_CLUSTERING_FIELD = "log"
NOT_CLUSTERING_FILTER_RULE = " where ip is null"
OPERATOR_AND = "and"
# 聚类不参与sql字段
NOT_CONTAIN_SQL_FIELD_LIST = ["timestamp", "_startTime_", "_endTime_"]
DIST_FIELDS = ["dist_01", "dist_03", "dist_05", "dist_07", "dist_09"]
DIST_CLUSTERING_FIELDS = [
    "dist_01 AS __dist_01",
    "dist_03 AS __dist_03",
    "dist_05 AS __dist_05",
    "dist_07 AS __dist_07",
    "dist_09 AS __dist_09",
]
DEFAULT_SPARK_EXECUTOR_INSTANCES = 8
DEFAULT_SPARK_EXECUTOR_CORES = 2
DEFAULT_PSEUDO_SHUFFLE = 200
DEFAULT_SPARK_LOCALITY_WAIT = "0s"
STREAM_SOURCE_NODE_TYPE = "stream_source"
DIVERSION_NODE_NAME = _("回流数据")
TSPIDER_STORAGE_NODE_TYPE = "tspider_storage"
TSPIDER_STORAGE_NODE_NAME = _("回流数据(tspider_storage)")
TSPIDER_STORAGE_INDEX_FIELDS = ["history_time", "event_time"]

SPLIT_TYPE = "split"


class ActionEnum(object):
    START = "start"
    RESTART = "restart"
    STOP = "stop"


class ActionHandler(object):
    action_handler = {
        ActionEnum.START: BkDataDataFlowApi.start_flow,
        ActionEnum.RESTART: BkDataDataFlowApi.restart_flow,
        ActionEnum.STOP: BkDataDataFlowApi.stop_flow,
    }

    @classmethod
    def get_action_handler(cls, action_num):
        return cls.action_handler.get(action_num, BkDataDataFlowApi.start_flow)


class FlowMode(ChoicesEnum):
    # 预处理flow
    PRE_TREAT_FLOW = "pre_treat_flow"
    # 结果处理flow
    AFTER_TREAT_FLOW = "after_treat_flow"
    # 修改flow的某些节点
    MODIFY_FLOW = "modify_flow"
    # 计算平台rt flow
    AFTER_TREAT_FLOW_BKDATA = "after_treat_flow_bkdata"

    _choices_labels = (
        (PRE_TREAT_FLOW, "templates/flow/pre_treat_flow.json"),
        (AFTER_TREAT_FLOW, "templates/flow/after_treat_flow.json"),
        (MODIFY_FLOW, "templates/flow/modify_flow.json"),
        (AFTER_TREAT_FLOW_BKDATA, "templates/flow/after_treat_flow_bkdata.json"),
    )


class NodeType(object):
    REALTIME = "realtime"
    REDIS_KV_SOURCE = "redis_kv_source"
    ELASTIC_STORAGE = "elastic_storage"
    MODEL = "model_ts_custom"
    STREAM_SOURCE = "stream_source"


class RealTimeFlowNode(object):
    PRE_TREAT_NOT_CLUSTERING = "pre_treat_not_clustering"
    PRE_TREAT_SAMPLE_SET = "pre_treat_sample_set"
    AFTER_TREAT_CHANGE_FIELD = "after_treat_change_field"


DEFAULT_MODEL_INPUT_FIELDS = [
    {
        "field_index": 1,
        "data_field_name": "__index__",
        "field_alias": "系统索引",
        "components": [],
        "roles": ["system", "index"],
        "data_field_alias": "index",
        "properties": {
            "constraint_type": None,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "role_changeable": False,
            "deletable": False,
            "compatibility": False,
            "extra": {},
            "constraints": {},
            "required": True,
            "complex": False,
        },
        "field_name": "__index__",
        "field_type": "string",
    },
    {
        "field_name": "__id__",
        "field_type": "string",
        "components": ["__group_id__", "timestamp"],
        "field_alias": "用户索引",
        "data_field_name": "__id__",
        "data_field_alias": "用户索引",
        "roles": ["index"],
        "field_index": 2,
        "properties": {
            "required": True,
            "extra": {},
            "constraint_type": None,
            "compatibility": False,
            "deletable": False,
            "name_inherited": True,
            "complex": True,
            "role_changeable": False,
            "passthrough": False,
            "value_fixed": False,
            "constraints": {},
        },
    },
    {
        "data_field_name": [],
        "data_field_alias": "",
        "field_alias": "分组字段",
        "field_type": "string",
        "properties": {
            "name_inherited": True,
            "role_changeable": False,
            "deletable": False,
            "passthrough": False,
            "compatibility": False,
            "complex": False,
            "value_fixed": True,
            "constraints": {},
            "required": True,
            "constraint_type": None,
            "extra": {},
        },
        "roles": ["index_component", "group"],
        "components": [],
        "field_name": "__group_id__",
        "field_index": 3,
    },
    {
        "data_field_name": "log",
        "field_name": "log",
        "field_alias": "日志内容",
        "field_type": "string",
        "field_index": 4,
        "data_field_alias": "",
        "components": [],
        "roles": ["passthrough", "feature"],
        "properties": {
            "complex": False,
            "compatibility": False,
            "passthrough": False,
            "required": True,
            "constraint_type": "",
            "role_changeable": False,
            "deletable": False,
            "extra": {},
            "value_fixed": False,
            "name_inherited": False,
            "constraints": {},
        },
    },
    {
        "roles": ["timestamp"],
        "field_index": 5,
        "properties": {
            "constraint_type": "",
            "deletable": False,
            "name_inherited": False,
            "passthrough": False,
            "role_changeable": False,
            "required": True,
            "compatibility": False,
            "constraints": {},
            "extra": {},
            "complex": False,
            "value_fixed": False,
        },
        "field_name": "timestamp",
        "data_field_name": "timestamp",
        "data_field_alias": "",
        "field_alias": "时间戳",
        "components": [],
        "field_type": "timestamp",
    },
]


DEFAULT_MODEL_OUTPUT_FIELDS = [
    {
        "data_field_alias": "index",
        "components": [],
        "field_type": "string",
        "properties": {
            "complex": False,
            "constraints": {},
            "extra": {},
            "compatibility": False,
            "constraint_type": None,
            "deletable": False,
            "name_inherited": True,
            "required": True,
            "value_fixed": False,
            "role_changeable": False,
            "passthrough": False,
        },
        "field_alias": "系统索引",
        "field_index": 1,
        "roles": ["index"],
        "field_name": "__index__",
        "data_field_name": "__index__",
    },
    {
        "field_alias": "用户索引",
        "data_field_alias": "用户索引",
        "components": ["__group_id__", "timestamp"],
        "roles": ["index"],
        "properties": {
            "role_changeable": False,
            "name_inherited": True,
            "value_fixed": False,
            "complex": True,
            "deletable": False,
            "passthrough": False,
            "required": True,
            "constraints": {},
            "extra": {},
            "constraint_type": None,
            "compatibility": False,
        },
        "field_name": "__id__",
        "field_index": 2,
        "data_field_name": "__id__",
        "field_type": "string",
    },
    {
        "field_alias": "分组索引",
        "roles": ["index_component", "group"],
        "properties": {
            "deletable": False,
            "passthrough": False,
            "complex": False,
            "constraints": {},
            "extra": {},
            "name_inherited": True,
            "compatibility": False,
            "constraint_type": None,
            "role_changeable": False,
            "value_fixed": True,
            "required": True,
        },
        "field_type": "string",
        "field_name": "__group_id__",
        "components": [],
        "field_index": 3,
        "data_field_name": "__group_id__",
        "data_field_alias": "分组字段",
    },
    {
        "roles": ["predict_result"],
        "properties": {
            "deletable": False,
            "complex": False,
            "constraint_type": "",
            "role_changeable": False,
            "extra": {},
            "value_fixed": False,
            "constraints": {},
            "required": True,
            "name_inherited": False,
            "passthrough": False,
            "compatibility": False,
        },
        "data_field_alias": None,
        "field_index": 4,
        "field_name": "token",
        "field_type": "text",
        "components": [],
        "field_alias": "token",
        "data_field_name": "",
    },
    {
        "properties": {
            "name_inherited": False,
            "value_fixed": False,
            "constraint_type": "",
            "deletable": False,
            "extra": {},
            "passthrough": False,
            "compatibility": False,
            "role_changeable": False,
            "required": True,
            "complex": False,
            "constraints": {},
        },
        "field_name": "log_signature",
        "components": [],
        "data_field_name": "",
        "field_alias": "log_signature",
        "field_type": "text",
        "data_field_alias": None,
        "field_index": 5,
        "roles": ["predict_result"],
    },
    {
        "field_name": "timestamp",
        "roles": ["timestamp"],
        "properties": {
            "constraint_type": "",
            "extra": {},
            "compatibility": False,
            "value_fixed": False,
            "passthrough": False,
            "complex": False,
            "role_changeable": False,
            "required": True,
            "constraints": {},
            "deletable": False,
            "name_inherited": True,
        },
        "field_index": 6,
        "data_field_name": "timestamp",
        "components": [],
        "data_field_alias": None,
        "field_type": "timestamp",
        "field_alias": "timestamp",
    },
    {
        "components": [],
        "field_index": 7,
        "properties": {
            "value_fixed": False,
            "required": True,
            "compatibility": False,
            "constraint_type": "",
            "constraints": {},
            "name_inherited": False,
            "role_changeable": False,
            "deletable": False,
            "passthrough": False,
            "complex": False,
            "extra": {},
        },
        "data_field_alias": None,
        "field_type": "string",
        "field_alias": "日志内容",
        "roles": ["passthrough", "feature"],
        "data_field_name": "log",
        "field_name": "log",
    },
]
