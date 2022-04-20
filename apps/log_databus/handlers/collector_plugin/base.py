import logging
from typing import Union

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils.module_loading import import_string

from apps.constants import UserOperationActionEnum, UserOperationTypeEnum
from apps.decorators import user_operation_record
from apps.log_databus.constants import ETLProcessorChoices, META_DATA_ENCODING
from apps.log_databus.exceptions import (
    CollectorConfigNotExistException,
    CollectorPluginNameDuplicateException,
    CollectorPluginNotExistException,
)
from apps.log_databus.handlers.collector import CollectorHandler
from apps.log_databus.handlers.collector_scenario import CollectorScenario
from apps.log_databus.models import CollectorConfig, CollectorPlugin, DataLinkConfig
from apps.log_search.constants import CollectorScenarioEnum
from apps.models import model_to_dict
from apps.utils.local import get_request_username

logger = logging.getLogger("app")


def get_collector_plugin_handler(etl_processor, collector_plugin_id=None, collector_config_id=None):
    mapping = {
        ETLProcessorChoices.BKBASE.value: "BKBaseCollectorPluginHandler",
        ETLProcessorChoices.TRANSFER.value: "TransferCollectorPluginHandler",
    }
    try:
        collector_plugin_handler = import_string(
            "apps.log_databus.handlers.collector_plugin.{}.{}".format(etl_processor, mapping.get(etl_processor))
        )
        return collector_plugin_handler(collector_plugin_id, collector_config_id)
    except ImportError as error:
        raise NotImplementedError(f"CollectorPluginHandler of {etl_processor} not implement, error: {error}")


