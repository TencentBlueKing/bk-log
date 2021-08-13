# -*- coding: utf-8 -*
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
import arrow

from django.utils.translation import ugettext_lazy as _

from apps.utils.local import get_local_param
from apps.constants import UserOperationActionEnum, UserOperationTypeEnum


class AuditRecordHandler(object):
    @staticmethod
    def response_format(data: dict):
        action = UserOperationActionEnum.get_choice_label(data["action"])
        record_type = UserOperationTypeEnum.get_choice_label(data["record_type"])
        param = json.dumps(data["params"]) if data["params"] else _("空")
        time_zone = get_local_param("time_zone")
        return {
            "id": data["id"],
            "bk_biz_id": data["bk_biz_id"],
            "content": "{} {} {}：{}".format(action, record_type, _("请求内容"), param),
            "created_by": data["created_by"],
            "created_at": arrow.get(data["created_at"]).to(tz=time_zone).strftime("%Y-%m-%d %H:%M:%S%z"),
            "result": True,
            "record_type": data["record_type"],
            "action": data["action"],
            "record_object_id": data["record_object_id"],
        }
