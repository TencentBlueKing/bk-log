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

from django.db import migrations
from django.utils.translation import ugettext_lazy as _


SCENARIO_ID_BKDATA = "bkdata"
SCENARIO_ID_ES = "es"
SCENARIO_ID_LOG = "log"


def forwards_func(apps, schema_editor):
    # 接入场景
    scenario = apps.get_model("log_search", "AccessScenarioConfig")
    db_alias = schema_editor.connection.alias
    if not scenario.objects.using(db_alias).exists():
        scenario.objects.using(db_alias).bulk_create(
            [
                scenario(scenario_id=SCENARIO_ID_BKDATA, scenario_name=_("数据平台"), is_active=True, orders=0),
                scenario(scenario_id=SCENARIO_ID_ES, scenario_name=_("ES"), is_active=True, orders=1),
                scenario(scenario_id=SCENARIO_ID_LOG, scenario_name=_("日志文件"), is_active=False, orders=1),
            ]
        )

    # 默认数据源
    source = apps.get_model("log_search", "AccessSourceConfig")
    db_alias = schema_editor.connection.alias
    if not source.objects.filter(scenario_id=SCENARIO_ID_BKDATA):
        source.objects.using(db_alias).bulk_create(
            [source(source_name="数据平台", scenario_id=SCENARIO_ID_BKDATA, orders=0, is_editable=False)]
        )

    # 监控配置
    monitor = apps.get_model("log_search", "MonitorConfig")
    db_alias = schema_editor.connection.alias
    if not monitor.objects.using(db_alias).exists():
        monitor.objects.using(db_alias).bulk_create(
            [
                monitor(
                    monitor_id="threshold",
                    monitor_name=_("阈值监控"),
                    module_path="apps.bk_monitor.monitor.Monitor",
                    is_active=True,
                    description="蓝鲸监控",
                ),
            ]
        )


def reverse_func(apps, schema_editor):
    scenario = apps.get_model("log_search", "AccessScenarioConfig")
    db_alias = schema_editor.connection.alias
    scenario.objects.using(db_alias).delete()

    source = apps.get_model("log_search", "AccessSourceConfig")
    db_alias = schema_editor.connection.alias
    source.objects.using(db_alias).filter(scenario_id=SCENARIO_ID_BKDATA).delete()

    monitor = apps.get_model("log_search", "MonitorConfig")
    monitor.objects.using(db_alias).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_func)]
