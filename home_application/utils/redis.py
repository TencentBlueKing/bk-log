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
import logging

import redis

import settings

logger = logging.getLogger()


class RedisClient(object):
    _instance = None

    def __init__(self) -> None:
        try:
            if settings.REDIS_PASSWD:
                self.rds = redis.StrictRedis(
                    host=settings.REDIS_HOST,
                    port=int(settings.REDIS_PORT),
                    password=settings.REDIS_PASSWD,
                )
            else:
                self.rds = redis.StrictRedis(
                    host=settings.REDIS_HOST,
                    port=int(settings.REDIS_PORT),
                )
            self.info = self.rds.info()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to connect to redis, err: {e}")
            self.rds = None
            self.info = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            cls._instance = RedisClient(*args, **kwargs)
            return cls._instance

    @classmethod
    def del_instance(cls):
        cls._instance = None

    def get_variables(self, variable_name: str):
        try:
            if self.rds.info:
                return self.info[variable_name]
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get redis info[{variable_name}], err: {e}")
            return None

    def ping(self):
        try:
            return self.rds.ping()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to connect to redis, err: {e}")
            return None

    def hit_rate(self):
        try:
            hits = self.info["keyspace_hits"]
            misses = self.info["keyspace_misses"]
            rate = float(hits) / float(int(hits) + int(misses))
            return "%.2f" % (rate * 100)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get hit_rate, err: {e}")
            return None

    def queue_len(self, queue_name: str):
        try:
            return self.rds.llen(queue_name)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get llen[{queue_name}], err: {e}")
            return None
