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
from apps.constants import UserOperationTypeEnum, UserOperationActionEnum
from apps.log_extract.exceptions import TaskNotHaveExtractLink
from apps.log_extract.models import ExtractLink, Tasks, ExtractLinkHost
from apps.log_extract import exceptions, constants
from apps.utils.local import get_request_username
from apps.decorators import user_operation_record


class LinkHandler(object):
    def __init__(self, link_id=None):
        self.link_id = link_id
        if link_id:
            try:
                self.data = ExtractLink.objects.get(link_id=self.link_id)
            except ExtractLink.DoesNotExist:
                raise exceptions.ExtractLinkDoesNotExistException
        else:
            self.data = None

    def list(self):
        all_extract_links = ExtractLink.objects.filter(is_enable=True).all()
        if not all_extract_links.exists():
            raise TaskNotHaveExtractLink()
        return [{"link_id": link.link_id, "show_name": link.name} for link in all_extract_links]

    def retrieve(self):
        extract_link_hosts = self.data.extractlinkhost_set.all()
        link_hosts = {
            "link_id": self.data.link_id,
            "name": self.data.name,
            "link_type": self.data.link_type,
            "operator": self.data.operator,
            "op_bk_biz_id": self.data.op_bk_biz_id,
            "qcloud_secret_id": self.data.qcloud_secret_id,
            "qcloud_secret_key": self.data.qcloud_secret_key,
            "qcloud_cos_bucket": self.data.qcloud_cos_bucket,
            "qcloud_cos_region": self.data.qcloud_cos_region,
            "is_enable": self.data.is_enable,
            "hosts": [
                {
                    "target_dir": host.target_dir,
                    "bk_cloud_id": host.bk_cloud_id,
                    "ip": host.ip,
                }
                for host in extract_link_hosts
            ],
        }
        return link_hosts

    def create_or_update(
        self,
        name,
        link_type,
        operator,
        op_bk_biz_id,
        qcloud_secret_id,
        qcloud_secret_key,
        qcloud_cos_bucket,
        qcloud_cos_region,
        is_enable,
        hosts,
    ):
        is_add = False if self.data else True

        is_extract_link_name_existed = ExtractLink.objects.filter(name=name)

        # 当前是策略更新请求
        if self.link_id:
            is_extract_link_name_existed = is_extract_link_name_existed.exclude(link_id=self.link_id)

        if is_extract_link_name_existed:
            raise exceptions.ExtractLinkExistedException(exceptions.ExtractLinkExistedException.MESSAGE.format(name))

        if self.data:
            if (
                Tasks.objects.filter(link_id=self.data.link_id)
                .exclude(
                    download_status__in=[
                        constants.DownloadStatus.EXPIRED.value,
                        constants.DownloadStatus.FAILED.value,
                    ]
                )
                .exists()
            ):
                raise exceptions.ExtractLinkCannotModifyException
            self.data.name = name
            self.data.link_type = link_type
            self.data.operator = operator
            self.data.op_bk_biz_id = op_bk_biz_id
            self.data.qcloud_secret_id = qcloud_secret_id
            self.data.qcloud_secret_key = qcloud_secret_key
            self.data.qcloud_cos_bucket = qcloud_cos_bucket
            self.data.qcloud_cos_region = qcloud_cos_region
            self.data.is_enable = is_enable
            self.data.save()
            ExtractLinkHost.objects.filter(link=self.data).delete()
        else:
            params = {
                "name": name,
                "link_type": link_type,
                "operator": operator,
                "op_bk_biz_id": op_bk_biz_id,
                "qcloud_secret_id": qcloud_secret_id,
                "qcloud_secret_key": qcloud_secret_key,
                "qcloud_cos_bucket": qcloud_cos_bucket,
                "qcloud_cos_region": qcloud_cos_region,
                "is_enable": is_enable,
            }
            self.data = ExtractLink.objects.create(**params)

        ExtractLinkHost.objects.bulk_create(
            [
                ExtractLinkHost(
                    target_dir=host["target_dir"], bk_cloud_id=host["bk_cloud_id"], ip=host["ip"], link=self.data
                )
                for host in hosts
            ]
        )

        # add user_operation_record
        operation_record = {
            "username": get_request_username(),
            "biz_id": op_bk_biz_id,
            "record_type": UserOperationTypeEnum.LOG_EXTRACT_LINKS,
            "record_object_id": self.data.link_id,
            "action": UserOperationActionEnum.CREATE if is_add else UserOperationActionEnum.UPDATE,
            "params": {
                "name": name,
                "link_type": link_type,
                "operator": operator,
                "op_bk_biz_id": op_bk_biz_id,
                "qcloud_secret_id": qcloud_secret_id,
                "qcloud_secret_key": qcloud_secret_key,
                "qcloud_cos_bucket": qcloud_cos_bucket,
                "qcloud_cos_region": qcloud_cos_region,
                "is_enable": is_enable,
                "hosts": hosts,
            },
        }
        user_operation_record.delay(operation_record)

        return {"link_id": self.data.link_id}

    def destroy(self):
        if self.data:
            if (
                Tasks.objects.filter(link_id=self.data.link_id)
                .exclude(
                    download_status__in=[
                        constants.DownloadStatus.EXPIRED.value,
                        constants.DownloadStatus.FAILED.value,
                    ]
                )
                .exists()
            ):
                raise exceptions.ExtractLinkCannotModifyException
            biz_id = self.data.op_bk_biz_id
            link_id = self.data.link_id
            self.data.delete()

            # add user_operation_record
            operation_record = {
                "username": get_request_username(),
                "biz_id": biz_id,
                "record_type": UserOperationTypeEnum.LOG_EXTRACT_LINKS,
                "record_object_id": link_id,
                "action": UserOperationActionEnum.DESTROY,
                "params": "",
            }
            user_operation_record.delay(operation_record)

        return True
