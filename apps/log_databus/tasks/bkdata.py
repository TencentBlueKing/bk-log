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
from typing import Dict, Any

from celery.schedules import crontab
from celery.task import periodic_task, task

from apps.api import CCApi
from apps.api.modules.bkdata_access import BkDataAccessApi
from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import FEATURE_BKDATA_DATAID, SCENARIO_BKDATA
from apps.log_databus.constants import (
    ADMIN_REQUEST_USER,
    BKDATA_DATA_REGION,
    BKDATA_DATA_SCENARIO,
    BKDATA_DATA_SCENARIO_ID,
    BKDATA_DATA_SENSITIVITY,
    BKDATA_DATA_SOURCE,
    BKDATA_DATA_SOURCE_TAGS,
    BKDATA_PERMISSION,
    BKDATA_TAGS,
    MAX_CREATE_BKDATA_DATA_ID_FAIL_COUNT,
    META_DATA_ENCODING,
)
from apps.log_databus.models import CollectorConfig
from apps.log_databus.utils.bkdata_clean import BKDataCleanUtils
from apps.utils.function import ignored
from apps.utils.log import logger
from apps.api.modules.utils import get_non_bkcc_space_related_bkcc_biz_id


@task(ignore_result=True)
def async_create_bkdata_data_id(collector_config_id: int, platform_username: str = None):
    create_bkdata_data_id(CollectorConfig.objects.get(collector_config_id=collector_config_id), platform_username)


def create_bkdata_data_id(collector_config: CollectorConfig, platform_username: str = None):
    # 对应开关未开启
    toggle_switch = FeatureToggleObject.switch(name=FEATURE_BKDATA_DATAID)
    if not toggle_switch:
        return

    if not collector_config.bk_data_id or collector_config.bkdata_data_id:
        return

    # 检验非CC业务的空间是否关联了CC业务, 如果不关联, 则跳过同步
    bk_biz_id = collector_config.get_bk_biz_id()
    if bk_biz_id < 0:
        related_bk_biz_id = get_non_bkcc_space_related_bkcc_biz_id(bk_biz_id)
        if related_bk_biz_id < 0:
            return
        bk_biz_id = related_bk_biz_id

    # 获取采集项的维护人员maintainers, 请求bkdata的platform_username
    collector_maintainers_and_platform_username = get_collector_maintainers_and_platform_username(
        collector_config=collector_config, bk_biz_id=bk_biz_id, platform_username=platform_username
    )
    maintainers = collector_maintainers_and_platform_username["maintainers"]
    platform_username = collector_maintainers_and_platform_username["platform_username"]

    if not (collector_config.collector_config_name_en or collector_config.table_id):
        logger.error(
            "collector_config {} dont have enough raw_data_name to create deploy plan".format(
                collector_config.collector_config_id
            )
        )
        return

    with ignored(Exception):
        _, table_id = collector_config.table_id.split(".")

    # 这里可能遇到的exception有:
    # - 权限不足, 无法创建, 可以看下计算平台的权限与CC的业务运维权限人员是否能对应
    # - 解析关联的channel_id失败，[1500004] 对象不存在：databus_channel[name=xxx], 链路新增了kafka集群, 需要联系计算平台同步
    BkDataAccessApi.deploy_plan_post(
        params={
            "bk_username": platform_username or collector_config.get_updated_by(),
            "data_scenario": BKDATA_DATA_SCENARIO,
            "data_scenario_id": BKDATA_DATA_SCENARIO_ID,
            "permission": BKDATA_PERMISSION,
            "bk_biz_id": bk_biz_id,
            "description": collector_config.description,
            "access_raw_data": {
                "tags": BKDATA_TAGS,
                "raw_data_name": collector_config.collector_config_name_en or table_id,
                "maintainer": ",".join(maintainers),
                "raw_data_alias": collector_config.collector_config_name,
                "data_source_tags": BKDATA_DATA_SOURCE_TAGS,
                "data_region": BKDATA_DATA_REGION,
                "data_source": BKDATA_DATA_SOURCE,
                "data_encoding": META_DATA_ENCODING,  # 接入到计算平台是经过的kafka，此时kafka中的数据已经是utf-8，所以这里应该固定编码
                "sensitivity": BKDATA_DATA_SENSITIVITY,
                "description": collector_config.description,
                "preassigned_data_id": collector_config.bk_data_id,
            },
        }
    )
    collector_config.bkdata_data_id = collector_config.bk_data_id
    collector_config.save(update_fields=["bkdata_data_id"])


