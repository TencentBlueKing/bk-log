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
import socket

from django.utils.translation import ugettext_lazy as _

from elasticsearch import Elasticsearch as Elasticsearch
from elasticsearch5 import Elasticsearch as Elasticsearch5
from elasticsearch6 import Elasticsearch as Elasticsearch6

from apps.log_esquery.exceptions import EsClientSocketException, EsClientHostPortException


def get_es_client(
    *,
    version: str,
    hosts: list,
    username: str,
    password: str,
    port: int,
    sniffer_timeout=600,
    verify_certs=False,
    **kwargs
) -> Elasticsearch:
    # 根据版本加载客户端
    if version.startswith("5."):
        es_client = Elasticsearch5
    elif version.startswith("6."):
        es_client = Elasticsearch6
    else:
        es_client = Elasticsearch

    # 由于IPV6地址需要加[], 所以需要对hosts进行处理
    new_hosts = []
    for host in hosts:
        if not host.startswith("["):
            host = "[" + host
        if not host.endswith("]"):
            host += "]"
        new_hosts.append(host)
    hosts = new_hosts

    http_auth = (username, password) if password else None
    return es_client(
        hosts, http_auth=http_auth, port=port, sniffer_timeout=sniffer_timeout, verify_certs=verify_certs, **kwargs
    )


def es_socket_ping(host: str, port: int):
    """
    ES ping by socket
    """
    if not host or not port:
        raise EsClientHostPortException()

    es_address: tuple = (host, port)
    try:
        # 先尝试ipv4
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cs.settimeout(2)
        status: int = cs.connect_ex(es_address)
    except socket.gaierror:  # ip协议不匹配时, 会抛出gaierror
        # ipv4失败，尝试ipv6
        cs = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        cs.settimeout(2)
        status: int = cs.connect_ex(es_address)
    except Exception as e:  # pylint: disable=broad-except
        raise EsClientSocketException(
            EsClientSocketException.MESSAGE.format(error=_("IP or PORT can not be reached, %s").format(e=e))
        )

    if status != 0:
        raise EsClientSocketException(EsClientSocketException.MESSAGE.format(error=_("IP or PORT can not be reached")))
    cs.close()
