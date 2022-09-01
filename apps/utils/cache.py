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
import functools
import json
import zlib

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_bytes

from apps.utils.log import logger
from apps.utils import md5_sum
from apps.log_search.constants import TimeEnum

MIN_LEN = 15


def using_cache(key: str, duration, need_md5=False, compress=False):
    """
    :param key: key 名可以使用format进行格式
    :param duration:
    :param need_md5: 缓冲是redis的时候 key不能带有空格等字符，需要用md5 hash一下
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            refresh = kwargs.get("refresh", False)
            kwargs.pop("refresh", None)
            try:
                actual_key = key.format(*args, **kwargs)
            except (IndexError, KeyError):
                actual_key = key

            logger.info(f"[using cache] build key => [{actual_key}] duration => [{duration}]")

            if need_md5:
                actual_key = md5_sum(actual_key)

            cache_result = cache.get(actual_key)

            if cache_result and not refresh:
                if compress:
                    try:
                        cache_result = zlib.decompress(cache_result)
                    except Exception:  # pylint: disable=broad-except
                        pass
                return json.loads(force_bytes(cache_result))

            result = func(*args, **kwargs)
            if result:
                value = json.dumps(result, cls=DjangoJSONEncoder)
                if compress:
                    if len(value) > MIN_LEN:
                        value = zlib.compress(value.encode("utf-8"))
                cache.set(actual_key, value, duration)
            return result

        return inner

    return decorator


def using_caches(key: str, need_deconstruction_name: str, duration, need_md5=False):
    """
    批量获取缓存装饰器，要求：需要被修饰的方法显式传参key列表，以及方法执行结果为dict类型
    :param key: key 名可以使用format进行格式，由于是可迭代对象，请勿使用字符串参数格式化
    :param duration:
    :param need_deconstruction_name: key列表名，该参数需要key列表显式传参，通过key列表名获得入参的key列表
    :param need_md5: 缓冲是redis的时候 key不能带有空格等字符，需要用md5 hash一下
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            need_deconstruction_param = kwargs.get(need_deconstruction_name, list())
            temp_result = dict()
            in_cache_keys = set()
            for value in need_deconstruction_param:
                actual_key = key.format(value)

                if need_md5:
                    actual_key = md5_sum(actual_key)
                cache_result = cache.get(actual_key)
                if cache_result:
                    temp_result.update({value: json.loads(cache_result)})
                    in_cache_keys.add(value)

            not_in_cache_keys = list(set(kwargs[need_deconstruction_name]) - in_cache_keys)
            result = dict()

            if not_in_cache_keys:
                kwargs[need_deconstruction_name] = not_in_cache_keys
                func_result = func(*args, **kwargs)
                if not isinstance(func_result, dict):
                    logger.warning("decorated method execute result non-dictionary")
                else:
                    result.update(func_result)

            if result:
                for item in result:
                    actual_key = key.format(item)

                    if need_md5:
                        actual_key = md5_sum(actual_key)

                    cache.set(actual_key, json.dumps(result[item], cls=DjangoJSONEncoder), duration)

            result.update(temp_result)

            return result

        return inner

    return decorator


cache_half_minute = functools.partial(using_cache, duration=0.5 * TimeEnum.ONE_MINUTE_SECOND.value)
cache_one_minute = functools.partial(using_cache, duration=TimeEnum.ONE_MINUTE_SECOND.value)
cache_five_minute = functools.partial(using_cache, duration=5 * TimeEnum.ONE_MINUTE_SECOND.value)
cache_ten_minute = functools.partial(using_cache, duration=10 * TimeEnum.ONE_MINUTE_SECOND.value)
cache_one_hour = functools.partial(using_cache, duration=TimeEnum.ONE_HOUR_SECOND.value)
cache_half_hour = functools.partial(using_cache, duration=0.5 * TimeEnum.ONE_HOUR_SECOND.value)
cache_one_day = functools.partial(using_cache, duration=TimeEnum.ONE_DAY_SECOND.value)

caches_one_hour = functools.partial(using_caches, duration=TimeEnum.ONE_HOUR_SECOND.value)
