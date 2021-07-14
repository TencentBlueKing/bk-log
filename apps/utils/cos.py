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

import typing

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from qcloud_cos import CosConfig, CosS3Client


class ConfigMap(typing.NamedTuple):
    target: str
    source: str
    error: str


class QcloudCos(object):
    CONFIG_MAP = [
        ConfigMap(target="qcloud_secret_id", source="QCLOUD_COS_SECRET_ID", error=_("请设置腾讯云cos SecretId")),
        ConfigMap(target="qcloud_secret_key", source="QCLOUD_COS_SECRET_KEY", error=_("请设置腾讯云cos SecretKey")),
        ConfigMap(target="qcloud_cos_region", source="QCLOUD_COS_REGION", error=_("请设置腾讯云cos 区域")),
        ConfigMap(target="qcloud_cos_bucket", source="QCLOUD_COS_BUCKET", error=_("请设置腾讯云cos 桶名称")),
    ]

    def __init__(self, qcloud_secret_id: str, qcloud_secret_key: str, qcloud_cos_region: str, qcloud_cos_bucket: str):
        self._init_config()
        self._qcloud_cos_region = qcloud_cos_region
        config = CosConfig(
            Region=qcloud_cos_region.strip().strip(),
            SecretId=qcloud_secret_id.strip(),
            SecretKey=qcloud_secret_key.strip().strip(),
        )
        self._qcloud_cos_bucket = qcloud_cos_bucket
        self._client = CosS3Client(config)

    def _init_config(self):
        self.expired = settings.EXTRACT_TRANSIT_EXPIRED

    def get_download_url(self, file_name: str) -> str:
        url: str = self._client.get_presigned_download_url(
            Bucket=self._qcloud_cos_bucket.strip(), Key=file_name, Expired=self.expired
        )
        if self._has_accelerate():
            return url.replace(f"cos.{self._qcloud_cos_region.strip()}.myqcloud.com", settings.EXTRACT_COS_DOMAIN)
        return url

    def upload_file(self, file_path: str, file_name: str):
        """
        从本地路径上传到到cos对应文件
        @param file_path 本地路径
        @param file_name 上传文件名
        """
        response = self._client.put_object_from_local_file(
            Bucket=self._qcloud_cos_bucket.strip(), LocalFilePath=file_path, Key=file_name
        )
        return response["ETag"]

    def _has_accelerate(self):
        return settings.EXTRACT_COS_DOMAIN is not None
