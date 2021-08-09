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
import json
import os
import subprocess

from django.utils.translation import ugettext_lazy as _
from apps.utils.log import logger
from apps.exceptions import ValidationError
from apps.log_databus import exceptions


def preview(separator_node_action, data, etl_only=False, **kwargs):
    """
    字段提取预览
    :param separator_node_action: 提取类型
    :param data: 样例数据
    :param etl_only: 是否直接返回ETL结果
    :return:
    """
    try:
        transfer_path = os.path.abspath(os.path.dirname(__file__)) + "/transfer-min"
        os.chmod(transfer_path, 0o755)
        args = [
            transfer_path,
            "test",
            "-t",
            "option.separator_node_action:{action}".format(action=separator_node_action),
            "-t",
            "option.separator_node_source:data",
            "-t",
            "option.separator_node_name:etl",
            "-f",
            "etl.type:object",
            "-f",
            "etl.option.real_path:etl",
            "-f",
            "etl.is_config_by_user:true",
            "-n",
            "flat",
        ]

        if separator_node_action == "regexp":
            args.extend(["-t", "option.separator_regexp:{}".format(kwargs.get("separator_regexp"))])
        elif separator_node_action == "delimiter":
            args.extend(["-t", 'option.separator:"{}"'.format(kwargs.get("separator"))])
            separator_field_list = kwargs.get("separator_field_list", [])
            if not isinstance(separator_field_list, list):
                raise ValidationError(_("separator_field_list类型不符合"))
            separator_field_list = json.dumps(separator_field_list)
            args.extend(["-t", f"option.separator_field_list:{separator_field_list}"])
        elif separator_node_action == "json":
            pass
        else:
            raise exceptions.EtlNotSupportedException(
                exceptions.EtlNotSupportedException.MESSAGE.format(separator_node_action=separator_node_action)
            )

        logger.info(f"[transfer][preview]{args}")

        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(
            bytes(json.dumps({"data": data}), encoding="utf8")
        )  # pylint: disable=unused-variable

        p.poll()
        result = json.loads(stdout)["result"][0]
        data = json.loads(result)["etl"]

        if etl_only:
            return data

        return [{"field_name": k, "value": v} for k, v in data.items()]
    except Exception as error:
        logger.exception(f"字段提取异常: {error})")
        raise exceptions.EtlPreviewException
