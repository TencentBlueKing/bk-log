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
TRAINING_HOUR = 1


class StepName(object):
    """
    模型执行步骤（对应计算平台执行步骤step_name）
    """

    # 样本准备
    SAMPLE_LOADING = "sample_loading"
    # 样本切分
    SAMPLE_PREPARATION = "sample_preparation"
    # 模型训练
    MODEL_TRAIN = "model_train"
    # 模型评估
    MODEL_EVALUATION = "model_evaluation"


TRAINING_INPUT_VALUE = {
    "training_input": [
        {
            "field_type": "string",
            "field_alias": "系统索引",
            "field_name": "__index__",
            "field_index": 0,
            "properties": {
                "role_changeable": False,
                "deletable": False,
                "name_inherited": True,
                "value_fixed": False,
                "passthrough": False,
                "compatibility": False,
                "required": True,
                "complex": False,
                "constraint_type": None,
                "constraints": {},
                "extra": {},
                "input_type": "field",
            },
            "data_field_name": "__index__",
            "data_field_alias": "index",
            "roles": ["index", "system", "original_feature"],
            "components": [],
        },
        {
            "field_type": "string",
            "field_alias": "用户索引",
            "field_name": "__id__",
            "field_index": 1,
            "properties": {
                "role_changeable": False,
                "deletable": False,
                "name_inherited": True,
                "value_fixed": False,
                "passthrough": False,
                "compatibility": False,
                "required": True,
                "complex": True,
                "constraint_type": None,
                "constraints": {},
                "extra": {},
                "input_type": "field",
            },
            "data_field_name": "__id__",
            "data_field_alias": "用户索引",
            "roles": ["index"],
            "components": ["__group_id__", "timestamp"],
        },
        {
            "field_type": "string",
            "field_alias": "分组索引",
            "field_name": "__group_id__",
            "field_index": 2,
            "properties": {
                "role_changeable": False,
                "deletable": False,
                "name_inherited": True,
                "value_fixed": True,
                "passthrough": False,
                "compatibility": False,
                "required": True,
                "complex": False,
                "constraint_type": None,
                "constraints": {},
                "extra": {},
                "input_type": "field",
            },
            "data_field_name": "__group_id__",
            "data_field_alias": "分组字段",
            "roles": ["index_component", "group"],
            "components": [],
        },
        {
            "field_type": "string",
            "field_alias": "group",
            "field_name": "line_id",
            "field_index": 3,
            "properties": {
                "role_changeable": False,
                "deletable": False,
                "name_inherited": True,
                "value_fixed": False,
                "passthrough": False,
                "compatibility": True,
                "required": True,
                "complex": False,
                "constraint_type": None,
                "constraints": {},
                "extra": {},
                "input_type": "field",
            },
            "data_field_name": "line_id",
            "data_field_alias": None,
            "roles": ["group", "data", "original_feature"],
            "components": [],
        },
        {
            "field_type": "string",
            "field_alias": "日志内容",
            "field_name": "log",
            "field_index": 4,
            "properties": {
                "role_changeable": False,
                "deletable": False,
                "name_inherited": False,
                "value_fixed": False,
                "passthrough": False,
                "compatibility": False,
                "required": True,
                "complex": False,
                "constraint_type": "",
                "constraints": {},
                "extra": {},
                "input_type": "field",
            },
            "data_field_name": "log",
            "data_field_alias": None,
            "roles": ["feature", "original_feature"],
            "components": [],
        },
        {
            "field_type": "timestamp",
            "field_alias": "timestamp",
            "field_name": "timestamp",
            "field_index": 5,
            "properties": {
                "role_changeable": False,
                "deletable": False,
                "name_inherited": False,
                "value_fixed": False,
                "passthrough": False,
                "compatibility": False,
                "required": True,
                "complex": False,
                "constraint_type": "",
                "constraints": {},
                "extra": {},
                "input_type": "field",
            },
            "data_field_name": "timestamp",
            "data_field_alias": None,
            "roles": ["timestamp", "original_feature"],
            "components": [],
        },
    ],
}

