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
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging  # noqa
from functools import partial  # noqa
from multiprocessing.pool import ThreadPool as _ThreadPool  # noqa

from django import db  # noqa
from django.utils import timezone, translation  # noqa

from apps.utils.local import activate_request, get_request  # noqa
from .local import local  # noqa

logger = logging.getLogger(__name__)


def run_func_with_local(items, tz, lang, request, func, *args, **kwargs):
    """
    线程执行函数
    :param request: added by jairwu API request
    :param func: 待执行函数
    :param items: Thread Local Items
    :param tz: 时区
    :param lang: 语言
    :param args: 位置参数
    :param kwargs: 关键字参数
    :return: 函数返回值
    """
    # 同步local数据
    for item in items:
        setattr(local, item[0], item[1])

    # 设置时区及语言
    timezone.activate(tz)
    translation.activate(lang)
    activate_request(request)
    try:
        data = func(*args, **kwargs)
    except Exception as e:
        raise e
    finally:
        # 关闭db连接
        db.connections.close_all()

        # 清理local数据
        for item in local:
            delattr(local, item[0])

    return data


class ThreadPool(_ThreadPool):
    """
    线程池
    """

    @staticmethod
    def get_func_with_local(func):
        tz = timezone.get_current_timezone().zone
        lang = translation.get_language()
        items = [item for item in local]
        request = get_request()
        return partial(run_func_with_local, items, tz, lang, request, func)

    def map_ignore_exception(self, func, iterable, return_exception=False):
        """
        忽略错误版的map
        """
        futures = []
        for params in iterable:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            futures.append(self.apply_async(func, args=params))

        results = []
        for future in futures:
            try:
                results.append(future.get())
            except Exception as e:
                if return_exception:
                    results.append(e)
                logger.exception(e)

        return results

    def map_async(self, func, iterable, chunksize=None, callback=None):
        return super(ThreadPool, self).map_async(
            self.get_func_with_local(func), iterable, chunksize=chunksize, callback=callback
        )

    def apply_async(self, func, args=(), kwds={}, callback=None):
        return super(ThreadPool, self).apply_async(
            self.get_func_with_local(func), args=args, kwds=kwds, callback=callback
        )

    def imap(self, func, iterable, chunksize=1):
        return super(ThreadPool, self).imap(self.get_func_with_local(func), iterable, chunksize)

    def imap_unordered(self, func, iterable, chunksize=1):
        func = partial(run_func_with_local, func, local)
        return super(ThreadPool, self).imap_unordered(self.get_func_with_local(func), iterable, chunksize=chunksize)
