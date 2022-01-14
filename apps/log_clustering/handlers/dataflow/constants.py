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
from apps.utils import ChoicesEnum

DEFAULT_CLUSTERING_FIELD = "log"
NOT_CLUSTERING_FILTER_RULE = " where ip is null"
UUID_FIELDS = "uuid"
OPERATOR_AND = "and"
# 聚类不参与sql字段
NOT_CONTAIN_SQL_FIELD_LIST = ["timestamp", "_startTime_", "_endTime_"]
DIST_FIELDS = ["dist_01", "dist_03", "dist_05", "dist_07", "dist_09"]
DEFAULT_SPARK_EXECUTOR_INSTANCES = 20
DEFAULT_PSEUDO_SHUFFLE = 200
DEFAULT_SPARK_LOCALITY_WAIT = "0s"


class FlowMode(ChoicesEnum):
    # 预处理flow
    PRE_TREAT_FLOW = "pre_treat_flow"
    # 结果处理flow
    AFTER_TREAT_FLOW = "after_treat_flow"
    # 修改flow的某些节点
    MODIFY_FLOW = "modify_flow"

    _choices_labels = (
        (PRE_TREAT_FLOW, "templates/flow/pre_treat_flow.json"),
        (AFTER_TREAT_FLOW, "templates/flow/after_treat_flow.json"),
        (MODIFY_FLOW, "templates/flow/modify_flow.json"),
    )


class NodeType(object):
    REALTIME = "realtime"
    UNIFIED_KV_SOURCE = "unified_kv_source"
