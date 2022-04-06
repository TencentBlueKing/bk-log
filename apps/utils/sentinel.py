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
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from django.core.exceptions import ImproperlyConfigured
from django_redis.client import DefaultClient
from django_redis.pool import ConnectionFactory
from redis.connection import to_bool
from redis.sentinel import Sentinel, SentinelConnectionPool


class SentinelConnectionFactory(ConnectionFactory):
    def __init__(self, options):
        # allow overriding the default SentinelConnectionPool class
        options.setdefault("CONNECTION_POOL_CLASS", "redis.sentinel.SentinelConnectionPool")
        super().__init__(options)

        sentinels = options.get("SENTINELS")
        if not sentinels:
            raise ImproperlyConfigured("SENTINELS must be provided as a list of (host, port).")

        # provide the connection pool kwargs to the sentinel in case it
        # needs to use the socket options for the sentinels themselves
        connection_kwargs = self.make_connection_params(None)
        connection_kwargs.pop("url")
        connection_kwargs.update(self.pool_cls_kwargs)
        self._sentinel = Sentinel(
            sentinels,
            sentinel_kwargs=options.get("SENTINEL_KWARGS"),
            **connection_kwargs,
        )

    def get_connection_pool(self, params):
        """
        Given a connection parameters, return a new sentinel connection pool
        for them.
        """
        url = urlparse(params["url"])

        # explicitly set service_name and sentinel_manager for the
        # SentinelConnectionPool constructor since will be called by from_url
        cp_params = dict(params)
        cp_params.update(service_name=url.hostname, sentinel_manager=self._sentinel)
        pool = super().get_connection_pool(cp_params)

        # convert "is_master" to a boolean if set on the URL, otherwise if not
        # provided it defaults to True.
        is_master = parse_qs(url.query).get("is_master")
        if is_master:
            pool.is_master = to_bool(is_master[0])

        return pool


def replace_query(url, query):
    return urlunparse((*url[:4], urlencode(query, doseq=True), url[5]))


class SentinelClient(DefaultClient):
    """
    Sentinel client which uses the single redis URL specified by the CACHE's
    LOCATION to create a LOCATION configuration for two connection pools; One
    pool for the primaries and another pool for the replicas, and upon
    connecting ensures the connection pool factory is configured correctly.
    """

    def __init__(self, server, params, backend):
        if isinstance(server, str):
            url = urlparse(server)
            primary_query = parse_qs(url.query, keep_blank_values=True)
            replica_query = dict(primary_query)
            primary_query["is_master"] = [1]
            replica_query["is_master"] = [0]

            server = [replace_query(url, i) for i in (primary_query, replica_query)]

        super().__init__(server, params, backend)

    def connect(self, *args, **kwargs):
        connection = super().connect(*args, **kwargs)
        if not isinstance(connection.connection_pool, SentinelConnectionPool):
            raise ImproperlyConfigured(
                "Settings DJANGO_REDIS_CONNECTION_FACTORY or "
                "CACHE[].OPTIONS.CONNECTION_POOL_CLASS is not configured correctly."
            )

        return connection