ALGORITHM_CONFIG_TRAINING_INPUT = [
    {
        "field_type": "string",
        "field_alias": "系统索引",
        "field_name": "__index__",
        "field_index": 0,
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
            "input_type": "field",
        },
        "data_field_name": "__index__",
        "data_field_alias": "index",
        "roles": ["index", "system", "original_feature"],
        "components": [],
    },
    {
        "field_type": "string",
        "field_alias": "用户索引",
        "field_name": "__id__",
        "field_index": 1,
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": True,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
            "input_type": "field",
        },
        "data_field_name": "__id__",
        "data_field_alias": "用户索引",
        "roles": ["index"],
        "components": ["__group_id__", "timestamp"],
    },
    {
        "field_type": "string",
        "field_alias": "分组索引",
        "field_name": "__group_id__",
        "field_index": 2,
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": True,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
            "input_type": "field",
        },
        "data_field_name": "__group_id__",
        "data_field_alias": "分组字段",
        "roles": ["index_component", "group"],
        "components": [],
    },
    {
        "field_type": "string",
        "field_alias": "group",
        "field_name": "line_id",
        "field_index": 3,
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": True,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
            "input_type": "field",
        },
        "data_field_name": "line_id",
        "data_field_alias": None,
        "roles": ["group", "data", "original_feature"],
        "components": [],
    },
    {
        "field_type": "string",
        "field_alias": "日志内容",
        "field_name": "log",
        "field_index": 4,
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
            "input_type": "field",
        },
        "data_field_name": "log",
        "data_field_alias": None,
        "roles": ["feature", "original_feature"],
        "components": [],
    },
    {
        "field_type": "timestamp",
        "field_alias": "timestamp",
        "field_name": "timestamp",
        "field_index": 5,
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
            "input_type": "field",
        },
        "data_field_name": "timestamp",
        "data_field_alias": None,
        "roles": ["timestamp", "original_feature"],
        "components": [],
    },
]

ALGORITHM_CONFIG_TRAINING_META = {
    "input": {
        "table_name": None,
        "table_desc": None,
        "ts_depend": "0d",
        "input_columns_changeable": {"value": False, "condition": "lt", "condition_value": 99},
    },
    "output": {"table_name": None, "table_desc": None},
    "add_on_input": [],
}

EVALUATE_INPUT_VALUE = {
    "evaluate_input": []
    # "evaluate_input": [
    #     {
    #         "field_type": "string",
    #         "field_alias": "系统索引",
    #         "field_name": "__index__",
    #         "field_index": 0,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": True,
    #             "value_fixed": False,
    #             "passthrough": False,
    #             "compatibility": False,
    #             "required": True,
    #             "complex": False,
    #             "constraint_type": None,
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "__index__",
    #         "data_field_alias": "系统索引",
    #         "roles": ["index", "system"],
    #         "components": [],
    #     },
    #     {
    #         "field_type": "string",
    #         "field_alias": "用户索引",
    #         "field_name": "__id__",
    #         "field_index": 1,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": True,
    #             "value_fixed": False,
    #             "passthrough": False,
    #             "compatibility": False,
    #             "required": True,
    #             "complex": True,
    #             "constraint_type": None,
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "__id__",
    #         "data_field_alias": "user index",
    #         "roles": ["index"],
    #         "components": ["__group_id__", "timestamp"],
    #     },
    #     {
    #         "field_type": "string",
    #         "field_alias": "分组索引",
    #         "field_name": "__group_id__",
    #         "field_index": 2,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": True,
    #             "value_fixed": True,
    #             "passthrough": False,
    #             "compatibility": False,
    #             "required": True,
    #             "complex": False,
    #             "constraint_type": None,
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "__group_id__",
    #         "data_field_alias": "分组字段",
    #         "roles": ["index_component", "group"],
    #         "components": [],
    #     },
    #     {
    #         "field_type": "string",
    #         "field_alias": "group",
    #         "field_name": "line_id",
    #         "field_index": 3,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": True,
    #             "value_fixed": False,
    #             "passthrough": False,
    #             "compatibility": True,
    #             "required": True,
    #             "complex": False,
    #             "constraint_type": None,
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "line_id",
    #         "data_field_alias": None,
    #         "roles": ["data"],
    #         "components": [],
    #     },
    #     {
    #         "field_type": "text",
    #         "field_alias": "token",
    #         "field_name": "token",
    #         "field_index": 4,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": False,
    #             "value_fixed": False,
    #             "passthrough": False,
    #             "compatibility": False,
    #             "required": True,
    #             "complex": False,
    #             "constraint_type": None,
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "token",
    #         "data_field_alias": None,
    #         "roles": ["feature"],
    #         "components": [],
    #     },
    #     {
    #         "field_type": "text",
    #         "field_alias": "log_signature",
    #         "field_name": "log_signature",
    #         "field_index": 5,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": False,
    #             "value_fixed": False,
    #             "passthrough": False,
    #             "compatibility": False,
    #             "required": True,
    #             "complex": False,
    #             "constraint_type": "",
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "log_signature",
    #         "data_field_alias": None,
    #         "roles": ["feature"],
    #         "components": [],
    #     },
    #     {
    #         "field_type": "timestamp",
    #         "field_alias": "timestamp",
    #         "field_name": "timestamp",
    #         "field_index": 6,
    #         "properties": {
    #             "role_changeable": False,
    #             "deletable": False,
    #             "name_inherited": False,
    #             "value_fixed": False,
    #             "passthrough": False,
    #             "compatibility": False,
    #             "required": True,
    #             "complex": False,
    #             "constraint_type": "",
    #             "constraints": {},
    #             "extra": {},
    #             "input_type": "field",
    #         },
    #         "data_field_name": "timestamp",
    #         "data_field_alias": None,
    #         "roles": ["timestamp"],
    #         "components": [],
    #     },
    # ]
}