@periodic_task(run_every=crontab(minute="30", hour="3"))
def review_bkdata_data_id():
    """
    检测采集项bkdata_id: 处理未同步到数据平台的data_id
    """
    toggle_switch = FeatureToggleObject.switch(name=FEATURE_BKDATA_DATAID)
    if not toggle_switch:
        return
    collector_configs = CollectorConfig.objects.filter(bkdata_data_id__isnull=True)
    for collector_config in collector_configs:
        if collector_config.bkdata_data_id_sync_times >= MAX_CREATE_BKDATA_DATA_ID_FAIL_COUNT:
            logger.error(
                "{collector_config_name} Creating bkdata_data_id exceeded the maximum number of retries: {cnt}".format(
                    collector_config_name=collector_config.collector_config_name,
                    cnt=MAX_CREATE_BKDATA_DATA_ID_FAIL_COUNT,
                )
            )
            continue

        try:
            create_bkdata_data_id(collector_config)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"{collector_config.collector_config_name} create bkdata data_id failed: {e}")
            collector_config.bkdata_data_id_sync_times += 1
        else:
            collector_config.bkdata_data_id_sync_times = 0

        collector_config.save()


@periodic_task(run_every=crontab(minute="*/30"))
def review_clean():
    """
    定期同步计算平台入库列表
    """
    if not FeatureToggleObject.switch(name=SCENARIO_BKDATA):
        return
    collector_configs = CollectorConfig.objects.filter(bkdata_data_id__isnull=False)
    for collector_config in collector_configs:
        with ignored(Exception, log_exception=True):
            BKDataCleanUtils(raw_data_id=collector_config.bkdata_data_id).update_or_create_clean(
                collector_config_id=collector_config.collector_config_id,
                bk_biz_id=collector_config.bk_biz_id,
                category_id=collector_config.category_id,
            )


@task(ignore_result=True)
def sync_clean(bk_biz_id: int):
    try:
        collector_configs = CollectorConfig.objects.filter(bk_biz_id=bk_biz_id, bkdata_data_id__isnull=False)
        for collector_config in collector_configs:
            with ignored(Exception, log_exception=True):
                BKDataCleanUtils(raw_data_id=collector_config.bkdata_data_id).update_or_create_clean(
                    collector_config_id=collector_config.collector_config_id,
                    bk_biz_id=collector_config.bk_biz_id,
                    category_id=collector_config.category_id,
                )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "bk_biz_id: {bk_biz_id} get collector_configs failed: {reason}".format(bk_biz_id=bk_biz_id, reason=e)
        )
    finally:
        BKDataCleanUtils.unlock_sync_clean(bk_biz_id=bk_biz_id)


def get_collector_maintainers_and_platform_username(
    collector_config: CollectorConfig, bk_biz_id: int, platform_username: str = None
) -> Dict[str, Any]:
    """
    获取当前采集项的维护人(maintainers)
    以及请求bkdata的用户名(platform_username)
    这里指定传bk_biz_id是因为非bkcc的业务会转换成关联bkcc的业务, 避免二次查关联
    """
    result = {
        "maintainers": set(),
        "platform_username": platform_username,
    }

    params = {
        "biz_property_filter": {
            "condition": "AND",
            "rules": [
                {
                    "field": "bk_biz_id",
                    "operator": "equal",
                    "value": bk_biz_id,
                },
            ],
        },
        "fields": ["bk_biz_maintainer"],
    }
    app_list = CCApi.get_app_list(params)
    if app_list and app_list["info"]:
        for maintainer in app_list["info"][0].get("bk_biz_maintainer", "").split(","):
            if not maintainer:
                continue
            result["maintainers"].add(maintainer)
    # 去除ADMIN_REQUEST_USER
    if ADMIN_REQUEST_USER in result["maintainers"]:
        result["maintainers"].discard(ADMIN_REQUEST_USER)

    if not result["maintainers"]:
        raise BaseException(f"dont have enough maintainer only {ADMIN_REQUEST_USER}")

    # 如果指定了平台运维人员，且在业务运维人员中，则使用指定的平台运维人员, 否则使用业务运维人员中的一个
    if not platform_username or platform_username not in result["maintainers"]:
        result["platform_username"] = list(result["maintainers"])[0]
    else:
        result["platform_username"] = platform_username

    # 最后添加创建人和更新人, 是因为创建人和更新人可能不在业务运维人员中, 没有bkdata的权限导致platform_username没有权限
    if collector_config.created_by:
        result["maintainers"].add(collector_config.created_by)
    if collector_config.updated_by:
        result["maintainers"].add(collector_config.updated_by)
    return result
