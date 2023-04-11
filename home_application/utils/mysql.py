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

import pymysql

import settings

logger = logging.getLogger()


class MySQLClient(object):
    _instance = None

    def __init__(self) -> None:
        try:
            self.db = pymysql.connect(
                host=settings.DATABASES["default"]["HOST"],
                port=int(settings.DATABASES["default"]["PORT"]),
                user=settings.DATABASES["default"]["USER"],
                password=settings.DATABASES["default"]["PASSWORD"],
                db=settings.DATABASES["default"]["NAME"],
            )
            self.cursor = self.db.cursor()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to connect to database, err: {e}")
            self.db = None
            self.cursor = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            cls._instance = MySQLClient(*args, **kwargs)
            return cls._instance

    def __del__(self):
        """垃圾回收时关闭连接"""
        if self.db:
            self.db.close()

    @classmethod
    def del_instance(cls):
        cls._instance = None

    def show_variables(self, variable_name: str):
        result = {"status": False, "data": None, "message": ""}
        try:
            if self.cursor:
                stmt = r"""show global variables like '{}';""".format(variable_name)
                self.cursor.execute(stmt)
                result["data"] = self.cursor.fetchone()[1]
                result["status"] = True
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get global variables[{variable_name}], err: {e}")
            result["message"] = str(e)

        return result

    def show_status(self, status_name: str):
        result = {"status": False, "data": None, "message": ""}
        try:
            if self.cursor:
                stmt = r"""show global status like '{}';""".format(status_name)
                self.cursor.execute(stmt)
                result["data"] = self.cursor.fetchone()[1]
                result["status"] = True
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get global status[{status_name}], err: {e}")
            result["message"] = str(e)
        return result

    def ping(self):
        result = {"status": False, "data": None, "message": "", "suggestion": ""}
        start_time = time.time()
        try:
            self.db.ping()
            result["status"] = True
        except Exception as e:  # pylint: disable=broad-except
            logger.error("failed to ping MySQL, err: {e}")
            result["message"] = str(e)
            result["suggestion"] = _("确认MySQL连接是否可用")

        spend_time = time.time() - start_time
        result["data"] = "{}ms".format(int(spend_time * 1000))
        return result
