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
from abc import ABC, abstractmethod

from apps.feature_toggle.plugins.constants import ITSM_SERVICE_ID
from apps.utils.log import logger

FEATURE_TOGGLE = {}


def get_feature_toggle(name):
    return FEATURE_TOGGLE.get(name, FEATURE_TOGGLE.get("dummy"))


def register(target_class: "FeatureToggleBase"):
    FEATURE_TOGGLE[target_class.target] = target_class


class FeatureToggleBase(ABC):
    target = None

    @abstractmethod
    def set_status(self, param: dict) -> dict:
        """
        执行plugin决定是否修改当前数据值
        Args:
            param [Dict] 请求的param
        Returns:
            param: [Dict] 返回处理后的param
        """
        pass

    @abstractmethod
    def action(self):
        """
        trigger action if need at update config
        must try any exception
        """
        pass


@register
class DummyFeatureToggle(FeatureToggleBase):
    target = "dummy"

    def set_status(self, param: dict) -> dict:
        return param

    def action(self):
        pass


@register
class FeatureBKDataDataId(FeatureToggleBase):
    target = "feature_bkdata_dataid"

    def set_status(self, param):
        from apps.feature_toggle.handlers.toggle import FeatureToggleObject
        if param["status"] != "off" and not FeatureToggleObject.switch("scenario_bkdata"):
            param["status"] = "off"
        return param

    def action(self):
        pass


@register
class FeatureCollectorITSM(FeatureToggleBase):
    target = "collect_itsm"

    def set_status(self, param: dict) -> dict:
        if param["status"] != "off":
            # 如果status是打开的情况则需要前往itsm获取相关参数
            from apps.log_databus.handlers.itsm import ItsmHandler

            try:
                itsm_service_id = ItsmHandler().get_log_itsm_service_id()
                param["feature_config"] = {ITSM_SERVICE_ID: itsm_service_id}
                logger.info(f"[BKLOG] itsm service id is {itsm_service_id}")
            except Exception as e:  # pylint: disable=broad-except
                logger.exception("[BKLOG] get itsm service fail => %s", e)
                param["status"] = "off"

        return param

    def action(self):
        pass


@register
class BkLogTrace(FeatureToggleBase):
    target = "bk_log_trace"

    def set_status(self, param: dict) -> dict:
        return param

    def action(self):
        from apps.log_trace.trace import BluekingInstrumentor
        BluekingInstrumentor().instrument()