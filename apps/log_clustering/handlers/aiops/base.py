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
from dataclasses import asdict

from apps.log_clustering.constants import LATEST_PUBLISH_STATUS
from apps.log_clustering.handlers.aiops.aiops_model.data_cls import AiopsReleaseCls
from apps.utils.log import logger
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import BKDATA_CLUSTERING_TOGGLE
from apps.log_clustering.exceptions import ClusteringClosedException, ModelReleaseNotFoundException
from apps.api import BkDataAIOPSApi


class BaseAiopsHandler(object):
    def __init__(self):
        if not FeatureToggleObject.switch(BKDATA_CLUSTERING_TOGGLE):
            raise ClusteringClosedException()
        self.conf = FeatureToggleObject.toggle(BKDATA_CLUSTERING_TOGGLE).feature_config

    def _set_username(self, request_data_cls, bk_username: str = ""):
        if isinstance(request_data_cls, dict):
            request_dict = request_data_cls
        else:
            request_dict = asdict(request_data_cls)
        logger.info("request_dict=> {}".format(request_dict))
        if bk_username:
            request_dict["bk_username"] = bk_username
            return request_dict
        request_dict["bk_username"] = self.conf.get("bk_username")
        return request_dict

    def aiops_release(self, model_id: str):
        """
        备选模型列表
        @param model_id 模型id
        """
        aiops_release_request = AiopsReleaseCls(model_id=model_id, project_id=self.conf.get("project_id"))
        request_dict = self._set_username(aiops_release_request)
        return BkDataAIOPSApi.aiops_release(request_dict)

    def get_latest_released_id(self, model_id: str):
        """
        获取最新release_id
        """
        release_info = self.aiops_release(model_id=model_id).get("list", [])
        release_ids = [
            info["model_release_id"] for info in release_info if info.get("publish_status") == LATEST_PUBLISH_STATUS
        ]
        if not release_ids:
            raise ModelReleaseNotFoundException(ModelReleaseNotFoundException.MESSAGE.format(model_id=model_id))
        release_id, *_ = release_ids
        return release_id

    def transfer_fields_to_origin(self):
        pass
