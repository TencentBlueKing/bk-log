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
import copy
import json

from django.utils.translation import ugettext_lazy as _

from apps.utils.db import array_group
from apps.exceptions import ValidationError
from apps.utils.log import logger
from apps.log_databus.constants import EtlConfig, BKDATA_ES_TYPE_MAP
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.exceptions import EtlDelimiterParseException
from apps.log_databus.handlers.etl_storage.utils.transfer import preview
from apps.log_databus.constants import (
    ETL_DELIMITER_END,
    ETL_DELIMITER_DELETE,
    ETL_DELIMITER_IGNORE,
    FIELD_TEMPLATE,
)


class BkLogDelimiterEtlStorage(EtlStorage):
    etl_config = EtlConfig.BK_LOG_DELIMITER

    def etl_preview(self, data, etl_params=None) -> list:
        """
        字段提取预览
        :param data: 日志原文
        :param etl_params: 字段提取参数
        :return: 字段列表 list
        """
        if not etl_params.get("separator"):
            raise ValidationError(_("分隔符不能为空"))
        values = data.split(etl_params["separator"])

        result = []
        separator_field_list = []
        for index, key in enumerate(values):
            field_index = index + 1
            result.append({"field_index": field_index, "field_name": "", "value": values[index]})
            separator_field_list.append(f"key{field_index}")

        # 调用SDK
        etl_params["separator_field_list"] = separator_field_list
        preview_fields = preview("delimiter", data, etl_only=True, **etl_params)
        result = []
        for index, key in enumerate(separator_field_list):
            result.append({"field_index": index + 1, "field_name": "", "value": preview_fields.get(key, "")})

        return result

    def get_result_table_config(self, fields, etl_params, built_in_config, es_version="5.X"):
        """
        配置清洗入库策略，需兼容新增、编辑
        """
        # option
        option = {
            "retain_original_text": etl_params.get("retain_original_text", False),
            "separator_node_source": "data",
            "separator_node_action": etl_params.get("separator_node_action", "delimiter"),
            "separator_node_name": self.separator_node_name,
            "separator": etl_params["separator"],
            "etl_flat": etl_params.get("etl_flat", False),
        }

        if built_in_config.get("option") and isinstance(built_in_config["option"], dict):
            option = dict(built_in_config["option"], **option)

        # 根据字段列表生成separator_field_list
        # 1. 找到最大的field_index
        user_fields = {}
        max_index = 0
        for field in fields:
            field_index = int(field["field_index"])
            user_fields[str(field_index)] = field
            if field_index > max_index:
                max_index = field_index

        # 2. 生成分隔符字段列表
        separator_field_list = []
        for i in range(max_index):
            user_field = user_fields.get(str(i + 1))
            if not user_field:
                separator_field_list.append(ETL_DELIMITER_IGNORE)
            else:
                separator_field_list.append(
                    user_field["field_name"] if not user_field["is_delete"] else ETL_DELIMITER_DELETE
                )
        separator_field_list.append(ETL_DELIMITER_END)
        if len(json.dumps(separator_field_list)) >= 256:
            logger.error(f"[etl][delimiter]separator_field_list => {separator_field_list}")

        option["separator_field_list"] = separator_field_list
        result_table_fields = self.get_result_table_fields(fields, etl_params, built_in_config, es_version=es_version)

        return {
            "option": option,
            "field_list": result_table_fields["fields"],
            "time_alias_name": result_table_fields["time_field"]["alias_name"],
            "time_option": result_table_fields["time_field"]["option"],
        }

    @classmethod
    def parse_result_table_config(cls, result_table_config, result_table_storage=None):
        if not result_table_config["option"].get("separator_field_list"):
            raise EtlDelimiterParseException()

        collector_config = super().parse_result_table_config(result_table_config, result_table_storage)
        collector_fields = array_group(
            [field for field in collector_config["fields"] if not field["is_built_in"]], "field_name", 1
        )

        fields = []
        for index, key in enumerate(result_table_config["option"]["separator_field_list"]):
            if key in collector_fields:
                field_info = collector_fields[key]
                field_info["field_index"] = index + 1
                fields.append(field_info)
            elif key == ETL_DELIMITER_DELETE:
                field_info = copy.deepcopy(FIELD_TEMPLATE)
                field_info["field_index"] = index + 1
                fields.append(field_info)

        # 加上内置字段
        fields += [field for field in collector_config["fields"] if field["is_built_in"]]
        collector_config["fields"] = fields

        return collector_config

    def get_bkdata_etl_config(self, fields, etl_params, built_in_config):
        retain_original_text = etl_params.get("retain_original_text", False)
        built_in_fields = built_in_config.get("fields", [])
        result_table_fields = self.get_result_table_fields(fields, etl_params, copy.deepcopy(built_in_config))
        time_field = result_table_fields.get("time_field")
        bkdata_fields = [field for field in fields if not field["is_delete"]]
        return {
            "extract": {
                "next": {
                    "next": [
                        {
                            "next": {
                                "next": {
                                    "next": [
                                        {
                                            "next": {
                                                "next": [
                                                    {
                                                        "next": {
                                                            "next": None,
                                                            "subtype": "assign_pos",
                                                            "label": "labela2dfe3",
                                                            "assign": [
                                                                {
                                                                    # 这里是为了对齐计算平台和监控field_index与index
                                                                    "index": str(field["field_index"] - 1),
                                                                    "assign_to": field["alias_name"]
                                                                    if field["alias_name"]
                                                                    else field["field_name"],
                                                                    "type": BKDATA_ES_TYPE_MAP.get(
                                                                        field.get("option").get("es_type"), "string"
                                                                    ),
                                                                }
                                                                for field in bkdata_fields
                                                            ],
                                                            "type": "assign",
                                                        },
                                                        "label": "label5e3d6f",
                                                        "type": "fun",
                                                        "method": "split",
                                                        "args": [etl_params["separator"]],
                                                        "result": "split_log",
                                                    }
                                                ],
                                                "name": "",
                                                "label": None,
                                                "type": "branch",
                                            },
                                            "result": "log_data",
                                            "type": "access",
                                            "default_value": "",
                                            "subtype": "access_obj",
                                            "label": "labelb140",
                                            "default_type": "null",
                                            "key": "data",
                                        },
                                        {
                                            "next": None,
                                            "subtype": "assign_obj",
                                            "label": "labelb140f1",
                                            "assign": (
                                                [{"key": "data", "assign_to": "data", "type": "text"}]
                                                if retain_original_text
                                                else []
                                            )
                                            + [
                                                self._to_bkdata_assign(built_in_field)
                                                for built_in_field in built_in_fields
                                                if built_in_field.get("flat_field", False)
                                            ],
                                            "type": "assign",
                                        },
                                    ],
                                    "name": "",
                                    "type": "branch",
                                    "label": None,
                                },
                                "label": "label21ca91",
                                "type": "fun",
                                "method": "iterate",
                                "args": [],
                                "result": "iter_item",
                            },
                            "result": "item_data",
                            "type": "access",
                            "default_value": "",
                            "subtype": "access_obj",
                            "label": "label36c8ad",
                            "default_type": "null",
                            "key": "items",
                        },
                        {
                            "next": None,
                            "subtype": "assign_obj",
                            "label": "labelf676c9",
                            "assign": self._get_bkdata_default_fields(built_in_fields, time_field),
                            "type": "assign",
                        },
                    ],
                    "name": "",
                    "label": None,
                    "type": "branch",
                },
                "label": "label04a222",
                "type": "fun",
                "method": "from_json",
                "args": [],
                "result": "json_data",
            },
            "conf": self._to_bkdata_conf(time_field),
        }
