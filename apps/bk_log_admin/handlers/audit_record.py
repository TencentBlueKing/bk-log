# -*- coding: utf-8 -*

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
