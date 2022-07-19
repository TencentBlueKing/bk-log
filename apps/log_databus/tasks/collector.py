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
import datetime
from collections import defaultdict

import pytz

from celery.task import periodic_task, task
from celery.schedules import crontab

from apps.api.modules.bkdata_databus import BkDataDatabusApi
from apps.log_databus.models import CollectorConfig
from apps.log_databus.handlers.collector import CollectorHandler
from apps.api import TransferApi, BkLogApi
from apps.log_databus.constants import (
    STORAGE_CLUSTER_TYPE,
    REGISTERED_SYSTEM_DEFAULT,
    CollectItsmStatus,
)
from apps.feature_toggle.plugins.constants import FEATURE_BKDATA_DATAID
from apps.log_measure.handlers.elastic import ElasticHandle
from apps.utils.log import logger
from apps.log_databus.models import StorageUsed
from apps.feature_toggle.handlers.toggle import FeatureToggleObject


@task(ignore_result=True)
def shutdown_collector_warm_storage_config(cluster_id):
    """异步关闭冷热集群的采集项"""
    result_table_list = []
    for collector in CollectorConfig.objects.all():
        if not collector.table_id:
            continue
        result_table_list.append(collector.table_id)

    if not result_table_list:
        return

    cluster_infos = CollectorHandler.bulk_cluster_infos(result_table_list=result_table_list)
    for collector in CollectorConfig.objects.all():
        try:
            if not collector.table_id:
                continue
            cluster_info = cluster_infos.get(collector.table_id)
            if not cluster_info:
                continue
            if cluster_info["cluster_config"]["cluster_id"] != cluster_id:
                continue
            TransferApi.modify_result_table(
                {
                    "table_id": collector.table_id,
                    "default_storage": "elasticsearch",
                    "default_storage_config": {
                        "warm_phase_days": 0,
                    },
                }
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("refresh collector storage config error", e)
            continue


@periodic_task(run_every=crontab(minute="0", hour="1"))
def collector_status():
    """
    检测采集项：24小时未入库自动停止
    :return:
    """

    # 筛选24小时未入库的采集项
    day_ago = datetime.datetime.now(pytz.timezone("UTC")) - datetime.timedelta(days=1)
    collector_configs = CollectorConfig.objects.filter(table_id=None, is_active=True, created_at__lt=day_ago).exclude(
        itsm_ticket_status=CollectItsmStatus.APPLYING
    )
    # 停止采集项
    for _collector in collector_configs:
        if (
            FeatureToggleObject.switch(FEATURE_BKDATA_DATAID)
            and _collector.bkdata_data_id
            and BkDataDatabusApi.get_cleans(params={"raw_data_id": _collector.bkdata_data_id})
        ):
            continue
        CollectorHandler(collector_config_id=_collector.collector_config_id).stop()


@periodic_task(run_every=crontab(minute="0"))
def sync_storage_capacity():
    """
    每小时同步业务各集群已用容量
    :return:
    """

    # 1、获取已有采集项业务
    business_list = CollectorConfig.objects.all().values("bk_biz_id").distinct()

    # 2、获取所有集群
    params = {"cluster_type": STORAGE_CLUSTER_TYPE}
    cluster_obj = TransferApi.get_cluster_info(params)

    from apps.log_search.models import LogIndexSet

    cluster_biz_cnt_map = defaultdict(lambda: defaultdict(int))
    for index_set in LogIndexSet.objects.all():
        cluster_biz_cnt_map[index_set.storage_cluster_id][index_set.project_id] += 1

    for _cluster in cluster_obj:
        try:
            usage, total = get_storage_usage_and_all(_cluster["cluster_config"]["cluster_id"])

            index_count = LogIndexSet.objects.filter(
                storage_cluster_id=_cluster["cluster_config"]["cluster_id"]
            ).count()

            StorageUsed.objects.update_or_create(
                bk_biz_id=0,
                storage_cluster_id=_cluster["cluster_config"]["cluster_id"],
                defaults={
                    "storage_used": 0,
                    "storage_total": total,
                    "storage_usage": usage,
                    "index_count": index_count,
                    "biz_count": len(cluster_biz_cnt_map.get(_cluster["cluster_config"]["cluster_id"], {}).keys()),
                },
            )

            # 2-1公共集群：所有业务都需要查询
            if _cluster["cluster_config"].get("registered_system") == REGISTERED_SYSTEM_DEFAULT:
                for _business in business_list:
                    storage_used = get_biz_storage_capacity(_business["bk_biz_id"], _cluster)

                    StorageUsed.objects.update_or_create(
                        bk_biz_id=_business["bk_biz_id"],
                        storage_cluster_id=_cluster["cluster_config"]["cluster_id"],
                        defaults={"storage_used": storage_used},
                    )
            # 2-2第三方集群：只需查询指定业务
            else:
                bk_biz_id = _cluster["cluster_config"].get("custom_option", {}).get("bk_biz_id")
                if not bk_biz_id:
                    continue
                storage_used = get_biz_storage_capacity(bk_biz_id, _cluster)
                StorageUsed.objects.update_or_create(
                    bk_biz_id=bk_biz_id,
                    storage_cluster_id=_cluster["cluster_config"]["cluster_id"],
                    defaults={"storage_used": storage_used},
                )
        except Exception as e:
            logger.exception("sync_storage_info error: %s" % e)


def query(cluster_id):
    def get(url):
        try:
            return BkLogApi.es_route(
                {
                    "scenario_id": "es",
                    "storage_cluster_id": cluster_id,
                    "url": url,
                }
            )
        except Exception as e:  # pylint:disable=broad-except
            logger.exception(f"request es info error {e}")
            return None

    return get


def get_storage_usage_and_all(cluster_id):
    storage_config = query(cluster_id)("_cat/allocation?bytes=b")
    usage = 0
    total = 0
    if not storage_config:
        return usage, total
    for _storage in storage_config:
        total += int(_storage.get("disk.total") or 0)
        usage += int(_storage.get("disk.used") or 0)
    return int((usage / total) * 100), total


def get_biz_storage_capacity(bk_biz_id, cluster):
    # 集群信息
    cluster_config = cluster["cluster_config"]
    domain_name = cluster_config["domain_name"]
    port = cluster_config["port"]
    auth_info = cluster.get("auth_info", {})
    username = auth_info.get("username")
    password = auth_info.get("password")
    index_format = f"{bk_biz_id}_bklog_*"

    # 索引信息
    try:
        indices_info = ElasticHandle(domain_name, port, username, password).get_indices_cat(
            index=index_format, bytes="mb", column=["index", "store.size", "status"]
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(f"集群[{domain_name}] 索引cat信息获取失败，错误信息：{e}")
        return 0

    # 汇总容量
    total_size = 0
    for _info in indices_info:
        if _info["status"] == "close":
            continue
        total_size += int(_info["store.size"])

    return round(total_size / 1024, 2)
