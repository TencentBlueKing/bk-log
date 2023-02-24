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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.log_esquery.constants import ES_ROUTE_ALLOW_URL
from apps.log_search.models import Scenario
from apps.exceptions import ValidationError
from apps.log_esquery.exceptions import (
    BaseSearchIndexSetDataDoseNotExists,
    BaseSearchIndexSetException,
    BaseSearchIndexSetIdTimeFieldException,
)

from apps.log_search.models import LogIndexSet
from apps.log_search.constants import SCROLL
from apps.utils.cache import cache_one_minute


class EsQuerySearchAttrSerializer(serializers.Serializer):
    # 通过索引集ID或获取接入场景、索引、集群ID、时间字段等配置信息
    index_set_id = serializers.IntegerField(required=False, allow_null=True)

    # 索引列表和查询类型必须
    indices = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    scenario_id = serializers.CharField(required=False, default="log", allow_null=True, allow_blank=True)
    storage_cluster_id = serializers.IntegerField(required=False, default=-1, allow_null=True)

    # 时间字段
    time_field = serializers.CharField(required=False, default="", allow_blank=True, allow_null=True)
    time_field_type = serializers.CharField(required=False, default="date", allow_blank=True, allow_null=True)
    time_field_unit = serializers.CharField(required=False, default="second", allow_blank=True, allow_null=True)

    use_time_range = serializers.BooleanField(default=True, label=_("默认使用time_range的方式检索"),)
    include_start_time = serializers.BooleanField(default=True, label=_("是否包含开始时间点(gte/gt)"))
    include_end_time = serializers.BooleanField(default=True, label=_("是否包含结束时间点(lte/lt)"))
    start_time = serializers.CharField(required=False, default="", allow_blank=True, allow_null=True)
    end_time = serializers.CharField(required=False, default="", allow_blank=True, allow_null=True)
    time_range = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)
    time_zone = serializers.CharField(required=False, allow_blank=True, default=None, allow_null=True)

    # dsl校验
    query_string = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    # ip过滤和filter条件
    filter = serializers.ListField(allow_empty=True, required=False, default=[], allow_null=True)
    # 排序
    sort_list = serializers.ListField(required=False, allow_empty=True, default=[], allow_null=True)

    # 切片
    start = serializers.IntegerField(required=False, default=0)
    size = serializers.IntegerField(required=False, default=10)

    # 用于上下文查询
    dtEventTimeStamp = serializers.CharField(required=False, default=None)
    search_type_tag = serializers.CharField(required=False, default="search")

    # 聚合透传
    aggs = serializers.DictField(required=False, default={})
    # 高亮透传
    highlight = serializers.DictField(required=False, default={})
    # 折叠查询
    collapse = serializers.DictField(required=False, default={}, allow_null=True)

    bkdata_authentication_method = serializers.CharField(required=False)
    bkdata_data_token = serializers.CharField(required=False)

    # search_after 支持
    search_after = serializers.ListField(required=False, allow_empty=True, default=[], allow_null=True)
    # 6.8之后的版本搜索可选择带该参数以返回正确total hits, 如果为5+版本将自动去掉该字段以免引发异常(在5+版本本身返回去正确的total值)
    track_total_hits = serializers.BooleanField(required=False, default=True)

    # 添加scroll参数
    scroll = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # index_set_id覆盖信息
        index_set_id = attrs.get("index_set_id")
        if index_set_id:
            index_info = _get_index_info(index_set_id)
            indices = index_info["indices"]
            scenario_id = index_info["scenario_id"]
            storage_cluster_id = index_info["storage_cluster_id"]
            time_field = index_info["time_field"]

            attrs["indices"] = indices
            attrs["scenario_id"] = scenario_id
            attrs["storage_cluster_id"] = storage_cluster_id
            attrs["time_field"] = attrs.get("time_field") or time_field
        else:
            scenario_id = attrs.get("scenario_id")
            if scenario_id in [Scenario.ES] and not attrs.get("storage_cluster_id"):
                raise ValidationError(_("第三方ES需传集群ID：storage_cluster_id"))

            # time_field
            if scenario_id in [Scenario.BKDATA, Scenario.LOG]:
                attrs["time_field"] = attrs.get("time_field") or "dtEventTimeStamp"
            elif not attrs.get("time_field"):
                raise ValidationError(_("请提供时间字段"))

        new_filter: list = self.deal_filter(attrs)
        attrs["filter"] = new_filter
        return attrs

    def deal_filter(self, attrs):
        new_filter: list = []
        _filter: list = attrs.get("filter")
        if _filter and isinstance(_filter, list):
            for __filter in _filter:
                field: str = __filter.get("key") if __filter.get("key") else __filter.get("field")
                value = __filter.get("value")
                operator: str = __filter.get("method") if __filter.get("method") else __filter.get("operator")

                if isinstance(value, list) and value:
                    value = ",".join([str(v) for v in value])

                if field and operator and value or isinstance(value, str):
                    if operator in ["is", "eq"]:
                        new_value = value
                    elif operator == "is one of":
                        # 逗号分隔是存在问题的
                        new_value = value.split(",")
                    elif operator == "is not":
                        new_value = value
                    elif operator == "is not one of":
                        new_value = value.split(",")
                    else:
                        new_value = value

                    new_filter.append(
                        {
                            "field": field,
                            "operator": operator,
                            "value": new_value,
                            "condition": __filter.get("condition", "and"),
                            "type": __filter.get("type", "field"),
                        }
                    )
                if operator in ["exists", "does not exists"]:
                    new_filter.append(
                        {
                            "field": field,
                            "operator": operator,
                            "value": "0",  # avoid post condition filter
                            "condition": __filter.get("condition", "and"),
                            "type": __filter.get("type", "field"),
                        }
                    )

        return new_filter


