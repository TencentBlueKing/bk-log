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

"""
节点管理调用接口汇总
"""
from apps.api.base import DataAPI  # noqa
from config.domains import BK_NODE_APIGATEWAY_ROOT  # noqa
from apps.api.modules.utils import add_esb_info_before_request  # noqa

from bkm_space.utils import bk_biz_id_to_space_uid  # noqa
from bkm_space.define import SpaceTypeEnum  # noqa


def adapt_space_id_before(params):
    """
    适配节点管理的space_id
    """
    params = add_esb_info_before_request(params)
    if params.get("scope", {}).get("bk_biz_id", 0) < 0:
        from apps.log_search.models import SpaceApi

        space_uid = bk_biz_id_to_space_uid(params["scope"]["bk_biz_id"])
        related_space = SpaceApi.get_related_space(space_uid=space_uid, related_space_type=SpaceTypeEnum.BKCC.value)
        if related_space:
            params["scope"]["bk_biz_id"] = related_space.bk_biz_id

    return params


class _BKNodeApi:
    MODULE = "节点管理"

    def __init__(self):
        self.create_subscription = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/create/",
            module=self.MODULE,
            description="创建订阅配置",
            before_request=adapt_space_id_before,
        )
        self.update_subscription_info = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/update/",
            module=self.MODULE,
            description="更新订阅配置",
            before_request=adapt_space_id_before,
        )
        self.get_subscription_info = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/info/",
            module=self.MODULE,
            description="查询订阅配置信息",
            before_request=add_esb_info_before_request,
        )
        self.run_subscription_task = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/run/",
            module=self.MODULE,
            description="执行订阅下发任务",
            before_request=add_esb_info_before_request,
        )
        self.get_subscription_instance_status = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/instance_status/",
            module=self.MODULE,
            description="查询订阅实例状态",
            before_request=add_esb_info_before_request,
        )
        self.get_subscription_task_status = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/task_result/",
            module=self.MODULE,
            description="查看订阅任务运行状态",
            before_request=add_esb_info_before_request,
        )
        self.check_subscription_task_ready = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/check_task_ready/",
            module=self.MODULE,
            description="查看订阅任务是否发起",
            before_request=add_esb_info_before_request,
        )
        self.delete_subscription = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/delete/",
            module=self.MODULE,
            description="删除订阅配置",
            before_request=add_esb_info_before_request,
        )
        self.get_subscription_task_detail = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/task_result_detail/",
            module=self.MODULE,
            description="查询订阅任务中实例的详细状态",
            before_request=add_esb_info_before_request,
        )
        self.switch_subscription = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/switch/",
            module=self.MODULE,
            description="节点管理订阅功能开关",
            before_request=add_esb_info_before_request,
        )

        self.subscription_statistic = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/statistic/",
            module=self.MODULE,
            description="节点管理统计订阅任务数据",
            before_request=add_esb_info_before_request,
        )
        self.query_host_subscriptions = DataAPI(
            method="GET",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/query_host_subscriptions/",
            module=self.MODULE,
            description="获取主机订阅列表",
            before_request=add_esb_info_before_request,
        )
        self.retry_subscription = DataAPI(
            method="POST",
            url=BK_NODE_APIGATEWAY_ROOT + "backend/api/subscription/retry/",
            module=self.MODULE,
            description="重试失败的任务",
            before_request=add_esb_info_before_request,
        )


BKNodeApi = _BKNodeApi()
