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

from blueapps.utils.unique import uniqid
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection
from rest_framework import throttling

from apps.log_search.permission import Permission
from apps.utils.log import logger
from apps.log_search.constants import TimeEnum


redis_client = None
if settings.USE_REDIS:
    redis_client = get_redis_connection("default")


def get_current_window_range():
    now = datetime.datetime.now()
    next = now + datetime.timedelta(minutes=settings.BKLOG_QOS_LIMIT_WINDOW)
    return now.timestamp(), next.timestamp()


def get_window_time_point():
    now = datetime.datetime.now()
    next = now + datetime.timedelta(minutes=settings.BKLOG_QOS_LIMIT_WINDOW)
    return next.timestamp()


def get_window_count(request):
    count = 0
    values = redis_client.zrange(build_qos_key(request), 0, settings.BKLOG_QOS_LIMIT, desc=True, withscores=True)
    window_start, window_end = get_current_window_range()
    for value in values:
        _, score = value
        if window_start <= score <= window_end:
            count += 1
    return count


def clear_redis_zset(request):
    redis_client.delete(build_qos_key(request))


def esquery_qos(request):
    if not settings.USE_REDIS:
        return
    if not settings.BKLOG_QOS_USE:
        return
    auth_info = Permission.get_auth_info(request)
    if auth_info["bk_app_code"] not in settings.BKLOG_QOS_LIMIT_APP:
        return
    token = uniqid()
    key = build_qos_key(request)
    window_time_point = get_window_time_point()
    redis_client.zadd(f"{key}", {f"{token}_{window_time_point}": window_time_point})
    logger.info(f"[Esquery Qos] qos count [{build_qos_key(request)}] increment")


def _get_request_data(request):
    if request.method in ["GET"]:
        return request.query_params
    return request.data


def build_qos_key(request) -> str:
    path = request.path
    data = _get_request_data(request)
    index_set_id = data.get("index_set_id")
    if index_set_id is not None:
        return f"{settings.APP_CODE}_qos_{path}_{index_set_id}"
    scenario_id = data.get("scenario_id")
    indices = data.get("indices")
    return f"{settings.APP_CODE}_qos_{path}_{scenario_id}_{indices}"


def build_qos_limit_key(request) -> str:
    return f"{build_qos_key(request)}_limit"


def qos_recover(request, response):
    if not settings.USE_REDIS:
        return
    count = get_window_count(request)
    if not response.exception:
        if count != 0:
            logger.info(f"[Esquery Qos] qos recover [{build_qos_key(request)}]")
            clear_redis_zset(request)


class QosThrottle(throttling.BaseThrottle):
    def __init__(self):
        self.limit_key = ""

    def allow_request(self, request, view):
        if not settings.USE_REDIS:
            return True

        self.limit_key = build_qos_limit_key(request)

        # 如果已经被限制 直接禁止
        if cache.has_key(self.limit_key):  # noqa
            return False

        # 检查超时次数
        qos_limit_time = settings.BKLOG_QOS_LIMIT_TIME * TimeEnum.ONE_MINUTE_SECOND.value
        count = get_window_count(request)
        if count >= settings.BKLOG_QOS_LIMIT:
            # 设置禁止标记 并删除计数
            if cache.set(self.limit_key, "1", timeout=qos_limit_time, nx=True):
                logger.warning(f"[Esquery Qos] query limit key [{self.limit_key}] set")
                clear_redis_zset(request)
            return False
        return True

    def wait(self):
        return cache.ttl(self.limit_key)
