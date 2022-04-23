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
import copy
import json
import os
import arrow
from django.conf import settings
from jinja2 import Environment, FileSystemLoader
from dataclasses import asdict

from apps.log_search.models import LogIndexSet
from apps.api import BkDataDataFlowApi, BkDataAIOPSApi, BkDataMetaApi
from apps.log_clustering.constants import DEFAULT_NEW_CLS_HOURS, AGGS_FIELD_PREFIX, PatternEnum
from apps.log_clustering.exceptions import (
    ClusteringConfigNotExistException,
    BkdataStorageNotExistException,
    BkdataFlowException,
)
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
    STREAM_SOURCE_NODE_TYPE,
    DIVERSION_NODE_NAME,
    TSPIDER_STORAGE_NODE_NAME,
    TSPIDER_STORAGE_NODE_TYPE,
    TSPIDER_STORAGE_INDEX_FIELDS,
    SPLIT_TYPE,
    ActionEnum,
    ActionHandler,
    RealTimeFlowNode,
    DIST_CLUSTERING_FIELDS,
)
from apps.log_clustering.handlers.dataflow.data_cls import (
    ExportFlowCls,
    OperatorFlowCls,
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
    SplitCls,
)
from apps.log_clustering.models import ClusteringConfig
from apps.log_databus.models import CollectorConfig
from apps.utils.log import logger


