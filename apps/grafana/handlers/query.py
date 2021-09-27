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
import copy
import re
import time
from collections import defaultdict
from functools import partial

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.api import CCApi
from apps.utils.log import logger
from apps.grafana.constants import TIME_SERIES_FIELD_TYPE, LOG_SEARCH_DIMENSION_LIST, CMDB_EXTEND_FIELDS
from apps.iam import Permission, ActionEnum, ResourceEnum
from apps.log_search.constants import GlobalCategoriesEnum
from apps.log_search.exceptions import BaseSearchIndexSetDataDoseNotExists
from apps.log_search.handlers.biz import BizHandler
from apps.log_search.handlers.search.aggs_handlers import AggsViewAdapter
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler
from apps.log_search.models import LogIndexSet, ProjectInfo, Scenario
from bk_dataview.grafana import client


class GrafanaQueryHandler:
    MINUTE_SECOND = 60

    AGG_METHOD_CHOICES = [
        {"id": "value_count", "name": "COUNT"},
        {"id": "sum", "name": "SUM"},
        {"id": "min", "name": "MIN"},
        {"id": "max", "name": "MAX"},
        {"id": "avg", "name": "AVG"},
    ]

    CONDITION_CHOICES = [
        {"id": "is", "name": "is", "placeholder": _("请输入，注意空格符号")},
        {"id": "is one of", "name": "is one of", "placeholder": _("逗号分隔")},
        {"id": "is not", "name": "is not", "placeholder": _("请输入，注意空格符号")},
        {"id": "is not one of", "name": "is not one of", "placeholder": _("逗号分隔")},
        {"id": "gt", "name": ">", "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
        {"id": "gte", "name": ">=", "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
        {"id": "lt", "name": "<", "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
        {"id": "lte", "name": "<=", "placeholder": _("请输入可以支持范围过滤字段相应的值，如整数")},
    ]

    def __init__(self, bk_biz_id: int):
        self.bk_biz_id = bk_biz_id

    @property
    def project_id(self):
        project = ProjectInfo.objects.filter(bk_biz_id=self.bk_biz_id).first()
        return project.project_id if project else None

    def _get_aggregations(self, metric_field, agg_method, dimensions, time_field, interval):
        """
        组装聚合条件
        """
        # datetime aggregation
        aggragations = {
            time_field: {
                "date_histogram": {"field": time_field, "interval": self._parse_interval(interval)},
                "aggregations": {metric_field: {agg_method: {"field": metric_field}}},
            },
        }

        # dimension aggregation
        for dimension in dimensions:
            _aggs = {dimension: {"terms": {"field": dimension, "size": 10000}}}
            _aggs[dimension]["aggregations"] = aggragations
            aggragations = _aggs

        return aggragations

    def _parse_interval(self, interval):
        if interval % self.MINUTE_SECOND != 0:
            return f"{interval}s"
        return f"{interval // self.MINUTE_SECOND}m"

    def _get_buckets(self, records, record, dimensions, aggregations, metric_field, depth=0):
        """
        解析桶
        """
        if dimensions:
            count = len(dimensions)
            buckets = aggregations.get(dimensions[depth]).get("buckets")
            dimension = dimensions[depth]
            for bucket in buckets:
                record[dimension] = bucket.get("key")
                if depth + 1 == count:
                    record[metric_field] = bucket.get(metric_field).get("value")
                    records.append(copy.deepcopy(record))
                else:
                    self._get_buckets(records, record, dimensions, bucket, metric_field, depth + 1)
        else:
            record[metric_field] = aggregations.get(metric_field).get("value")
            records.append(copy.deepcopy(record))

    def _format_time_series(self, params, data, time_field):
        """
        转换为Grafana TimeSeries的格式
        :param params: 请求参数
        :param data: [{
            "xxx": 32960991004.444443,
            "bk_target_ip": "127.0.0.1",
            "minute60": 1581350400000,
            "time": 1581350400000
        }]
        :type data: list
        :return:
        :rtype: list
        """
        formatted_data = defaultdict(list)
        for record in data:
            dimensions = tuple(
                sorted(
                    (key, value)
                    for key, value in record.items()
                    if key not in [params["metric_field"], "time", time_field, "minute{}".format(params["interval"])]
                )
            )
            formatted_data[dimensions].append([record[params["metric_field"]], record.get(time_field, 0)])

        result = []
        for dimensions, value in formatted_data.items():
            target = "{}({})".format(params["method"], params["metric_field"])
            dimension_string = ", ".join("{}={}".format(dimension[0], dimension[1]) for dimension in dimensions)

            if dimension_string:
                target += "{{{}}}".format(dimension_string)

            result.append(
                {
                    "dimensions": {dimension[0]: dimension[1] for dimension in dimensions},
                    "target": target,
                    "datapoints": value,
                }
            )

        return result

    @staticmethod
    def _get_org_id(org_name):
        """
        根据业务ID查询grafana组织ID
        """
        resp = client.get_organization_by_name(org_name)
        if resp.status_code == 200:
            _org = resp.json()
            return _org["id"]

        if resp.status_code == 404:
            resp = client.create_organization(org_name)
            _org = resp.json()
            return _org["orgId"]

    def validate_panel_config(self, dashboard_id, panel_id, index_set_id):
        """
        校验查询所使用的索引集与面板配置的索引集是否一致
        """
        if not dashboard_id or not panel_id:
            return False

        org_id = self._get_org_id(self.bk_biz_id)
        resp = client.search_dashboard(org_id, dashboard_id)

        if not resp.status_code == 200 or resp.json():
            # 仪表盘找不到，校验失败
            return False
        dashboards = resp.json()

        dashboard_uid = dashboards[0]["uid"]
        resp = client.get_dashboard_by_uid(org_id, dashboard_uid)
        if not resp.status_code == 200:
            # 返回异常，校验失败
            return False

        valid_index_set_ids = []
        dashboard_info = resp.json().get("dashboard", {})
        for outer_panel in dashboard_info.get("panels", []):
            if outer_panel["type"] == "row":
                # 如果是行类型，需要取嵌套数据
                panels = outer_panel.get("panels", [])
            else:
                panels = [outer_panel]
            for p in panels:
                if not p["id"] == panel_id:
                    continue
                for target in p["targets"]:
                    try:
                        # 尝试从数据源配置中获取到索引集ID
                        valid_index_set_ids.append(target["data"]["index"]["id"][1])
                    except Exception:  # pylint: disable=broad-except
                        pass
        return index_set_id in valid_index_set_ids

    def check_panel_permission(self, dashboard_id, panel_id, index_set_id):
        # api module not validate
        if not settings.BKAPP_IS_BKLOG_API:
            is_valid = self.validate_panel_config(dashboard_id, panel_id, index_set_id)
            if is_valid:
                return True

        # 如果视图校验不通过，则检查用户是否有索引集的检索权限
        perm = Permission()
        perm.is_allowed(
            action=ActionEnum.SEARCH_LOG,
            resources=[ResourceEnum.INDICES.create_instance(index_set_id)],
            raise_exception=True,
        )

    def query(self, query_dict: dict):
        """
        数据查询
        """
        self.check_panel_permission(query_dict["dashboard_id"], query_dict["panel_id"], query_dict["result_table_id"])

        time_field = SearchHandler(query_dict["result_table_id"], {}).time_field

        # 如果是统计数量，则无需提供指标字段，用 _id 字段统计即可
        if query_dict["method"] == "value_count":
            query_dict["metric_field"] = "_index"

        aggs = self._get_aggregations(
            metric_field=query_dict["metric_field"],
            agg_method=query_dict["method"],
            dimensions=query_dict.get("group_by", []),
            interval=query_dict["interval"],
            time_field=time_field,
        )
        search_dict = {
            "start_time": query_dict["start_time"],
            "end_time": query_dict["end_time"],
            "host_scopes": {
                "modules": [],
                "ips": ",".join([host["bk_target_ip"] for host in query_dict.get("target", [])]),
            },
            "addition": [
                {
                    "field": cond["key"],
                    "operator": cond["method"],
                    "value": ",".join(cond["value"]) if isinstance(cond["value"], list) else cond["value"],
                    "condition": cond.get("condition", "and"),
                }
                for cond in query_dict.get("where", [])
            ],
            "begin": 0,
            "size": 1,
            # "time_range": f"1m",
            "bk_biz_id": self.bk_biz_id,
            "keyword": query_dict.get("query_string", ""),
            "aggs": aggs,
        }
        search_handler = SearchHandler(query_dict["result_table_id"], search_dict)
        result = search_handler.search(search_type=None)

        all_dimensions = query_dict["group_by"][::-1] + [time_field]

        if not result["aggregations"]:
            # 无数据
            return []

        records = []
        self._get_buckets(records, {}, all_dimensions, result["aggregations"], query_dict["metric_field"])

        records = self._format_time_series(query_dict, records, search_handler.time_field)

        return records

    def query_log(self, query_dict: dict):
        """
        数据查询
        """
        self.check_panel_permission(query_dict["dashboard_id"], query_dict["panel_id"], query_dict["result_table_id"])

        time_field = SearchHandler(query_dict["result_table_id"], {}).time_field

        search_dict = {
            "start_time": query_dict["start_time"],
            "end_time": query_dict["end_time"],
            "host_scopes": {
                "modules": [],
                "ips": ",".join([host["bk_target_ip"] for host in query_dict.get("target", [])]),
            },
            "addition": [
                {
                    "field": cond["key"],
                    "operator": cond["method"],
                    "value": ",".join(cond["value"]) if isinstance(cond["value"], list) else cond["value"],
                    "condition": cond.get("condition", "and"),
                }
                for cond in query_dict.get("where", [])
            ],
            "begin": 0,
            "size": query_dict.get("size", 10),
            "bk_biz_id": self.bk_biz_id,
            "keyword": query_dict.get("query_string", ""),
        }
        search_handler = SearchHandler(query_dict["result_table_id"], search_dict)
        result = search_handler.search(search_type=None)

        # 前面的字段固定
        fields = [time_field, "log"] if "log" in result["fields"] else [time_field]

        for field in list(result["fields"].keys()):
            if field not in fields:
                fields.append(field)

        rows = [[r.get(field) for field in fields] for r in result["list"]]

        # 按照 grafana 的要求，第一个字段的名称必须为time
        fields[0] = "time"

        table = {
            "columns": [{"text": field} for field in fields],
            "rows": rows,
        }

        return table

    def get_metric_list(self, category_id=None):
        project_id = self.project_id
        if not project_id:
            return []
        index_set_list = LogIndexSet.objects.filter(project_id=project_id)

        if category_id:
            index_set_list = index_set_list.filter(category_id=category_id)

        metrics_by_category = defaultdict(list)

        scenario_name_mapping = dict(Scenario.CHOICES)

        for index_set in index_set_list:
            try:
                fields = index_set.get_fields()
            except BaseSearchIndexSetDataDoseNotExists:
                # 若无可用的索引，则忽略该索引集
                continue
            except Exception as e:  # pylint: disable=broad-except
                logger.warning(
                    "[get_metric_list] index_set({}) get_fields failed: {}".format(index_set.index_set_id, e)
                )
                continue

            if not fields:
                continue
            if not fields.get("fields", []):
                continue

            metric_conf = {
                "id": index_set.index_set_id,
                "name": index_set.index_set_name,
                "result_table_label": index_set.category_id,
                "result_table_label_name": GlobalCategoriesEnum.get_display(index_set.category_id) or _("未分类"),
                "scenario_id": index_set.scenario_id,
                "scenario_name": scenario_name_mapping.get(index_set.scenario_id, index_set.scenario_id),
                "metric_fields": [],
                "dimension_fields": [],
            }

            for field_info in fields.get("fields", []):
                field_id = field_description = field_info["field_name"]
                if field_info["description"]:
                    field_description = field_info["description"]

                if field_info["es_doc_values"] and field_info.get("field_type") != "date":
                    metric_conf["dimension_fields"].append({"id": field_id, "name": field_description})

                if all(
                    [
                        field_info["es_doc_values"],
                        field_info.get("field_type") in TIME_SERIES_FIELD_TYPE,
                        field_info.get("field_name") not in LOG_SEARCH_DIMENSION_LIST,
                    ]
                ):
                    metric_conf["metric_fields"].append({"id": field_id, "name": field_description})

            metrics_by_category[index_set.category_id].append(metric_conf)

        result = []
        for category_id, metrics in metrics_by_category.items():
            result.append(
                {"id": category_id, "name": GlobalCategoriesEnum.get_display(category_id), "children": metrics}
            )

        return result

    def get_variable_field(self, bk_obj_id):
        try:
            properties = CCApi.search_object_attribute({"bk_biz_id": self.bk_biz_id, "bk_obj_id": bk_obj_id})
        except Exception as e:  # pylint: disable=broad-except
            logger.error("[get_variable_field] request CMDB API failed for type({}): {}".format(bk_obj_id, e))
            properties = []

        data = [{"bk_property_id": p["bk_property_id"], "bk_property_name": p["bk_property_name"]} for p in properties]

        data.extend(CMDB_EXTEND_FIELDS.get(bk_obj_id, []))
        return data

    @staticmethod
    def is_single_condition_match(instance, condition_item):
        """
        校验单个条件匹配
        """
        field_name = condition_item["field"]
        method = condition_item.get("method", "eq")
        field_values = condition_item["value"]

        if field_name not in instance:
            # 如果字段不存在，则不进行过滤判断
            return True

        if not isinstance(field_values, list):
            field_values = [field_values]

        if not field_values:
            return True

        field_values = [str(field_value) for field_value in field_values if field_value]

        instance_value = instance[field_name]

        if instance_value is None:
            return True

        if method == "eq":
            # 当前等于任一字符串即匹配
            for value in field_values:
                if instance_value == value:
                    return True
            else:
                return False

        if method == "neq":
            # 当前值等于任一字符串即不匹配
            for value in field_values:
                if instance_value == value:
                    return False
            else:
                return True

        if method == "include":
            # 当前值包含任一字符串即匹配
            for value in field_values:
                if value in instance_value:
                    return True
            else:
                return False

        if method == "exclude":
            # 当前值包含任一字符串即不匹配
            for value in field_values:
                if value in instance_value:
                    return False
            else:
                return True

        if method == "reg":
            # 当前值正则匹配任一字符串
            for value in field_values:
                if re.match(value, str(instance_value)):
                    return True
            else:
                return False

        raise Exception("invalid where method: {}".format(method))

    def is_match_condition(self, instance, conditions_config):
        """
        check condition match
        """
        if not isinstance(conditions_config, (list, tuple)):
            raise Exception("Config Incorrect, Check your settings.")

        # 构造条件数据结构
        conditions = [[]]

        for c in conditions_config:
            if c.get("condition") == "or":
                conditions.append([c])
            else:
                conditions[-1].append(c)

        for condition_group in conditions:
            for cond_item in condition_group:
                if not self.is_single_condition_match(instance, cond_item):
                    # 只要有其中一个条件不满足，则跳出当前的条件组，进入下一个条件组
                    break
            else:
                # 当一个条件组中的所有条件都匹配，那么条件成立，直接返回
                return True

        # 当所有条件组都不满足时，则返回不匹配
        return False

    def _query_cmdb(self, variable_type, params):
        label_field = params["label_field"]
        value_field = params["value_field"]
        conditions_config = params.get("where", [])

        biz_handler = BizHandler(bk_biz_id=self.bk_biz_id)

        if variable_type == "host":
            host_fields = [c["field"] for c in conditions_config] + [label_field, value_field]
            instances = biz_handler.get_hosts(host_fields)
            for instance in instances:
                instance.update(instance["host"])
                instance["bk_set_ids"] = [s["id"] for s in instance["set"]]
                instance["bk_module_ids"] = [m["id"] for m in instance["module"]]
        elif variable_type == "module":
            instances = biz_handler.list_module()
        elif variable_type == "set":
            instances = biz_handler.list_set()
        else:
            return []

        value_dict = {}

        for instance in instances:

            if not self.is_match_condition(instance, conditions_config):
                continue

            label = instance.get(label_field, None)
            value = instance.get(value_field, None)

            if not value and value != 0:
                continue

            if isinstance(value, list):
                value = ",".join([str(x) for x in value])
            else:
                value = str(value)

            if not label:
                label = value
            elif isinstance(label, list):
                label = ",".join([str(x) for x in label])
            else:
                label = str(label)

            value_dict[value] = label

        return [{"label": k, "value": v} for v, k in value_dict.items()]

    def _query_dimension(self, params):
        """
        查询维度
        """
        index_set_id = params["index_set_id"]
        field = params["field"]
        query_string = params.get("query_string", "")
        where_conditions = params.get("where", [])

        timestamp = int(time.time() // 60 * 60)

        end_time = params.get("end_time", timestamp)
        start_time = params.get("start_time", timestamp - 5 * 60)

        dimension_values = self.get_dimension_values(
            index_set_id=index_set_id,
            field=field,
            start_time=start_time,
            end_time=end_time,
            query_string=query_string,
            where_conditions=where_conditions,
        )
        dimension_values = set(dimension_values)

        return [{"label": v, "value": v} for v in dimension_values]

    def get_variable_value(self, variable_type, params):
        query_cmdb = partial(self._query_cmdb, variable_type=variable_type)
        query_processor = {
            "host": query_cmdb,
            "module": query_cmdb,
            "set": query_cmdb,
            "service_instance": query_cmdb,
            "dimension": self._query_dimension,
        }

        if variable_type not in query_processor:
            return []

        result = query_processor[variable_type](params=params)
        return result

    def get_dimension_values(
        self,
        index_set_id: int,
        field: str,
        start_time: int,
        end_time: int,
        query_string: str = "",
        size: int = 500,
        where_conditions: list = None,
    ):
        data = {
            "fields": [field],
            "start_time": start_time,
            "end_time": end_time,
            "keyword": query_string,
            "size": size,
        }
        if where_conditions:
            data["addition"] = [
                {
                    "field": cond["key"],
                    "operator": cond["method"],
                    "value": ",".join(cond["value"]) if isinstance(cond["value"], list) else cond["value"],
                    "condition": cond.get("condition", "and"),
                }
                for cond in where_conditions
            ]
        result = AggsViewAdapter().terms(index_set_id, data)
        return result["aggs_items"].get(field, [])
