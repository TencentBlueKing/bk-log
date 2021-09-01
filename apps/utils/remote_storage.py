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
import os
from abc import ABC, abstractmethod
from shutil import copyfile

from django.utils.http import urlencode

from apps.constants import RemoteStorageType
from apps.utils.cos import QcloudCos
from apps.utils.base_crypt import BaseCrypt
from bkstorages.backends.bkrepo import BKRepoStorage


class Storage(ABC):
    @abstractmethod
    def export_upload(self, *args, **kwargs):
        pass

    @abstractmethod
    def generate_download_url(self, *args, **kwargs):
        pass


class CosStorage(Storage):
    def __init__(
        self,
        qcloud_secret_id: str,
        qcloud_secret_key: str,
        qcloud_cos_region: str,
        qcloud_cos_bucket: str,
        expired: int,
    ):
        self.qcloud_cos = QcloudCos(
            qcloud_secret_id=qcloud_secret_id,
            qcloud_secret_key=qcloud_secret_key,
            qcloud_cos_region=qcloud_cos_region,
            qcloud_cos_bucket=qcloud_cos_bucket,
        )
        if expired:
            self.qcloud_cos.expired = expired

    def export_upload(self, file_path, file_name, **kwargs):
        return self.qcloud_cos.upload_file(file_path, file_name)

    def generate_download_url(self, file_name, **kwargs):
        return self.qcloud_cos.get_download_url(file_name)


class NfsStorage(Storage):
    def __init__(self, nfs_path):
        self.nfs_path = nfs_path

    def export_upload(self, file_path, file_name, **kwargs):
        target_file_dir = os.path.join(self.nfs_path, file_name)
        copyfile(file_path, target_file_dir)

    def generate_download_url(self, url_path: str, file_name: str, **kwargs):
        url_params = {"target_file": BaseCrypt().encrypt(file_name.encode())}
        url_params = urlencode(url_params)
        return f"{url_path}?{url_params}"


class BKREPOStorage(Storage):
    def __init__(self, expired: int):
        self.bk_repo_storage = BKRepoStorage()
        self.expired = expired

    def export_upload(self, file_path, file_name, **kwargs):
        self.bk_repo_storage.client.upload_file(filepath=file_path, key=file_name)

    def generate_download_url(self, url_path: str, file_name: str, **kwargs):
        full_path = os.path.join(url_path, file_name)
        return self.bk_repo_storage.client.generate_presigned_url(key=full_path, expires_in=self.expired)


class StorageType(object):
    @classmethod
    def get_instance(cls, storage_type=None):
        mapping = {
            RemoteStorageType.COS.value: CosStorage,
            RemoteStorageType.NFS.value: NfsStorage,
            RemoteStorageType.BKREPO.value: BKREPOStorage,
        }
        return mapping.get(storage_type, NfsStorage)
