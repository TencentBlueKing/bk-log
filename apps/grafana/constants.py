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

from django.utils.translation import ugettext_lazy as _

TRACE_DATASOURCE_TYPE = "jaeger"

CMDB_EXTEND_FIELDS = {
    "host": [
        {"bk_property_id": "bk_host_id", "bk_property_name": _("主机ID")},
        {"bk_property_id": "bk_set_ids", "bk_property_name": _("集群ID")},
        {"bk_property_id": "bk_module_ids", "bk_property_name": _("模块ID")},
    ],
    "module": [
        {"bk_property_id": "bk_module_id", "bk_property_name": _("模块ID")},
        {"bk_property_id": "bk_set_id", "bk_property_name": _("集群ID")},
    ],
    "set": [{"bk_property_id": "bk_set_id", "bk_property_name": _("集群ID")}],
}


# 时序指标filed_type
TIME_SERIES_FIELD_TYPE = ["integer", "long", "float", "double", "int"]

# 日志检索内置维度字段
LOG_SEARCH_DIMENSION_LIST = ["cloudId", "gseIndex", "iterationIndex", "container_id", "_iteration_idx"]