class EsQueryScrollAttrSerializer(serializers.Serializer):
    indices = serializers.CharField(required=False)
    scenario_id = serializers.ChoiceField(choices=Scenario.CHOICES)
    storage_cluster_id = serializers.IntegerField()
    scroll_id = serializers.CharField(required=True)
    scroll = serializers.CharField(required=False, default=SCROLL)

    def validata(self, attrs):
        super().validate(attrs)
        scenario_id = attrs.get("scenario_id")
        indices = attrs.get("indices")

        if scenario_id == Scenario.LOG and not indices:
            raise ValidationError(_("indices该字段是必填项"))

        return attrs


class EsQueryIndicesAttrSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(required=False)
    indices = serializers.CharField(required=False)
    scenario_id = serializers.ChoiceField(choices=Scenario.CHOICES)
    storage_cluster_id = serializers.IntegerField(required=False)
    with_storage = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        bk_biz_id = attrs.get("bk_biz_id")
        scenario_id = attrs.get("scenario_id")
        storage_cluster_id = attrs.get("storage_cluster_id")

        if scenario_id in [Scenario.LOG, Scenario.BKDATA] and not bk_biz_id:
            raise ValidationError(_("bk_biz_id该字段是必填项"))
        if scenario_id == Scenario.ES and not storage_cluster_id:
            raise ValidationError(_("storage_cluster_id该字段是必填项"))

        return attrs


class EsQueryClusterInfoAttrSerializer(serializers.Serializer):
    indices = serializers.CharField(required=False)
    scenario_id = serializers.ChoiceField(choices=Scenario.CHOICES)
    storage_cluster_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        scenario_id = attrs.get("scenario_id")
        indices = attrs.get("indices")
        storage_cluster_id = attrs.get("storage_cluster_id")

        if scenario_id in [Scenario.LOG, Scenario.BKDATA] and not indices:
            raise ValidationError(_("indices该字段是必填项"))
        if scenario_id == Scenario.ES and not storage_cluster_id:
            raise ValidationError(_("storage_cluster_id该字段是必填项"))

        return attrs


class EsQueryClusterStatsSerializer(serializers.Serializer):
    indices = serializers.CharField(required=False)
    scenario_id = serializers.ChoiceField(choices=Scenario.CHOICES)
    storage_cluster_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        scenario_id = attrs.get("scenario_id")
        indices = attrs.get("indices")
        storage_cluster_id = attrs.get("storage_cluster_id")

        if scenario_id in [Scenario.LOG, Scenario.BKDATA] and not indices:
            raise ValidationError(_("indices该字段是必填项"))
        if scenario_id == Scenario.ES and not storage_cluster_id:
            raise ValidationError(_("storage_cluster_id该字段是必填项"))
        return attrs


class EsQueryEsRouteSerializer(EsQueryClusterStatsSerializer):
    url = serializers.CharField(label=_("转发的url"), required=True)

    def validate_url(self, url: str):
        url = url.lstrip("/")
        for allow_url_prefix in ES_ROUTE_ALLOW_URL:
            if url.startswith(allow_url_prefix):
                if "format=" not in url and "?" not in url:
                    return f"{url}?format=json"
                if "format=" not in url:
                    return f"{url}&format=json"
                return url
        raise ValidationError(_("非法的url路径"))


class EsQueryCatIndicesSerializer(serializers.Serializer):
    indices = serializers.CharField(required=False)
    storage_cluster_id = serializers.IntegerField(required=False)
    scenario_id = serializers.ChoiceField(choices=Scenario.CHOICES)
    bytes = serializers.CharField(required=False, default="mb")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        scenario_id = attrs.get("scenario_id")
        storage_cluster_id = attrs.get("storage_cluster_id")
        indices = attrs.get("indices")

        if scenario_id == Scenario.ES and not storage_cluster_id:
            raise ValidationError(_("storage_cluster_id该字段是必填项"))
        if scenario_id == Scenario.BKDATA and not indices:
            raise ValidationError(_("indices 该字段是必填项"))
        return attrs


