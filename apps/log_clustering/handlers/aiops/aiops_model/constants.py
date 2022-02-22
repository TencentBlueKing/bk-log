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
