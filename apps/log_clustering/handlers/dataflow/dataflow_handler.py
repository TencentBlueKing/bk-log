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
import json
import os
import arrow
from django.conf import settings
from jinja2 import Environment, FileSystemLoader
from dataclasses import asdict

from apps.api import BkDataDataFlowApi, BkDataAIOPSApi
from apps.log_clustering.exceptions import ClusteringConfigNotExistException
from apps.log_clustering.handlers.aiops.base import BaseAiopsHandler
from apps.log_clustering.handlers.data_access.data_access import DataAccessHandler
from apps.log_clustering.handlers.dataflow.constants import (
    DEFAULT_CLUSTERING_FIELD,
    NOT_CLUSTERING_FILTER_RULE,
    NOT_CONTAIN_SQL_FIELD_LIST,
    UUID_FIELDS,
    DIST_FIELDS,
    FlowMode,
    NodeType,
    DEFAULT_SPARK_EXECUTOR_INSTANCES,
    DEFAULT_PSEUDO_SHUFFLE,
    DEFAULT_SPARK_LOCALITY_WAIT,
    OPERATOR_AND,
)
from apps.log_clustering.handlers.dataflow.data_cls import (
    ExportFlowCls,
    StopFlowCls,
    StartFlowCls,
    PreTreatDataFlowCls,
    StreamSourceCls,
    RealTimeCls,
    HDFSStorageCls,
    CreateFlowCls,
    AfterTreatDataFlowCls,
    ModelCls,
    MergeNodeCls,
    TspiderStorageCls,
    IgniteStorageCls,
    AddFlowNodesCls,
    ModifyFlowCls,
    RequireNodeCls,
    UpdateModelInstanceCls,
)
from apps.log_clustering.models import ClusteringConfig
from apps.log_databus.models import CollectorConfig