class EsQueryClusterNodesStatsSerializer(serializers.Serializer):
    indices = serializers.CharField(required=False)
    storage_cluster_id = serializers.IntegerField(required=False)
    scenario_id = serializers.ChoiceField(choices=Scenario.CHOICES)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        scenario_id = attrs.get("scenario_id")
        indices = attrs.get("indices")
        storage_cluster_id = attrs.get("storage_cluster_id")

        if scenario_id in [Scenario.LOG, Scenario.BKDATA] and not indices:
            raise ValidationError(_("indices该字段是必填项"))
        if scenario_id == Scenario.ES and not storage_cluster_id:
            raise ValidationError(_("storage_cluster_id该字段是必填项"))
        return attrs


class EsQueryDslAttrSerializer(serializers.Serializer):
    # 索引列表和查询类型必须
    indices = serializers.CharField(required=True)
    body = serializers.JSONField(required=True)

    scenario_id = serializers.CharField(required=False, default="log", allow_null=True, allow_blank=True)
    storage_cluster_id = serializers.IntegerField(required=False, default=-1, allow_null=True)

    bkdata_authentication_method = serializers.CharField(required=False)
    bkdata_data_token = serializers.CharField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        scenario_id = attrs.get("scenario_id")
        if scenario_id in [Scenario.ES] and not attrs.get("storage_cluster_id"):
            raise ValidationError(_("第三方ES需传集群ID：storage_cluster_id"))
        return attrs


# mapping序列化器
class EsQueryMappingAttrSerializer(serializers.Serializer):
    # 索引列表和查询类型必须
    indices = serializers.CharField(required=True)

    scenario_id = serializers.CharField(required=False, default="log", allow_null=True, allow_blank=True)
    storage_cluster_id = serializers.IntegerField(required=False, default=-1, allow_null=True)

    index_set_id = serializers.CharField(required=False, allow_blank=False, allow_null=False)

    bkdata_authentication_method = serializers.CharField(required=False)
    bkdata_data_token = serializers.CharField(required=False)

    start_time = serializers.CharField(required=False, default="", allow_blank=True, allow_null=True)
    end_time = serializers.CharField(required=False, default="", allow_blank=True, allow_null=True)
    time_zone = serializers.CharField(required=False, allow_blank=True, default=None, allow_null=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # index_set_id覆盖信息
        index_set_id = attrs.get("index_set_id")
        if index_set_id:
            index_info = _get_index_info(index_set_id)
            indices = index_info["indices"]
            scenario_id = index_info["scenario_id"]
            storage_cluster_id = index_info["storage_cluster_id"]
            time_field = index_info["time_field"]

            attrs["indices"] = indices
            attrs["scenario_id"] = scenario_id
            attrs["storage_cluster_id"] = storage_cluster_id
            attrs["time_field"] = time_field
        else:
            scenario_id = attrs.get("scenario_id")
            if scenario_id in [Scenario.ES] and not attrs.get("storage_cluster_id"):
                raise ValidationError(_("第三方ES需传集群ID：storage_cluster_id"))
        return attrs


def _get_index_info(index_set_id):
    return _init_index_info(index_set_id=index_set_id)


@cache_one_minute("esquery_index_set_info_{index_set_id}")
def _init_index_info(*, index_set_id):
    tmp_index_obj = LogIndexSet.objects.filter(index_set_id=index_set_id).first()
    if tmp_index_obj:
        scenario_id = tmp_index_obj.scenario_id
        storage_cluster_id = tmp_index_obj.storage_cluster_id
        index_set_data_obj_list = tmp_index_obj.get_indexes(has_applied=True, project_info=False)
        if len(index_set_data_obj_list) > 0:
            index = [x.get("result_table_id", None) for x in index_set_data_obj_list]
            indices = ",".join(index)
            if scenario_id not in [Scenario.BKDATA, Scenario.LOG]:
                time_field = None
                for x in index_set_data_obj_list:
                    time_field = x.get("time_field")
                    if time_field:
                        break
                time_field = time_field or tmp_index_obj.time_field
                if time_field is None:
                    raise BaseSearchIndexSetIdTimeFieldException(
                        BaseSearchIndexSetIdTimeFieldException.MESSAGE.format(index_set_id=index_set_id)
                    )
            else:
                time_field = "dtEventTimeStamp"
            return {
                "indices": indices,
                "scenario_id": scenario_id,
                "storage_cluster_id": storage_cluster_id,
                "time_field": time_field,
            }
        else:
            raise BaseSearchIndexSetDataDoseNotExists(
                BaseSearchIndexSetDataDoseNotExists.MESSAGE.format(
                    index_set_id=f"{index_set_id}_{tmp_index_obj.index_set_name}"
                )
            )
    else:
        raise BaseSearchIndexSetException(BaseSearchIndexSetException.MESSAGE.format(index_set_id=index_set_id))
