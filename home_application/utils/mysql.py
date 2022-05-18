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

    @classmethod
    def del_instance(cls):
        cls._instance = None

    def get_variables(self, variable_name: str):
        try:
            if self.cursor:
                stmt = r"""show global variables like '{}';""".format(variable_name)
                self.cursor.execute(stmt)
                return self.cursor.fetchone()[1]
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get global variables[{variable_name}], err: {e}")
            return None

    def get_status(self, status_name: str):
        try:
            if self.cursor:
                stmt = r"""show global status like '{}';""".format(status_name)
                self.cursor.execute(stmt)
                return self.cursor.fetchone()[1]
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to get global status[{status_name}], err: {e}")
            return None
