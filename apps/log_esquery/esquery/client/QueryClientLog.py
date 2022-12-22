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
"""
import socket

from typing import Dict, Any
from elasticsearch import Elasticsearch as Elasticsearch
from elasticsearch6 import Elasticsearch as Elasticsearch6
from elasticsearch5 import Elasticsearch as Elasticsearch5
from django.utils.translation import ugettext as _
from django.conf import settings

from apps.log_esquery.esquery.client.QueryClientTemplate import QueryClientTemplate
from apps.api import TransferApi
from apps.log_esquery.exceptions import (
    EsClientMetaInfoException,
    EsClientConnectInfoException,
    EsClientSocketException,
    EsClientSearchException,
    BaseSearchFieldsException,
    EsClientScrollException,
    EsException,
)
from apps.log_esquery.type_constants import type_mapping_dict
from apps.utils.log import logger
from apps.utils.cache import cache_five_minute
from apps.log_databus.models import CollectorConfig
from apps.utils.thread import MultiExecuteFunc
from apps.log_search.exceptions import IndexResultTableApiException
from apps.log_esquery.constants import DEFAULT_SCHEMA


class QueryClientLog(QueryClientTemplate):
    def __init__(self):
        super(QueryClientLog, self).__init__()
        self._client: Elasticsearch

    def query(self, index: str, body: Dict[str, Any], scroll=None, track_total_hits=False):
        self._build_connection(index)

        # 如果版本不是5.0且track_total_hits为True时
        if track_total_hits and not isinstance(self._client, Elasticsearch5):
            body.update({"track_total_hits": True})

        try:
            params = {"request_timeout": settings.ES_QUERY_TIMEOUT}
            return self._client.search(index=index, body=body, scroll=scroll, params=params)
        except Exception as e:  # pylint: disable=broad-except
            self.catch_timeout_raise(e)
            raise EsClientSearchException(EsClientSearchException.MESSAGE.format(error=e))

    def mapping(self, index: str) -> Dict:
        index_target = self._get_index_target(index)
        try:
            logger.info("mapping for index=>{}, index_target=>{}".format(index, index_target))
            mapping_dict: type_mapping_dict = self._client.indices.get_mapping(index=index_target)
            return mapping_dict
        except Exception as e:  # pylint: disable=broad-except
            self.catch_timeout_raise(e)
            raise BaseSearchFieldsException(BaseSearchFieldsException.MESSAGE.format(error=e))

    def _get_index_target(self, index: str):
        index_list: list = index.split(",")
        new_index_list: list = []
        for _index in index_list:
            if not _index.endswith("*"):
                _index = _index + "_*"
            new_index_list.append(_index)
        index = ",".join(new_index_list)
        self._build_connection(index)
        # log的index转换逻辑
        return index.replace(".", "_")

    def scroll(self, index, scroll_id: str, scroll: str) -> Dict:
        self._build_connection(index)
        try:
            return self._client.scroll(scroll_id=scroll_id, scroll=scroll)
        except Exception as e:  # pylint: disable=broad-except
            self.catch_timeout_raise(e)
            raise EsClientScrollException(EsClientScrollException.MESSAGE.format(error=e))

    def cat_indices(self, index=None, bytes="mb", format="json", params=None):
        if params is None:
            params = {"request_timeout": 10}
        index_target = self._get_index_target(index)
        return self._client.cat.indices(index=index_target, bytes=bytes, format=format, params=params)

    def cluster_nodes_stats(self, index=None):
        self._get_index_target(index)
        return self._client.nodes.stats()

    def cluster_stats(self, index=None):
        self._get_index_target(index)
        try:
            return self._client.cluster.stats()
        except Exception as e:  # pylint: disable=broad-except
            self.catch_timeout_raise(e)
            raise EsException

    def es_route(self, url: str, index=None):
        self._get_index_target(index)
        if not url.startswith("/"):
            url = "/" + url
        try:
            return self._client.transport.perform_request("GET", url)
        except Exception as e:  # pylint: disable=broad-except
            self.catch_timeout_raise(e)
            raise

    def _build_connection(self, index: str):
        index: str = self._get_meta_index(index)
        if not self._active:
            self._get_connection(index)
            if not self._active:
                raise EsClientSearchException(EsClientSearchException.MESSAGE.format(error=_("EsClient链接失败")))

    @staticmethod
    def _get_meta_index(index: str):
        index_list: list = index.split(",")
        new_index_list = []
        for _index in index_list:
            tmp_index: str = _index.replace("_%s_" % settings.TABLE_ID_PREFIX, "_%s." % settings.TABLE_ID_PREFIX)
            tmp_index_list = tmp_index.split("_")
            new_index: str = tmp_index.replace("_%s" % tmp_index_list[-1], "")
            new_index_list.append(new_index)
        return new_index_list[-1]

    def _get_connection(self, index: str):
        self.host, self.port, self.username, self.password, self.version, self.schema = self._connect_info(index)
        self._active: bool = False

        if not self.host or not self.port:
            raise EsClientConnectInfoException()

        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        es_address: tuple = (str(self.host), int(self.port))
        cs.settimeout(2)
        try:
            status: int = cs.connect_ex(es_address)
            # this status is returnback from tcpserver
            if status != 0:
                raise EsClientSocketException(EsClientSocketException.MESSAGE.format(error=""))
        except Exception as e:  # pylint: disable=broad-except
            raise EsClientSocketException(EsClientSocketException.MESSAGE.format(error=e))
        cs.close()

        logger.info(f"[esquery]get connection with {self.host}:{self.port} by {self.username}")

        # 根绝版本加载客户端
        if self.version.startswith("5."):
            self.elastic_client = Elasticsearch5
        elif self.version.startswith("6."):
            self.elastic_client = Elasticsearch6
        else:
            self.elastic_client = Elasticsearch

        http_auth = (self.username, self.password) if self.username and self.password else None
        self._client: Elasticsearch = self.elastic_client(
            [self.host], http_auth=http_auth, scheme=self.schema, port=self.port, sniffer_timeout=600, verify_certs=True
        )
        if not self._client.ping():
            self._active = False

        else:
            self._active = True

    @staticmethod
    def _connect_info(index: str) -> tuple:
        transfer_api_response: dict = TransferApi.get_result_table_storage(
            {"result_table_list": index, "storage_type": "elasticsearch"}
        )
        # if transfer_api_response.get("code") == "0":
        if len(transfer_api_response) == 1:
            data: dict = transfer_api_response.get(index)
            cluster_config: dict = data.get("cluster_config")
            domain_name: str = cluster_config.get("domain_name")
            port: int = cluster_config.get("port")
            version: str = cluster_config.get("version")
            auth_info_dict: dict = data.get("auth_info")
            username: str = auth_info_dict.get("username")
            password: str = auth_info_dict.get("password")
            # 添加协议字段 由于是后添加的 所以放置在这个地方
            schema: str = cluster_config.get("schema") or DEFAULT_SCHEMA

            _es_password = password
            _es_host = domain_name
            _es_port = port
            _es_user = username
            _es_version = version
            _es_schema = schema

            return _es_host, _es_port, _es_user, _es_password, _es_version, _es_schema
        else:
            raise EsClientMetaInfoException(
                EsClientMetaInfoException.MESSAGE.format(message=transfer_api_response.get("message"))
            )

    @classmethod
    def indices(cls, bk_biz_id, result_table_id=None, with_storage=False):
        """
        获取索引列表
        :param bk_biz_id:
        :param result_table_id:
        :param with_storage
        :return:
        """
        collect_obj = CollectorConfig.objects.filter(bk_biz_id=bk_biz_id).exclude(table_id=None)
        if result_table_id:
            collect_obj = collect_obj.filter(table_id=result_table_id)

        index_list = [
            {
                "bk_biz_id": _collect.bk_biz_id,
                "collector_config_id": _collect.collector_config_id,
                "result_table_id": _collect.table_id,
                "result_table_name_alias": _collect.collector_config_name,
            }
            for _collect in collect_obj
        ]

        # 补充索引集群信息
        if with_storage and index_list:
            indices = [_collect.table_id for _collect in collect_obj]
            storage_info = cls.bulk_cluster_infos(indices)
            for _index in index_list:
                cluster_config = storage_info.get(_index["result_table_id"], {}).get("cluster_config", {})
                _index.update(
                    {
                        "storage_cluster_id": cluster_config.get("cluster_id"),
                        "storage_cluster_name": cluster_config.get("cluster_name"),
                    }
                )
        return index_list

    @staticmethod
    @cache_five_minute("bulk_cluster_info_{result_table_list}", need_md5=True)
    def bulk_cluster_infos(result_table_list: list = None):
        multi_execute_func = MultiExecuteFunc()
        for rt in result_table_list:
            multi_execute_func.append(
                rt, TransferApi.get_result_table_storage, {"result_table_list": rt, "storage_type": "elasticsearch"}
            )
        result = multi_execute_func.run()
        cluster_infos = {}
        for _, cluster_info in result.items():  # noqa
            cluster_infos.update(cluster_info)
        return cluster_infos

    def get_cluster_info(self, result_table_id):
        result_table_id = result_table_id.split(",")[0]
        # 并发查询所需的配置
        multi_execute_func = MultiExecuteFunc()

        multi_execute_func.append(
            "result_table_config", TransferApi.get_result_table, params={"table_id": result_table_id}
        )
        multi_execute_func.append(
            "result_table_storage",
            TransferApi.get_result_table_storage,
            params={"result_table_list": result_table_id, "storage_type": "elasticsearch"},
        )

        result = multi_execute_func.run()
        if "result_table_config" not in result or "result_table_storage" not in result:
            raise IndexResultTableApiException()

        if result_table_id not in result["result_table_storage"]:
            raise IndexResultTableApiException(_("结果表不存在"))

        cluster_config = result["result_table_storage"][result_table_id].get("cluster_config")
        return {
            "bk_biz_id": result["result_table_config"]["bk_biz_id"],
            "storage_cluster_id": cluster_config.get("cluster_id"),
            "storage_cluster_name": cluster_config.get("cluster_name"),
        }