class DataFlowHandler(BaseAiopsHandler):
    def export(self, flow_id: int):
        """
        导出flow
        @param flow_id flow id
        """
        export_request = ExportFlowCls(flow_id=flow_id)
        request_dict = self._set_username(export_request)
        return BkDataDataFlowApi.export_flow(request_dict)

    def operator_flow(
        self, flow_id: int, consuming_mode: str = "continue", cluster_group: str = "default", action=ActionEnum.START
    ):
        """
        启动flow
        @param flow_id flow id
        @param cluster_group 计算集群组
        @param consuming_mode 数据处理模式
        @param action 操作flow
        """
        cluster_group = self.conf.get("aiops_default_cluster_group", cluster_group)
        start_request = OperatorFlowCls(flow_id=flow_id, consuming_mode=consuming_mode, cluster_group=cluster_group)
        request_dict = self._set_username(start_request)
        return ActionHandler.get_action_handler(action_num=action)(request_dict)

    @classmethod
    def get_fields_dict(cls, clustering_config):
        if clustering_config.collector_config_id:
            all_etl_fields = CollectorConfig.objects.get(
                collector_config_id=clustering_config.collector_config_id
            ).get_all_etl_fields()
            return {field["field_name"]: field["alias_name"] or field["field_name"] for field in all_etl_fields}
        log_index_set_all_fields = LogIndexSet.objects.get(index_set_id=clustering_config.index_set_id).get_fields()
        return {field["field_name"]: field["field_alias"] for field in log_index_set_all_fields["fields"]}

    def create_pre_treat_flow(self, index_set_id: int):
        """
        创建pre-treat flow
        """
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if not ClusteringConfig:
            raise ClusteringConfigNotExistException()
        all_fields_dict = self.get_fields_dict(clustering_config=clustering_config)
        filter_rule, not_clustering_rule = self._init_filter_rule(
            clustering_config.filter_rules, all_fields_dict, clustering_config.clustering_fields
        )
        pre_treat_flow_dict = asdict(
            self._init_pre_treat_flow(
                result_table_id=clustering_config.bkdata_etl_result_table_id,
                filter_rule=filter_rule,
                not_clustering_rule=not_clustering_rule,
                clustering_fields=all_fields_dict.get(clustering_config.clustering_fields),
                time_format=arrow.now().format("YYYYMMDDHHmmssSSS"),
            )
        )
        pre_treat_flow = self._render_template(
            flow_mode=FlowMode.PRE_TREAT_FLOW.value, render_obj={"pre_treat": pre_treat_flow_dict}
        )
        flow = json.loads(pre_treat_flow)
        create_pre_treat_flow_request = CreateFlowCls(
            nodes=flow,
            flow_name="{}_pre_treat_flow".format(
                clustering_config.collector_config_name_en
                if clustering_config.collector_config_name_en
                else clustering_config.source_rt_name
            ),
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
        # 这里是因为默认连接符号需要
        filter_rule_list.append(OPERATOR_AND)
        not_clustering_rule_list.append(OPERATOR_AND)
        for filter_rule in filter_rules:
            if not all_fields_dict.get(filter_rule.get("fields_name")):
                continue
            rule = [
                all_fields_dict.get(filter_rule.get("fields_name")),
                cls.change_op(filter_rule.get("op")),
                "'{}'".format(filter_rule.get("value")),
                filter_rule.get("logic_operator"),
            ]
            filter_rule_list.extend(rule)
            not_clustering_rule_list.extend(rule)
        # 这里是因为需要去掉最后一个and（可能是前面添加的and）
        filter_rule_list.pop(-1)
        not_clustering_rule_list.pop(-1)
        # 不参与聚类日志需要增加括号修改优先级
        not_clustering_rule_list.append(")")
        return " ".join(filter_rule_list), " ".join(not_clustering_rule_list)

    @classmethod
    def change_op(cls, op):
        if op == "!=":
            return "<>"
        return op

    @classmethod
    def _init_default_filter_rule(cls, clustering_field):
        if not clustering_field:
            return ""
        return "{} is not null and length({}) > 1".format(clustering_field, clustering_field)

    def _init_pre_treat_flow(
        self,
        result_table_id: str,
        filter_rule: str,
        not_clustering_rule: str,
        time_format: str,
        clustering_fields="log",
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

    def create_after_treat_flow(self, index_set_id):
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if not ClusteringConfig:
            raise ClusteringConfigNotExistException()
        all_fields_dict = self.get_fields_dict(clustering_config=clustering_config)
        source_rt_name = (
            clustering_config.collector_config_name_en
            if clustering_config.collector_config_name_en
            else clustering_config.source_rt_name
        )
        after_treat_flow_dict = asdict(
            self._init_after_treat_flow(
                clustering_fields=all_fields_dict.get(clustering_config.clustering_fields),
                add_uuid_result_table_id=clustering_config.pre_treat_flow["add_uuid"]["result_table_id"],
                sample_set_result_table_id=clustering_config.pre_treat_flow["sample_set"]["result_table_id"],
                non_clustering_result_table_id=clustering_config.pre_treat_flow["not_clustering"]["result_table_id"],
                model_id=clustering_config.model_id,
                model_release_id=self.get_latest_released_id(clustering_config.model_id),
                src_rt_name=source_rt_name,
                target_bk_biz_id=clustering_config.bk_biz_id,
                clustering_config=clustering_config,
                time_format=arrow.now().format("YYYYMMDDHHmmssSSS"),
            )
        )
        after_treat_flow = self._render_template(
            flow_mode=FlowMode.AFTER_TREAT_FLOW.value
            if clustering_config.collector_config_id
            else FlowMode.AFTER_TREAT_FLOW_BKDATA.value,
            render_obj={"after_treat": after_treat_flow_dict},
        )
        flow = json.loads(after_treat_flow)
        new_cls_pattern_rt = after_treat_flow_dict["diversion"]["result_table_id"]
        # 这里是为了越过分流节点
        if clustering_config.bk_biz_id == self.conf.get("bk_biz_id"):
            flow, new_cls_pattern_rt = self.deal_diversion_node(flow=flow, after_treat_flow_dict=after_treat_flow_dict)
        create_pre_treat_flow_request = CreateFlowCls(
            nodes=flow,
            flow_name="{}_after_treat_flow".format(clustering_config.source_rt_name),
            project_id=self.conf.get("project_id"),
        )
        request_dict = self._set_username(create_pre_treat_flow_request)
        result = BkDataDataFlowApi.create_flow(request_dict)
        clustering_config.after_treat_flow = after_treat_flow_dict
        clustering_config.after_treat_flow_id = result["flow_id"]
        clustering_config.new_cls_pattern_rt = new_cls_pattern_rt
        clustering_config.save()
        self.add_kv_source_node(
            clustering_config.after_treat_flow_id,
            clustering_config.after_treat_flow["join_signature_tmp"]["result_table_id"],
        )
        if clustering_config.bk_biz_id != self.conf.get("bk_biz_id"):
            stream_source_node = self.add_stream_source(
                flow_id=clustering_config.after_treat_flow_id,
                stream_source_table_id=clustering_config.after_treat_flow["diversion"]["result_table_id"],
                target_bk_biz_id=clustering_config.bk_biz_id,
            )
            self.add_tspider_storage(
                flow_id=clustering_config.after_treat_flow_id,
                tspider_storage_table_id=clustering_config.after_treat_flow["diversion"]["result_table_id"],
                target_bk_biz_id=clustering_config.bk_biz_id,
                expires=clustering_config.after_treat_flow["diversion_tspider"]["expires"],
                cluster=clustering_config.after_treat_flow["diversion_tspider"]["cluster"],
                source_node_id=stream_source_node["node_id"],
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

    def deal_diversion_node(self, flow, after_treat_flow_dict):
        # 为了处理分流节点不能分流到同业务id
        for flow_obj in flow:
            if flow_obj["node_type"] == SPLIT_TYPE:
                flow.remove(flow_obj)
                flow.append(
                    {
                        "name": "新类判断(tspider_storage)",
                        "result_table_id": after_treat_flow_dict["judge_new_class"]["result_table_id"],
                        "bk_biz_id": after_treat_flow_dict["target_bk_biz_id"],
                        "indexed_fields": TSPIDER_STORAGE_INDEX_FIELDS,
                        "cluster": after_treat_flow_dict["diversion_tspider"]["cluster"],
                        "expires": after_treat_flow_dict["diversion_tspider"]["expires"],
                        "has_unique_key": False,
                        "storage_keys": [],
                        "id": 283090,
                        "from_nodes": [
                            {
                                "id": 268099,
                                "from_result_table_ids": [after_treat_flow_dict["judge_new_class"]["result_table_id"]],
                            }
                        ],
                        "node_type": TSPIDER_STORAGE_NODE_TYPE,
                        "frontend_info": {"x": 2231, "y": 73},
                    }
                )
        return flow, after_treat_flow_dict["judge_new_class"]["result_table_id"]

    def _init_after_treat_flow(
        self,
        add_uuid_result_table_id: str,
        sample_set_result_table_id: str,
        non_clustering_result_table_id: str,
        model_release_id: int,
        model_id: str,
        target_bk_biz_id: int,
        src_rt_name: str,
        clustering_config,
        time_format: str,
        clustering_fields: str = "log",
    ):
        # 这里是为了在新类中去除第一次启动24H内产生的大量异常新类
        new_cls_timestamp = int(arrow.now().shift(hours=DEFAULT_NEW_CLS_HOURS).float_timestamp * 1000)
        all_fields = DataAccessHandler.get_fields(result_table_id=add_uuid_result_table_id)
        is_dimension_fields = [
            field["field_name"] for field in all_fields if field["field_name"] not in NOT_CONTAIN_SQL_FIELD_LIST
        ]
        _, transform_fields = self._generate_fields(is_dimension_fields, clustering_field=clustering_fields)
        change_fields = [field for field in transform_fields if field != UUID_FIELDS]
        change_clustering_fields = copy.copy(change_fields)
        change_fields.extend(DIST_FIELDS)
        change_clustering_fields.extend(DIST_CLUSTERING_FIELDS)
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
            change_clustering_field=RealTimeCls(
                fields=", ".join(change_clustering_fields),
                table_name="after_treat_change_clustering_field_{}".format(time_format),
                result_table_id="{}_after_treat_change_clustering_field_{}".format(
                    self.conf.get("bk_biz_id"), time_format
                ),
                filter_rule="",
            ),
            merge_table=MergeNodeCls(
                table_name="bklog_{}_{}".format(settings.ENVIRONMENT, src_rt_name),
                result_table_id="{}_bklog_{}_{}".format(self.conf.get("bk_biz_id"), settings.ENVIRONMENT, src_rt_name),
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
                filter_rule="AND event_time > {}".format(new_cls_timestamp),
            ),
            join_signature=RealTimeCls(
                fields="",
                table_name="after_treat_join_signature_{}".format(time_format),
                result_table_id="{}_after_treat_join_signature_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            group_by=RealTimeCls(
                fields="",
                table_name="after_treat_group_by_{}".format(time_format),
                result_table_id="{}_after_treat_group_by_{}".format(self.conf.get("bk_biz_id"), time_format),
                filter_rule="",
            ),
            diversion=SplitCls(
                table_name="after_treat_diversion_{}".format(time_format),
                result_table_id="{}_after_treat_diversion_{}".format(target_bk_biz_id, time_format),
            ),
            diversion_tspider=TspiderStorageCls(
                cluster=self.conf.get("tspider_cluster"), expires=self.conf.get("tspider_cluster_expire")
            ),
            ignite=IgniteStorageCls(cluster=self.conf.get("ignite_cluster")),
            queue_cluster=self.conf.get("queue_cluster"),
            bk_biz_id=self.conf.get("bk_biz_id"),
            target_bk_biz_id=target_bk_biz_id,
        )
        if not clustering_config.collector_config_id:
            es_storage = self.get_es_storage_fields(clustering_config.bkdata_etl_result_table_id)
            if not es_storage:
                raise BkdataStorageNotExistException(
                    BkdataStorageNotExistException.MESSAGE.formate(index_set_id=clustering_config.index_set_id)
                )

            after_treat_flow.es_cluster = clustering_config.es_storage
            after_treat_flow.es.expires = es_storage["expires"]
            after_treat_flow.es.has_replica = json.dumps(es_storage["has_replica"])
            after_treat_flow.es.json_fields = json.dumps(es_storage["json_fields"])
            after_treat_flow.es.analyzed_fields = json.dumps(es_storage["analyzed_fields"])
            doc_values_fields = es_storage["doc_values_fields"]
            doc_values_fields.extend(
                [f"{AGGS_FIELD_PREFIX}_{pattern_level}" for pattern_level in PatternEnum.get_choices()]
            )
            after_treat_flow.es.doc_values_fields = json.dumps(doc_values_fields)
        return after_treat_flow

    @classmethod
    def get_es_storage_fields(cls, result_table_id):
        # 获取计算平台rt存储字段
        result = BkDataMetaApi.result_tables.storages({"result_table_id": result_table_id})
        es = result.get("es")
        if not es:
            return None
        storage_config = json.loads(es["storage_config"])
        # "expires": "3d"
        storage_config["expires"] = int(es["expires"][:-1])
        return storage_config

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

    def add_stream_source(self, flow_id, stream_source_table_id, target_bk_biz_id):
        add_stream_source_request = AddFlowNodesCls(
            flow_id=flow_id,
            result_table_id=stream_source_table_id,
        )
        add_stream_source_request.config["bk_biz_id"] = target_bk_biz_id
        add_stream_source_request.config["from_result_table_ids"].append(stream_source_table_id)
        add_stream_source_request.config["result_table_id"] = stream_source_table_id
        add_stream_source_request.config["name"] = DIVERSION_NODE_NAME
        add_stream_source_request.node_type = STREAM_SOURCE_NODE_TYPE
        request_dict = self._set_username(add_stream_source_request)
        return BkDataDataFlowApi.add_flow_nodes(request_dict)

    def add_tspider_storage(
        self, flow_id, tspider_storage_table_id, target_bk_biz_id, expires, cluster, source_node_id
    ):
        add_tspider_storage_request = AddFlowNodesCls(
            flow_id=flow_id,
            result_table_id=tspider_storage_table_id,
        )
        add_tspider_storage_request.config["bk_biz_id"] = target_bk_biz_id
        add_tspider_storage_request.config["from_result_table_ids"].append(tspider_storage_table_id)
        add_tspider_storage_request.config["result_table_id"] = tspider_storage_table_id
        add_tspider_storage_request.config["name"] = TSPIDER_STORAGE_NODE_NAME
        add_tspider_storage_request.config["expires"] = expires
        add_tspider_storage_request.config["indexed_fields"] = TSPIDER_STORAGE_INDEX_FIELDS
        add_tspider_storage_request.config["cluster"] = cluster
        add_tspider_storage_request.from_links.append(
            {
                "source": {"node_id": source_node_id, "id": "ch_{}".format(source_node_id), "arrow": "left"},
                "target": {
                    # 这里为为了契合计算平台的一个demo id 实际不起作用
                    "id": "ch_1536",
                    "arrow": "Left",
                },
            }
        )
        add_tspider_storage_request.node_type = TSPIDER_STORAGE_NODE_TYPE
        request_dict = self._set_username(add_tspider_storage_request)
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

    def update_filter_rules(self, index_set_id):
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if not ClusteringConfig:
            raise ClusteringConfigNotExistException()
        all_fields_dict = self.get_fields_dict(clustering_config=clustering_config)
        filter_rule, not_clustering_rule = self._init_filter_rule(
            clustering_config.filter_rules, all_fields_dict, clustering_config.clustering_fields
        )

        flow_id = clustering_config.pre_treat_flow_id
        flow_graph = self.get_flow_graph(flow_id=flow_id)

        nodes = flow_graph["nodes"]
        target_nodes = self.get_flow_node_config(
            nodes=nodes,
            filter_table_names=[RealTimeFlowNode.PRE_TREAT_FILTER, RealTimeFlowNode.PRE_TREAT_NOT_CLUSTERING],
        )

        self.deal_update_filter_flow_node(
            target_nodes=target_nodes,
            filter_rule=filter_rule,
            not_clustering_rule=not_clustering_rule if not_clustering_rule else NOT_CLUSTERING_FILTER_RULE,
            flow_id=flow_id,
        )
        self.operator_flow(flow_id=flow_id, action=ActionEnum.RESTART)

    def get_flow_graph(self, flow_id):
        return BkDataDataFlowApi.get_flow_graph(self._set_username(request_data_cls={"flow_id": flow_id}))

    def update_flow_nodes(self, config, flow_id, node_id):
        return BkDataDataFlowApi.patch_flow_nodes(
            self._set_username(request_data_cls={"flow_id": flow_id, "node_id": node_id, **config})
        )

    @staticmethod
    def get_flow_node_config(nodes, filter_table_names: list):
        result = {}
        for node in nodes:
            table_name = node["node_config"].get("table_name")
            if not table_name:
                continue
            table_name_prefix = table_name.rsplit("_", 1)[0]
            if table_name_prefix in filter_table_names:
                result[table_name_prefix] = node
        return result

    def deal_update_filter_flow_node(self, target_nodes, filter_rule, not_clustering_rule, flow_id):
        filter_nodes = target_nodes.get(RealTimeFlowNode.PRE_TREAT_FILTER)
        if filter_nodes:
            sql = self.deal_filter_sql(filter_nodes["node_config"]["sql"].split("where")[0], filter_rule)
            self.update_flow_nodes({"sql": sql}, flow_id=flow_id, node_id=filter_nodes["node_id"])
        not_cluster_nodes = target_nodes.get(RealTimeFlowNode.PRE_TREAT_NOT_CLUSTERING)
        if not_cluster_nodes:
            sql = self.deal_filter_sql(not_cluster_nodes["node_config"]["sql"].split("where")[0], not_clustering_rule)
            self.update_flow_nodes({"sql": sql}, flow_id=flow_id, node_id=not_cluster_nodes["node_id"])

    @staticmethod
    def deal_filter_sql(sql, rule):
        return f"{sql} {rule}"

    def update_flow(self, index_set_id):
        clustering_config = ClusteringConfig.objects.filter(index_set_id=index_set_id).first()
        if not clustering_config.after_treat_flow_id:
            logger.info(f"update pre_treat flow not found: index_set_id -> {index_set_id}")
            return
        if not ClusteringConfig:
            raise ClusteringConfigNotExistException()
        all_fields_dict = self.get_fields_dict(clustering_config=clustering_config)
        filter_rule, not_clustering_rule = self._init_filter_rule(
            clustering_config.filter_rules, all_fields_dict, clustering_config.clustering_fields
        )
        logger.info(f"update pre_treat flow beginning: flow_id -> {clustering_config.pre_treat_flow_id}")
        self.update_pre_treat_flow(
            flow_id=clustering_config.pre_treat_flow_id,
            result_table_id=clustering_config.bkdata_etl_result_table_id,
            filter_rule=filter_rule,
            not_clustering_rule=not_clustering_rule,
            clustering_fields=all_fields_dict.get(clustering_config.clustering_fields),
        )
        logger.info(f"update pre_treat flow success: flow_id -> {clustering_config.pre_treat_flow_id}")
        logger.info(f"update after_treat flow beginning: flow_id -> {clustering_config.after_treat_flow_id}")
        self.update_after_treat_flow(
            flow_id=clustering_config.after_treat_flow_id,
            all_fields_dict=all_fields_dict,
            clustering_config=clustering_config,
        )
        logger.info(f"update after_treat flow success: flow_id -> {clustering_config.after_treat_flow_id}")

    def update_pre_treat_flow(
        self, flow_id, result_table_id: str, filter_rule: str, not_clustering_rule: str, clustering_fields="log"
    ):
        flow_graph = self.get_flow_graph(flow_id=flow_id)
        nodes = flow_graph["nodes"]
        time_format = self.get_time_format(
            nodes=nodes, table_name_prefix=RealTimeFlowNode.PRE_TREAT_FILTER, flow_id=flow_id
        )
        pre_treat_flow_dict = asdict(
            self._init_pre_treat_flow(
                result_table_id, filter_rule, not_clustering_rule, time_format, clustering_fields=clustering_fields
            )
        )
        pre_treat_flow = self._render_template(
            flow_mode=FlowMode.PRE_TREAT_FLOW.value, render_obj={"pre_treat": pre_treat_flow_dict}
        )
        flow = json.loads(pre_treat_flow)
        self.deal_pre_treat_flow(nodes=nodes, flow=flow)
        self.operator_flow(flow_id=flow_id, action=ActionEnum.RESTART)

    def deal_pre_treat_flow(self, nodes, flow):
        target_real_time_node_dict, source_real_time_node_dict = self.get_real_time_nodes(flow=flow, nodes=nodes)
        for table_name, node in source_real_time_node_dict.items():
            target_node = target_real_time_node_dict.get(table_name)
            if not target_node:
                logger.error("could not find target_node --> [table_name]: ", table_name)
                continue
            self.deal_real_time_node(flow_id=node["flow_id"], node_id=node["node_id"], sql=target_node["sql"])
        return

    @classmethod
    def get_real_time_nodes(cls, flow, nodes):
        target_real_time_node_dict = {
            node["table_name"]: node for node in flow if node["node_type"] == NodeType.REALTIME
        }
        source_real_time_node_dict = {
            node["node_config"]["table_name"]: node for node in nodes if node["node_type"] == NodeType.REALTIME
        }
        return target_real_time_node_dict, source_real_time_node_dict

    @classmethod
    def get_elasticsearch_storage_nodes(cls, flow, nodes):
        target_es_storage_node_dict = {
            node["result_table_id"]: node for node in flow if node["node_type"] == NodeType.ELASTIC_STORAGE
        }
        source_es_storage_node_dict = {
            node["node_config"]["result_table_id"]: node
            for node in nodes
            if node["node_type"] == NodeType.ELASTIC_STORAGE
        }
        return target_es_storage_node_dict, source_es_storage_node_dict

    def update_after_treat_flow(self, flow_id, all_fields_dict, clustering_config):
        flow_graph = self.get_flow_graph(flow_id=flow_id)
        nodes = flow_graph["nodes"]
        time_format = self.get_time_format(
            nodes=nodes, table_name_prefix=RealTimeFlowNode.AFTER_TREAT_JOIN_AFTER_TREAT, flow_id=flow_id
        )

        source_rt_name = (
            clustering_config.collector_config_name_en
            if clustering_config.collector_config_name_en
            else clustering_config.source_rt_name
        )
        after_treat_flow_dict = asdict(
            self._init_after_treat_flow(
                clustering_fields=all_fields_dict.get(clustering_config.clustering_fields),
                add_uuid_result_table_id=clustering_config.pre_treat_flow["add_uuid"]["result_table_id"],
                sample_set_result_table_id=clustering_config.pre_treat_flow["sample_set"]["result_table_id"],
                non_clustering_result_table_id=clustering_config.pre_treat_flow["not_clustering"]["result_table_id"],
                model_id=clustering_config.model_id,
                model_release_id=self.get_latest_released_id(clustering_config.model_id),
                src_rt_name=source_rt_name,
                target_bk_biz_id=clustering_config.bk_biz_id,
                clustering_config=clustering_config,
                time_format=time_format,
            )
        )
        after_treat_flow = self._render_template(
            flow_mode=FlowMode.AFTER_TREAT_FLOW.value
            if clustering_config.collector_config_id
            else FlowMode.AFTER_TREAT_FLOW_BKDATA.value,
            render_obj={"after_treat": after_treat_flow_dict},
        )
        flow = json.loads(after_treat_flow)
        self.deal_after_treat_flow(nodes=nodes, flow=flow)
        self.operator_flow(flow_id=flow_id, action=ActionEnum.RESTART)

    def deal_after_treat_flow(self, nodes, flow):
        target_real_time_node_dict, source_real_time_node_dict = self.get_real_time_nodes(flow=flow, nodes=nodes)
        for table_name, node in source_real_time_node_dict.items():
            target_node = target_real_time_node_dict.get(table_name)
            if not target_node:
                logger.error("could not find target_node --> [table_name]: ", table_name)
                continue
            self.deal_real_time_node(flow_id=node["flow_id"], node_id=node["node_id"], sql=target_node["sql"])

        target_es_storage_node_dict, source_es_storage_node_dict = self.get_elasticsearch_storage_nodes(
            flow=flow, nodes=nodes
        )
        for result_table_id, node in source_es_storage_node_dict.items():
            target_node = target_es_storage_node_dict.get(result_table_id)
            if not target_node:
                logger.error("could not find target_node --> [result_table_id]: ", result_table_id)
                continue
            self.deal_elastic_storage_node(
                flow_id=node["flow_id"],
                node_id=node["node_id"],
                analyzed_fields=target_node["analyzed_fields"],
                date_fields=target_node["date_fields"],
                doc_values_fields=target_node["doc_values_fields"],
                json_fields=target_node["json_fields"],
            )

    def deal_real_time_node(self, flow_id, node_id, sql):
        return self.update_flow_nodes(config={"sql": sql}, flow_id=flow_id, node_id=node_id)

    def deal_elastic_storage_node(self, flow_id, node_id, analyzed_fields, date_fields, doc_values_fields, json_fields):
        return self.update_flow_nodes(
            config={
                "analyzed_fields": analyzed_fields,
                "date_fields": date_fields,
                "doc_values_fields": doc_values_fields,
                "json_fields": json_fields,
            },
            flow_id=flow_id,
            node_id=node_id,
        )

    def get_time_format(self, nodes, table_name_prefix, flow_id):
        target_nodes = self.get_flow_node_config(nodes=nodes, filter_table_names=[table_name_prefix])
        if not target_nodes:
            raise BkdataFlowException(BkdataFlowException.MESSAGE.format(flow_id=flow_id))

        return target_nodes[table_name_prefix]["node_config"]["table_name"].rsplit("_", 1)[1]
