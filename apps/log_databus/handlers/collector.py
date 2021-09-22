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
import re
import copy
import datetime
from collections import defaultdict
import arrow
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.api import CCApi
from apps.api import NodeApi, TransferApi
from apps.api.modules.bk_node import BKNodeApi
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import FEATURE_COLLECTOR_ITSM
from apps.utils.thread import MultiExecuteFunc
from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.iam import ResourceEnum, Permission
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_esquery.utils.es_route import EsRoute
from apps.utils.log import logger
from apps.exceptions import ApiError, ApiRequestError, ApiResultError
from apps.utils.local import get_local_param, get_request_username
from apps.log_databus.constants import (
    TargetNodeTypeEnum,
    CollectStatus,
    RunStatus,
    LogPluginInfo,
    BK_SUPPLIER_ACCOUNT,
    META_DATA_ENCODING,
    NOT_FOUND_CODE,
    CHECK_TASK_READY_NOTE_FOUND_EXCEPTION_CODE,
    SEARCH_BIZ_INST_TOPO_LEVEL,
    INTERNAL_TOPO_INDEX,
    BIZ_TOPO_INDEX,
)
from apps.log_databus.exceptions import (
    CollectorConfigNotExistException,
    CollectorConfigNameDuplicateException,
    CollectorConfigDataIdNotExistException,
    SubscriptionInfoNotFoundException,
    CollectorActiveException,
    RegexMatchException,
    RegexInvalidException,
    CollectNotSuccessNotCanStart,
    CollectNotSuccess,
    CollectorTaskRunningStatusException,
    CollectorCreateOrUpdateSubscriptionException,
    CollectorIllegalIPException,
    CollectorConfigNameENDuplicateException,
)
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.models import CollectorConfig, CleanStash
from apps.log_search.handlers.biz import BizHandler
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.constants import GlobalCategoriesEnum, CMDB_HOST_SEARCH_FIELDS
from apps.models import model_to_dict
from apps.log_databus.handlers.kafka import KafkaConsumerHandle
from apps.log_databus.constants import EtlConfig
from apps.decorators import user_operation_record
from apps.log_search.models import LogIndexSet, LogIndexSetData, Scenario
from apps.utils.time_handler import format_user_time_zone
from apps.log_databus.tasks.bkdata import async_create_bkdata_data_id


