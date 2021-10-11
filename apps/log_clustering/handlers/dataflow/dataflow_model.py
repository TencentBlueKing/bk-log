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
import copy
from typing import Union, Any, List

from dataclasses import asdict

from apps.log_clustering.handlers.dataflow.data_cls import (
    StreamSourceNodeCls,
    ModelTsCustomNodeCls,
    RealTimeNodeCls,
    TspiderStorageNodeCls,
    QueueStorageNodeCls,
    FromNodesCls,
    InputConfigCls,
    InputNodeCls,
    OutputConfigCls,
    OutputNodeCls,
    ScheduleConfigCls,
    ServingSchedulerParamsCls,
)


class FlowModel(object):
    def __init__(self):
        self._flow_list = []

    def add(
        self,
        node: Union[
            StreamSourceNodeCls, ModelTsCustomNodeCls, RealTimeNodeCls, TspiderStorageNodeCls, QueueStorageNodeCls
        ],
    ):
        self._flow_list.append(asdict(node))
        return self

    @property
    def flow(self):
        return copy.deepcopy(self._flow_list)

    @classmethod
    def stream_source_node(cls, bk_biz_id: int, name: str, result_table_id: str, node_id: int) -> StreamSourceNodeCls:
        """
        实时数据源节点
        """
        return StreamSourceNodeCls(
            result_table_id=result_table_id,
            bk_biz_id=bk_biz_id,
            name=name,
            id=node_id,
        )

    @classmethod
    def real_time_node(
        cls,
        bk_biz_id: int,
        sql: str,
        table_name: str,
        name: str,
        count_freq: Any,
        waiting_time: Any,
        window_time: Any,
        window_type: str,
        output_name: str,
        window_lateness: dict,
        node_id: int,
        from_nodes: List[FromNodesCls],
    ):
        return RealTimeNodeCls(
            bk_biz_id=bk_biz_id,
            sql=sql,
            table_name=table_name,
            name=name,
            count_freq=count_freq,
            waiting_time=waiting_time,
            window_time=window_time,
            window_type=window_type,
            output_name=output_name,
            window_lateness=window_lateness,
            id=node_id,
            from_nodes=from_nodes,
        )

    @classmethod
    def model_ts_custom_node(
        cls,
        bk_biz_id: int,
        table_name: str,
        output_name: str,
        name: str,
        model_release_id: int,
        serving_fields_mapping: dict,
        input_result_table: str,
        output_fields: list,
        model_id: str,
        node_id: int,
        from_nodes: List[FromNodesCls],
    ):
        """
        时序模型节点
        """
        return ModelTsCustomNodeCls(
            bk_biz_id=bk_biz_id,
            table_name=table_name,
            output_name=output_name,
            name=name,
            model_release_id=model_release_id,
            input_config=InputConfigCls(
                input_node=InputNodeCls(
                    serving_fields_mapping=serving_fields_mapping,
                    input_result_table=input_result_table,
                )
            ),
            output_config=OutputConfigCls(
                output_node=OutputNodeCls(
                    output_fields=output_fields,
                    table_alias=output_name,
                    table_name=table_name,
                    table_zh_name=output_name,
                )
            ),
            schedule_config=ScheduleConfigCls(serving_scheduler_params=ServingSchedulerParamsCls()),
            model_id=model_id,
            id=node_id,
            from_nodes=from_nodes,
        )

    @classmethod
    def tspider_storage_node(
        cls,
        name: str,
        result_table_id: str,
        bk_biz_id: int,
        indexed_fields: List[str],
        cluster: str,
        expires: int,
        has_unique_key: bool,
        storage_keys: List[str],
        node_id: int,
        from_nodes: List[FromNodesCls],
    ):
        return TspiderStorageNodeCls(
            name=name,
            result_table_id=result_table_id,
            bk_biz_id=bk_biz_id,
            indexed_fields=indexed_fields,
            cluster=cluster,
            expires=expires,
            has_unique_key=has_unique_key,
            storage_keys=storage_keys,
            id=node_id,
            from_nodes=from_nodes,
        )
