# -*- coding: utf-8 -*-
import logging
from typing import List

from django.db.transaction import atomic

from bkm_ipchooser.config import IP_CHOOSER_CC_ROOT_URL
from bkm_ipchooser.models import IPChooserConfig

logger = logging.getLogger("bkm_ipchooser")


class ConfigHandler:
    """用户配置处理器"""

    def __init__(self, username: str = None) -> None:
        self.username = username

    @staticmethod
    def get_global_settings() -> dict:
        return {"CC_ROOT_URL": IP_CHOOSER_CC_ROOT_URL}

    def batch_get(self, module_list: List[str] = None) -> dict:
        """批量获取用户配置"""
        user_config_obj = IPChooserConfig.objects.filter(username=self.username).first()
        if not user_config_obj:
            return {config_name: {} for config_name in module_list}
        if not module_list:
            return user_config_obj.config

        return {config_name: user_config_obj.config.get(config_name, {}) for config_name in module_list}

    @atomic
    def update(self, config: dict):
        """更新用户配置"""
        user_config_obj, is_created = IPChooserConfig.objects.get_or_create(
            username=self.username, defaults={"config": config}
        )
        if not is_created:
            user_config_obj.config.update(config)
            user_config_obj.save()

    @atomic
    def batch_delete(self, module_list: List[str] = None):
        """批量删除用户配置"""
        user_config_obj = IPChooserConfig.objects.filter(username=self.username).first()
        if not user_config_obj:
            return
        # 不传模块列表，删除整个用户配置
        if not module_list:
            user_config_obj.delete()
            return

        for config_name in module_list:
            user_config_obj.config.pop(config_name, None)
        # 如果用户配置为空，删除整个用户配置
        if not user_config_obj.config:
            user_config_obj.delete()
            return
        user_config_obj.save()