class CollectorHandler(object):
    def __init__(self, collector_config_id=None):
        super().__init__()
        self.collector_config_id = collector_config_id
        self.data = None
        if collector_config_id:
            try:
                self.data = CollectorConfig.objects.get(collector_config_id=self.collector_config_id)
            except CollectorConfig.DoesNotExist:
                raise CollectorConfigNotExistException()

    def _multi_info_get(self):
        # 并发查询所需的配置
        multi_execute_func = MultiExecuteFunc()
        if self.data.bk_data_id:
            multi_execute_func.append(
                "data_id_config", TransferApi.get_data_id, params={"bk_data_id": self.data.bk_data_id}
            )
        if self.data.table_id:
            multi_execute_func.append(
                "result_table_config", TransferApi.get_result_table, params={"table_id": self.data.table_id}
            )
            multi_execute_func.append(
                "result_table_storage",
                TransferApi.get_result_table_storage,
                params={"result_table_list": self.data.table_id, "storage_type": "elasticsearch"},
            )
        if self.data.subscription_id:
            multi_execute_func.append(
                "subscription_config",
                BKNodeApi.get_subscription_info,
                params={"subscription_id_list": [self.data.subscription_id]},
            )
        return multi_execute_func.run()

    RETRIEVE_CHAIN = [
        "set_itsm_info",
        "set_split_rule",
        "set_target",
        "set_default_field",
        "set_categorie_name",
        "complement_metadata_info",
        "complement_nodeman_info",
        "fields_is_empty",
        "deal_time",
    ]

    def set_itsm_info(self, collector_config, context):  # noqa
        from apps.log_databus.handlers.itsm import ItsmHandler

        itsm_info = ItsmHandler().collect_itsm_status(collect_config_id=collector_config["collector_config_id"])
        collector_config.update(
            {
                "ticket_url": itsm_info["ticket_url"],
                "itsm_ticket_status": itsm_info["collect_itsm_status"],
                "itsm_ticket_status_display": itsm_info["collect_itsm_status_display"],
            }
        )
        return collector_config

    def set_default_field(self, collector_config, context):  # noqa
        collector_config.update(
            {
                "collector_scenario_name": self.data.get_collector_scenario_id_display(),
                "bk_data_name": self.data.bk_data_name,
                "storage_cluster_id": None,
                "retention": None,
                "etl_params": {},
                "fields": [],
            }
        )
        return collector_config

    def set_split_rule(self, collector_config, context):  # noqa
        collector_config["index_split_rule"] = "--"
        if self.data.table_id and collector_config["storage_shards_size"]:
            slice_size = collector_config["storage_shards_nums"] * collector_config["storage_shards_size"]
            collector_config["index_split_rule"] = _("ES索引主分片大小达到{}G后分裂").format(slice_size)
        return collector_config

    def set_target(self, collector_config: dict, context):  # noqa
        if collector_config["target_node_type"] == "INSTANCE":
            collector_config["target"] = collector_config.get("target_nodes", [])
            return collector_config
        nodes = collector_config.get("target_nodes", [])
        bk_module_inst_ids = self._get_ids("module", nodes)
        bk_set_inst_ids = self._get_ids("set", nodes)
        collector_config["target"] = []
        biz_handler = BizHandler(bk_biz_id=collector_config["bk_biz_id"])
        result_module = biz_handler.get_modules_info(bk_module_inst_ids)
        result_set = biz_handler.get_sets_info(bk_set_inst_ids)
        collector_config["target"].extend(result_module)
        collector_config["target"].extend(result_set)
        return collector_config

    def set_categorie_name(self, collector_config, context):
        # 分类名称
        collector_config["category_name"] = GlobalCategoriesEnum.get_display(collector_config["category_id"])
        return collector_config

    def complement_metadata_info(self, collector_config, context):
        """
        补全保存在metadata 结果表中的配置
        """
        result = context
        if not self.data.table_id:
            collector_config.update(
                {"table_id_prefix": f"{self.data.bk_biz_id}_{settings.TABLE_ID_PREFIX}_", "table_id": ""}
            )
            return collector_config
        table_id_prefix, table_id = self.data.table_id.split(".")
        collector_config.update({"table_id_prefix": table_id_prefix + "_", "table_id": table_id})

        if "result_table_config" in result and "result_table_storage" in result:
            if self.data.table_id in result["result_table_storage"]:
                # etl_config以META为准
                self.data.etl_config = EtlStorage.get_etl_config(result["result_table_config"])
                etl_storage = EtlStorage.get_instance(etl_config=self.data.etl_config)
                collector_config.update(
                    etl_storage.parse_result_table_config(
                        result_table_config=result["result_table_config"],
                        result_table_storage=result["result_table_storage"][self.data.table_id],
                    )
                )
            return collector_config
        return collector_config

    def complement_nodeman_info(self, collector_config, context):
        # 补全保存在节点管理的订阅配置
        result = context
        if self.data.subscription_id and "subscription_config" in result:
            if not result["subscription_config"]:
                raise SubscriptionInfoNotFoundException()
            subscription_config = result["subscription_config"][0]
            collector_scenario = CollectorScenario.get_instance(collector_scenario_id=self.data.collector_scenario_id)
            params = collector_scenario.parse_steps(subscription_config["steps"])
            collector_config.update({"params": params})
            data_encoding = params.get("encoding")
            if data_encoding:
                # 将对应data_encoding 转换成大写供前端
                collector_config.update({"data_encoding": data_encoding.upper()})
        return collector_config

    def fields_is_empty(self, collector_config, context):  # noqa
        # 如果数据未入库，则fields为空，直接使用默认标准字段返回
        if not collector_config["fields"]:
            etl_storage = EtlStorage.get_instance(EtlConfig.BK_LOG_TEXT)
            collector_scenario = CollectorScenario.get_instance(collector_scenario_id=self.data.collector_scenario_id)
            built_in_config = collector_scenario.get_built_in_config()
            result_table_config = etl_storage.get_result_table_config(
                fields=None, etl_params=None, built_in_config=built_in_config
            )
            etl_config = etl_storage.parse_result_table_config(result_table_config)
            collector_config["fields"] = etl_config.get("fields", [])
        return collector_config

    def deal_time(self, collector_config, context):  # noqa
        # 对 collector_config进行时区转换
        time_zone = get_local_param("time_zone", settings.TIME_ZONE)
        collector_config["updated_at"] = format_user_time_zone(collector_config["updated_at"], time_zone=time_zone)
        collector_config["created_at"] = format_user_time_zone(collector_config["created_at"], time_zone=time_zone)
        return collector_config

    def retrieve(self):
        """
        获取采集配置
        :return:
        """
        context = self._multi_info_get()
        collector_config = model_to_dict(self.data)
        for process in self.RETRIEVE_CHAIN:
            collector_config = getattr(self, process, lambda x, y: x)(collector_config, context)
            logger.info(f"[databus retrieve] process => [{process}] collector_config => [{collector_config}]")

        return collector_config

    def _get_ids(self, node_type: str, nodes: list):
        return [node["bk_inst_id"] for node in nodes if node["bk_obj_id"] == node_type]

    @staticmethod
    def add_cluster_info(data):
        """
        补充集群信息
        """
        result_table_list = [_data["table_id"] for _data in data if _data.get("table_id")]
        try:
            cluster_infos = TransferApi.get_result_table_storage(
                {"result_table_list": ",".join(result_table_list), "storage_type": "elasticsearch"}
            )
        except ApiError as error:
            logger.exception(f"request cluster info error => [{error}]")
            cluster_infos = {}

        time_zone = get_local_param("time_zone")
        for _data in data:
            cluster_info = cluster_infos.get(
                _data["table_id"], {"cluster_config": {"cluster_id": -1, "cluster_name": ""}}
            )
            _data["storage_cluster_id"] = cluster_info["cluster_config"]["cluster_id"]
            _data["storage_cluster_name"] = cluster_info["cluster_config"]["cluster_name"]
            # table_id
            if _data.get("table_id"):
                table_id_prefix, table_id = _data["table_id"].split(".")
                _data["table_id_prefix"] = table_id_prefix + "_"
                _data["table_id"] = table_id
            # 分类名
            _data["category_name"] = GlobalCategoriesEnum.get_display(_data["category_id"])

            # 时间处理
            _data["created_at"] = (
                arrow.get(_data["created_at"])
                .replace(tzinfo=settings.TIME_ZONE)
                .to(time_zone)
                .strftime(settings.BKDATA_DATETIME_FORMAT)
            )
            _data["updated_at"] = (
                arrow.get(_data["updated_at"])
                .replace(tzinfo=settings.TIME_ZONE)
                .to(time_zone)
                .strftime(settings.BKDATA_DATETIME_FORMAT)
            )

            # 是否可以检索
            if _data["is_active"] and _data["index_set_id"]:
                _data["is_search"] = (
                    not LogIndexSetData.objects.filter(index_set_id=_data["index_set_id"])
                    .exclude(apply_status="normal")
                    .exists()
                )
            else:
                _data["is_search"] = False

        return data

    @transaction.atomic
    def only_create_or_update_model(self, params):
        model_fields = {
            "collector_config_name": params["collector_config_name"],
            "collector_config_name_en": params["collector_config_name_en"],
            "target_object_type": params["target_object_type"],
            "target_node_type": params["target_node_type"],
            "target_nodes": params["target_nodes"],
            "description": params.get("description") or params["collector_config_name"],
            "is_active": True,
            "data_encoding": params["data_encoding"],
            "params": params["params"],
        }
        # 判断是否存在非法IP列表
        self.cat_illegal_ips(params)
        # 判断是否已存在同英文名collector
        if self._pre_check_collector_config_en(model_fields=model_fields, bk_biz_id=params.get("bk_biz_id")):
            logger.error(
                "collector_config_name_en {collector_config_name_en} already exists".format(
                    collector_config_name_en=model_fields["collector_config_name_en"]
                )
            )
            raise CollectorConfigNameENDuplicateException(
                CollectorConfigNameENDuplicateException.MESSAGE.format(
                    collector_config_name_en=model_fields["collector_config_name_en"]
                )
            )

        is_create = False
        collect_config = self.data
        try:
            if not self.data:
                model_fields.update(
                    {
                        "category_id": params["category_id"],
                        "collector_scenario_id": params["collector_scenario_id"],
                        "bk_biz_id": params["bk_biz_id"],
                        "data_link_id": int(params["data_link_id"]) if params.get("data_link_id") else 0,
                    }
                )
                collect_config = CollectorConfig.objects.create(**model_fields)
                is_create = True
            else:
                model_fields["target_subscription_diff"] = self.diff_target_nodes(params["target_nodes"])
                for key, value in model_fields.items():
                    setattr(self.data, key, value)
                self.data.save()
        except IntegrityError:
            logger.warning(f"collector config name duplicate => [{params['collector_config_name']}]")
            raise CollectorConfigNameDuplicateException()

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.data.bk_biz_id if not is_create else collect_config.bk_biz_id,
            "record_type": UserOperationTypeEnum.COLLECTOR,
            "record_object_id": self.data.collector_config_id if not is_create else collect_config.collector_config_id,
            "action": UserOperationActionEnum.CREATE if is_create else UserOperationActionEnum.UPDATE,
            "params": params,
        }
        user_operation_record.delay(operation_record)

        if is_create:
            self._authorization_collector(collect_config)
        return model_to_dict(collect_config, fields=["collector_config_name", "collector_config_id"])

    def update_or_create(self, params: dict) -> dict:
        """
        创建采集配置
        :return:
        {
            "collector_config_id": 1,
            "collector_config_name": "采集项名称",
            "bk_data_id": 2001,
            "subscription_id": 1,
            "task_id_list": [1]
        }
        """
        if self.data and not self.data.is_active:
            raise CollectorActiveException()

        collector_config_name = params["collector_config_name"]
        collector_config_name_en = params["collector_config_name_en"]
        target_object_type = params["target_object_type"]
        target_node_type = params["target_node_type"]
        target_nodes = params["target_nodes"]
        data_encoding = params["data_encoding"]
        description = params.get("description") or collector_config_name
        params["params"]["encoding"] = data_encoding
        params["params"]["run_task"] = params.get("run_task", True)
        # 1. 创建CollectorConfig记录
        model_fields = {
            "collector_config_name": collector_config_name,
            "collector_config_name_en": collector_config_name_en,
            "target_object_type": target_object_type,
            "target_node_type": target_node_type,
            "target_nodes": target_nodes,
            "description": description,
            "data_encoding": data_encoding,
            "params": params["params"],
            "is_active": True,
        }
        # 判断是否存在非法IP列表
        self.cat_illegal_ips(params)

        is_create = False

        # 判断是否已存在同英文名collector
        if self._pre_check_collector_config_en(model_fields=model_fields, bk_biz_id=params.get("bk_biz_id")):
            logger.error(
                "collector_config_name_en {collector_config_name_en} already exists".format(
                    collector_config_name_en=collector_config_name_en
                )
            )
            raise CollectorConfigNameENDuplicateException(
                CollectorConfigNameENDuplicateException.MESSAGE.format(
                    collector_config_name_en=collector_config_name_en
                )
            )

        # 2. 创建/更新采集项，并同步到bk_data_id
        with transaction.atomic():
            try:
                # 2.1 创建/更新采集项
                if not self.data:
                    # 创建后不允许修改的字段
                    model_fields.update(
                        {
                            "category_id": params["category_id"],
                            "collector_scenario_id": params["collector_scenario_id"],
                            "bk_biz_id": params["bk_biz_id"],
                            "data_link_id": int(params["data_link_id"]) if params.get("data_link_id") else 0,
                        }
                    )
                    model_fields["collector_scenario_id"] = params["collector_scenario_id"]
                    self.data = CollectorConfig.objects.create(**model_fields)
                    is_create = True
                else:
                    _collector_config_name = copy.deepcopy(self.data.collector_config_name)

                    # 当更新itsm流程时 将diff更新前移
                    if not FeatureToggleObject.switch(name=FEATURE_COLLECTOR_ITSM):
                        self.data.target_subscription_diff = self.diff_target_nodes(target_nodes)
                    for key, value in model_fields.items():
                        setattr(self.data, key, value)
                    self.data.save()

                    # collector_config_name更改后更新索引集名称
                    if _collector_config_name != self.data.collector_config_name and self.data.index_set_id:
                        index_set_name = _("[采集项]") + self.data.collector_config_name
                        LogIndexSet.objects.filter(index_set_id=self.data.index_set_id).update(
                            index_set_name=index_set_name
                        )

                # 2.2 meta-创建或更新数据源
                collector_scenario = CollectorScenario.get_instance(
                    collector_scenario_id=self.data.collector_scenario_id
                )

                bk_data_id = collector_scenario.update_or_create_data_id(
                    self.data.bk_data_id,
                    self.data.data_link_id,
                    data_name=f"{self.data.bk_biz_id}_{settings.TABLE_ID_PREFIX}_{collector_config_name}",
                    description=description,
                    encoding=META_DATA_ENCODING,
                )
                self.data.bk_data_id = bk_data_id
                self.data.save()

            except IntegrityError:
                logger.warning(f"collector config name duplicate => [{collector_config_name}]")
                raise CollectorConfigNameDuplicateException()

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.data.bk_biz_id,
            "record_type": UserOperationTypeEnum.COLLECTOR,
            "record_object_id": self.data.collector_config_id,
            "action": UserOperationActionEnum.CREATE if is_create else UserOperationActionEnum.UPDATE,
            "params": model_to_dict(self.data, exclude=["deleted_at", "created_at", "updated_at"]),
        }
        user_operation_record.delay(operation_record)

        if is_create:
            self._authorization_collector(self.data)
        try:
            self._update_or_create_subscription(
                collector_scenario=collector_scenario, params=params["params"], is_create=is_create
            )
        finally:
            # 创建数据平台data_id
            async_create_bkdata_data_id.delay(self.data.collector_config_id)

        return {
            "collector_config_id": self.data.collector_config_id,
            "collector_config_name": self.data.collector_config_name,
            "bk_data_id": self.data.bk_data_id,
            "subscription_id": self.data.subscription_id,
            "task_id_list": self.data.task_id_list,
        }

    def _pre_check_collector_config_en(self, model_fields: dict, bk_biz_id: int):
        if not bk_biz_id:
            bk_biz_id = self.data.bk_biz_id
        qs = CollectorConfig.objects.filter(
            collector_config_name_en=model_fields["collector_config_name_en"],
            bk_biz_id=bk_biz_id,
        )
        if self.collector_config_id:
            qs = qs.exclude(collector_config_id=self.collector_config_id)
        return qs.exists()

    def _update_or_create_subscription(self, collector_scenario, params: dict, is_create=False):
        try:
            self.data.subscription_id = collector_scenario.update_or_create_subscription(self.data, params)
            self.data.save()
            subscription_status = self.get_subscription_status_by_list([self.data.collector_config_id])
            if subscription_status[0]["status"] == CollectStatus.RUNNING:
                logger.warning(
                    f"nodeman get status aleady is ready， collector_config_id -> {self.data.collector_config_id}, "
                    + f" subscription_id -> {self.data.subscription_id}"
                )
                raise CollectorTaskRunningStatusException
            if params.get("run_task", True):
                # if not has action, not do START
                if self.data.task_id_list:
                    self._run_subscription_task()
                else:
                    self._run_subscription_task("START")
            # start nodeman sunscrption
            NodeApi.switch_subscription({"subscription_id": self.data.subscription_id, "action": "enable"})
        except Exception as error:  # pylint: disable=broad-except
            logger.exception(f"create or update collector config failed => [{error}]")
            if not is_create:
                raise CollectorCreateOrUpdateSubscriptionException(
                    CollectorCreateOrUpdateSubscriptionException.MESSAGE.format(err=error)
                )

    def _authorization_collector(self, collector_config: CollectorConfig):
        try:
            # 如果是创建，需要做新建授权
            Permission().grant_creator_action(
                resource=ResourceEnum.COLLECTION.create_simple_instance(
                    collector_config.collector_config_id, attribute={"name": collector_config.collector_config_name}
                ),
                creator=collector_config.created_by,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "collector_config->({}) grant creator action failed, reason: {}".format(
                    collector_config.collector_config_id, e
                )
            )

    @transaction.atomic
    def destroy(self):
        """
        删除采集配置
        :return: task_id
        """
        # 1. 重新命名采集项名称
        collector_config_name = (
            self.data.collector_config_name + "_delete_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        )

        # 2. 停止采集（删除配置文件）
        self.stop()

        # 3. 节点管理-删除订阅配置
        self._delete_subscription()

        # 4. 删除索引集
        if self.data.index_set_id:
            index_set_handler = IndexSetHandler(index_set_id=self.data.index_set_id)
            index_set_handler.delete(self.data.collector_config_name)

        # 5. 删除CollectorConfig记录
        self.data.collector_config_name = collector_config_name
        self.data.save()
        self.data.delete()

        # 6. 删除META采集项：直接重命名采集项名称
        collector_scenario = CollectorScenario.get_instance(collector_scenario_id=self.data.collector_scenario_id)
        if self.data.bk_data_id:
            collector_scenario.delete_data_id(self.data.bk_data_id, collector_config_name)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.data.bk_biz_id,
            "record_type": UserOperationTypeEnum.COLLECTOR,
            "record_object_id": self.data.collector_config_id,
            "action": UserOperationActionEnum.DESTROY,
            "params": "",
        }
        user_operation_record.delay(operation_record)

        return True

    @transaction.atomic
    def start(self):
        """
        启动采集配置
        :return: task_id
        """
        self._itsm_start_judge()

        self.data.is_active = True
        self.data.save()

        # 启用采集项
        if self.data.index_set_id:
            index_set_handler = IndexSetHandler(self.data.index_set_id)
            index_set_handler.start()

        # 启动节点管理订阅功能
        if self.data.subscription_id:
            NodeApi.switch_subscription({"subscription_id": self.data.subscription_id, "action": "enable"})

        # 存在RT则启用RT
        if self.data.table_id:
            _, table_id = self.data.table_id.split(".")  # pylint: disable=unused-variable
            etl_storage = EtlStorage.get_instance(self.data.etl_config)
            etl_storage.switch_result_table(collector_config=self.data, is_enable=True)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.data.bk_biz_id,
            "record_type": UserOperationTypeEnum.COLLECTOR,
            "record_object_id": self.data.collector_config_id,
            "action": UserOperationActionEnum.START,
            "params": "",
        }
        user_operation_record.delay(operation_record)

        if self.data.subscription_id:
            return self._run_subscription_task("START")
        return True

    def _itsm_start_judge(self):
        if not self.data.itsm_has_success() and FeatureToggleObject.switch(name=FEATURE_COLLECTOR_ITSM):
            raise CollectNotSuccessNotCanStart

    @transaction.atomic
    def stop(self):
        """
        停止采集配置
        :return: task_id
        """
        self.data.is_active = False
        self.data.save()

        # 停止采集项
        if self.data.index_set_id:
            index_set_handler = IndexSetHandler(self.data.index_set_id)
            index_set_handler.stop()

        if self.data.subscription_id:
            # 停止节点管理订阅功能
            NodeApi.switch_subscription({"subscription_id": self.data.subscription_id, "action": "disable"})

        # 存在RT则停止RT
        if self.data.table_id:
            _, table_id = self.data.table_id.split(".")  # pylint: disable=unused-variable
            etl_storage = EtlStorage.get_instance(self.data.etl_config)
            etl_storage.switch_result_table(collector_config=self.data, is_enable=False)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.data.bk_biz_id,
            "record_type": UserOperationTypeEnum.COLLECTOR,
            "record_object_id": self.data.collector_config_id,
            "action": UserOperationActionEnum.STOP,
            "params": "",
        }
        user_operation_record.delay(operation_record)

        if self.data.subscription_id:
            return self._run_subscription_task("STOP")
        return True

    def tail(self):
        if not self.data.bk_data_id:
            raise CollectorConfigDataIdNotExistException()
        data_result = TransferApi.get_data_id({"bk_data_id": self.data.bk_data_id})
        params = {
            "server": settings.DEFAULT_KAFKA_HOST or data_result["mq_config"]["cluster_config"]["domain_name"],
            "port": data_result["mq_config"]["cluster_config"]["port"],
            "topic": data_result["mq_config"]["storage_config"]["topic"],
            "username": data_result["mq_config"]["auth_info"]["username"],
            "password": data_result["mq_config"]["auth_info"]["password"],
        }

        message_data = KafkaConsumerHandle(**params).get_latest_log()
        return_data = []
        for _message in message_data:

            # 数据预览
            etl_message = copy.deepcopy(_message)
            data_items = etl_message.get("items")
            if data_items:
                etl_message.update(
                    {
                        "data": data_items[0]["data"],
                        "log": data_items[0]["data"],
                        "iterationindex": data_items[0]["iterationindex"],
                        "batch": [_item["data"] for _item in data_items],
                    }
                )
            else:
                etl_message.update({"data": "", "iterationindex": "", "bathc": []})

            return_data.append({"etl": etl_message, "origin": _message})
        return return_data

    def retry_target_nodes(self, target_nodes):
        """
        重试部分实例或主机
        :return: task_id
        """
        res = self._run_subscription_task("START", target_nodes)

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": self.data.bk_biz_id,
            "record_type": UserOperationTypeEnum.COLLECTOR,
            "record_object_id": self.data.collector_config_id,
            "action": UserOperationActionEnum.RETRY,
            "params": {"target_nodes": target_nodes},
        }
        user_operation_record.delay(operation_record)

        return res

    def _run_subscription_task(self, action=None, nodes=None):
        """
        触发订阅事件
        :param: action 动作 [START, STOP, INSTALL, UNINSTALL]
        :param: nodes 需要重试的实例
        :return: task_id 任务ID
        """
        collector_scenario = CollectorScenario.get_instance(collector_scenario_id=self.data.collector_scenario_id)
        params = {"subscription_id": self.data.subscription_id}
        if action:
            params.update({"actions": {collector_scenario.PLUGIN_NAME: action}})

        # 无nodes时，节点管理默认对全部已配置的nodes进行操作
        # 有nodes时，对指定nodes进行操作，可用于重试的场景
        if nodes:
            params["scope"] = {"node_type": TargetNodeTypeEnum.INSTANCE.value, "nodes": nodes}

        task_id = str(NodeApi.run_subscription_task(params)["task_id"])

        # 对指定nodes进行重试，合并任务
        if nodes is not None:
            self.data.task_id_list.append(task_id)
        else:
            self.data.task_id_list = [str(task_id)]
        self.data.save()
        return self.data.task_id_list

    def _delete_subscription(self):
        """
        删除订阅事件
        :return: [dict]
        {
            "message": "",
            "code": "OK",
            "data": null,
            "result": true
        }
        """
        if not self.data.subscription_id:
            return
        subscription_params = {"subscription_id": self.data.subscription_id}
        return NodeApi.delete_subscription(subscription_params)

    def diff_target_nodes(self, target_nodes: list) -> list:
        """
        比较订阅节点的变化
        :param target_nodes 目标节点
        :return
        [
            {
                'type': 'add',
                'bk_inst_id': 2,
                'bk_obj_id': 'biz'
            },
            {
                'type': 'add',
                'bk_inst_id': 3,
                'bk_obj_id': 'module'
            },
            {
                'type': 'delete',
                'bk_inst_id': 4,
                'bk_obj_id': 'set'
            },
            {
                'type': 'modify',
                'bk_inst_id': 5,
                'bk_obj_id': 'module'
            }
        ]
        """

        def genera_nodes_tuples(nodes):
            return [
                (node["bk_inst_id"], node["bk_obj_id"]) for node in nodes if "bk_inst_id" in node or "bk_obj_id" in node
            ]

        current_nodes_tuples = genera_nodes_tuples(self.data.target_nodes)
        target_nodes_tuples = genera_nodes_tuples(target_nodes)
        add_nodes = [
            {"type": "add", "bk_inst_id": node[0], "bk_obj_id": node[1]}
            for node in set(target_nodes_tuples) - set(current_nodes_tuples)
        ]
        delete_nodes = [
            {"type": "delete", "bk_inst_id": node[0], "bk_obj_id": node[1]}
            for node in set(current_nodes_tuples) - set(target_nodes_tuples)
        ]
        return add_nodes + delete_nodes

    def get_subscription_task_status(self, task_id_list):
        """
        查询采集任务状态
        :param  [list] task_id_list:
        :return: [dict]
        {
            "contents": [
                {
                "is_label": true,
                "label_name": "modify",
                "bk_obj_name": "模块",
                "node_path": "蓝鲸_test1_配置平台_adminserver",
                "bk_obj_id": "module",
                "bk_inst_id": 33,
                "bk_inst_name": "adminserver",
                "child": [
                    {
                        "status": "FAILED",
                        "ip": "127.0.0.1",
                        "bk_cloud_id": 0,
                        "log": "[unifytlogc] 下发插件配置-重载插件进程",
                        "instance_id": "host|instance|host|127.0.0.1-0-0",
                        "instance_name": "127.0.0.1",
                        "task_id": 24516,
                        "bk_supplier_id": "0",
                        "create_time": "2019-09-17 19:23:02",
                        "steps": {1 item}
                        }
                    ]
                }
            ]
        }
        """
        if not self.data.subscription_id:
            self._update_or_create_subscription(
                collector_scenario=CollectorScenario.get_instance(
                    collector_scenario_id=self.data.collector_scenario_id
                ),
                params=self.data.params,
            )
        # 查询采集任务状态
        param = {
            "subscription_id": self.data.subscription_id,
        }
        if self.data.task_id_list:
            param["task_id_list"] = self.data.task_id_list

        task_ready = self._check_task_ready(param=param)

        # 如果任务未启动，则直接返回结果
        if not task_ready:
            return {"task_ready": task_ready, "contents": []}

        status_result = NodeApi.get_subscription_task_status(param)
        instance_status = self.format_task_instance_status(status_result)

        # 如果采集目标是HOST-INSTANCE
        if self.data.target_node_type == TargetNodeTypeEnum.INSTANCE.value:
            content_data = [
                {
                    "is_label": False,
                    "label_name": "",
                    "bk_obj_name": "主机",
                    "node_path": "主机",
                    "bk_obj_id": "host",
                    "bk_inst_id": "",
                    "bk_inst_name": "",
                    "child": instance_status,
                }
            ]
            return {"task_ready": task_ready, "contents": content_data}

        # 如果采集目标是HOST-TOPO
        # 获取target_nodes获取采集目标及差异节点target_subscription_diff合集
        node_collect = self._get_collect_node()
        node_mapping, template_mapping = self._get_mapping(node_collect=node_collect)
        content_data = list()
        target_mapping = self.get_target_mapping()
        total_host_result = self._get_host_result(node_collect)
        for node_obj in node_collect:
            map_key = "{}|{}".format(str(node_obj["bk_obj_id"]), str(node_obj["bk_inst_id"]))
            host_result = total_host_result.get(map_key, [])
            label_name = target_mapping.get(map_key, "")
            node_path, bk_obj_name, bk_inst_name = self._get_node_obj(
                node_obj=node_obj, template_mapping=template_mapping, node_mapping=node_mapping, map_key=map_key
            )

            content_obj = {
                "is_label": False if not label_name else True,
                "label_name": label_name,
                "bk_obj_name": bk_obj_name,
                "node_path": node_path,
                "bk_obj_id": node_obj["bk_obj_id"],
                "bk_inst_id": node_obj["bk_inst_id"],
                "bk_inst_name": bk_inst_name,
                "child": [],
            }

            for instance_obj in instance_status:

                # delete 标签如果订阅任务状态action不为UNINSTALL
                if label_name == "delete" and instance_obj["steps"].get(LogPluginInfo.NAME) != "UNINSTALL":
                    continue
                host_key = {"bk_host_innerip": instance_obj["ip"], "bk_cloud_id": instance_obj["bk_cloud_id"]}
                if host_key in host_result:
                    content_obj["child"].append(instance_obj)
            content_data.append(content_obj)
        return {"task_ready": task_ready, "contents": content_data}

    def _check_task_ready(self, param: dict):
        """
        查询任务是否下发: 兼容节点管理未发布的情况
        @param param {Dict} NodeApi.check_subscription_task_ready 请求
        """
        try:
            task_ready = NodeApi.check_subscription_task_ready(param)
        # 如果节点管理路由不存在或服务异常等request异常情况
        except BaseException as e:  # pylint: disable=broad-except
            task_ready = self._check_task_ready_exception(e)
        return task_ready

    def _get_collect_node(self):
        """
        获取target_nodes和target_subscription_diff集合之后组成的node_collect
        """
        node_collect = copy.deepcopy(self.data.target_nodes)
        for target_obj in self.data.target_subscription_diff:
            node_dic = {"bk_inst_id": target_obj["bk_inst_id"], "bk_obj_id": target_obj["bk_obj_id"]}
            if node_dic not in node_collect:
                node_collect.append(node_dic)
        return node_collect

    def _get_host_result(self, node_collect):
        """
        根据业务、节点查询主机
        node_collect {List} _get_collect_node处理后组成的node_collect
        """
        conditions = [
            {"bk_obj_id": node_obj["bk_obj_id"], "bk_inst_id": node_obj["bk_inst_id"]} for node_obj in node_collect
        ]
        host_result = BizHandler(self.data.bk_biz_id).search_host(conditions)
        host_result_dict = defaultdict(list)
        for host in host_result:
            for inst_id in host["parent_inst_id"]:
                key = "{}|{}".format(str(host["bk_obj_id"]), str(inst_id))
                host_result_dict[key].append(
                    {"bk_host_innerip": host["bk_host_innerip"], "bk_cloud_id": host["bk_cloud_id"]}
                )
        return host_result_dict

    def _get_mapping(self, node_collect):
        """
        查询业务TOPO，按采集目标节点进行分类
        node_collect {List} _get_collect_node处理后组成的node_collect
        """
        biz_topo = self._get_biz_topo()
        node_mapping = self.get_node_mapping(biz_topo)
        template_mapping = self._get_template_mapping(node_collect=node_collect)

        return node_mapping, template_mapping

    def _get_biz_topo(self):
        """
        查询业务TOPO，按采集目标节点进行分类
        """
        biz_topo = CCApi.search_biz_inst_topo({"bk_biz_id": self.data.bk_biz_id, "level": SEARCH_BIZ_INST_TOPO_LEVEL})
        try:
            internal_topo = self.get_biz_internal_module()
            if internal_topo:
                biz_topo[BIZ_TOPO_INDEX]["child"].insert(INTERNAL_TOPO_INDEX, internal_topo)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"call CCApi.search_biz_inst_topo error: {e}")
            pass
        return biz_topo

    def _get_template_mapping(self, node_collect):
        """
        获取模板dict
        @param node_collect {List} _get_collect_node处理后组成的node_collect
        """
        service_template_mapping = {}
        set_template_mapping = {}
        bk_boj_id_set = {node_obj["bk_obj_id"] for node_obj in node_collect}

        if TargetNodeTypeEnum.SERVICE_TEMPLATE.value in bk_boj_id_set:
            service_templates = CCApi.list_service_template.bulk_request({"bk_biz_id": self.data.bk_biz_id})
            service_template_mapping = {
                "{}|{}".format(TargetNodeTypeEnum.SERVICE_TEMPLATE.value, str(template.get("id", ""))): {
                    "name": template.get("name")
                }
                for template in service_templates
            }

        if TargetNodeTypeEnum.SET_TEMPLATE.value in bk_boj_id_set:
            set_templates = CCApi.list_set_template.bulk_request({"bk_biz_id": self.data.bk_biz_id})
            set_template_mapping = {
                "{}|{}".format(TargetNodeTypeEnum.SET_TEMPLATE.value, str(template.get("id", ""))): {
                    "name": template.get("name")
                }
                for template in set_templates
            }

        return {**service_template_mapping, **set_template_mapping}

    @classmethod
    def _get_node_obj(cls, node_obj, template_mapping, node_mapping, map_key):
        """
        获取node_path, bk_obj_name, bk_inst_name
        @param node_obj {dict} _get_collect_node处理后组成的node_collect对应元素
        @param template_mapping {dict} 模板集合
        @param node_mapping {dict} 拓扑节点集合
        @param map_key {str} 集合对应key
        """

        if node_obj["bk_obj_id"] in [
            TargetNodeTypeEnum.SET_TEMPLATE.value,
            TargetNodeTypeEnum.SERVICE_TEMPLATE.value,
        ]:
            node_path = template_mapping.get(map_key, {}).get("name", "")
            bk_obj_name = TargetNodeTypeEnum.get_choice_label(node_obj["bk_obj_id"])
            bk_inst_name = template_mapping.get(map_key, {}).get("name", "")
            return node_path, bk_obj_name, bk_inst_name

        node_path = "_".join(
            [node_mapping.get(node).get("bk_inst_name") for node in node_mapping.get(map_key, {}).get("node_link", [])]
        )
        bk_obj_name = node_mapping.get(map_key, {}).get("bk_obj_name", "")
        bk_inst_name = node_mapping.get(map_key, {}).get("bk_inst_name", "")

        return node_path, bk_obj_name, bk_inst_name

    @classmethod
    def _check_task_ready_exception(cls, error: BaseException):
        """
        处理task_ready_exception 返回error
        @param error {BaseException} 返回错误
        """
        task_ready = True
        if isinstance(error, ApiRequestError):
            return task_ready
        if isinstance(error, ApiResultError) and str(error.code) == CHECK_TASK_READY_NOTE_FOUND_EXCEPTION_CODE:
            return task_ready
        logger.error(f"Call NodeApi check_task_ready error: {error}")
        raise error

    def format_task_instance_status(self, instance_data):
        """
        格式化任务状态数据
        :param  [list] instance_data: 任务状态data数据
        :return: [list]
        """
        instance_list = list()
        host_list = list()
        latest_id = self.data.task_id_list[-1]
        if self.data.target_node_type == TargetNodeTypeEnum.INSTANCE.value:
            host_list = [(_node["ip"], _node["bk_cloud_id"]) for _node in self.data.target_nodes]

        for instance_obj in instance_data:
            bk_cloud_id = instance_obj["instance_info"]["host"]["bk_cloud_id"]
            if isinstance(bk_cloud_id, list):
                bk_cloud_id = bk_cloud_id[0]["bk_inst_id"]
            bk_host_innerip = instance_obj["instance_info"]["host"]["bk_host_innerip"]

            # 静态节点：排除订阅任务历史IP（不是最新订阅且不在当前节点范围的ip）
            if (
                self.data.target_node_type == TargetNodeTypeEnum.INSTANCE.value
                and str(instance_obj["task_id"]) != latest_id
                and (bk_host_innerip, bk_cloud_id) not in host_list
            ):
                continue
            instance_list.append(
                {
                    "status": instance_obj["status"],
                    "ip": bk_host_innerip,
                    "bk_cloud_id": bk_cloud_id,
                    "log": self.get_instance_log(instance_obj),
                    "instance_id": instance_obj["instance_id"],
                    "instance_name": bk_host_innerip,
                    "task_id": instance_obj.get("task_id", ""),
                    "bk_supplier_id": instance_obj["instance_info"]["host"].get("bk_supplier_account"),
                    "create_time": instance_obj["create_time"],
                    "steps": {i["id"]: i["action"] for i in instance_obj.get("steps", []) if i["action"]},
                }
            )
        return instance_list

    @staticmethod
    def get_instance_log(instance_obj):
        """
        获取采集实例日志
        :param  [dict] instance_obj: 实例状态日志
        :return: [string]
        """
        for step_obj in instance_obj.get("steps", []):
            if step_obj == CollectStatus.SUCCESS:
                continue
            for sub_step_obj in step_obj["target_hosts"][0]["sub_steps"]:
                if sub_step_obj["status"] != CollectStatus.SUCCESS:
                    return "{}-{}".format(step_obj["node_name"], sub_step_obj["node_name"])
        return ""

    def get_node_mapping(self, topo_tree):
        """
        节点映射关系
        :param  [list] topo_tree: 拓扑树
        :return: [dict]
        """
        node_mapping = {}

        def mapping(node, node_link, node_mapping):
            node.update(node_link=node_link)
            node_mapping[node_link[-1]] = node

        BizHandler().foreach_topo_tree(topo_tree, mapping, node_mapping=node_mapping)
        return node_mapping

    def get_target_mapping(self) -> dict:
        """
        节点和标签映射关系
        :return: [dict] {"module|33": "modify", "set|6": "add", "set|7": "delete"}
        """
        target_mapping = dict()
        for target in self.data.target_subscription_diff:
            key = "{}|{}".format(target["bk_obj_id"], target["bk_inst_id"])
            target_mapping[key] = target["type"]
        return target_mapping

    def get_subscription_task_detail(self, instance_id, task_id=None):
        """
        采集任务实例日志详情
        :param [string] instance_id: 实例ID
        :param [string] task_id: 任务ID
        :return: [dict]
        """
        # 详情接口查询，原始日志
        param = {"subscription_id": self.data.subscription_id, "instance_id": instance_id}
        if task_id:
            param["task_id"] = task_id
        detail_result = NodeApi.get_subscription_task_detail(param)

        # 日志详情，用于前端展示
        log = list()
        for step in detail_result.get("steps", []):
            log.append("{}{}{}\n".format("=" * 20, step["node_name"], "=" * 20))
            for sub_step in step["target_hosts"][0].get("sub_steps", []):
                log.extend(["{}{}{}".format("-" * 20, sub_step["node_name"], "-" * 20), sub_step["log"]])
                # 如果ex_data里面有值，则在日志里加上它
                if sub_step["ex_data"]:
                    log.append(sub_step["ex_data"])
                if sub_step["status"] != CollectStatus.SUCCESS:
                    return {"log_detail": "\n".join(log), "log_result": detail_result}
        return {"log_detail": "\n".join(log), "log_result": detail_result}

    def get_subscription_status_by_list(self, collector_id_list: list, multi_flag=False) -> list:
        """
        批量获取采集项订阅状态
        :param  [list] collector_id_list: 采集项ID列表
        :param [Boolean] multi_flag:是否使用并发
        :return: [dict]
        """
        return_data = list()
        subscription_id_list = list()
        subscription_collector_map = dict()

        collector_list = CollectorConfig.objects.filter(collector_config_id__in=collector_id_list).values(
            "collector_config_id", "subscription_id", "itsm_ticket_status"
        )
        status_result = {}
        if multi_flag:
            multi_execute_func = MultiExecuteFunc()
        for collector_obj in collector_list:

            # 若订阅ID未写入
            if not collector_obj["subscription_id"]:
                return_data.append(
                    {
                        "collector_id": collector_obj["collector_config_id"],
                        "subscription_id": None,
                        "status": CollectStatus.PREPARE,
                        "status_name": RunStatus.PREPARE,
                        "total": 0,
                        "success": 0,
                        "failed": 0,
                        "pending": 0,
                    }
                )
                continue

            # 订阅ID和采集配置ID的映射关系 & 需要查询订阅ID列表
            subscription_collector_map[collector_obj["subscription_id"]] = collector_obj["collector_config_id"]
            subscription_id_list.append(collector_obj["subscription_id"])
            if multi_flag:
                multi_execute_func.append(
                    collector_obj["collector_config_id"],
                    NodeApi.subscription_statistic,
                    params={
                        "subscription_id_list": [collector_obj["subscription_id"]],
                        "plugin_name": LogPluginInfo.NAME,
                    },
                )
            else:
                status_result[collector_obj["collector_config_id"]] = NodeApi.subscription_statistic(
                    params={
                        "subscription_id_list": [collector_obj["subscription_id"]],
                        "plugin_name": LogPluginInfo.NAME,
                    }
                )

        # 如果没有订阅ID，则直接返回
        if not subscription_id_list:
            return self._clean_terminated(return_data)

        # 并发查询所需的配置
        if multi_flag:
            status_result = multi_execute_func.run()
        # 接口查询到的数据进行处理
        subscription_status_data, subscription_id_list = self.format_subscription_status(
            status_result, subscription_id_list
        )
        return_data += subscription_status_data

        # 节点管理接口未查到相应订阅ID数据
        for subscription_id in subscription_id_list:
            collector_key = subscription_collector_map[subscription_id]
            return_data.append(
                {
                    "collector_id": collector_key,
                    "subscription_id": subscription_id,
                    "status": CollectStatus.FAILED,
                    "status_name": RunStatus.FAILED,
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "pending": 0,
                }
            )

        # 若采集项已停用，则采集状态修改为“已停用”
        return self._clean_terminated(return_data)

    def _clean_terminated(self, data: list):
        for _data in data:
            # RUNNING状态
            if _data["status"] == CollectStatus.RUNNING:
                continue

            _collector_config = CollectorConfig.objects.get(collector_config_id=_data["collector_id"])
            if not _collector_config.is_active:
                _data["status"] = CollectStatus.TERMINATED
                _data["status_name"] = RunStatus.TERMINATED
        return data

    def format_subscription_status(self, status_result, subscription_id_list):
        return_data = list()

        for collector_id, status_obj in status_result.items():
            if not status_obj:
                continue
            total_count = int(status_obj[0]["instances"])
            status_group = {
                status["status"]: int(status["count"]) for status in status_obj[0]["status"] if status["count"]
            }

            # status_group = array_group(self.format_subscription_instance_status(status_obj), "status")
            #
            # 订阅状态
            group_status_keys = status_group.keys()
            if not status_group:
                status = CollectStatus.UNKNOWN
                status_name = RunStatus.UNKNOWN
            elif CollectStatus.PENDING in group_status_keys or CollectStatus.RUNNING in group_status_keys:
                status = CollectStatus.RUNNING
                status_name = RunStatus.RUNNING
            elif CollectStatus.FAILED in group_status_keys and CollectStatus.SUCCESS in group_status_keys:
                status = CollectStatus.FAILED
                status_name = RunStatus.PARTFAILED
            elif CollectStatus.FAILED in group_status_keys and CollectStatus.SUCCESS not in group_status_keys:
                status = CollectStatus.FAILED
                status_name = RunStatus.FAILED
            elif CollectStatus.TERMINATED in group_status_keys and CollectStatus.SUCCESS not in group_status_keys:
                status = CollectStatus.TERMINATED
                status_name = RunStatus.TERMINATED
            else:
                status = CollectStatus.SUCCESS
                status_name = RunStatus.SUCCESS

            # 各订阅状态实例数量
            pending_count = status_group.get(CollectStatus.PENDING, 0) + status_group.get(CollectStatus.RUNNING, 0)
            failed_count = status_group.get(CollectStatus.FAILED, 0)
            success_count = status_group.get(CollectStatus.SUCCESS, 0)

            subscription_id_list.remove(status_obj[0]["subscription_id"])
            return_data.append(
                {
                    "collector_id": collector_id,
                    "subscription_id": status_obj[0]["subscription_id"],
                    "status": status,
                    "status_name": status_name,
                    "total": total_count,
                    "success": success_count,
                    "failed": failed_count,
                    "pending": pending_count,
                }
            )
        return return_data, subscription_id_list

    def get_subscription_status(self):
        """
        查看订阅的插件运行状态
        :return:
        """
        param = {"subscription_id_list": [self.data.subscription_id]}
        status_result = NodeApi.get_subscription_instance_status(param)
        instance_status = self.format_subscription_instance_status(status_result[0])

        # 如果采集目标是HOST-INSTANCE
        if self.data.target_node_type == TargetNodeTypeEnum.INSTANCE.value:
            content_data = [
                {
                    "is_label": False,
                    "label_name": "",
                    "bk_obj_name": "主机",
                    "node_path": "主机",
                    "bk_obj_id": "host",
                    "bk_inst_id": "",
                    "bk_inst_name": "",
                    "child": instance_status,
                }
            ]
            return {"contents": content_data}

        # 如果采集目标是HOST-TOPO
        # 从数据库target_nodes获取采集目标，查询业务TOPO，按采集目标节点进行分类
        target_nodes = self.data.target_nodes
        biz_topo = self._get_biz_topo()

        node_mapping = self.get_node_mapping(biz_topo)
        template_mapping = self._get_template_mapping(target_nodes)
        total_host_result = self._get_host_result(node_collect=target_nodes)

        content_data = list()
        for node_obj in target_nodes:
            map_key = "{}|{}".format(str(node_obj["bk_obj_id"]), str(node_obj["bk_inst_id"]))
            host_result = total_host_result.get(map_key, [])
            node_path, bk_obj_name, bk_inst_name = self._get_node_obj(
                node_obj=node_obj, template_mapping=template_mapping, node_mapping=node_mapping, map_key=map_key
            )
            content_obj = {
                "is_label": False,
                "label_name": "",
                "bk_obj_name": bk_obj_name,
                "node_path": node_path,
                "bk_obj_id": node_obj["bk_obj_id"],
                "bk_inst_id": node_obj["bk_inst_id"],
                "bk_inst_name": bk_inst_name,
                "child": [],
            }

            for instance_obj in instance_status:
                host_key = {"bk_host_innerip": instance_obj["ip"], "bk_cloud_id": instance_obj["bk_cloud_id"]}
                if host_key in host_result:
                    content_obj["child"].append(instance_obj)
            content_data.append(content_obj)
        return {"contents": content_data}

    @staticmethod
    def format_subscription_instance_status(instance_data):
        """
        对订阅状态数据按照实例运行状态进行归类
        :param [dict] instance_data:
        :return: [dict]
        """
        instance_list = list()
        for instance_obj in instance_data.get("instances", []):
            # 日志采集暂时只支持本地采集
            host_statuses = (instance_obj.get("host_statuses") or [{}])[0]
            host_status = host_statuses.get("status", CollectStatus.FAILED)

            status = CollectStatus.FAILED
            status_name = RunStatus.FAILED
            if instance_obj["status"] in [CollectStatus.PENDING, CollectStatus.RUNNING]:
                status = CollectStatus.RUNNING
                status_name = RunStatus.RUNNING
            elif instance_obj["status"] == CollectStatus.FAILED:
                status = CollectStatus.FAILED
                status_name = RunStatus.FAILED
            else:
                if host_status == CollectStatus.RUNNING:
                    status = CollectStatus.SUCCESS
                    status_name = RunStatus.SUCCESS
                elif host_status == CollectStatus.UNKNOWN:
                    status = CollectStatus.FAILED
                    status_name = RunStatus.FAILED
                elif host_status == CollectStatus.TERMINATED:
                    status = CollectStatus.TERMINATED
                    status_name = RunStatus.TERMINATED

            bk_cloud_id = instance_obj["instance_info"]["host"]["bk_cloud_id"]
            if isinstance(bk_cloud_id, list):
                bk_cloud_id = bk_cloud_id[0]["bk_inst_id"]

            status_obj = {
                "status": status,
                "status_name": status_name,
                "ip": instance_obj["instance_info"]["host"]["bk_host_innerip"],
                "bk_cloud_id": bk_cloud_id,
                "instance_id": instance_obj["instance_id"],
                "instance_name": instance_obj["instance_info"]["host"]["bk_host_innerip"],
                "plugin_name": host_statuses.get("name"),
                "plugin_version": host_statuses.get("version"),
                "bk_supplier_id": instance_obj["instance_info"]["host"].get("bk_supplier_account"),
                "create_time": instance_obj["create_time"],
            }
            instance_list.append(status_obj)

        return instance_list

    @staticmethod
    def regex_debug(data):
        """
        行首正则调试，返回匹配行数
        """
        lines = data["log_sample"].split("\n")
        match_lines = 0
        for line in lines:
            try:
                if re.match(data["multiline_pattern"], line):
                    match_lines += 1
            except re.error as e:
                raise RegexInvalidException(RegexInvalidException.MESSAGE.format(error=e))
        if not match_lines:
            raise RegexMatchException
        data.update({"match_lines": match_lines})
        return data

    def get_biz_internal_module(self):
        internal_module = CCApi.get_biz_internal_module(
            {"bk_biz_id": self.data.bk_biz_id, "bk_supplier_account": BK_SUPPLIER_ACCOUNT}
        )
        internal_topo = {
            "host_count": 0,
            "default": 0,
            "bk_obj_name": _("集群"),
            "bk_obj_id": "set",
            "child": [
                {
                    "host_count": 0,
                    "default": _module.get("default", 0),
                    "bk_obj_name": _("模块"),
                    "bk_obj_id": "module",
                    "child": [],
                    "bk_inst_id": _module["bk_module_id"],
                    "bk_inst_name": _module["bk_module_name"],
                }
                for _module in internal_module.get("module", [])
            ],
            "bk_inst_id": internal_module["bk_set_id"],
            "bk_inst_name": internal_module["bk_set_name"],
        }
        return internal_topo

    def indices_info(self):
        result_table_id = self.data.table_id
        if not result_table_id:
            raise CollectNotSuccess
        result = EsRoute(scenario_id=Scenario.LOG, indices=result_table_id).cat_indices()
        return StorageHandler.sort_indices(result)

    def list_collectors_by_host(self, params):
        bk_biz_id = params.get("bk_biz_id")
        node_result = []
        try:
            node_result = NodeApi.query_host_subscriptions({**params, "source_type": "subscription"})
        except ApiRequestError as error:
            if NOT_FOUND_CODE in error.message:
                node_result = []

        subscription_ids = [ip_subscription["source_id"] for ip_subscription in node_result]
        collectors = CollectorConfig.objects.filter(
            subscription_id__in=subscription_ids, bk_biz_id=bk_biz_id, is_active=True, table_id__isnull=False
        )
        return [
            {
                "collector_config_id": collector.collector_config_id,
                "collector_config_name": collector.collector_config_name,
                "collector_scenario_id": collector.collector_scenario_id,
                "index_set_id": collector.index_set_id,
                "description": collector.description,
            }
            for collector in collectors
        ]

    def cat_illegal_ips(self, params: dict):
        """
        当采集项对应节点为静态主机时判定是否有非法越权IP
        @param params {dict} 创建或者编辑采集项时的请求
        """
        # 这里是为了避免target_node_type, target_nodes参数为空的情况
        target_node_type = params.get("target_node_type")
        target_nodes = params.get("target_nodes", [])
        bk_biz_id = params["bk_biz_id"] if not self.data else self.data.bk_biz_id
        if target_node_type and target_node_type == TargetNodeTypeEnum.INSTANCE.value:
            illegal_ips = self._filter_illegal_ips(
                bk_biz_id=bk_biz_id,
                ip_list=[target_node["ip"] for target_node in target_nodes],
            )
            if illegal_ips:
                logger.error("cat illegal IPs: {illegal_ips}".format(illegal_ips=illegal_ips))
                raise CollectorIllegalIPException(
                    CollectorIllegalIPException.MESSAGE.format(bk_biz_id=bk_biz_id, illegal_ips=illegal_ips)
                )

    @classmethod
    def _filter_illegal_ips(cls, bk_biz_id: int, ip_list: list):
        """
        过滤出非法ip列表
        @param bk_biz_id [Int] 业务id
        @param ip_list [List] ip列表
        """
        legal_ip_list = CCApi.list_biz_hosts.bulk_request(
            {
                "bk_biz_id": bk_biz_id,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [{"field": "bk_host_innerip", "operator": "in", "value": [host for host in ip_list]}],
                },
                "fields": CMDB_HOST_SEARCH_FIELDS,
            }
        )

        legal_ip_set = {legal_ip["bk_host_innerip"] for legal_ip in legal_ip_list}

        return [ip for ip in ip_list if ip not in legal_ip_set]

    def get_clean_stash(self):
        clean_stash = CleanStash.objects.filter(collector_config_id=self.collector_config_id).first()
        if not clean_stash:
            return None
        return model_to_dict(CleanStash.objects.filter(collector_config_id=self.collector_config_id).first())

    def create_clean_stash(self, params: dict):
        model_fields = {
            "clean_type": params["clean_type"],
            "etl_params": params["etl_params"],
            "etl_fields": params["etl_fields"],
            "collector_config_id": int(self.collector_config_id),
            "bk_biz_id": params["bk_biz_id"],
        }
        CleanStash.objects.filter(collector_config_id=self.collector_config_id).delete()
        logger.info("delete clean stash {}".format(self.collector_config_id))
        return model_to_dict(CleanStash.objects.create(**model_fields))
