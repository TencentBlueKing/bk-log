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

import requests

import settings

logger = logging.getLogger()


class RabbitMQClient(object):
    def __init__(self) -> None:
        try:
            broker_url = settings.BROKER_URL.split("//")[1]
            user_and_password, host_and_port_and_vhost = broker_url.split("@")
            self.user, self.password = user_and_password.split(":")
            host_and_port, self.vhost = host_and_port_and_vhost.split("/")
            self.host, self.port = host_and_port.split(":")

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Failed to get rabbitmq infomation, err: {e}")

    def _call_api(self, path: str):
        headers = {"content-type": "application/json"}
        url = f"http://{self.host}:{self.port}/api/{path}"
        try:
            resp = requests.get(url, headers=headers, auth=(self.user, self.password))
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Failed to call rabbitmq api[{path}], err: {e}")
            return None

    def get_queues(self):
        if self.vhost == "/":
            return self._call_api("queues")
        return self._call_api(f"queues/{self.vhost}")
