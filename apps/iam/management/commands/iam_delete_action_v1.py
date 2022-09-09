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

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.iam import Permission, ActionEnum
from iam.api.http import http_delete

ACTIONS_TO_UPGRADE = [
    ActionEnum.VIEW_BUSINESS,
    ActionEnum.SEARCH_LOG,
    ActionEnum.VIEW_COLLECTION,
    ActionEnum.CREATE_COLLECTION,
    ActionEnum.MANAGE_COLLECTION,
    ActionEnum.CREATE_ES_SOURCE,
    ActionEnum.MANAGE_ES_SOURCE,
    ActionEnum.CREATE_INDICES,
    ActionEnum.MANAGE_INDICES,
    ActionEnum.VIEW_DASHBOARD,
    ActionEnum.MANAGE_DASHBOARD,
    ActionEnum.MANAGE_EXTRACT_CONFIG,
]


class Command(BaseCommand):
    OPERATOR = "admin"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.iam_client = Permission.get_iam_client()
        self.system_id = settings.BK_IAM_SYSTEM_ID

    def handle(self, **options):
        """
        删除 IAM 的旧操作
        注意！！！此为高危操作，请慎用！！！
        """
        print("[delete_all_old_actions] [START]")
        for action in ACTIONS_TO_UPGRADE:
            old_action_id = action.id.replace("_v2", "")
            self.delete_action(old_action_id)
        print("[delete_all_old_actions] [END]")

    def delete_action(self, action_id):
        """
        根据操作ID删除操作策略及操作定义
        注意！！！此为高危操作，请慎用！！！
        """
        result = self.delete_action_policy(system_id=self.system_id, action_id=action_id)
        print("delete iam action policy [{}], result: {}".format(action_id, result))
        result = self.iam_client._client.batch_delete_actions(system_id=self.system_id, data=[{"id": action_id}])
        print("delete iam action [{}], result: {}".format(action_id, result))

    def delete_action_policy(self, system_id, action_id):
        path = "/api/v1/model/systems/{system_id}/actions/{action_id}/policies".format(
            system_id=system_id, action_id=action_id
        )
        ok, message, data = self.iam_client._client._call_iam_api(http_delete, path, data=None)
        return ok, message
