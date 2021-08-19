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

from apps.api import TransferApi
from apps.log_databus.exceptions import (
    DataLinkConfigNotExistException,
    StorageNotExistException,
    SameLinkNameException,
    EditLinkException,
)
from apps.log_databus.models import DataLinkConfig
from apps.log_databus.constants import KAFKA_CLUSTER_TYPE, STORAGE_CLUSTER_TYPE, REGISTERED_SYSTEM_DEFAULT


class DataLinkHandler(object):
    def __init__(self, data_link_id=None):
        self.data_link_id = data_link_id
        self.data = None
        if data_link_id:
            try:
                self.data = DataLinkConfig.objects.get(data_link_id=self.data_link_id)
            except DataLinkConfig.DoesNotExist:
                raise DataLinkConfigNotExistException()

    @staticmethod
    def list(param):
        """
        获取所有链路信息
        """
        link_objects = DataLinkConfig.objects.all()
        if param.get("bk_biz_id"):
            link_objects = link_objects.filter(bk_biz_id__in=[0, param["bk_biz_id"]])
        response = [
            {
                "data_link_id": link.data_link_id,
                "link_group_name": link.link_group_name,
                "bk_biz_id": link.bk_biz_id,
                "kafka_cluster_id": link.kafka_cluster_id,
                "transfer_cluster_id": link.transfer_cluster_id,
                "es_cluster_ids": link.es_cluster_ids,
                "is_active": link.is_active,
                "description": link.description,
            }
            for link in link_objects
        ]
        return response

    def retrieve(self):
        """
        获取单个链路信息
        """
        link = self.data
        response = {
            "data_link_id": link.data_link_id,
            "link_group_name": link.link_group_name,
            "bk_biz_id": link.bk_biz_id,
            "kafka_cluster_id": link.kafka_cluster_id,
            "transfer_cluster_id": link.transfer_cluster_id,
            "es_cluster_ids": link.es_cluster_ids,
            "is_active": link.is_active,
            "description": link.description,
        }
        return response

    def update_or_create(self, params: dict) -> dict:
        """
        创建/修改链路配置
        """
        link_group_name = params["link_group_name"]
        bk_biz_id = int(params["bk_biz_id"]) if params["bk_biz_id"] != "" else 0
        kafka_cluster_id = params["kafka_cluster_id"]
        transfer_cluster_id = params["transfer_cluster_id"]
        es_cluster_ids = params["es_cluster_ids"]
        is_active = params["is_active"]
        description = params["description"]

        model_fields = {
            "link_group_name": link_group_name,
            "bk_biz_id": bk_biz_id,
            "kafka_cluster_id": kafka_cluster_id,
            "transfer_cluster_id": transfer_cluster_id,
            "es_cluster_ids": es_cluster_ids,
            "is_active": is_active,
            "description": description,
        }
        if not self.data:
            if DataLinkConfig.objects.filter(link_group_name=link_group_name).exists():
                raise SameLinkNameException
            self.data = DataLinkConfig.objects.create(**model_fields)
        else:
            if (
                model_fields["kafka_cluster_id"] != self.data.kafka_cluster_id
                or model_fields["transfer_cluster_id"] != self.data.transfer_cluster_id
                or not set(es_cluster_ids) >= set(self.data.es_cluster_ids)
            ):
                raise EditLinkException
            if (
                DataLinkConfig.objects.filter(link_group_name=link_group_name)
                .exclude(link_group_name=self.data.link_group_name)
                .exists()
            ):
                raise SameLinkNameException
            for key, value in model_fields.items():
                setattr(self.data, key, value)
            self.data.save()
        model_fields.update({"data_link_id": self.data.data_link_id})

        # todo 链路创建
        response = model_fields
        return response

    def destroy(self):
        """
        删除链路配置
        """
        self.data.delete()
        return True

    @staticmethod
    def get_cluster_list(cluster_type):
        """
        获取各个集群列表
        """
        if cluster_type == "transfer":
            cluster_res = TransferApi.list_transfer_cluster()
            cluster_record = set()
            res = []
            for cluster in cluster_res:
                cluster_id = cluster.get("cluster_id", "")
                if cluster_id not in cluster_record:
                    res.append(
                        {
                            "cluster_id": cluster_id,
                            "cluster_name": cluster_id,
                            "domain_name": cluster.get("domain_name", ""),
                            "port": cluster.get("port", ""),
                        }
                    )
                    cluster_record.add(cluster_id)
            return res
        if cluster_type == "kafka":
            cluster_param = KAFKA_CLUSTER_TYPE
        elif cluster_type == "es":
            cluster_param = STORAGE_CLUSTER_TYPE
        else:
            raise StorageNotExistException()

        cluster_res = TransferApi.get_cluster_info({"cluster_type": cluster_param})

        # 仅过滤公共集群
        res = [
            {
                "cluster_id": c["cluster_config"]["cluster_id"],
                "cluster_name": c["cluster_config"]["cluster_name"],
                "domain_name": c["cluster_config"]["domain_name"],
                "port": c["cluster_config"]["port"],
            }
            for c in cluster_res
            if c["cluster_config"].get("registered_system") == REGISTERED_SYSTEM_DEFAULT
        ]
        return res