class CollectorPluginHandler:
    collector_plugin: CollectorPlugin = None
    collector_config: CollectorConfig = None

    def __init__(self, collector_plugin_id=None, collector_config_id=None):
        if collector_plugin_id:
            self._get_collector_plugin(collector_plugin_id)
        if collector_config_id:
            self._get_collector_config(collector_config_id)

    def _get_collector_plugin(self, collector_plugin_id: int) -> None:
        """绑定采集插件Model"""
        self.collector_plugin_id = collector_plugin_id
        try:
            self.collector_plugin: CollectorPlugin = CollectorPlugin.objects.get(
                collector_plugin_id=collector_plugin_id
            )
        except CollectorPlugin.DoesNotExist:
            raise CollectorPluginNotExistException()

    def _get_collector_config(self, collector_config_id: int) -> None:
        """绑定采集项Model"""
        self.collector_config_id = collector_config_id
        try:
            self.collector_config: CollectorConfig = CollectorConfig.objects.get(
                collector_config_id=collector_config_id
            )
        except CollectorConfig.DoesNotExist:
            raise CollectorConfigNotExistException()

    def _create_operation_log(
        self,
        action: str,
        bk_biz_id: int,
        record_type: str,
        obj: Union[CollectorPlugin, CollectorConfig],
    ) -> None:
        """记录用户操作"""
        user_operation_record.delay(
            {
                "username": get_request_username(),
                "biz_id": bk_biz_id,
                "record_type": record_type,
                "record_object_id": obj.pk,
                "action": action,
                "params": model_to_dict(obj, exclude=["deleted_at", "created_at", "updated_at"]),
            }
        )

    def _create_collector_plugin_operation_log(self, action: str) -> None:
        """记录用户对采集插件操作"""
        self._create_operation_log(
            action,
            self.collector_plugin.bk_biz_id,
            UserOperationTypeEnum.COLLECTOR_PLUGIN.value,
            self.collector_plugin,
        )

    def _create_collector_config_operation_log(self, action: str) -> None:
        """记录用户对采集项操作"""
        self._create_operation_log(
            action,
            self.collector_config.bk_biz_id,
            UserOperationTypeEnum.COLLECTOR.value,
            self.collector_config,
        )

    def _create_data_id(self) -> int:
        """创建DATAID"""
        collector_scenario = CollectorScenario.get_instance(CollectorScenarioEnum.CUSTOM.value)
        bk_data_id = collector_scenario.update_or_create_data_id(
            bk_data_id=self.collector_plugin.bk_data_id,
            data_link_id=self.collector_plugin.data_link_id,
            data_name="{bk_biz_id}_{table_id_prefix}_{name}".format(
                bk_biz_id=self.collector_plugin.bk_biz_id,
                table_id_prefix=settings.TABLE_ID_PREFIX,
                name=self.collector_plugin.collector_plugin_name_en,
            ),
            description=self.collector_plugin.description,
            encoding=META_DATA_ENCODING,
        )
        return bk_data_id

    def _build_plugin_etl_template(self, params: dict) -> dict:
        raise NotImplementedError

    def _pre_check_en_name(self, en_name: str) -> None:
        # 校验英文名称，不能与插件或实例的名字重复
        config_name_duplicate = CollectorConfig.objects.filter(collector_config_name_en=en_name).exists()
        plugin_name_duplicate = CollectorPlugin.objects.filter(collector_plugin_name_en=en_name).exists()
        if config_name_duplicate or plugin_name_duplicate:
            raise CollectorPluginNameDuplicateException()

    @transaction.atomic()
    def _create(self, params: dict) -> None:
        """
        创建采集插件
        1. 创建采集插件
        2. 根据需要初始化 data id & 数据链路
        3. 根据需要创建清洗规则
        4. 根据需要创建存储集群
        """
        # 必须的参数
        model_fields = {
            "bk_biz_id": params["bk_biz_id"],
            "collector_plugin_name": params["collector_plugin_name"],
            "collector_plugin_name_en": params["collector_plugin_name_en"],
            "description": params["description"],
            "is_enabled_display_collector": params["is_enabled_display_collector"],
            "is_allow_alone_data_id": params["is_allow_alone_data_id"],
            "is_allow_alone_etl_config": params["is_allow_alone_etl_config"],
            "is_allow_alone_storage": params["is_allow_alone_storage"],
            "etl_processor": params["etl_processor"],
            "params": params.get("params", {}),
            "data_link_id": params.get("data_link_id"),
        }

        # 校验英文名
        self._pre_check_en_name(params["collector_plugin_name_en"])

        # 创建采集插件
        try:
            self.collector_plugin = CollectorPlugin.objects.create(**model_fields)
        except IntegrityError:
            logger.warning(f"collector plugin name duplicate => [{params.get('collector_plugin_name')}]")
            raise CollectorPluginNameDuplicateException()

        # 创建 DATA_ID
        if not params["is_allow_alone_data_id"] or params.get("create_public_data_id", False):
            # 绑定链路
            if not self.collector_plugin.data_link_id:
                data_links = DataLinkConfig.objects.filter(bk_biz_id__in=[0, self.collector_plugin.bk_biz_id]).order_by(
                    "data_link_id"
                )
                if data_links.exists():
                    self.collector_plugin.data_link_id = data_links.first().data_link_id
            # 创建 DATA ID
            self.collector_plugin.bk_data_id = self._create_data_id()
            # 指定结果表
            self.collector_plugin.table_id = self.collector_plugin.collector_plugin_name_en

        # 存储集群
        if not params["is_allow_alone_storage"] or self.collector_plugin.bk_data_id:
            self.collector_plugin.storage_cluster_id = params["storage_cluster_id"]
            self.collector_plugin.retention = params["retention"]
            self.collector_plugin.allocation_min_days = params["allocation_min_days"]
            self.collector_plugin.storage_replies = params["storage_replies"]

        # 清洗规则
        if not params["is_allow_alone_etl_config"] or self.collector_plugin.bk_data_id:
            self.collector_plugin.etl_config = params["etl_config"]
            self.collector_plugin.etl_template = self._build_plugin_etl_template(params)

        self.collector_plugin.save()

    def create(self, params: dict) -> dict:
        """
        创建采集插件
        :return:
        {
            "collector_plugin_id": 1,
            "collector_plugin_name": "采集插件名称"
        }
        """
        # create plugin
        self._create(params)

        # add user_operation_record
        self._create_collector_plugin_operation_log(UserOperationActionEnum.CREATE.value)

        return {
            "collector_plugin_id": self.collector_plugin.collector_plugin_id,
            "collector_plugin_name": self.collector_plugin.collector_plugin_name,
        }

    def _build_create_instance_params(self, params: dict) -> dict:
        """
        构造创建必须的参数
        """
        # 采集场景
        params["collector_scenario_id"] = CollectorScenarioEnum.CUSTOM.value
        # 是否展示采集项
        params["is_display"] = self.collector_plugin.is_enabled_display_collector
        # 不允许独立DATAID
        if not self.collector_plugin.is_allow_alone_data_id:
            params["bk_data_id"] = self.collector_plugin.bk_data_id
            params["data_link_id"] = self.collector_plugin.data_link_id
            params["table_id"] = self.collector_plugin.table_id
        # 不允许独立清洗配置
        if not self.collector_plugin.is_allow_alone_etl_config:
            params["etl_processor"] = self.collector_plugin.etl_processor
            params["etl_config"] = self.collector_plugin.etl_config
        # 不允许独立存储
        if not self.collector_plugin.is_allow_alone_storage:
            params["storage_cluster_id"] = self.collector_plugin.storage_cluster_id
            params["retention"] = self.collector_plugin.retention
            params["allocation_min_days"] = self.collector_plugin.allocation_min_days
            params["storage_replies"] = self.collector_plugin.storage_replies
        return params

    def _create_instance_etl_storage(self, params: dict):
        """
        创建清洗入库
        """
        raise NotImplementedError

    @transaction.atomic()
    def create_instance(self, params: dict) -> dict:
        """
        实例化采集插件
        :return:
        {
            "collector_config_id": 1,
            "collector_config_name": "采集插件名称"
        }
        """
        # 获取插件
        self._get_collector_plugin(params["collector_plugin_id"])

        # 校验英文名
        self._pre_check_en_name(params["collector_config_name_en"])

        # 构造基本参数
        collector_config_params = self._build_create_instance_params(params)

        # 创建采集项
        collector_config = CollectorHandler().update_or_create(collector_config_params)
        self._get_collector_config(collector_config["collector_config_id"])

        # 创建清洗入库
        self._create_instance_etl_storage(params)

        return collector_config
