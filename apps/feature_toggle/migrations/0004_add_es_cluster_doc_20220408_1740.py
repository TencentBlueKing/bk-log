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
from apps.log_databus.constants import EsSourceType, FEATURE_TOGGLE_ES_CLUSTER_TYPE


def forwards_func(apps, schema_editor):
    feature_toggle = apps.get_model("feature_toggle", "FeatureToggle")
    feature_toggle.objects.create(
        name=FEATURE_TOGGLE_ES_CLUSTER_TYPE,
        alias="集群类型配置",
        status="on",
        description="ES集群各种集群类型的说明文档",
        is_viewed=True,
        feature_config={
            EsSourceType.OTHER.value: {
                "help_md": "",
                "id": EsSourceType.OTHER.value,
                "name": "其他",
                "name_en": EsSourceType.OTHER.name,
                "button_list": []
            },
            EsSourceType.AWS.value: {
                "help_md": """# AWS

OpenSearch 是一种分布式开源搜索和分析套件，可用于一组广泛的使用案例，如实时应用程序监控、日志分析和网站搜索。OpenSearch 提供了一个高度可扩展的系统，通过集成的可视化工具 OpenSearch 控制面板为大量数据提供快速访问和响应，使用户可以轻松地探索他们的数据。与 Elasticsearch 和 Apache Solr 相同的是，OpenSearch 由 Apache Lucene 搜索库提供支持。

<a target="_blank" id="blank" url="https://aws.amazon.com/cn/opensearch-service/the-elk-stack/what-is-opensearch/">跳转AWS</a>""",
                "id": EsSourceType.AWS.value,
                "name": "AWS",
                "name_en": EsSourceType.AWS.name,
                "button_list": [
                    {
                        "type": "blank",
                        "url": "https://aws.amazon.com/cn/opensearch-service/the-elk-stack/what-is-opensearch/"
                    }
                ]
            },
            EsSourceType.QCLOUD.value: {
                "help_md": """# 腾讯云
腾讯云 Elasticsearch Service（ES）是基于开源搜索引擎 Elasticsearch 打造的高可用、可伸缩的云端全托管的 Elasticsearch 服务，包含 Kibana 及常用插件，并集成了安全、SQL、机器学习、告警、监控等高级特性（X-Pack）。使用腾讯云 ES，您可以快速部署、轻松管理、按需扩展您的集群，简化复杂运维操作，快速构建日志分析、异常监控、网站搜索、企业搜索、BI 分析等各类业务。

<a target="_blank" id="blank" url="https://cloud.tencent.com/document/product/845">跳转腾讯云</a>""",
                "id": EsSourceType.QCLOUD.value,
                "name": "腾讯云",
                "name_en": EsSourceType.QCLOUD.name,
                "button_list": [
                    {
                        "type": "blank",
                        "url": "https://cloud.tencent.com/document/product/845"
                    }
                ]
            },
            EsSourceType.ALIYUN.value: {
                "help_md": "",
                "id": EsSourceType.ALIYUN.value,
                "name": "阿里云",
                "name_en": EsSourceType.ALIYUN.name,
                "button_list": []
            },
            EsSourceType.GOOGLE.value: {
                "help_md": """# Google

Elastic 和 Google Cloud 已建立稳固的合作关系，可以帮助各种规模的企业在 Google Cloud 上部署 Elastic 企业搜索、可观测性和安全解决方案，让您能够在数分钟内从数据中获得强大的实时见解。

<a target="_blank" id="blank" url="https://www.elastic.co/cn/partners/google-cloud">跳转Goole</a>""",
                "id": EsSourceType.GOOGLE.value,
                "name": "google",
                "name_en": EsSourceType.GOOGLE.name,
                "button_list": [
                    {
                        "type": "blank",
                        "url": "https://www.elastic.co/cn/partners/google-cloud"
                    }
                ]
            },
            EsSourceType.PRIVATE.value: {
                "help_md": "",
                "id": EsSourceType.PRIVATE.value,
                "name": "私有自建",
                "name_en": EsSourceType.PRIVATE.name,
                "button_list": []
            },
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("feature_toggle", "0002_auto_20210714_1040"),
    ]

    operations = [migrations.RunPython(forwards_func)]
