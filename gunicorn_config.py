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

from __future__ import absolute_import, print_function, unicode_literals

import hashlib
import os
import signal
import sys

# gunicorn 19.8.0之前的一个bug: 配置文件所在路径如果未在环境变量：PYTHONPATH中，则配置文件无法引入同目录下第三方模块
# detail: https://github.com/benoitc/gunicorn/issues/1349
# 当前gunicorn指定版本19.6.0，在未升级情况下，单独修复

try:
    from apps.utils.consul import BKConsul, consul
except ImportError:
    sys.path.insert(0, os.getcwd())
    from apps.utils.consul import BKConsul, consul


bind = f"{os.getenv('LAN_IP', '0.0.0.0')}:{os.getenv('BKLOG_API_PORT', '8000')}"
workers = 8
# worker_class = 'gevent'
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '[%(h)s] %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
timeout = 65
max_requests = 1000

module_name = "bklog"
submodule_name = "api"
node_name_prefix = f"{module_name}-{submodule_name}"


def get_bind_info(server):
    bind_info = server.cfg.settings["bind"].get()[0]
    _ip, _port = bind_info.split(":")
    _port = int(_port)
    return _ip, _port


def get_node_id(server):
    return hashlib.md5(server.cfg.settings["bind"].get()[0].encode("utf-8")).hexdigest()


def when_ready(server):
    _ip, _port = get_bind_info(server)
    node_name = f"{node_name_prefix}-{get_node_id(server)}"

    if server.cfg.settings["worker_class"].get() == "gevent":
        from gevent import monkey

        monkey.patch_all()

    check = consul.Check.tcp(_ip, _port, "10s")
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    client = BKConsul()

    # 注册服务
    client.agent.service.register(module_name, node_name, address=_ip, port=_port, check=check, tags=[submodule_name])
    signal.signal(signal.SIGCHLD, server.handle_chld)

    server.log.info(f"Server register node: {node_name}")


def on_exit(server):
    client = BKConsul()
    node_name = f"{node_name_prefix}-{get_node_id(server)}"
    client.agent.service.deregister(node_name)
    server.log.info(f"Server deregister node: {node_name}")
