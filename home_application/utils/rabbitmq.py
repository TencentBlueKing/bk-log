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
import pika
from pika.exceptions import ChannelClosedByBroker
from kombu.utils.url import url_to_parts
from django.utils.translation import ugettext_lazy as _

import settings
from home_application.constants import ALARM_QUEUE_LEN

logger = logging.getLogger()


class RabbitMQClient(object):
    _instance = None

    def __init__(self) -> None:
        try:
            broker_url = settings.BROKER_URL
            scheme, host, port, user, password, path, query = url_to_parts(broker_url)
            self.scheme = scheme
            self.host = host
            self.port = port
            self.user = user
            self.password = password
            self.path = path
            self.query = query

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Failed to get rabbitmq infomation, err: {e}")

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            cls._instance = RabbitMQClient(*args, **kwargs)
            return cls._instance

    @classmethod
    def del_instance(cls):
        cls._instance = None

    def ping(self):
        result = {"status": False, "data": None, "message": "", "suggestion": ""}
        start_time = time.time()
        try:
            auth = pika.PlainCredentials(self.user, self.password)
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, self.path, auth))
            if connection:
                result["status"] = True
                self.connection = connection
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to ping rabbitmq, msg: {e}")
            result["message"] = str(e)
            result["suggestion"] = _("确认RabbitMQ是否可用")
        spend_time = time.time() - start_time
        result["data"] = "{}ms".format(int(spend_time * 1000))
        return result

    def queue_len(self, queue_name: str):
        result = {"status": False, "data": None, "message": ""}
        try:
            channel = self.connection.channel()
            declear_queue_result = channel.queue_declare(queue=queue_name, durable=True)
            result["data"] = declear_queue_result.method.message_count
            result["status"] = True
            channel.close()
        except ChannelClosedByBroker as e:
            x_max_priority = str(e).split("received none but current is the value '")[1].split("' of type")[0]
            x_max_priority = int(x_max_priority)
            channel = self.connection.channel()
            declear_queue_result = channel.queue_declare(
                queue=queue_name, durable=True, arguments={"x-max-priority": x_max_priority}
            )
            result["data"] = declear_queue_result.method.message_count
            result["status"] = True
            channel.close()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get llen[{queue_name}], err: {e}")
            result["message"] = str(e)
        if result["data"] >= ALARM_QUEUE_LEN:
            result["status"] = False
            result["message"] = f"queue_len is larger than {ALARM_QUEUE_LEN}"
        return result
