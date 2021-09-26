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

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class ExportFlowCls(object):
    """
    导出flow
    """

    flow_id: int


@dataclass
class CreateFlowCls(object):
    """
    创建flow
    """

    nodes: List[dict]
    flow_name: str
    project_id: int


@dataclass
class StartFlowCls(object):
    """
    开启flow
    """

    consuming_mode: str
    cluster_group: str


@dataclass
class FrontendInfoCls(object):
    x: float = 30.0
    y: float = 51.0


@dataclass
class StreamSourceNode(object):
    """
    实时数据源node
    """

    result_table_id: str
    bk_biz_id: int
    name: str
    id: int
    from_nodes: List[str] = field(default_factory=list)
    node_type: str = "stream_source"
    frontend_info: FrontendInfoCls = FrontendInfoCls()


@dataclass
class InputNodeCls(object):
    grouped_training: bool
    group_serving: bool
    serving_fields_mapping: dict
    group_serving_enable: bool
    input_fields: list
    group_columns: list
    input_result_table: str


@dataclass
class InputConfigCls(object):
    input_node: InputNodeCls


@dataclass
class OutputNodeFieldsCls(object):
    origin: list
    default_value: bool
    field_alias: str
    description: Any
    roles: dict
    field_type: str
    sample_value: Any
    used_by: str
    data_field_alias: Any
    value: Any
    allowed_values: list
    properties: dict
    is_ts_field: bool
    data_field_name: Any
    field_name: str
    attr_type: str
    field_index: int


@dataclass
class OutputNodeCls(object):
    output_fields: List[OutputNodeFieldsCls]
    table_alias: str
    table_name: str
    table_zh_name: str


@dataclass
class OutputConfigCls(object):
    output_node: OutputNodeCls


@dataclass
class ServingSchedulerParamsCls(object):
    recovery: dict
    data_period: int
    data_period_unit: str
    period: int
    fixed_delay: int
    first_run_time: str
    dependency_rule: str
    period_unit: str


@dataclass
class ScheduleConfigCls(object):
    training_scheduler_params: bool
    serving_scheduler_params: ServingSchedulerParamsCls


@dataclass
class SpecificUpdateConfigCls(object):
    update_time: str
    specific_update: bool


@dataclass
class SampleFeedbackConfigCls(object):
    result_table_feedback: bool
    specific_update_config: SpecificUpdateConfigCls


@dataclass
class UpgradeConfigCls(object):
    auto_upgrade: bool
    notification: bool


@dataclass
class FromNodesCls(object):
    id: int
    from_result_table_ids: List[str]


@dataclass
class ModelTsCustomNode(object):
    """
    时序模型应用
    """

    bk_biz_id: str
    table_name: str
    output_name: str
    name: str
    model_release_id: int
    input_config: InputConfigCls
    output_config: OutputConfigCls
    schedule_config: ScheduleConfigCls
    serving_mode: str
    sample_feedback_config: SampleFeedbackConfigCls
    upgrade_config: SampleFeedbackConfigCls
    model_id: str
    model_extra_config: dict
    scene_name: str
    id: int
    from_nodes: List[FromNodesCls]
    node_type: str = "model_ts_custom"
    frontend_info: FrontendInfoCls = FrontendInfoCls()


@dataclass
class RealTimeNode(object):
    """
    实时计算
    """

    bk_biz_id: int
    sql: str
    table_name: str
    name: str
    count_freq: int
    waiting_time: int
    window_time: Any
    window_type: str
    counter: Any
    output_name: str
    session_gap: Any
    expired_time: Any
    window_lateness: dict
    correct_config_id: Any
    is_open_correct: bool
    id: int
    from_nodes: List[FromNodesCls]
    node_type: str = "realtime"
    frontend_info: FrontendInfoCls = FrontendInfoCls()


@dataclass
class TspiderStorageCls(object):
    """
    tspider落地存储
    """

    name: str
    result_table_id: str
    bk_biz_id: int
    indexed_fields: List[str]
    cluster: str
    expires: int
    has_unique_key: bool
    storage_keys: list
    id: int
    from_nodes: List[FromNodesCls]
    node_type: str = "tspider_storage"
    frontend_info: FrontendInfoCls = FrontendInfoCls()


@dataclass
class QueueStorageCls(object):
    """
    队列存储节点
    """

    name: str
    bk_biz_id: int
    cluster: str
    expires: int
    result_table_id: str
    id: int
    from_nodes: List[FromNodesCls]
    node_type: str = "queue_storage"
    frontend_info: FrontendInfoCls = FrontendInfoCls()