class DataFlowHandler(BaseAiopsHandler):
    def export(self, flow_id: int):
        """
        导出flow
        @param flow_id flow id
        """
        export_request = ExportFlowCls(flow_id=flow_id)
        request_dict = self._set_username(export_request)
        return BkDataDataFlowApi.export_flow(request_dict)

    def stop(self, flow_id: int):
        """
        停止flow
        @param flow_id flow id
        """
        stop_request = StopFlowCls(flow_id=flow_id)
        request_dict = self._set_username(stop_request)
        return BkDataDataFlowApi.stop_flow(request_dict)

    def start(self, flow_id: int, consuming_mode: str = "continue", cluster_group: str = "default"):
        """
        启动flow
        @param flow_id flow id
        @param cluster_group 计算集群组
        @param consuming_mode 数据处理模式
        """
        cluster_group = self.conf.get("aiops_default_cluster_group", cluster_group)
        start_request = StartFlowCls(flow_id=flow_id, consuming_mode=consuming_mode, cluster_group=cluster_group)
        request_dict = self._set_username(start_request)
        return BkDataDataFlowApi.start_flow(request_dict)

    def create_pre_treat_flow(self, collector_config_id: int):
        """
        创建pre-treat flow
        """
        clustering_config = ClusteringConfig.objects.filter(collector_config_id=collector_config_id).first()
        if not ClusteringConfig:
            raise ClusteringConfigNotExistException()
        all_etl_fields = CollectorConfig.objects.get(
            collector_config_id=clustering_config.collector_config_id
        ).get_all_etl_fields()
        all_fields_dict = {field["field_name"]: field["alias_name"] or field["field_name"] for field in all_etl_fields}
        filter_rule, not_clustering_rule = self._init_filter_rule(
            clustering_config.filter_rules, all_fields_dict, clustering_config.clustering_fields
        )
        pre_treat_flow_dict = asdict(
            self._init_pre_treat_flow(
                result_table_id=clustering_config.bkdata_etl_result_table_id,
                filter_rule=filter_rule,
                not_clustering_rule=not_clustering_rule,
                clustering_fields=all_fields_dict.get(clustering_config.clustering_fields),
            )
        )
        pre_treat_flow = self._render_template(
            flow_mode=FlowMode.PRE_TREAT_FLOW.value, render_obj={"pre_treat": pre_treat_flow_dict}
        )
        flow = json.loads(pre_treat_flow)
        create_pre_treat_flow_request = CreateFlowCls(
            nodes=flow,
            flow_name="{}_pre_treat_flow".format(clustering_config.collector_config_name_en),
            project_id=self.conf.get("project_id"),
        )
        request_dict = self._set_username(create_pre_treat_flow_request)
        result = BkDataDataFlowApi.create_flow(request_dict)
        clustering_config.pre_treat_flow = pre_treat_flow_dict
        clustering_config.pre_treat_flow_id = result["flow_id"]
        clustering_config.save()
        return result

    @classmethod
    def _init_filter_rule(cls, filter_rules, all_fields_dict, clustering_field):
        # add default_filter_rule where data is not null and length(data) > 1
        default_filter_rule = cls._init_default_filter_rule(all_fields_dict.get(clustering_field))
        filter_rule_list = ["where", default_filter_rule]
        not_clustering_rule_list = ["where", "NOT", "(", default_filter_rule]
        if not filter_rules:
            return " ".join(filter_rule_list), " ".join(not_clustering_rule_list)

        filter_rule_list.append(OPERATOR_AND)
        not_clustering_rule_list.append(OPERATOR_AND)
        for filter_rule in filter_rules:
            if not all_fields_dict.get(filter_rule.get("fields_name")):
                continue
            rule = [
                all_fields_dict.get(filter_rule.get("fields_name")),
                filter_rule.get("op"),
                filter_rule.get("value"),
                filter_rule.get("logic_operator"),
            ]
            filter_rule_list.extend(rule)
            not_clustering_rule_list.extend(rule)
            # 不参与聚类日志需要增加括号修改优先级
        not_clustering_rule_list.append(")")
        return " ".join(filter_rule_list), " ".join(not_clustering_rule_list)

    @classmethod
    def _init_default_filter_rule(cls, clustering_field):
        if not clustering_field:
            return ""
        return "{} is not null and length({}) > 1".format(clustering_field, clustering_field)

    def _init_pre_treat_flow(
        self, result_table_id: str, filter_rule: str, not_clustering_rule: str, clustering_fields="log"
    ):
        """
        初始化预处理flow
        """
        all_fields = DataAccessHandler.get_fields(result_table_id=result_table_id)
        is_dimension_fields = [
            field["field_name"] for field in all_fields if field["field_name"] not in NOT_CONTAIN_SQL_FIELD_LIST
        ]
        dst_transform_fields, transform_fields = self._generate_fields(
            is_dimension_fields, clustering_field=clustering_fields
        )
        time_format = arrow.now().format("YYYYMMDDHHmmssSSS")
        pre_treat_flow = PreTreatDataFlowCls(
            stream_source=StreamSourceCls(result_table_id=result_table_id),
            transform=RealTimeCls(
                fields=", ".join(transform_fields),
                table_name="pre_treat_transform_{}".format(time_format),
                result_table_id="{}_pre_treat_transform_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            add_uuid=RealTimeCls(
                fields="{}, udf_gen_uuid(log) AS uuid".format(", ".join(dst_transform_fields)),
                table_name="pre_treat_add_uuid_{}".format(time_format),
                result_table_id="{}_pre_treat_add_uuid_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            sample_set=RealTimeCls(
                fields="log, uuid",
                table_name="pre_treat_sample_set_{}".format(time_format),
                result_table_id="{}_pre_treat_sample_set_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            sample_set_hdfs=HDFSStorageCls(
                table_name="pre_treat_sample_set_{}".format(time_format), expires=self.conf.get("hdfs_expires")
            ),
            filter=RealTimeCls(
                fields=", ".join(is_dimension_fields),
                table_name="pre_treat_filter_{}".format(time_format),
                result_table_id="{}_pre_treat_filter_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule=filter_rule,
            ),
            add_uuid_hdfs=HDFSStorageCls(
                table_name="pre_treat_add_uuid_{}".format(time_format), expires=self.conf.get("hdfs_expires")
            ),
            not_clustering=RealTimeCls(
                fields=", ".join(is_dimension_fields),
                table_name="pre_treat_not_clustering_{}".format(time_format),
                result_table_id="{}_pre_treat_not_clustering_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule=not_clustering_rule if not_clustering_rule else NOT_CLUSTERING_FILTER_RULE,
            ),
            not_clustering_hdfs=HDFSStorageCls(
                table_name="pre_treat_not_clustering_{}".format(time_format), expires=self.conf.get("hdfs_expires")
            ),
            bk_biz_id=self.conf.get("bk_biz_id"),
            cluster=self.conf.get("hdfs_cluster"),
        )
        return pre_treat_flow

    @classmethod
    def _generate_fields(cls, is_dimension_fields: list, clustering_field: str):
        if clustering_field == DEFAULT_CLUSTERING_FIELD:
            return copy.copy(is_dimension_fields), copy.copy(is_dimension_fields)
        # 转换节点之后的fields数组
        dst_transform_fields = []
        # 转换节点的fields数组
        transform_fields = []
        for field in is_dimension_fields:
            if field == clustering_field:
                dst_transform_fields.append(DEFAULT_CLUSTERING_FIELD)
                transform_fields.append("{} as {}".format(field, DEFAULT_CLUSTERING_FIELD))
                continue
            if field == DEFAULT_CLUSTERING_FIELD:
                dst_transform_fields.append(clustering_field)
                transform_fields.append("{} as {}".format(field, clustering_field))
                continue
            dst_transform_fields.append(field)
            transform_fields.append(field)
        return dst_transform_fields, transform_fields

    @classmethod
    def _render_template(cls, flow_mode: str, render_obj):
        flow_path = FlowMode.get_choice_label(flow_mode)
        file_path, file_name = os.path.split(flow_path)
        file_loader = FileSystemLoader(file_path)
        env = Environment(loader=file_loader)
        template = env.get_template(file_name)
        return template.render(**render_obj)

    def create_after_treat_flow(self, collector_config_id):
        clustering_config = ClusteringConfig.objects.filter(collector_config_id=collector_config_id).first()
        if not ClusteringConfig:
            raise ClusteringConfigNotExistException()
        all_etl_fields = CollectorConfig.objects.get(
            collector_config_id=clustering_config.collector_config_id
        ).get_all_etl_fields()
        all_fields_dict = {field["field_name"]: field["alias_name"] or field["field_name"] for field in all_etl_fields}
        after_treat_flow_dict = asdict(
            self._init_after_treat_flow(
                clustering_fields=all_fields_dict.get(clustering_config.clustering_fields),
                add_uuid_result_table_id=clustering_config.pre_treat_flow["add_uuid"]["result_table_id"],
                sample_set_result_table_id=clustering_config.pre_treat_flow["sample_set"]["result_table_id"],
                non_clustering_result_table_id=clustering_config.pre_treat_flow["not_clustering"]["result_table_id"],
                model_id=clustering_config.model_id,
                model_release_id=self.get_latest_released_id(clustering_config.model_id),
                collector_config_name_en=clustering_config.collector_config_name_en,
            )
        )
        after_treat_flow = self._render_template(
            flow_mode=FlowMode.AFTER_TREAT_FLOW.value, render_obj={"after_treat": after_treat_flow_dict}
        )
        flow = json.loads(after_treat_flow)
        create_pre_treat_flow_request = CreateFlowCls(
            nodes=flow,
            flow_name="{}_after_treat_flow".format(clustering_config.collector_config_name_en),
            project_id=self.conf.get("project_id"),
        )
        request_dict = self._set_username(create_pre_treat_flow_request)
        result = BkDataDataFlowApi.create_flow(request_dict)
        clustering_config.after_treat_flow = after_treat_flow_dict
        clustering_config.after_treat_flow_id = result["flow_id"]
        clustering_config.new_cls_pattern_rt = after_treat_flow_dict["judge_new_class"]["result_table_id"]
        clustering_config.save()
        self.add_kv_source_node(
            clustering_config.after_treat_flow_id,
            clustering_config.after_treat_flow["join_signature_tmp"]["result_table_id"],
        )
        modify_flow_dict = asdict(
            self.modify_flow(
                after_treat_flow_id=clustering_config.after_treat_flow_id,
                group_by_result_table_id=clustering_config.after_treat_flow["group_by"]["result_table_id"],
                ignite_result_table_id=clustering_config.after_treat_flow["join_signature_tmp"]["result_table_id"],
                modify_node_result_table_id=clustering_config.after_treat_flow["join_signature"]["result_table_id"],
                modify_node_result_table_name=clustering_config.after_treat_flow["join_signature"]["table_name"],
            )
        )
        modify_flow = self._render_template(
            flow_mode=FlowMode.MODIFY_FLOW.value, render_obj={"modify_flow": modify_flow_dict}
        )
        modify_flow_json = json.loads(modify_flow)
        request_dict = self._set_username(modify_flow_json)
        clustering_config.modify_flow = modify_flow_dict
        clustering_config.save()
        flow_res = BkDataDataFlowApi.put_flow_nodes(request_dict)
        data_processing_id_config = self.get_serving_data_processing_id_config(
            clustering_config.after_treat_flow["model"]["result_table_id"]
        )
        self.update_model_instance(model_instance_id=data_processing_id_config["id"])
        return flow_res

    def _init_after_treat_flow(
        self,
        add_uuid_result_table_id: str,
        sample_set_result_table_id: str,
        non_clustering_result_table_id: str,
        model_release_id: int,
        model_id: str,
        collector_config_name_en: str,
        clustering_fields: str = "log",
    ):
        all_fields = DataAccessHandler.get_fields(result_table_id=add_uuid_result_table_id)
        is_dimension_fields = [
            field["field_name"] for field in all_fields if field["field_name"] not in NOT_CONTAIN_SQL_FIELD_LIST
        ]
        time_format = arrow.now().format("YYYYMMDDHHmmssSSS")
        _, transform_fields = self._generate_fields(is_dimension_fields, clustering_field=clustering_fields)
        change_fields = [field for field in transform_fields if field != UUID_FIELDS]
        change_fields.extend(DIST_FIELDS)
        after_treat_flow = AfterTreatDataFlowCls(
            add_uuid_stream_source=StreamSourceCls(result_table_id=add_uuid_result_table_id),
            sample_set_stream_source=StreamSourceCls(result_table_id=sample_set_result_table_id),
            non_clustering_stream_source=StreamSourceCls(result_table_id=non_clustering_result_table_id),
            model=ModelCls(
                table_name="after_treat_model_{}".format(time_format),
                model_release_id=model_release_id,
                model_id=model_id,
                result_table_id="{}_after_treat_model_{}".format(self.conf.get("bk_biz_id"), time_format),
            ),
            join_after_treat=RealTimeCls(
                table_name="after_treat_join_after_treat_{}".format(time_format),
                fields="param.{}".format(", param.".join(is_dimension_fields)),
                result_table_id="{}_after_treat_join_after_treat_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            change_field=RealTimeCls(
                fields=", ".join(change_fields),
                table_name="after_treat_change_field_{}".format(time_format),
                result_table_id="{}_after_treat_change_field_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            merge_table=MergeNodeCls(
                table_name="bklog_{}_{}".format(settings.ENVIRONMENT, collector_config_name_en),
                result_table_id="{}_bklog_{}_{}".format(
                    self.conf.get("bk_biz_id"), settings.ENVIRONMENT, collector_config_name_en
                ),
            ),
            format_signature=RealTimeCls(
                fields="",
                table_name="after_treat_format_signature_{}".format(time_format),
                result_table_id="{}_after_treat_format_signature_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            join_signature_tmp=RealTimeCls(
                fields="",
                table_name="after_treat_join_signature_tmp_{}".format(time_format),
                result_table_id="{}_after_treat_join_signature_tmp_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            judge_new_class=RealTimeCls(
                fields="",
                table_name="after_treat_judge_new_class_{}".format(time_format),
                result_table_id="{}_after_treat_judge_new_class_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            join_signature=RealTimeCls(
                fields="",
                table_name="after_treat_join_signature_{}".format(time_format),
                result_table_id="{}_after_treat_join_signature_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            judge_new_class_tspider=TspiderStorageCls(
                cluster=self.conf.get("tspider_cluster"), expire=self.conf.get("tspider_cluster_expire")
            ),
            ignite=IgniteStorageCls(cluster=self.conf.get("ignite_cluster")),
            queue_cluster=self.conf.get("queue_cluster"),
            bk_biz_id=self.conf.get("bk_biz_id"),
            group_by=RealTimeCls(
                fields="",
                table_name="after_treat_group_by_{}".format(time_format),
                result_table_id="{}_after_treat_group_by_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
        )
        return after_treat_flow

    def add_kv_source_node(self, flow_id, kv_source_result_table_id):
        """
        给flow添加kv_source节点
        """
        add_kv_source_node_request = AddFlowNodesCls(
            flow_id=flow_id,
            result_table_id=kv_source_result_table_id,
        )
        add_kv_source_node_request.config["bk_biz_id"] = self.conf.get("bk_biz_id")
        add_kv_source_node_request.config["from_result_table_ids"].append(kv_source_result_table_id)
        add_kv_source_node_request.config["result_table_id"] = kv_source_result_table_id
        request_dict = self._set_username(add_kv_source_node_request)
        return BkDataDataFlowApi.add_flow_nodes(request_dict)

    def modify_flow(
        self,
        after_treat_flow_id: int,
        group_by_result_table_id: str,
        ignite_result_table_id: str,
        modify_node_result_table_id: str,
        modify_node_result_table_name: str,
    ):
        graph = BkDataDataFlowApi.get_flow_graph(
            params={"flow_id": after_treat_flow_id, "bk_username": self.conf.get("bk_username")}
        )
        graph_nodes_dict = {
            (node["result_table_ids"][0], node["node_type"]): node["node_id"] for node in graph["nodes"]
        }
        modify_flow_cls = ModifyFlowCls(
            flow_id=after_treat_flow_id,
            node_id=graph_nodes_dict.get((modify_node_result_table_id, NodeType.REALTIME)),
            id="ch_{}".format(graph_nodes_dict.get((modify_node_result_table_id, NodeType.REALTIME))),
            bk_biz_id=self.conf.get("bk_biz_id"),
            table_name=modify_node_result_table_name,
            group_by_node=RequireNodeCls(
                node_id=graph_nodes_dict.get((group_by_result_table_id, NodeType.REALTIME)),
                result_table_id=group_by_result_table_id,
                id="ch_{}".format(graph_nodes_dict.get((group_by_result_table_id, NodeType.REALTIME))),
            ),
            ignite_node=RequireNodeCls(
                node_id=graph_nodes_dict.get((ignite_result_table_id, NodeType.UNIFIED_KV_SOURCE)),
                result_table_id=ignite_result_table_id,
                id="ch_{}".format(graph_nodes_dict.get((ignite_result_table_id, NodeType.UNIFIED_KV_SOURCE))),
            ),
        )
        return modify_flow_cls

    def get_latest_deploy_data(self, flow_id):
        return BkDataDataFlowApi.get_latest_deploy_data(
            params={"flow_id": flow_id, "bk_username": self.conf.get("bk_username")}
        )

    def get_serving_data_processing_id_config(self, result_table_id):
        return BkDataAIOPSApi.serving_data_processing_id_config(
            params={"data_processing_id": result_table_id, "bk_username": self.conf.get("bk_username")}
        )

    def update_model_instance(self, model_instance_id):
        update_model_instance_request = UpdateModelInstanceCls(
            filter_id=model_instance_id,
            execute_config={
                "spark.executor.instances": self.conf.get("spark.executor.instances", DEFAULT_SPARK_EXECUTOR_INSTANCES),
                "pseudo_shuffle": self.conf.get("pseudo_shuffle", DEFAULT_PSEUDO_SHUFFLE),
                "spark.locality.wait": self.conf.get("spark.locality.wait", DEFAULT_SPARK_LOCALITY_WAIT),
            },
        )
        request_dict = self._set_username(update_model_instance_request)
        return BkDataAIOPSApi.update_execute_config(request_dict)
