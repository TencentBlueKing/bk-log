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

from dataclasses import dataclass, field
from typing import List, Any, Dict


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

    nodes: Any
    flow_name: str
    project_id: int


@dataclass
class OperatorFlowCls(object):
    """
    开启flow
    """

    flow_id: int
    consuming_mode: str
    cluster_group: str


@dataclass
class StopFlowCls(object):
    """
    停止flow
    """

    flow_id: int


@dataclass
class FrontendInfoCls(object):
    x: float = 30.0
    y: float = 51.0


@dataclass
class StreamSourceNodeCls(object):
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
    serving_fields_mapping: dict
    input_result_table: str
    group_serving: bool = False
    grouped_training: bool = False
    group_serving_enable: bool = True
    input_fields: List[str] = field(default_factory=list)
    group_columns: List[str] = field(default_factory=list)


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
    recovery: Dict = field(default_factory=lambda: {"enable": False, "interval_time": "5m", "retry_times": 1})
    data_period: int = 1
    data_period_unit: str = "day"
    period: int = 1
    fixed_delay: int = 1
    first_run_time: str = ""
    dependency_rule: str = "all_finished"
    period_unit: str = "day"


@dataclass
class ScheduleConfigCls(object):
    serving_scheduler_params: ServingSchedulerParamsCls
    training_scheduler_params: Any = None


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
class ModelTsCustomNodeCls(object):
    """
    时序模型应用
    """

    bk_biz_id: int
    table_name: str
    output_name: str
    name: str
    model_release_id: int
    input_config: InputConfigCls
    output_config: OutputConfigCls
    schedule_config: ScheduleConfigCls
    model_id: str
    id: int
    from_nodes: List[FromNodesCls]
    serving_mode: str = "realtime"
    sample_feedback_config: Dict = field(default_factory=lambda: {"result_table_feedback": False})
    upgrade_config: Dict = field(
        default_factory=lambda: {
            "auto_upgrade": True,
            "notification": False,
            "specific_update_config": {"update_time": "12:00:00", "specific_update": False},
        }
    )
    model_extra_config: Dict = field(default_factory=lambda: {"predict_args": []})
    scene_name: str = "custom"
    node_type: str = "model_ts_custom"
    frontend_info: FrontendInfoCls = FrontendInfoCls()


@dataclass
class RealTimeNodeCls(object):
    """
    实时计算
    """

    bk_biz_id: int
    sql: str
    table_name: str
    name: str
    count_freq: Any
    waiting_time: Any
    window_time: Any
    window_type: str
    output_name: str
    window_lateness: dict
    id: int
    from_nodes: List[FromNodesCls]
    node_type: str = "realtime"
    counter: Any = None
    session_gap: Any = None
    expired_time: Any = None
    correct_config_id: Any = None
    is_open_correct: bool = False
    frontend_info: FrontendInfoCls = FrontendInfoCls()


@dataclass
class TspiderStorageNodeCls(object):
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
class QueueStorageNodeCls(object):
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


@dataclass
class StreamSourceCls(object):
    """
    实时数据源节点输入
    """

    result_table_id: str


@dataclass
class RealTimeCls(object):
    """
    实时计算输入
    """

    fields: str
    table_name: str
    result_table_id: str
    filter_rule: Any


@dataclass
class HDFSStorageCls(object):
    """
    hdfs存储
    """

    table_name: str
    expires: int


@dataclass
class PreTreatDataFlowCls(object):
    stream_source: StreamSourceCls
    sample_set: RealTimeCls
    sample_set_hdfs: HDFSStorageCls
    not_clustering: RealTimeCls
    not_clustering_hdfs: HDFSStorageCls
    bk_biz_id: int
    cluster: str


@dataclass
class ModelCls(object):
    table_name: str
    model_release_id: int
    model_id: str
    result_table_id: str
    input_fields: str
    output_fields: str


@dataclass
class MergeNodeCls(object):
    table_name: str
    result_table_id: str


@dataclass
class TspiderStorageCls(object):
    cluster: str
    expires: int


@dataclass
class RedisStorageCls(object):
    cluster: str


@dataclass
class SplitCls(object):
    table_name: str
    result_table_id: str


@dataclass
class ElasticsearchCls(object):
    analyzed_fields: str = ""
    doc_values_fields: str = ""
    json_fields: str = ""
    expires: str = ""
    has_replica: bool = False


@dataclass
class AfterTreatDataFlowCls(object):
    sample_set_stream_source: StreamSourceCls
    non_clustering_stream_source: StreamSourceCls
    model: ModelCls
    group_by: RealTimeCls
    change_field: RealTimeCls
    merge_table: MergeNodeCls
    format_signature: RealTimeCls
    join_signature_tmp: RealTimeCls
    judge_new_class: RealTimeCls
    join_signature: RealTimeCls
    change_clustering_field: RealTimeCls
    diversion_tspider: TspiderStorageCls
    redis: RedisStorageCls
    diversion: SplitCls
    queue_cluster: str
    bk_biz_id: int
    target_bk_biz_id: int
    es: ElasticsearchCls = ElasticsearchCls()
    es_cluster: str = ""
    is_flink_env: bool = False


@dataclass
class AddFlowNodesCls(object):
    flow_id: int
    result_table_id: str
    from_links: List = field(default_factory=list)
    node_type: str = "redis_kv_source"
    frontend_info: Dict = field(default_factory=lambda: {"x": 1247.0, "y": 426.0})
    config: Dict = field(
        default_factory=lambda: {
            "bk_biz_id": 0,
            "from_result_table_ids": [],
            "name": "join signature缓存",
            "result_table_id": "",
        }
    )


@dataclass
class RequireNodeCls(object):
    node_id: int
    result_table_id: str
    id: str


@dataclass
class ModifyFlowCls(object):
    id: str
    flow_id: int
    node_id: int
    bk_biz_id: int
    table_name: str
    group_by_node: RequireNodeCls
    redis_node: RequireNodeCls


@dataclass
class UpdateModelInstanceCls(object):
    filter_id: str
    execute_config: Dict
    table_name: str = "model_instance"
