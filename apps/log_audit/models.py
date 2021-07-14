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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.models import JsonField


class UserOperationRecord(models.Model):
    created_at = models.DateTimeField(_("操作时间"), auto_now_add=True)
    created_by = models.CharField(_("操作者"), max_length=32)
    bk_biz_id = models.IntegerField(_("业务id"), db_index=True)
    record_type = models.CharField(_("操作对象类型"), max_length=64, db_index=True)
    record_sub_type = models.CharField(_("操作对象子类型"), max_length=64, blank=True, default="")
    record_object_id = models.IntegerField(_("操作对象id"), db_index=True)
    action = models.CharField(_("操作方法"), max_length=128)
    params = JsonField(_("请求参数"), blank=True, default="")

    class Meta:
        verbose_name = _("操作日志")
        verbose_name_plural = _("操作日志")
