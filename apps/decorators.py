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

"""
自定义装饰器
"""
from celery.task import task  # noqa

from apps.log_audit.models import UserOperationRecord  # noqa
from bkm_space.utils import space_uid_to_bk_biz_id  # noqa


@task
def user_operation_record(operation_record: dict):
    bk_biz_id = operation_record.get("biz_id")
    space_uid = operation_record.get("space_uid")
    if space_uid:
        bk_biz_id = space_uid_to_bk_biz_id(space_uid)
    if not bk_biz_id:
        bk_biz_id = 0
    UserOperationRecord.objects.create(
        created_by=operation_record["username"],
        bk_biz_id=bk_biz_id,
        record_type=operation_record["record_type"].value,
        record_sub_type=operation_record.get("record_sub_type", ""),
        record_object_id=operation_record["record_object_id"],
        action=operation_record["action"].value,
        params=operation_record["params"],
    )
