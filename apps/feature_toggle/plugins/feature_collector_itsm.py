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
from django.conf import settings

from apps.utils.log import logger
from apps.feature_toggle.plugins.base import FeatureToggleBase


class FeatureCollectorITSM(FeatureToggleBase):
    def set_status(self, param: dict) -> dict:
        if param["status"] != "off":
            # 如果status是打开的情况则需要前往itsm获取相关参数
            from apps.log_databus.handlers.itsm import ItsmHandler

            try:
                itsm_service_id = ItsmHandler().get_log_itsm_service_id()
                settings.COLLECTOR_ITSM_SERVICE_ID = itsm_service_id
                logger.info(f"[BKLOG] itsm service id is {settings.COLLECTOR_ITSM_SERVICE_ID}")
            except Exception as e:  # pylint: disable=broad-except
                logger.exception("[BKLOG] get itsm service fail => %s", e)
                param["status"] = "off"

        return param