ALGORITHM_CONFIG_PREDICT_META = {
    "input": {
        "table_name": "predict_input1",
        "ts_depend": "0d",
        "input_columns_changeable": {"value": True, "condition": "lt", "condition_value": "500"},
    },
    "output": {"table_name": "预测输出"},
    "add_on_input": [],
}

ALGORITHM_CONFIG_PREDICT_INPUT = [
    {
        "field_name": "__index__",
        "field_alias": "系统索引",
        "field_index": 1,
        "data_field_name": "__index__",
        "data_field_alias": "index",
        "field_type": "string",
        "roles": ["index", "system"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "__id__",
        "field_alias": "用户索引",
        "field_index": 2,
        "data_field_name": "__id__",
        "data_field_alias": "用户索引",
        "field_type": "string",
        "roles": ["index"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": True,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": ["__group_id__", "timestamp"],
    },
    {
        "field_name": "__group_id__",
        "field_alias": "分组索引",
        "field_index": 3,
        "data_field_name": "__group_id__",
        "data_field_alias": "分组字段",
        "field_type": "string",
        "roles": ["group", "index_component"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": True,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "line_id",
        "field_alias": "group",
        "field_index": 4,
        "data_field_name": "line_id",
        "data_field_alias": None,
        "field_type": "string",
        "roles": ["data"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": True,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "log",
        "field_alias": "日志内容",
        "field_index": 5,
        "data_field_name": "log",
        "data_field_alias": None,
        "field_type": "string",
        "roles": ["feature", "passthrough"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "timestamp",
        "field_alias": "timestamp",
        "field_index": 6,
        "data_field_name": "timestamp",
        "data_field_alias": None,
        "field_type": "timestamp",
        "roles": ["timestamp"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
]

ALGORITHM_CONFIG_PREDICT_OUTPUT = [
    {
        "field_name": "__index__",
        "field_alias": "系统索引",
        "field_index": 1,
        "data_field_name": "__index__",
        "data_field_alias": "index",
        "field_type": "string",
        "roles": ["index"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "__id__",
        "field_alias": "用户索引",
        "field_index": 2,
        "data_field_name": "__id__",
        "data_field_alias": "用户索引",
        "field_type": "string",
        "roles": ["index"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": True,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": ["__group_id__", "timestamp"],
    },
    {
        "field_name": "__group_id__",
        "field_alias": "分组索引",
        "field_index": 3,
        "data_field_name": "__group_id__",
        "data_field_alias": "分组字段",
        "field_type": "string",
        "roles": ["group", "index_component"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": True,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "line_id",
        "field_alias": "group",
        "field_index": 4,
        "data_field_name": "line_id",
        "data_field_alias": None,
        "field_type": "string",
        "roles": ["data"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": True,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": True,
            "required": True,
            "complex": False,
            "constraint_type": None,
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "token",
        "field_alias": "token",
        "field_index": 5,
        "data_field_name": "",
        "data_field_alias": None,
        "field_type": "text",
        "roles": ["predict_result"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "log_signature",
        "field_alias": "log_signature",
        "field_index": 6,
        "data_field_name": "",
        "data_field_alias": None,
        "field_type": "text",
        "roles": ["predict_result"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "timestamp",
        "field_alias": "timestamp",
        "field_index": 7,
        "data_field_name": "timestamp",
        "data_field_alias": None,
        "field_type": "timestamp",
        "roles": ["timestamp"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
    {
        "field_name": "log",
        "field_alias": "日志内容",
        "field_index": 8,
        "data_field_name": "log",
        "data_field_alias": None,
        "field_type": "string",
        "roles": ["feature", "passthrough"],
        "properties": {
            "role_changeable": False,
            "deletable": False,
            "name_inherited": False,
            "value_fixed": False,
            "passthrough": False,
            "compatibility": False,
            "required": True,
            "complex": False,
            "constraint_type": "",
            "constraints": {},
            "extra": {},
        },
        "components": [],
    },
]

# ["IP-PORT:\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\s+:\\d{1,5}/","IP:
# \\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}","DATETIME:datetime.datetime
# \\(\\d{4},\\s\\d{1,2},\\s\\d{1,2},\\s\\d{1,2},\\s\\d{1,2},\\s\\d{1,2},
# \\s\\d{5},\\stzinfo=<\\w{3,4}>\\)>","DATETIME:\\d{2}/\\w{3,4}/\\d{4}:
# \\d{1,2}:\\d{1,2}:\\d{1,2}\\s\\+\\d{4}","DATETIME:\\d{4}-\\d{1,2}-\
# \d{1,2}\\s\\d{1,2}:\\d{1,2}:\\d{1,2}\\.\\d*\\+\\d{2}:\\d{2}","DATETIME
# :\\d{4}-\\d{1,2}-\\d{1,2}T\\d{1,2}:\\d{1,2}:\\d{1,2}\\.\\d*\\+\\d{2}
# :\\d{2}","DATETIME:\\d{6,8}\\s\\d{1,2}:\\d{1,2}:\\d{1,2}\\.\\d*\\+\
# \d{2}:\\d{2}","DATETIME:\\d{4}-\\d{1,2}-\\d{1,2}\\s\\d{1,2}:\\d{1,2}
# :\\d{1,2}\\+\\d{2}:\\d{2}","DATETIME:\\d{4}-\\d{1,2}-\\d{1,2}\\s\\d{1,2}
# :\\d{1,2}:\\d{1,2}\\.\\d{6}","DATETIME:\\d{4}-\\d{1,2}-\\d{1,2}\\s\\d{1,2}
# :\\d{1,2}:\\d{1,2},\\d{3}","DATETIME:\\d{4}-\\d{1,2}-\\d{1,2}\\s\\d{1,2}
# :\\d{1,2}:\\d{1,2}\\s\\+\\d{4}","DATETIME:\\d{4}\\d{1,2}\\d{1,2}\\s\\d{1,2}
# :\\d{1,2}:\\d{1,2}\\.\\d{6}","DATETIME:\\d{4}/\\d{1,2}/\\d{1,2}\\s\\d{1,2}
# :\\d{1,2}:\\d{1,2}","DATETIME:\\d{4}-\\d{1,2}-\\d{1,2}\\s\\d{2}:\\d{2}:
# \\d{2}","DATE:20\\d{2}\\d{1,2}\\d{1,2}/","DATE:\\d{4}-\\d{1,2}-\\d{1,2}/"
# ,"TIME:\\d{1,2}:\\d{1,2}:\\d{1,2}.\\d{6}","NUMBER:^[-+]?[0-9]+$","
# NUMBER:^[-+]?[0-9]*\\.[0-9]+","UUID:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}
# -[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}","UUID:[0-9a-fA-F]{32}"]

PREDEFINED_VARIBLES_DEFAULT_VALUE = (
    "WyJJUC1QT1JUOlxcZHsxLDN9XFwuXFxkezEsM31cXC5cXGR7MSwzfVxcLlxcZHsxLDN9XFx"
    "zKzpcXGR7MSw1fS8iLCJJUDpcXGR7MSwzfVxcLlxcZHsxLDN9XFwuXFxkezEsM31cXC5cXG"
    "R7MSwzfSIsIkRBVEVUSU1FOmRhdGV0aW1lLmRhdGV0aW1lXFwoXFxkezR9LFxcc1xcZHsxL"
    "DJ9LFxcc1xcZHsxLDJ9LFxcc1xcZHsxLDJ9LFxcc1xcZHsxLDJ9LFxcc1xcZHsxLDJ9LFxc"
    "c1xcZHs1fSxcXHN0emluZm89PFxcd3szLDR9PlxcKT4iLCJEQVRFVElNRTpcXGR7Mn0vXFx"
    "3ezMsNH0vXFxkezR9OlxcZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9XFxzXFwrXFxkezR9Ii"
    "wiREFURVRJTUU6XFxkezR9LVxcZHsxLDJ9LVxcZHsxLDJ9XFxzXFxkezEsMn06XFxkezEsM"
    "n06XFxkezEsMn1cXC5cXGQqXFwrXFxkezJ9OlxcZHsyfSIsIkRBVEVUSU1FOlxcZHs0fS1c"
    "XGR7MSwyfS1cXGR7MSwyfVRcXGR7MSwyfTpcXGR7MSwyfTpcXGR7MSwyfVxcLlxcZCpcXCt"
    "cXGR7Mn06XFxkezJ9IiwiREFURVRJTUU6XFxkezYsOH1cXHNcXGR7MSwyfTpcXGR7MSwyfT"
    "pcXGR7MSwyfVxcLlxcZCpcXCtcXGR7Mn06XFxkezJ9IiwiREFURVRJTUU6XFxkezR9LVxcZ"
    "HsxLDJ9LVxcZHsxLDJ9XFxzXFxkezEsMn06XFxkezEsMn06XFxkezEsMn1cXCtcXGR7Mn06"
    "XFxkezJ9IiwiREFURVRJTUU6XFxkezR9LVxcZHsxLDJ9LVxcZHsxLDJ9XFxzXFxkezEsMn0"
    "6XFxkezEsMn06XFxkezEsMn1cXC5cXGR7Nn0iLCJEQVRFVElNRTpcXGR7NH0tXFxkezEsMn"
    "0tXFxkezEsMn1cXHNcXGR7MSwyfTpcXGR7MSwyfTpcXGR7MSwyfSxcXGR7M30iLCJEQVRFVE"
    "lNRTpcXGR7NH0tXFxkezEsMn0tXFxkezEsMn1cXHNcXGR7MSwyfTpcXGR7MSwyfTpcXGR7MS"
    "wyfVxcc1xcK1xcZHs0fSIsIkRBVEVUSU1FOlxcZHs0fVxcZHsxLDJ9XFxkezEsMn1cXHNcXG"
    "R7MSwyfTpcXGR7MSwyfTpcXGR7MSwyfVxcLlxcZHs2fSIsIkRBVEVUSU1FOlxcZHs0fS9cXG"
    "R7MSwyfS9cXGR7MSwyfVxcc1xcZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9IiwiREFURVRJTU"
    "U6XFxkezR9LVxcZHsxLDJ9LVxcZHsxLDJ9XFxzXFxkezJ9OlxcZHsyfTpcXGR7Mn0iLCJEQV"
    "RFOjIwXFxkezJ9XFxkezEsMn1cXGR7MSwyfS8iLCJEQVRFOlxcZHs0fS1cXGR7MSwyfS1cXG"
    "R7MSwyfS8iLCJUSU1FOlxcZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9LlxcZHs2fSIsIk5VTU"
    "JFUjpeWy0rXT9bMC05XSskIiwiTlVNQkVSOl5bLStdP1swLTldKlxcLlswLTldKyIsIlVVSU"
    "Q6WzAtOWEtZkEtRl17OH0tWzAtOWEtZkEtRl17NH0tWzAtOWEtZkEtRl17NH0tWzAtOWEtZk"
    "EtRl17NH0tWzAtOWEtZkEtRl17MTJ9IiwiVVVJRDpbMC05YS1mQS1GXXszMn0iXQ"
)

# ""\"|\\;|\\,|\\,|\\[|\\]|\\:|\\s|\\(|\\)|\\=|\\||\\{|\\}|\\>|\\<|\\
# ||'|\\\uff08|\\\uff0c|\\\uff09|\\/|\\\uff0c|\\\u3010|\\\u3011|\\。|\\:""
DELIMETER_DEFAULT_VALUE = (
    "IlwifFxcO3xcXCx8XFwsfFxcW3xcXF18XFw6fFxcc3xcXCh8XFwpfFxcPXxcXHx8XFx7fF"
    "xcfXxcXD58XFw8fFxcfHwnfFxcXHVmZjA4fFxcXHVmZjBjfFxcXHVmZjA5fFxcL3xcXFx1Z"
    "mYwY3xcXFx1MzAxMHxcXFx1MzAxMXxcXOOAgnxcXDoi"
)
