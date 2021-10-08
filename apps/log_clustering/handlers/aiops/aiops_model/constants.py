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
    "feature_columns": [
        {
            "field_type": "string",
            "field_alias": "日志内容",
            "description": None,
            "is_dimension": False,
            "field_name": "log",
            "field_index": 1,
            "default_value": None,
            "properties": {
                "used_by": "user",
                "allow_modified": True,
                "is_advanced": False,
                "allow_null": True,
                "support": True,
            },
            "sample_value": None,
            "attr_type": "not_defined",
            "data_field_name": "log",
            "data_field_alias": None,
            "roles": {},
            "is_ts_field": False,
            "origin": [],
            "used_by": "user",
            "deletable": False,
            "err": {"field_name": "", "data_field_name": ""},
            "is_save": True,
        },
        {
            "field_type": "string",
            "field_alias": "唯一辨识id",
            "description": None,
            "is_dimension": False,
            "field_name": "uuid",
            "field_index": 2,
            "default_value": None,
            "properties": {},
            "sample_value": None,
            "attr_type": "not_defined",
            "data_field_name": "uuid",
            "data_field_alias": None,
            "roles": {},
            "is_ts_field": False,
            "origin": [],
            "used_by": "user",
            "deletable": False,
            "err": {"field_name": "", "data_field_name": ""},
            "is_save": True,
        },
    ],
    "label_columns": [],
}

ALGORITHM_CONFIG_FEATURE_COLUMNS = [
    {
        "field_name": "log",
        "field_alias": "日志内容",
        "field_index": 1,
        "default_value": None,
        "sample_value": None,
        "value": None,
        "data_field_name": None,
        "data_field_alias": None,
        "field_type": "string",
        "allowed_values": [],
        "roles": {},
        "properties": {
            "used_by": "user",
            "allow_modified": True,
            "is_advanced": False,
            "allow_null": True,
            "support": True,
        },
        "origin": [],
        "description": None,
        "used_by": "user",
    },
    {
        "field_name": "uuid",
        "field_alias": "唯一辨识id",
        "field_index": 2,
        "default_value": None,
        "sample_value": None,
        "value": None,
        "data_field_name": None,
        "data_field_alias": None,
        "field_type": "string",
        "allowed_values": [],
        "roles": {},
        "properties": {},
        "origin": [],
        "description": None,
        "used_by": "user",
    },
]

ALGORITHM_CONFIG_PREDICT_OUTPUT = [
    {
        "field_name": "token",
        "field_alias": "token",
        "field_index": 1,
        "default_value": None,
        "sample_value": None,
        "value": None,
        "data_field_name": None,
        "data_field_alias": None,
        "field_type": "text",
        "allowed_values": [],
        "roles": {},
        "properties": {
            "used_by": "user",
            "allow_modified": True,
            "is_advanced": False,
            "allow_null": True,
            "support": True,
        },
        "origin": [],
        "description": None,
        "used_by": "user",
    },
    {
        "field_name": "log_signature",
        "field_alias": "log_signature",
        "field_index": 2,
        "default_value": None,
        "sample_value": None,
        "value": None,
        "data_field_name": None,
        "data_field_alias": None,
        "field_type": "text",
        "allowed_values": [],
        "roles": {},
        "properties": {},
        "origin": [],
        "description": None,
        "used_by": "user",
    },
    {
        "field_name": "log",
        "field_alias": "log",
        "field_index": 3,
        "default_value": None,
        "sample_value": None,
        "value": None,
        "data_field_name": None,
        "data_field_alias": None,
        "field_type": "string",
        "allowed_values": [],
        "roles": {},
        "properties": {},
        "origin": [],
        "description": None,
        "used_by": "user",
    },
    {
        "field_name": "uuid",
        "field_alias": "唯一辨识id",
        "field_index": 4,
        "default_value": None,
        "sample_value": None,
        "value": None,
        "data_field_name": None,
        "data_field_alias": None,
        "field_type": "string",
        "allowed_values": [],
        "roles": {},
        "properties": {},
        "origin": [],
        "description": None,
        "used_by": "user",
    },
]

