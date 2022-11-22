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

from apps.log_databus.constants import EtlConfig
from apps.log_databus.handlers.etl_storage import EtlStorage
from apps.log_databus.handlers.etl_storage.utils.transfer import preview


class BkLogJsonEtlStorage(EtlStorage):
    etl_config = EtlConfig.BK_LOG_JSON

    def etl_preview(self, data, etl_params=None) -> list:
        """
        字段提取预览
        :param data: 日志原文
        :param etl_params: 字段提取参数
        :return: 字段列表 list
        """
        return preview("json", data)

    def get_result_table_config(self, fields, etl_params, built_in_config, es_version="5.X"):
        """
        配置清洗入库策略，需兼容新增、编辑
        """

        # option
        option = {
            "retain_original_text": etl_params.get("retain_original_text", False),
            "separator_node_source": "data",
            "separator_node_action": etl_params.get("separator_node_action", "json"),
            "separator_node_name": self.separator_node_name,
            "separator_fields_remove": "",
            "etl_flat": etl_params.get("etl_flat", False),
        }

        # 保存删除的字段
        remove_fields = [item["field_name"] for item in fields if item.get("is_delete", False)]
        if len(remove_fields):  # pylint:disable=len-as-condition
            option["separator_fields_remove"] = ",".join(remove_fields)

        if built_in_config.get("option") and isinstance(built_in_config["option"], dict):
            option = dict(built_in_config["option"], **option)
        result_table_fields = self.get_result_table_fields(fields, etl_params, built_in_config, es_version=es_version)

        return {
            "option": option,
            "field_list": result_table_fields["fields"],
            "time_alias_name": result_table_fields["time_field"]["alias_name"],
            "time_option": result_table_fields["time_field"]["option"],
        }

    def get_bkdata_etl_config(self, fields, etl_params, built_in_config):
        retain_original_text = etl_params.get("retain_original_text", False)
        built_in_fields = built_in_config.get("fields", [])
        result_table_fields = self.get_result_table_fields(fields, etl_params, copy.deepcopy(built_in_config))
        time_field = result_table_fields.get("time_field")
        bkdata_fields = [field for field in fields if not field["is_delete"]]
        return {
            "extract": {
                "method": "from_json",
                "next": {
                    "next": [
                        {
                            "default_value": "",
                            "default_type": "null",
                            "next": {
                                "method": "iterate",
                                "next": {
                                    "next": [
                                        {
                                            "default_value": "",
                                            "default_type": "null",
                                            "next": {
                                                "next": [
                                                    {
                                                        "method": "from_json",
                                                        "next": {
                                                            "next": None,
                                                            "subtype": "assign_obj",
                                                            "label": "labela2dfe3",
                                                            "assign": [
                                                                self._to_bkdata_assign(field) for field in bkdata_fields
                                                            ],
                                                            "type": "assign",
                                                        },
                                                        "result": "log_json",
                                                        "label": "label5e3d6f",
                                                        "args": [],
                                                        "type": "fun",
                                                    },
                                                ],
                                                "name": "",
                                                "label": None,
                                                "type": "branch",
                                            },
                                            "label": "labelb140f1",
                                            "key": "data",
                                            "result": "log_data",
                                            "subtype": "access_obj",
                                            "type": "access",
                                        },
                                        {
                                            "next": None,
                                            "subtype": "assign_obj",
                                            "label": "labelb140",
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
                                "result": "iter_item",
                                "label": "label21ca91",
                                "args": [],
                                "type": "fun",
                            },
                            "label": "label36c8ad",
                            "key": "items",
                            "result": "item_data",
                            "subtype": "access_obj",
                            "type": "access",
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
                "result": "json_data",
                "label": "label04a222",
                "args": [],
                "type": "fun",
            },
            "conf": self._to_bkdata_conf(time_field),
        }
