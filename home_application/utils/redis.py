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
import time
import logging
from django.utils.translation import ugettext_lazy as _

import redis

import settings
from home_application.constants import ALARM_QUEUE_LEN

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

    def __del__(self):
        if self.rds:
            self.rds.close()

    def show_variables(self, variable_name: str):
        result = {"status": False, "data": None, "message": ""}
        try:
            if self.rds.info:
                result["data"] = self.info[variable_name]
                result["status"] = True
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get redis info[{variable_name}], err: {e}")
            result["message"] = str(e)
        return result

    def ping(self):
        result = {"status": False, "data": None, "message": "", "suggestion": ""}
        start_time = time.time()
        try:
            result["status"] = self.rds.ping()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to ping redis, err: {e}")
            result["message"] = str(e)
            result["suggestion"] = _("确认Redis是否可用")
        spend_time = time.time() - start_time
        result["data"] = "{}ms".format(int(spend_time * 1000))
        return result

    def hit_rate(self):
        result = {"status": False, "data": None, "message": ""}
        try:
            hits = self.info["keyspace_hits"]
            misses = self.info["keyspace_misses"]
            rate = float(hits) / float(int(hits) + int(misses))
            result["data"] = "%.2f" % (rate * 100)
            result["status"] = True
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get hit_rate, err: {e}")
            result["message"] = str(e)

        return result

    def queue_len(self, queue_name: str):
        result = {"status": False, "data": None, "message": ""}
        try:
            result["data"] = self.rds.llen(queue_name)
            result["status"] = True
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get llen[{queue_name}], err: {e}")
            result["message"] = str(e)
        if result["data"] >= ALARM_QUEUE_LEN:
            result["status"] = False
            result["message"] = f"queue_len is larger than {ALARM_QUEUE_LEN}"
        return result
