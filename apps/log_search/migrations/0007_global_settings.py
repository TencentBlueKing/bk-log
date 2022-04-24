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
初始化globalConfig信息
"""

from django.db import migrations

from apps.log_search.constants import (
    GlobalTypeEnum,
    EncodingsEnum,
)


def forwards_func(apps, schema_editor):

    global_object = apps.get_model("log_search", "GlobalConfig")
    db_alias = schema_editor.connection.alias
    if not global_object.objects.using(db_alias).exists():
        bulk_create_list = [
            # 初始化字符编码
            global_object(config_id=GlobalTypeEnum.DATA_ENCODING.value, configs=EncodingsEnum.get_choices_list_dict())
        ]
        global_object.objects.using(db_alias).bulk_create(bulk_create_list)


def reverse_func(apps, schema_editor):
    global_object = apps.get_model("log_search", "GlobalConfig")
    db_alias = schema_editor.connection.alias
    global_object.objects.using(db_alias).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0006_globalconfig"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_func)]
