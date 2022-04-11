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
from apps.log_databus.constants import EsSourceType


def forwards_func(apps, schema_editor):
    feature_toggle = apps.get_model("feature_toggle", "FeatureToggle")
    feature_toggle.objects.create(
        name="es_cluster_doc",
        alias="es集群说明文档",
        status="on",
        description="es集群各种集群类型的说明文档",
        is_viewed=True,
        feature_config={
            EsSourceType.OTHER.value: {
              "help_md": "",
              "id": EsSourceType.OTHER.value,
              "name": "其他",
              "name_en": EsSourceType.OTHER.name
            },
            EsSourceType.AWS.value: {
              "help_md": "",
              "id": EsSourceType.AWS.value,
              "name": "AWS",
              "name_en": EsSourceType.AWS.name
            },
            EsSourceType.QCLOUD.value: {
              "help_md": "",
              "id": EsSourceType.QCLOUD.value,
              "name": "腾讯云",
              "name_en": EsSourceType.QCLOUD.name
            },
            EsSourceType.ALIYUN.value: {
              "help_md": "",
              "id": EsSourceType.ALIYUN.value,
              "name": "阿里云",
              "name_en": EsSourceType.ALIYUN.name
            },
            EsSourceType.GOOGLE.value: {
              "help_md": "",
              "id": EsSourceType.GOOGLE.value,
              "name": "google",
              "name_en": EsSourceType.GOOGLE.name
            },
            EsSourceType.PRIVATE.value: {
              "help_md": "",
              "id": EsSourceType.PRIVATE.value,
              "name": "私有自建",
              "name_en": EsSourceType.PRIVATE.name
            },
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("feature_toggle", "0002_auto_20210714_1040"),
    ]

    operations = [migrations.RunPython(forwards_func)]
