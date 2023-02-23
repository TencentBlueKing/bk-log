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

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from apps.api import TransferApi
from apps.log_databus.models import DataLinkConfig, CollectorConfig
from apps.log_databus.constants import KAFKA_CLUSTER_TYPE, STORAGE_CLUSTER_TYPE


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--es_cluster_id", type=int, nargs="*", help="elasticsearch cluster ids")
        parser.add_argument("--kafka_cluster_id", type=int, help="kafka cluster id")
        parser.add_argument("--transfer_cluster_id", type=str, help="transfer cluster id")

    def handle(self, **options):
        default_es_cluster_ids = options.get("es_cluster_id") or []
        default_kafka_cluster_id = options.get("kafka_cluster_id")
        transfer_cluster_id = options.get("transfer_cluster_id")

        if DataLinkConfig.objects.all().exists():
            print("[Init Default Data Link] DataLinkConfig item exist. SKIP.")
            return

        if not default_es_cluster_ids:
            es_clusters = TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True})
            for es in es_clusters:
                if es["cluster_config"]["is_default_cluster"]:
                    default_es_cluster_ids.append(es["cluster_config"]["cluster_id"])

        if not default_kafka_cluster_id:
            kafka_clusters = TransferApi.get_cluster_info({"cluster_type": KAFKA_CLUSTER_TYPE, "no_request": True})
            for kafka in kafka_clusters:
                if kafka["cluster_config"]["is_default_cluster"]:
                    default_kafka_cluster_id = kafka["cluster_config"]["cluster_id"]
                    break

        if not transfer_cluster_id:
            transfer_cluster_id = "default"

        print(
            "create data link config with: es_cluster_ids: {}, kafka_cluster_id: {}, transfer_cluster_id: {}".format(
                default_es_cluster_ids, default_kafka_cluster_id, transfer_cluster_id
            )
        )

        link = DataLinkConfig.objects.get_or_create(
            defaults={
                "bk_biz_id": 0,
                "kafka_cluster_id": default_kafka_cluster_id,
                "transfer_cluster_id": transfer_cluster_id,
                "es_cluster_ids": default_es_cluster_ids,
                "is_active": True,
                "description": _("默认数据链路"),
            },
            link_group_name="default",
            is_deleted=False,
        )

        # 将存量采集配置的切换至默认链路
        CollectorConfig.objects.filter(Q(data_link_id__isnull=True) | Q(data_link_id=0)).update(
            data_link_id=link[0].data_link_id
        )

        print("[Init Default Data Link] operate SUCCESS!")
