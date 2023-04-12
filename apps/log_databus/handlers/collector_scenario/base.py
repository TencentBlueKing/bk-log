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
from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _

from apps.api import TransferApi, NodeApi
from apps.exceptions import ApiResultError
from apps.log_clustering.constants import PatternEnum
from apps.log_databus.constants import META_DATA_ENCODING
from apps.log_databus.handlers.collector_scenario.utils import build_es_option_type
from apps.log_databus.models import CollectorConfig, DataLinkConfig
from apps.log_databus.exceptions import BaseCollectorConfigException, DataLinkConfigPartitionException
from apps.log_search.constants import CollectorScenarioEnum
from apps.utils.function import ignored
from apps.utils.log import logger


class CollectorScenario(object):
    """
    采集场景：行日志、段日志、window event
    1. 根据采集场景加载具体实现的类
    2.
    """

    @classmethod
    def get_instance(cls, collector_scenario_id=None):
        mapping = {
            CollectorScenarioEnum.ROW.value: "RowCollectorScenario",
            CollectorScenarioEnum.SECTION.value: "SectionCollectorScenario",
            CollectorScenarioEnum.WIN_EVENT.value: "WinEventLogScenario",
            CollectorScenarioEnum.CUSTOM.value: "CustomCollectorScenario",
        }
        try:
            collector_scenario = import_string(
                "apps.log_databus.handlers.collector_scenario.{}.{}".format(
                    collector_scenario_id, mapping.get(collector_scenario_id)
                )
            )
            return collector_scenario()
        except ImportError as error:
            raise NotImplementedError(
                _("{collector_scenario_id}场景对应的采集器功能暂未实现, error: {error}").format(
                    collector_scenario_id=collector_scenario_id, error=error
                )
            )

    def get_subscription_steps(self, data_id, params):
        """
        根据采集场景返回节点管理插件下发步骤
        1. 获取配置模板信息
        2. 如果模板未发布，则配置并发布模板
        """
        raise NotImplementedError()

    @classmethod
    def parse_steps(cls, steps):
        """
        解析订阅配置中的步骤
        """
        raise NotImplementedError()

    def get_built_in_config(self, etl_params=None):
        """
        获取采集器内置配置
        """
        raise NotImplementedError()

    @classmethod
    def change_data_stream(
        cls, collector_config: CollectorConfig, mq_topic: Optional[str] = None, mq_partition: int = 1
    ):
        """
        change bk_data_id result_table_id
        :return:
        """
        from apps.log_databus.handlers.collector import build_bk_data_name

        new_bk_data_id = cls.update_or_create_data_id(
            data_link_id=collector_config.data_link_id,
            mq_config={"topic": mq_topic, "partition": mq_partition},
            data_name=build_bk_data_name(
                collector_config.bk_biz_id, f"clustering_{collector_config.collector_config_name_en}"
            ),
            description=collector_config.description,
            encoding=META_DATA_ENCODING,
        )
        TransferApi.modify_datasource_result_table(
            {"bk_data_id": new_bk_data_id, "table_id": collector_config.table_id}
        )
        logger.info(
            f"[change_bk_data_id] "
            f"change bk_data_id => [{new_bk_data_id}]"
            f" result_table_id => [{collector_config.table_id}]"
        )
        return new_bk_data_id

    @staticmethod
    def delete_data_id(bk_data_id, data_name):
        """
        删除data_id
        """
        params = {"data_id": bk_data_id, "data_name": data_name, "option": {"is_log_data": True}}
        TransferApi.modify_data_id(params)
        logger.info(f"[delete_data_id] bk_data_id=>{bk_data_id}, params=>{params}")
        return True

    @staticmethod
    def update_or_create_data_id(
        bk_data_id=None,
        data_link_id=None,
        data_name=None,
        description=None,
        encoding=None,
        option: dict = None,
        mq_config: dict = None,
    ):
        """
        创建或更新数据源
        :param bk_data_id: 数据源ID
        :param data_link_id: 数据链路ID
        :param data_name: 数据源名称
        :param description: 描述
        :param encoding: 字符集编码
        :param mq_config: mq配置
        :param option: 附加参数 {"topic": "xxxx", "partition": 1}
        :return: bk_data_id
        """
        default_option = {
            "encoding": "UTF-8" if encoding is None else encoding,
            "is_log_data": True,
            "allow_metrics_missing": True,
        }

        with ignored(ApiResultError):
            bk_data_id = TransferApi.get_data_id({"data_name": data_name, "no_request": True})["bk_data_id"]

        if not bk_data_id:
            # 创建数据源，创建时一定是BK_LOG_TEXT这种直接入库的方式，后面进行字段提取时再根据情况变更清洗方式
            if not data_name:
                raise BaseCollectorConfigException(_("创建采集项时名称不能为空"))
            if not mq_config:
                mq_config = {}

            params = {
                "data_name": data_name,
                "etl_config": "bk_flat_batch",
                "data_description": description,
                "source_label": "bk_monitor",
                "type_label": "log",
                "mq_config": mq_config,
                "option": default_option,
            }
            if data_link_id:
                data_link = DataLinkConfig.objects.filter(data_link_id=data_link_id).first()
                if not data_link:
                    raise DataLinkConfigPartitionException
                else:
                    params.update(
                        {
                            "transfer_cluster_id": data_link.transfer_cluster_id,
                            "mq_cluster": data_link.kafka_cluster_id,
                        }
                    )

            bk_data_id = TransferApi.create_data_id(params)["bk_data_id"]
            logger.info(f"[create_data_id] bk_data_id=>{bk_data_id}, params=>{params}")
        else:
            params = {"data_id": bk_data_id, "option": default_option}

            if data_name:
                params["data_name"] = data_name

            if description:
                params["data_description"] = description

            if option:
                params["option"] = dict(params["option"], **option)

            # 更新数据源
            TransferApi.modify_data_id(params)
            logger.info(f"[update_data_id] bk_data_id=>{bk_data_id}, params=>{params}")
        return bk_data_id

    def update_or_create_subscription(self, collector_config: CollectorConfig, params: dict):
        """
        创建或更新订阅事件
        :param collector_config: 采集项配置
        :param params: 配置参数，用于获取订阅步骤，不同的场景略有不同
        :return: subscription_id 订阅ID
        """
        if isinstance(collector_config.collector_config_overlay, dict):
            params["collector_config_overlay"] = collector_config.collector_config_overlay
        steps = self.get_subscription_steps(collector_config.bk_data_id, params)

        subscription_params = {
            "scope": {
                "bk_biz_id": collector_config.bk_biz_id,
                "node_type": collector_config.target_node_type,
                "object_type": collector_config.target_object_type,
                "nodes": collector_config.target_nodes,
            },
            "steps": steps,
        }
        if not collector_config.subscription_id:
            # 创建订阅配置
            collector_config.subscription_id = NodeApi.create_subscription(subscription_params)["subscription_id"]
        else:
            # 修改订阅配置
            subscription_params["subscription_id"] = collector_config.subscription_id
            NodeApi.update_subscription_info(subscription_params)
        return collector_config.subscription_id

    def _deal_text_public_params(self, local_params, params):
        need_define_params = [
            "clean_inactive",
            "harvester_limit",
            "scan_frequency",
            "close_inactive",
        ]
        local_params.update(
            {
                "paths": params["paths"],
                "encoding": params["encoding"],
                "tail_files": params["tail_files"],
                "ignore_older": params["ignore_older"],
                "max_bytes": params["max_bytes"],
                "package_count": settings.COLLECTOR_ROW_PACKAGE_COUNT,
                "delimiter": params["conditions"].get("separator") or "",
            }
        )
        local_params.update({param: params.get(param) for param in need_define_params if params.get(param) is not None})

        if params.get("collector_config_overlay"):
            local_params.update(params["collector_config_overlay"])
        return local_params

    @staticmethod
    def log_clustering_fields(es_version: str = "5.x"):
        return [
            {
                "field_name": f"__dist_{pattern_level}",
                "field_type": "string",
                "tag": "dimension",
                "alias_name": f"dist_{pattern_level}",
                "description": _("聚类数字签名{pattern_level}").format(pattern_level=pattern_level),
                "option": build_es_option_type("keyword", es_version),
                "is_built_in": False,
                "is_time": False,
                "is_analyzed": False,
                "is_dimension": False,
                "is_delete": False,
            }
            for pattern_level in PatternEnum.get_dict_choices().keys()
        ]

    @staticmethod
    def fields_insert_field_index(source_fields, dst_fields) -> list:
        """
        给dst_field添加field_index并且组成新的field_index返回回去
        @param source_fields list 包含field_index的原始数据
        @param dst_fields list 不包含field_index的目标数据
        """
        field_index = 0
        for field in source_fields:
            source_field_index = field.get("field_index")
            if source_field_index and source_field_index > field_index:
                field_index = source_field_index

        result_fields = copy.deepcopy(source_fields)
        for field in dst_fields:
            field_index += 1
            field["field_index"] = field_index
            result_fields.append(field)

        return result_fields
