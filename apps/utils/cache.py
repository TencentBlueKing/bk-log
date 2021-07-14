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
import functools

from django.core.cache import cache

from apps.utils.log import logger
from apps.utils import md5_sum
from apps.log_search.constants import TimeEnum


def using_cache(key: str, duration, need_md5=False):
    """
    :param key: key 名可以使用format进行格式
    :param duration:
    :param need_md5: 缓冲是redis的时候 key不能带有空格等字符，需要用md5 hash一下
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):

            try:
                actual_key = key.format(*args, **kwargs)
            except (IndexError, KeyError):
                actual_key = key

            logger.info(f"[using cache] build key => [{actual_key}] duration => [{duration}]")

            if need_md5:
                actual_key = md5_sum(actual_key)

            cache_result = cache.get(actual_key)

            if cache_result:
                return cache_result

            result = func(*args, **kwargs)
            if result:
                cache.set(actual_key, result, duration)
            return result

        return inner

    return decorator


cache_half_minute = functools.partial(using_cache, duration=0.5 * TimeEnum.ONE_MINUTE_SECOND.value)
cache_one_minute = functools.partial(using_cache, duration=TimeEnum.ONE_MINUTE_SECOND.value)
cache_five_minute = functools.partial(using_cache, duration=5 * TimeEnum.ONE_MINUTE_SECOND.value)
cache_ten_minute = functools.partial(using_cache, duration=10 * TimeEnum.ONE_MINUTE_SECOND.value)
cache_one_hour = functools.partial(using_cache, duration=TimeEnum.ONE_HOUR_SECOND.value)
cache_one_day = functools.partial(using_cache, duration=TimeEnum.ONE_DAY_SECOND.value)
