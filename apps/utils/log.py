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
from logging.handlers import DatagramHandler
from opentelemetry import trace
from opentelemetry.trace import format_trace_id

"""
Usage:

    from apps.common.log import logger

    logger.info("test")
    logger.error("wrong1")
    logger.exception("wrong2")

    # with traceback
    try:
        1 / 0
    except Exception:
        logger.exception("wrong3")
"""
import logging  # noqa

from apps.utils.local import get_request_id  # noqa

logger_detail = logging.getLogger("root")


class UdpHandler(DatagramHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            self.send(msg.encode())
        except Exception:  # pylint:disable=broad-except
            self.handleError(record)


# ===============================================================================
# 自定义添加打印内容
# ===============================================================================
# traceback--打印详细错误日志
class LoggerTraceback(object):
    """
    详细异常信息追踪
    """

    def error(self, message="", *args, **kwargs):
        """
        打印 error 日志方法
        """
        message = self.build_message(message)
        logger_detail.error(message, *args, **kwargs)

    def info(self, message="", *args, **kwargs):
        """
        info 日志
        """
        message = self.build_message(message)
        logger_detail.info(message, *args, **kwargs)

    def warning(self, message="", *args, **kwargs):
        """
        warning 日志
        """
        message = self.build_message(message)
        logger_detail.warning(message, *args, **kwargs)

    def debug(self, message="", *args, **kwargs):
        """
        debug 日志
        """
        message = self.build_message(message)
        logger_detail.debug(message, *args, **kwargs)

    def critical(self, message="", *args, **kwargs):
        """
        critical 日志
        """
        message = self.build_message(message)
        logger_detail.critical(message, *args, **kwargs)

    def exception(self, message="", *args, **kwargs):
        message = self.build_message(message)
        logger_detail.exception(message, *args, **kwargs)

    @staticmethod
    def build_message(message):
        trace_id = trace.get_current_span().get_span_context().trace_id
        return "{} | {}".format(format_trace_id(trace_id), message)


# traceback--打印详细错误日志
logger = LoggerTraceback()
