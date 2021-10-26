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
from celery.task import periodic_task
from celery.schedules import crontab
from concurrent.futures import ThreadPoolExecutor

from apps.log_clustering.handlers.aiops.aiops_model.aiops_model_handler import AiopsModelHandler
from apps.log_clustering.models import AiopsModel, AiopsSignatureAndPattern


@periodic_task(run_every=crontab(minute="00", hour="1"))
def sync_pattern():
    model_ids = AiopsModel.objects.all().values_list("model_id", flat=True)
    with ThreadPoolExecutor() as executor:
        executor.map(sync, model_ids)


def sync(model_id):
    release_id = get_release_id(model_id=model_id)
    if not release_id:
        return None
    patterns = get_pattern(model_id=model_id, release_id=release_id)
    created_patterns = get_created_pattern(patterns=patterns, model_id=model_id)
    AiopsSignatureAndPattern.objects.bulk_create(
        [
            AiopsSignatureAndPattern(
                model_id=model_id, signature=created_pattern["signature"], pattern=created_pattern["pattern"]
            )
            for created_pattern in created_patterns
        ]
    )


def get_release_id(model_id):
    release_info = AiopsModelHandler().aiops_release(model_id=model_id).get("list", [])
    release_ids = [info["model_release_id"] for info in release_info if info.get("publish_status") == "latest"]
    if not release_ids:
        return None
    release_id, *_ = release_ids
    return release_id


def get_pattern(model_id, release_id) -> list:
    content = AiopsModelHandler.pickle_decode(
        content=AiopsModelHandler().aiops_release_model_release_id_model_file(
            model_id=model_id, model_release_id=release_id
        )["file_content"]
    )
    patterns = []
    for _, sensitive_patterns in content[1].items():
        for sensitive_pattern in sensitive_patterns:
            signature = sensitive_pattern[5]
            pattern_list = []
            for pattern in sensitive_pattern[2]:
                if hasattr(pattern, "name"):
                    pattern_list.append("[{}]".format(pattern.name.upper()))
                    continue
                pattern_list.append(str(pattern))
            patterns.append({"signature": str(signature), "pattern": " ".join(pattern_list)})
    return patterns


def get_created_pattern(patterns, model_id):
    origin_pattern_map = {pattern["signature"]: pattern for pattern in patterns}
    existed_signature_map = set(
        AiopsSignatureAndPattern.objects.filter(model_id=model_id).values_list("signature", flat=True)
    )
    dst_patterns = []
    for origin_signature, origin_pattern in origin_pattern_map.items():
        if origin_signature not in existed_signature_map:
            dst_patterns.append(origin_pattern)
    return dst_patterns
