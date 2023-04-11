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
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.models import OperateRecordModel


class AccessIndexSet(OperateRecordModel):
    project_id = models.IntegerField(_("项目ID"))
    index_set_id = models.IntegerField(_("索引集ID"))
    nums = models.IntegerField(_("访问次数"))
    static_date = models.DateField(_("访问日期"), db_index=True)

    class Meta:
        verbose_name = _("索引集搜索统计")
        verbose_name_plural = _("索引集搜索统计")
        unique_together = (("project_id", "index_set_id", "static_date", "created_by"),)


class MetricDataHistory(models.Model):
    metric_id = models.CharField(_("指标ID"), max_length=256)
    metric_data = models.TextField(_("指标数据"))
    updated_at = models.IntegerField(_("指标时间戳"))