PREDEFINED_VARIBLES_DEFAULT_VALUE = (
    "WyJpcDpcXGR7MSwzfVxcLlxcZHsxLDN9XFwuXFxkezEsM31cXC5cXGR7MSwzfSIsICJk"
    "YXRldGltZTpkYXRldGltZS5kYXRldGltZVxcKFxcZHs0fSxcXHNcXGR7MSwyfSxcXHNc"
    "XGR7MSwyfSxcXHNcXGR7MSwyfSxcXHNcXGR7MSwyfSxcXHNcXGR7MSwyfSxcXHNcXGR7"
    "NX0sXFxzdHppbmZvPTxcXHd7Myw0fT5cXCk+IiwgImRhdGV0aW1lOlxcZHs0fS1cXGR7"
    "MSwyfS1cXGR7MSwyfVxcc1xcZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9XFwrXFxkezJ9"
    "OlxcZHsyfSIsICJkYXRldGltZTpcXGR7NH0tXFxkezEsMn0tXFxkezEsMn1cXHNcXGR7"
    "Mn06XFxkezJ9OlxcZHsyfSIsICJkYXRldGltZTpcXGR7NH0tXFxkezEsMn0tXFxkezEs"
    "Mn1cXHNcXGR7MSwyfTpcXGR7MSwyfTpcXGR7MSwyfVxcLlxcZHs2fSIsICJkYXRldGlt"
    "ZTpcXGR7NH0tXFxkezEsMn0tXFxkezEsMn1cXHNcXGR7MSwyfTpcXGR7MSwyfTpcXGR7"
    "MSwyfSxcXGR7M30iLCAiZGF0ZXRpbWU6XFxkezR9LVxcZHsxLDJ9LVxcZHsxLDJ9XFxz"
    "XFxkezEsMn06XFxkezEsMn06XFxkezEsMn1cXHNcXCtcXGR7NH0iLCAiZGF0ZXRpbWU6"
    "XFxkezR9XFxkezEsMn1cXGR7MSwyfVxcc1xcZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9"
    "XFwuXFxkezZ9IiwgImRhdGV0aW1lOlxcZHs0fS9cXGR7MSwyfS9cXGR7MSwyfVxcc1xc"
    "ZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9IiwgImRhdGV0aW1lOlxcZHsyfS9cXHd7Myw0"
    "fS9cXGR7NH06XFxkezEsMn06XFxkezEsMn06XFxkezEsMn1cXHNcXCtcXGR7NH0iLCAi"
    "ZGF0ZToyMFxcZHsyfVxcZHsxLDJ9XFxkezEsMn0vIiwgImRhdGU6XFxkezR9LVxcZHsx"
    "LDJ9LVxcZHsxLDJ9LyIsICJ0aW1lOlxcZHsxLDJ9OlxcZHsxLDJ9OlxcZHsxLDJ9Llxc"
    "ZHs2fSIsICJpcC1wb3J0OlxcZHsxLDN9XFwuXFxkezEsM31cXC5cXGR7MSwzfVxcLlxc"
    "ZHsxLDN9XFxzKzpcXGR7MSw1fS8iLCAiTlVNQkVSOl5bLStdP1swLTldKyQiXQ=="
)

DELIMETER_DEFAULT_VALUE = (
    "IlwifFxcO3xcXCx8XFwsfFxcW3xcXF18XFw6fFxcc3xcXCh8XFwpfFxcPXxcXHx8XFx7fFxcfXxcXD"
    "58XFw8fFxcfHwnfFxcXHVmZjA4fFxcXHVmZjBjfFxcXHVmZjA5fFxcL3xcXFx1ZmYwY3xcXFx1MzAx"
    "MHxcXFx1MzAxMSI="
)
