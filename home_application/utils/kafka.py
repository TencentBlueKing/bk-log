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

from kafka import KafkaAdminClient

import settings

logger = logging.getLogger()


class KafkaClient(object):
    _instance = None

    def __init__(self) -> None:
        start_time = time.time()
        try:
            self.client = KafkaAdminClient(bootstrap_servers=f"{settings.DEFAULT_KAFKA_HOST}:9092")
            self.message = "ok"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to connect to kafka, err: {e}")
            self.client = None
            self.message = str(e)

        spend_time = time.time() - start_time
        self.ms = "{}ms".format(int(spend_time * 1000))

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            cls._instance = KafkaClient(*args, **kwargs)
            return cls._instance

    @classmethod
    def del_instance(cls):
        cls._instance = None

    def __del__(self):
        if self.client:
            self.client.close()

    def ping(self):
        result = {"status": False, "data": self.ms, "message": self.message}
        if self.client:
            result["status"] = True
        return result

    def get_consumer_groups(self):
        if self.client:
            return self.client.list_consumer_groups()
        return None

    def get_consumer_group_offsets(self, group_name: str):
        if self.client:
            return self.client.list_consumer_group_offsets(group_name)
        return None
