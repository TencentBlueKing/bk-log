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
import abc

from django.db.models import Q

from apps.api import TransferApi
from apps.iam import Permission, ResourceEnum
from apps.log_databus.constants import STORAGE_CLUSTER_TYPE, REGISTERED_SYSTEM_DEFAULT
from apps.log_databus.models import CollectorConfig
from apps.log_search.models import LogIndexSet
from bkm_space.utils import bk_biz_id_to_space_uid, space_uid_to_bk_biz_id
from iam import PathEqDjangoQuerySetConverter, make_expression, ObjectSet, DjangoQuerySetConverter
from iam.eval.constants import KEYWORD_BK_IAM_PATH_FIELD_SUFFIX, OP
from iam.resource.provider import ResourceProvider, ListResult


class BaseResourceProvider(ResourceProvider, metaclass=abc.ABCMeta):
    def list_attr(self, **options):
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        return ListResult(results=[], count=0)


class CollectionResourceProvider(BaseResourceProvider):
    def list_instance(self, filter, page, **options):
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = CollectorConfig.objects.all()
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = CollectorConfig.objects.filter(bk_biz_id=parent_id)
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True

            keywords = filter.search.get("collection", [])

            q_filter = Q()
            for keyword in keywords:
                q_filter |= Q(collector_config_name__icontains=keyword)

            queryset = CollectorConfig.objects.filter(q_filter)

        if not with_path:
            results = [
                {"id": str(item.pk), "display_name": item.collector_config_name}
                for item in queryset[page.slice_from : page.slice_to]
            ]
        else:
            results = []
            for item in queryset[page.slice_from : page.slice_to]:
                results.append(
                    {
                        "id": str(item.pk),
                        "display_name": item.collector_config_name,
                        "_bk_iam_path_": [
                            [
                                {
                                    "type": ResourceEnum.BUSINESS.id,
                                    "id": str(item.bk_biz_id),
                                    "display_name": str(item.bk_biz_id),
                                }
                            ]
                        ],
                    }
                )

        return ListResult(results=results, count=queryset.count())

    def fetch_instance_info(self, filter, **options):
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        queryset = CollectorConfig.objects.filter(pk__in=ids)

        results = [
            {"id": str(item.pk), "display_name": item.collector_config_name, "_bk_iam_approver_": item.created_by}
            for item in queryset
        ]
        return ListResult(results=results, count=queryset.count())

    def list_instance_by_policy(self, filter, page, **options):
        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        converter = PathEqDjangoQuerySetConverter(
            key_mapping={
                "collection.id": "pk",
                "collection.owner": "created_by",
                "collection._bk_iam_path_": "bk_biz_id",
            },
            value_hooks={"bk_biz_id": lambda value: value[1:-1].split(",")[1]},
        )
        filters = converter.convert(expression)
        queryset = CollectorConfig.objects.filter(filters)
        results = [
            {"id": str(item.pk), "display_name": item.collector_config_name}
            for item in queryset[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results, count=queryset.count())

    def search_instance(self, filter, page, **options):

        if not filter.parent or "id" not in filter.parent:
            queryset = CollectorConfig.objects.filter(collector_config_name__icontains=filter.keyword)
        else:
            parent_id = filter.parent.get("id")
            queryset = CollectorConfig.objects.filter(
                bk_biz_id=parent_id, collector_config_name__icontains=filter.keyword
            )

        results = [
            {"id": item.collector_config_id, "display_name": item.collector_config_name}
            for item in queryset[page.slice_from : page.slice_to]
        ]
        return ListResult(results=results, count=queryset.count())


class EsSourceResourceProvider(BaseResourceProvider):
    @classmethod
    def list_clusters(cls):
        """
        获取非系统内置集群列表
        """
        # return [
        #     {
        #         "id": "1",
        #         "display_name": "蓝鲸",
        #         "bk_biz_id": "2",
        #         "owner": "admin",
        #         "_bk_iam_path_": "/biz,2/"
        #     },
        #     {
        #         "id": "2",
        #         "display_name": "蓝鲸2",
        #         "bk_biz_id": "2",
        #         "owner": "adminxx",
        #         "_bk_iam_path_": "/biz,2/"
        #     },
        #     {
        #         "id": "3",
        #         "display_name": "test",
        #         "bk_biz_id": "3",
        #         "owner": "admin",
        #         "_bk_iam_path_": "/biz,3/"
        #     },
        #     {
        #         "id": "10",
        #         "display_name": "xxxx",
        #         "bk_biz_id": "99",
        #         "owner": "test",
        #         "_bk_iam_path_": "/biz,99/"
        #     }
        # ]

        clusters = TransferApi.get_cluster_info({"cluster_type": STORAGE_CLUSTER_TYPE, "no_request": True})
        # 过滤非内置集群，且业务ID不为空的集群
        clusters = [
            {
                "id": str(cluster["cluster_config"]["cluster_id"]),
                "display_name": cluster["cluster_config"]["cluster_name"],
                "bk_biz_id": str(cluster["cluster_config"]["custom_option"]["bk_biz_id"]),
                "owner": cluster["cluster_config"]["creator"],
                "_bk_iam_path_": "/{},{}/".format(
                    ResourceEnum.BUSINESS.id, cluster["cluster_config"]["custom_option"]["bk_biz_id"],
                ),
            }
            for cluster in clusters
            if cluster["cluster_config"].get("registered_system") != REGISTERED_SYSTEM_DEFAULT
            and cluster["cluster_config"]["custom_option"].get("bk_biz_id")
        ]
        return clusters

    def list_instance(self, filter, page, **options):
        # 获取集群信息
        clusters = self.list_clusters()

        with_path = False
        if filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                clusters = [cluster for cluster in clusters if str(cluster["bk_biz_id"]) == str(parent_id)]
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True

            keywords = filter.search.get("es_source", [])

            filtered_clusters = []
            for cluster in clusters:
                cluster_name = cluster["display_name"]
                for keyword in keywords:
                    if keyword in cluster_name:
                        filtered_clusters.append(cluster)
            clusters = filtered_clusters

        if not with_path:
            results = [
                {"id": item["id"], "display_name": item["display_name"]}
                for item in clusters[page.slice_from : page.slice_to]
            ]
        else:
            results = []
            for item in clusters[page.slice_from : page.slice_to]:
                results.append(
                    {
                        {
                            "id": item["id"],
                            "display_name": item["display_name"],
                            "_bk_iam_path_": [
                                [
                                    {
                                        "type": ResourceEnum.BUSINESS.id,
                                        "id": str(item["bk_biz_id"]),
                                        "display_name": str(item["bk_biz_id"]),
                                    }
                                ]
                            ],
                        }
                    }
                )

        return ListResult(results=results, count=len(clusters))

    def fetch_instance_info(self, filter, **options):
        clusters = self.list_clusters()

        if filter.ids:
            ids = [str(i) for i in filter.ids]
            clusters = [cluster for cluster in clusters if str(cluster["id"]) in ids]

        results = [
            {"id": item["id"], "display_name": item["display_name"], "_bk_iam_approver_": item["owner"]}
            for item in clusters
        ]
        return ListResult(results=results, count=len(clusters))

    def list_instance_by_policy(self, filter, page, **options):
        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        expr = make_expression(expression)

        clusters = self.list_clusters()
        iam_client = Permission.get_iam_client()

        filtered_clusters = []

        # 这里需要手动匹配策略... Org
        for cluster in clusters:
            obj_set = ObjectSet()
            obj_set.add_object("es_source", cluster)
            is_allowed = iam_client._eval_expr(expr, obj_set)
            if is_allowed:
                filtered_clusters.append(cluster)

        results = [
            {"id": item["id"], "display_name": item["display_name"]}
            for item in filtered_clusters[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results, count=len(filtered_clusters))

    def search_instance(self, filter, page, **options):
        clusters = self.list_clusters()
        if filter.parent and "id" in filter.parent:
            parent_id = filter.parent.get("id")
            clusters = [
                cluster
                for cluster in clusters
                if str(cluster["bk_biz_id"]) == str(parent_id)
                and filter.keyword.lower() in cluster["display_name"].lower()
            ]
        else:
            clusters = [cluster for cluster in clusters if filter.keyword.lower() in cluster["display_name"].lower()]

        return ListResult(
            results=[
                {"id": item["id"], "display_name": item["display_name"]}
                for item in clusters[page.slice_from : page.slice_to]
            ],
            count=len(clusters),
        )


class IndicesResourceProvider(BaseResourceProvider):
    class PathInDjangoQuerySetConverter(DjangoQuerySetConverter):
        def operator_map(self, operator, field, value):
            if field.endswith(KEYWORD_BK_IAM_PATH_FIELD_SUFFIX) and operator == OP.STARTS_WITH:
                return self._in

    def list_instance(self, filter, page, **options):
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = LogIndexSet.objects.all()
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = LogIndexSet.objects.filter(space_uid=bk_biz_id_to_space_uid(parent_id))
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True

            keywords = filter.search.get("indices", [])

            q_filter = Q()
            for keyword in keywords:
                q_filter |= Q(index_set_name__icontains=keyword)

            queryset = LogIndexSet.objects.filter(q_filter)

        if not with_path:
            results = [
                {"id": str(item.pk), "display_name": item.index_set_name}
                for item in queryset[page.slice_from : page.slice_to]
            ]
        else:
            results = []
            bk_biz_id_mapping = {}
            for item in queryset[page.slice_from : page.slice_to]:
                if item.space_uid not in bk_biz_id_mapping:
                    bk_biz_id_mapping[item.space_uid] = str(space_uid_to_bk_biz_id(item.space_uid))
                results.append(
                    {
                        "id": str(item.pk),
                        "display_name": item.index_set_name,
                        "_bk_iam_path_": [
                            [
                                {
                                    "type": ResourceEnum.BUSINESS.id,
                                    "id": bk_biz_id_mapping[item.space_uid],
                                    "display_name": bk_biz_id_mapping[item.space_uid],
                                }
                            ]
                        ],
                    }
                )

        return ListResult(results=results, count=queryset.count())

    def fetch_instance_info(self, filter, **options):
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        queryset = LogIndexSet.objects.filter(pk__in=ids)

        results = [
            {"id": str(item.pk), "display_name": item.index_set_name, "_bk_iam_approver_": item.created_by}
            for item in queryset
        ]
        return ListResult(results=results, count=queryset.count())

    def list_instance_by_policy(self, filter, page, **options):
        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        key_mapping = {
            "indices.id": "pk",
            "indices.owner": "created_by",
            "indices._bk_iam_path_": "space_uid",
        }
        converter = self.PathInDjangoQuerySetConverter(
            key_mapping, {"space_uid": lambda value: bk_biz_id_to_space_uid(value[1:-1].split(",")[1])}
        )
        filters = converter.convert(expression)
        queryset = LogIndexSet.objects.filter(filters)
        results = [
            {"id": str(item.pk), "display_name": item.index_set_name}
            for item in queryset[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results, count=queryset.count())

    def search_instance(self, filter, page, **options):
        if not filter.parent or "id" not in filter.parent:
            queryset = LogIndexSet.objects.filter(index_set_name__icontains=filter.keyword)
        else:
            parent_id = filter.parent.get("id")
            queryset = LogIndexSet.objects.filter(
                space_uid=bk_biz_id_to_space_uid(parent_id), index_set_name__icontains=filter.keyword
            )

        return ListResult(
            results=[
                {"id": item.index_set_id, "display_name": item.index_set_name}
                for item in queryset[page.slice_from : page.slice_to]
            ],
            count=queryset.count(),
        )
