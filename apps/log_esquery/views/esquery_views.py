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

from django.conf import settings
from rest_framework import serializers
from rest_framework.response import Response
from apps.generic import APIViewSet
from apps.log_esquery import metrics

from apps.log_esquery.qos import QosThrottle, qos_recover
from apps.utils.drf import list_route

from apps.iam.handlers.drf import IAMPermission
from apps.log_esquery.exceptions import (
    EsqueryAccessDenyException,
    EsqueryIndexSetIdNotExistsException,
)
from apps.log_esquery.permission import Permission
from apps.log_esquery.serializers import (
    EsQuerySearchAttrSerializer,
    EsQueryDslAttrSerializer,
    EsQueryMappingAttrSerializer,
    EsQueryScrollAttrSerializer,
    EsQueryIndicesAttrSerializer,
    EsQueryClusterInfoAttrSerializer,
    EsQueryClusterStatsSerializer,
    EsQueryCatIndicesSerializer,
    EsQueryEsRouteSerializer,
)
from apps.log_esquery.esquery.esquery import EsQuery
from apps.log_search.models import Scenario


class EsQueryViewSet(APIViewSet):
    serializer_class = serializers.Serializer
    throttle_classes = (QosThrottle,)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super(EsQueryViewSet, self).finalize_response(request, response, *args, **kwargs)
        qos_recover(request, response)
        return response

    def get_permissions(self):
        auth_info = Permission.get_auth_info(self.request)
        # ESQUERY白名单不需要鉴权
        if auth_info["bk_app_code"] in settings.ESQUERY_WHITE_LIST:
            return []

        # 暂时只对外开放查询接口
        if self.action not in ["search", "dsl"]:
            raise EsqueryAccessDenyException()

        data = self.request.data
        scenario_id = data.get("scenario_id")

        # 数据平台已有鉴权，直接透传
        if scenario_id == Scenario.BKDATA:
            return []

        # 其它场景必须传index_set_id
        index_set_id = data.get("index_set_id")
        if self.action != "dsl" and not index_set_id:
            raise EsqueryIndexSetIdNotExistsException()

        return [IAMPermission([self.ActionEnum.SEARCH_LOG], [self.ResourceEnum.INDICES.create_instance(index_set_id)])]

    @list_route(methods=["POST"], url_path="search/")
    def search(self, request):
        """
        @api {post} /esquery/search/ 01_搜索-日志内容
        @apiName search_log
        @apiGroup 13_Esquery
        @apiParam {String} indices 索引列表（必填）
        @apiParam {String} [scenario_id] 查询的es类型（非必填） 默认为log，蓝鲸数据平台：bkdata 原生ES：es 自由链路：log
        @apiParam {Int} [storage_cluster_id] （非必填） 当scenario_id为es时候需要传入
        @apiParam {str} [index_set_id] （非必填） 与log_search app联动的索引集编号，传入该值后indices将失效
        @apiParam {String} [time_field] 时间字段（非必填，bkdata内部为dtEventTimeStamp，外部如果传入时间范围需要指定时间字段）
        @apiParam {String} [time_field_type] 时间字段（非必填，bkdata内部为dtEventTimeStamp，外部如果传入时间范围需要指定时间字段类型，默认为date）
        @apiParam {String} [time_field_unit] 时间字段（非必填，bkdata内部为dtEventTimeStamp，外部如果传入时间范围需要指定时间字段单位，默认为妙）
        @apiParam {String} [include_start_time] 是否包含开始时间点，true 为 gte, false 为 gt，默认为 true
        @apiParam {String} [include_end_time] 是否包含结束时间点，true 为 lte, false 为 lt，默认为 true
        @apiParam {String} [start_time] 开始时间(非必填)
        @apiParam {String} [end_time] 结束时间（非必填)
        @apiParam {String} [time_zone] 时区（非必填)
            当传入时间戳，时区会默认为0时区；当start_time和end_time参数传入符合ISO-8601的字符串，则会根据时区转换，不填默认为系统时区
        @apiParam {String} [time_range] 时间标识符符["15m", "30m", "1h", "4h", "12h", "1d", "customized"]（非必填，默认15m）
        @apiParam {String} [query_string] 搜索语句query_string(非必填，默认为*)
        @apiParam {List} [filter] 搜索过滤条件（非必填，默认为没有过滤，默认的操作符是is） 操作符支持 is|is one of|is not|is not one of|exists|is not exists  # pylint: disable=line-too-long  # noqa
        @apiParam {List} [sort_list] 排序条件 支持对应field的正序倒叙，支持优先级
        @apiParam {Int} [start] 起始位置（非必填，类似数组切片，默认为0）
        @apiParam {Int} [size] 条数（非必填，控制返回条目，默认为500）
        @apiParam {Dict} [aggs] ES的聚合参数 （非必填，默认为{}）
        @apiParam {Dict} [highlight] 高亮参数 （非必填，默认为{}）
        @apiParamExample {Json} 请求参数
        {
            "indices": "index_a,index_b",
            "scenario_id": "bkdata"
            "start_time": "2019-06-11 00:00:00",
            "end_time": "2019-06-12 11:11:11",
            "time_range": "customized"
            "query_string": "error",
            "filter": [
                {
                    "key": "ip",
                    "method": "is",
                    "value": "127.0.0.1",
                    "condition": "and",  (默认不传是and，只支持and or)
                    "type": "field" (默认field 目前支持field，其他无效)
                }
            ],
            "sort_list": [
                ["field_a", "desc"],
                ["field_b", "asc"]
            ]
            "start": 0,
            "size": 15,
            "aggs": {
                "docs_per_minute": {
                    "date_histogram": {
                        'field': "dtEventTimeStamp",
                        "interval": "1m",
                        # "time_zone": "+08: 00"
                    },
                },
                "top_ip": {
                    "terms": {
                        "field": "ip",
                        "size": 5,
                    }
                },

            },
            "highlight": {
                "pre_tags": [
                    "<mark>"
                ],
                "post_tags": [
                    "</mark>"
                ],
                "fields": {
                    "*": {
                    }
                },
                "require_field_match": False,
            }
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "result": true,
                "message": "查询成功",
                "data": {
                    "hits": {
                        "hits": [
                            {
                                "_score": 2,
                                "_type": "xx",
                                "_id": "xxx",
                                "_source": {
                                    "dtEventTimeStamp": 1565453112000,
                                    "report_time": "2019-08-11 00:05:12",
                                    "log": "xxxxxx",
                                    "ip": "127.0.0.1",
                                    "gseindex": 5857918,
                                    "_iteration_idx": 3,
                                    "path": "xxxxx"
                                },
                                "_index": "xxxxxxxx"
                            },
                            {
                                "_score": 2,
                                "_type": "xxxx",
                                "_id": "xxxxx",
                                "_source": {
                                    "dtEventTimeStamp": 1565453113000,
                                    "report_time": "2019-08-11 00:05:13",
                                    "log": "xxxxxxx",
                                    "ip": "127.0.0.1",
                                    "gseindex": 5857921,
                                    "_iteration_idx": 2,
                                    "path": "xxxxxxxxx"
                                },
                                "_index": "xxxxxxx"
                            }
                        ],
                        "total": 8429903,
                        "max_score": 2
                    },
                    "_shards": {
                        "successful": 9,
                        "failed": 0,
                        "total": 9
                    },
                    "took": 136,
                    "timed_out": false
                },
                "code": "00"
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(EsQuerySearchAttrSerializer)
        # 调用EsQuery实例
        esquery = EsQuery(data)

        start_at = time.time()
        exc = None

        try:
            result = esquery.search()
        except Exception as e:
            exc = e
            raise
        finally:
            labels = {
                "index_set_id": data.get("index_set_id") or -1,
                "indices": data.get("indices") or "",
                "scenario_id": data.get("scenario_id") or "",
                "storage_cluster_id": data.get("storage_cluster_id") or -1,
                "status": str(exc),
            }
            metrics.ESQUERY_SEARCH_LATENCY.labels(**labels).observe(time.time() - start_at)
            metrics.ESQUERY_SEARCH_COUNT.labels(**labels).inc()

        return Response(result)

    @list_route(methods=["POST"], url_path="dsl/")
    def dsl(self, request):
        """
        @api {post} /esquery/dsl/ 02_拉取-字段内容
        @apiName search_dsl
        @apiGroup 13_Esquery
        @apiParam {String} indices 结果表名称
        @apiParam {Json} body json字典
        @apiParam {Int} [scenario_id] 查询的es类型（非必填，如传入的不是log的索引则必须传入该字段） 默认为log，蓝鲸数据平台：bkdata 原生ES：es 自由链路：log
        @apiParam {Int} [storage_cluster_id] （非必填） 当scenario_id为es时候需要传入
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog_testwithpass_20191122*",
            "body": {}
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "took": 0,
                "timed_out": false,
                "_shards": {
                    "total": 2,
                    "successful": 2,
                    "skipped": 0,
                    "failed": 0
                },
                "hits": {
                    "total": 330,
                    "max_score": 1,
                    "hits": [
                        {
                            "_index": "2_bklog_testwithpass_2019112201",
                            "_type": "2_bklog_testwithpass",
                            "_id": "r077kG4BOXRw1_73ymEb",
                            "_score": 1,
                            "_source": {
                                "bk_biz_id": "1",
                                "cloudId": "default",
                                "dtEventTimeStamp": "1574390450000",
                                "gseIndex": 8,
                                "iterationIndex": 2,
                                "log": "error|hello world",
                                "path": "/tmp/durant.log",
                                "serverIp": "127.0.0.1",
                                "worldId": ""
                            }
                        },
                        {
                            "_index": "2_bklog_testwithpass_2019112201",
                            "_type": "2_bklog_testwithpass",
                            "_id": "sU77kG4BOXRw1_73ymEb",
                            "_score": 1,
                            "_source": {
                                "bk_biz_id": "1",
                                "cloudId": "default",
                                "dtEventTimeStamp": "1574390450000",
                                "gseIndex": 8,
                                "iterationIndex": 4,
                                "log": "info|hello world",
                                "path": "/tmp/durant.log",
                                "serverIp": "127.0.0.1",
                                "worldId": ""
                            }
                        }
                    ]
                },
                "dsl": "{}"
            },
            "code": 0,
            "message": ""
        }


        """
        data = self.params_valid(EsQueryDslAttrSerializer)
        # 调用EsQuery实例
        esquery = EsQuery(data)
        return Response(esquery.dsl())

    @list_route(methods=["POST"], url_path="mapping/")
    def mapping(self, request):
        """
        @api {post} /esquery/mapping/ 03_拉取-字段内容
        @apiName search_mapping
        @apiGroup 13_Esquery
        @apiParam {String} indices 结果表名称
        @apiParam {Int} [scenario_id] 查询的es类型（非必填，如传入的不是log的索引则必须传入该字段） 默认为log，蓝鲸数据平台：bkdata 原生ES：es 自由链路：log
        @apiParam {Int} [storage_cluster_id] （非必填） 当scenario_id为es时候需要传入
        @apiParam {str} [index_set_id] （非必填） 与log_search app联动的索引集编号，传入该值后indices将失效
        @apiParam {String} [start_time] 开始时间(非必填)
        @apiParam {String} [end_time] 结束时间（非必填)
        @apiParam {String} [time_zone] 时区（非必填)
            当传入时间戳，时区会默认为0时区；当start_time和end_time参数传入符合ISO-8601的字符串，则会根据时区转换，不填默认为系统时区

        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog.testwithpass",
            "storage_cluster_id": 2,
            "scenario_id": "log"
        }
        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "2_bklog_testwithpass_2019111801": {
                        "mappings": {
                            "dynamic_templates": [
                                {
                                    "strings_as_keywords": {
                                        "match_mapping_type": "string",
                                        "mapping": {
                                            "norms": "false",
                                            "type": "keyword"
                                        }
                                    }
                                }
                            ],
                            "properties": {
                                "bk_biz_id": {
                                    "type": "keyword"
                                },
                                "cloudId": {
                                    "type": "keyword"
                                },
                                "dtEventTimeStamp": {
                                    "type": "date",
                                    "format": "epoch_millis"
                                },
                                "gseIndex": {
                                    "type": "integer"
                                },
                                "iterationIndex": {
                                    "type": "integer"
                                },
                                "log": {
                                    "type": "text"
                                },
                                "path": {
                                    "type": "keyword"
                                },
                                "serverIp": {
                                    "type": "keyword"
                                },
                                "worldId": {
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                },
                {
                    "2_bklog_testwithpass_2019111601": {
                        "mappings": {
                            "dynamic_templates": [
                                {
                                    "strings_as_keywords": {
                                        "match_mapping_type": "string",
                                        "mapping": {
                                            "norms": "false",
                                            "type": "keyword"
                                        }
                                    }
                                }
                            ],
                            "properties": {
                                "bk_biz_id": {
                                    "type": "keyword"
                                },
                                "cloudId": {
                                    "type": "keyword"
                                },
                                "dtEventTimeStamp": {
                                    "type": "date",
                                    "format": "epoch_millis"
                                },
                                "gseIndex": {
                                    "type": "integer"
                                },
                                "iterationIndex": {
                                    "type": "integer"
                                },
                                "log": {
                                    "type": "text"
                                },
                                "path": {
                                    "type": "keyword"
                                },
                                "serverIp": {
                                    "type": "keyword"
                                },
                                "worldId": {
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                }
            ],
            "code": 0,
            "message": ""
        }

        """
        data = self.params_valid(EsQueryMappingAttrSerializer)
        # 调用EsQuery实例
        esquery = EsQuery(data)
        return Response(esquery.mapping())

    @list_route(methods=["POST"], url_path="scroll/")
    def scroll(self, request):
        """
        @api {post} /esquery/scroll/ 04_搜索-滚动查询
        @apiName search_scroll
        @apiGroup 13_Esquery
        @apiParam {String} indices (非必填，scenario_id为log必填)索引
        @apiParam {String} scenario_id (必填， 可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (必填)集群ID
        @apiParam {String} scroll (非必填)默认“1m”
        @apiParam {String} scroll_id (必填)scroll_id
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog_yuanshi",
            "scenario_id": "log"
            "storage_cluster_id": 11,
            "scroll": "1m",
            "scroll_id": "DnF1ZXJ5VGhlbkZldGNoDQAAAAAABhgjFkc4eXdmRENnUmxPUXRsc"
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "_scroll_id": "DnF1ZXJ5VGhlbkZldGNoDQAAAAAABi2YFkc4eXdmRENnUmxPUXRsc",
                "took": 46,
                "timed_out": false,
                "terminated_early": true,
                "_shards": {
                    "total": 13,
                    "successful": 13,
                    "skipped": 0,
                    "failed": 0
                },
                "hits": {
                    "total": {
                        "value": 1149398,
                        "relation": "eq"
                    },
                    "max_score": 1,
                    "hits": [
                        {
                            "_index": "nginx_access_log-2020.06.06",
                            "_type": "_doc",
                            "_id": "aj9piHIBJ81jTuEMr5Tj",
                            "_score": 1,
                            "_source": {
                                "responseBytes": "1164",
                                "requestMethod": "GET",
                                "path": "/data/bkee/logs/nginx/paas_fqdn_access.log",
                                "clientIP": "127.0.0.1",
                                "@timestamp": "2020-06-06T06:55:27.091Z",
                                "resposeStatus": "200",
                                "requestTime": "06/Jun/2020:14:55:27 +0800",
                                "httpHost": "-",
                            }
                        },
                        {
                            "_index": "nginx_access_log-2020.06.06",
                            "_type": "_doc",
                            "_id": "az9piHIBJ81jTuEMs5TP",
                            "_score": 1,
                            "_source": {
                                "responseBytes": "1425",
                                "requestMethod": "GET",
                                "path": "/data/bkee/logs/nginx/paas_fqdn_access.log",
                                "clientIP": "127.0.0.1",
                                "@timestamp": "2020-06-06T06:55:28.098Z",
                                "resposeStatus": "200",
                                "requestTime": "06/Jun/2020:14:55:27 +0800",
                                "httpHost": "-",
                            }
                        }
                    ]
                }
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(EsQueryScrollAttrSerializer)
        esquery = EsQuery(data)
        return Response(esquery.scroll())

    @list_route(methods=["GET"], url_path="indices/")
    def indices(self, request):
        """
        @api {get} /esquery/indices/ 05_搜索-索引列表
        @apiName search_indices
        @apiGroup 13_Esquery
        @apiParam {String} indices (非必填)索引
        @apiParam {String} scenario_id (必填，可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (scenario_id为es情况必填)集群ID
        @apiParam {int} bk_biz_id (scenario_id为log、bkdata情况必填)业务id
        @apiParam {bool} with_storage (非必填)是否查询索引集群信息，默认false
        @apiParamExample {Json} 请求参数
        {
            "indices": "nginx_access*",
            "scenario_id": "es"
            "storage_cluster_id": 11,
            "bk_biz_id": "2",
            "with_storage": ture
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": [
                {
                    "result_table_id": "nginx_access_log-20200610",
                    "result_table_name_alias": "nginx_access_log-20200610",
                    "storage_cluster_id": 11,
                    "storage_cluster_name": "es6-8"
                },
                {
                    "result_table_id": "nginx_access_log-20200613",
                    "result_table_name_alias": "nginx_access_log-20200613",
                    "storage_cluster_id": 11,
                    "storage_cluster_name": "es6-8"
                },
            ],
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(EsQueryIndicesAttrSerializer)
        esquery = EsQuery(data)
        return Response(esquery.indices())

    @list_route(methods=["GET"], url_path="cluster/")
    def cluster(self, request):
        """
        @api {get} /esquery/cluster/ 06_搜索-查询集群信息
        @apiName search_cluster
        @apiGroup 13_Esquery
        @apiParam {String} indices (scenario_id为log情况必填)索引
        @apiParam {String} scenario_id (必填，可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (scenario_id为es情况必填)集群ID
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog.yuanshi",
            "scenario_id": "log"
            "storage_cluster_id": 11
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "bk_biz_id": 2,
                "storage_cluster_id": 3,
                "storage_cluster_name": "es_cluster1"
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(EsQueryClusterInfoAttrSerializer)
        esquery = EsQuery(data)
        return Response(esquery.get_cluster_info())

    @list_route(methods=["GET"], url_path="cluster_stats/")
    def cluster_stats(self, request):
        """
        @api {get} /esquery/cluster_stats/ 搜索-查询状态信息
        @apiName cluster_stats
        @apiGroup 13_Esquery
        @apiParam {String} indices (scenario_id为log,bkdata情况必填)索引
        @apiParam {String} scenario_id (必填，可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (scenario_id为es情况必填)集群ID
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog.yuanshi",
            "scenario_id": "log"
            "storage_cluster_id": 11
            "storage_cluster_name": "eslog-sh4"
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": true,
            "data": {
                "_nodes": {
                    "total": 82,
                    "successful": 82,
                    "failed": 0
                },
                "cluster_name": "es-eslog-sh-common4",
                "timestamp": 1614856578890,
                "status": "green",
                "indices": {
                    "count": 977,
                    "shards": {
                        "total": 11090,
                        "primaries": 10192,
                        "replication": 0.08810832025117739,
                        "index": {
                            "shards": {
                                "min": 2,
                                "max": 32,
                                "avg": 11.3510747185261
                            },
                            "primaries": {
                                "min": 1,
                                "max": 16,
                                "avg": 10.431934493346981
                            },
                            "replication": {
                                "min": 0,
                                "max": 3,
                                "avg": 0.16786079836233367
                            }
                        }
                    },
                    "docs": {
                        "count": 1358587709661,
                        "deleted": 1417392
                    },
                    "store": {
                        "size_in_bytes": 252922098836872,
                        "throttle_time_in_millis": 0
                    },
                    "fielddata": {
                        "memory_size_in_bytes": 5490632,
                        "evictions": 0
                    },
                    "query_cache": {
                        "memory_size_in_bytes": 32908914744,
                        "total_count": 18720197,
                        "hit_count": 9411468,
                        "miss_count": 9308729,
                        "cache_size": 373814,
                        "cache_count": 517578,
                        "evictions": 143764
                    },
                    "completion": {
                        "size_in_bytes": 0
                    },
                    "segments": {
                        "count": 297658,
                        "memory_in_bytes": 1134391591529,
                        "terms_memory_in_bytes": 1077379476088,
                        "stored_fields_memory_in_bytes": 36122659264,
                        "term_vectors_memory_in_bytes": 0,
                        "norms_memory_in_bytes": 37045376,
                        "points_memory_in_bytes": 18117641349,
                        "doc_values_memory_in_bytes": 2734769452,
                        "index_writer_memory_in_bytes": 14649855268,
                        "version_map_memory_in_bytes": 3530465291,
                        "fixed_bit_set_memory_in_bytes": 0,
                        "max_unsafe_auto_id_timestamp": 1614855838175,
                        "file_sizes": {}
                    }
                },
                "nodes": {
                    "count": {
                        "total": 82,
                        "data": 69,
                        "coordinating_only": 0,
                        "master": 3,
                        "ingest": 82
                    },
                    "versions": [
                        "5.4.0"
                    ],
                    "os": {
                        "available_processors": 6864,
                        "allocated_processors": 1499,
                        "names": [
                            {
                                "name": "Linux",
                                "count": 82
                            }
                        ],
                        "mem": {
                            "total_in_bytes": 16752459579392,
                            "free_in_bytes": 281850990592,
                            "used_in_bytes": 16470608588800,
                            "free_percent": 2,
                            "used_percent": 98
                        }
                    },
                    "process": {
                        "cpu": {
                            "percent": 482
                        },
                        "open_file_descriptors": {
                            "min": 2232,
                            "max": 13517,
                            "avg": 10391
                        }
                    },
                    "jvm": {
                        "max_uptime_in_millis": 10483545412,
                        "versions": [
                            {
                                "version": "1.8.0_65",
                                "vm_name": "Java HotSpot(TM) 64-Bit Server VM",
                                "vm_version": "25.65-b01",
                                "vm_vendor": "Oracle Corporation",
                                "count": 82
                            }
                        ],
                        "mem": {
                            "heap_used_in_bytes": 1680712357488,
                            "heap_max_in_bytes": 2241723170816
                        },
                        "threads": 22509
                    },
                    "fs": {
                        "total_in_bytes": 477659000307712,
                        "free_in_bytes": 222069851725824,
                        "available_in_bytes": 197849403867136,
                        "spins": "true"
                    },
                    "plugins": [
                        {
                            "name": "search-guard-5",
                            "version": "5.4.0-16",
                            "description": "Provide access control related features for Elasticsearch 5",
                            "classname": "com.floragunn.searchguard.SearchGuardPlugin",
                            "has_native_controller": false
                        },
                        {
                            "name": "x-pack",
                            "version": "5.4.0",
                            "description": "Elasticsearch Expanded Pack Plugin",
                            "classname": "org.elasticsearch.xpack.XPackPlugin",
                            "has_native_controller": true
                        },
                        {
                            "name": "analysis-ik",
                            "version": "5.4.0",
                            "description": "IK Analyzer for Elasticsearch",
                            "classname": "org.elasticsearch.plugin.analysis.ik.AnalysisIkPlugin",
                            "has_native_controller": false
                        }
                    ],
                    "network_types": {
                        "transport_types": {
                            "com.floragunn.searchguard.ssl.http.netty.SearchGuardSSLNettyTransport": 82
                        },
                        "http_types": {
                            "com.floragunn.searchguard.http.SearchGuardHttpServerTransport": 82
                        }
                    }
                }
            },
            "code": 0,
            "message": ""
        }
        """
        data = self.params_valid(EsQueryClusterStatsSerializer)
        esquery = EsQuery(data)
        return Response(esquery.cluster_stats())

    @list_route(methods=["GET"], url_path="cluster_nodes_stats/")
    def cluster_nodes_stats(self, request):
        """
        @api {get} /esquery/cat_indices/ 搜索-查询节点状态信息
        @apiName cluster_nodes_stats
        @apiGroup 13_Esquery
        @apiParam {String} indices (scenario_id为log,bkdata情况必填)索引
        @apiParam {String} scenario_id (必填，可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (scenario_id为es情况必填)集群ID
        @apiParam {String} bytes 展示信息单位 b m g
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog.yuanshi",
            "scenario_id": "log"
            "storage_cluster_id": 11
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": True,
            "data":
                https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-nodes-stats.html#cluster-nodes-stats-api-response-body
            ,
            "message": ""
        }
        """
        data = self.params_valid(EsQueryCatIndicesSerializer)
        return Response(EsQuery(data).cluster_nodes_stats())

    @list_route(methods=["GET"], url_path="cat_indices/")
    def cat_indices(self, request):
        """
        @api {get} /esquery/cat_indices/ 搜索-查询索引状态信息
        @apiName cat_indices
        @apiGroup 13_Esquery
        @apiParam {String} indices (scenario_id为log,bkdata情况必填)索引
        @apiParam {String} scenario_id (必填，可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (scenario_id为es情况必填)集群ID
        @apiParam {String} bytes 展示信息单位 b m g
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog.yuanshi",
            "scenario_id": "log"
            "storage_cluster_id": 11
            "bytes": "b"
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": True,
            "data": [
            {
                "health": "green",
                "status": "open",
                "index": "706_cfm_prod_awx_idipsvrd_2021020500",
                "uuid": "D171hg7ST9mkxYIkP81TZg",
                "pri": "16",
                "rep": "0",
                "docs.count": "3019833086",
                "docs.deleted": "0",
                "store.size": "524368686486",
                "pri.store.size": "524368686486"
            }],
            "message": ""
        }
        """
        data = self.params_valid(EsQueryCatIndicesSerializer)
        return Response(EsQuery(data).cat_indices())

    @list_route(methods=["GET"], url_path="es_route/")
    def es_route(self, request):
        """
        @api {get} /esquery/es_route/ ES-转发get请求
        @apiName cat_indices
        @apiGroup 13_Esquery
        @apiParam {String} indices (scenario_id为log,bkdata情况必填)索引
        @apiParam {String} scenario_id (必填，可选范围log、es、bkdata)查询ES类型
        @apiParam {int} storage_cluster_id (scenario_id为es情况必填)集群ID
        @apiParam {String} url 需要转发的es url 只限 _cat,_cluster,_nodes
        @apiParamExample {Json} 请求参数
        {
            "indices": "2_bklog.yuanshi",
            "scenario_id": "log"
            "storage_cluster_id": 11
            "bytes": "b"
        }

        @apiSuccessExample {json} 成功返回:
        {
            "result": True,
            "data": "",
            "message": ""
        }
        """
        data = self.params_valid(EsQueryEsRouteSerializer)
        return Response(EsQuery(data).es_route())
