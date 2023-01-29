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
from concurrent.futures import ThreadPoolExecutor
from celery.task import periodic_task
from celery.schedules import crontab

from apps.log_clustering.constants import (
    PATTERN_INDEX,
    CONTENT_PATTERN_INDEX,
    PATTERN_SIGNATURE_INDEX,
    ORIGIN_LOG_INDEX,
)
from apps.log_clustering.exceptions import ModelReleaseNotFoundException
from apps.log_clustering.handlers.aiops.aiops_model.aiops_model_handler import AiopsModelHandler
from apps.log_clustering.models import AiopsModel, AiopsSignatureAndPattern


@periodic_task(run_every=crontab(hour="*/1"))
def sync_pattern():
    model_ids = AiopsModel.objects.all().values_list("model_id", flat=True)
    with ThreadPoolExecutor() as executor:
        executor.map(sync, model_ids)


def sync(model_id):
    try:
        release_id = AiopsModelHandler().get_latest_released_id(model_id=model_id)
    except ModelReleaseNotFoundException:
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


def get_pattern(model_id, release_id) -> list:
    """
    content demo:
    [
        '...',
        {
            0.1: [
                ['if', 'checker.check'],
                3903,
                ['if', 'checker.check', '*', Variable(name="ip", value='127.0.0.1')],
                ['if checker.check():', 'if checker.check()'],
                [282. 1877],
                27886975249790003104399390262688492018705644758766193963474214767849400520551
            ]
        },
        '...',
        '...'
    ]
    sensitive_pattern [List]:
    - representative tokens: 符合pattern的其中一个分词
    - numbers: 属于该pattern的日志数量
    - pattern: 聚类模式
    - raw_log: 所有原始log,list
    - log_index： 所有原始log的index
    - log_signature: 聚类模型signature
    """
    content = AiopsModelHandler.pickle_decode(
        content=AiopsModelHandler().aiops_release_model_release_id_model_file(
            model_id=model_id, model_release_id=release_id
        )["file_content"]
    )
    patterns = []
    for _, sensitive_patterns in content[CONTENT_PATTERN_INDEX].items():
        for sensitive_pattern in sensitive_patterns:
            signature = sensitive_pattern[PATTERN_SIGNATURE_INDEX]

            if not sensitive_pattern[ORIGIN_LOG_INDEX]:
                pattern_list = []
                for pattern in sensitive_pattern[PATTERN_INDEX]:
                    if hasattr(pattern, "name"):
                        pattern_list.append("#{}#".format(pattern.name))
                        continue
                    pattern_list.append(str(pattern))
                patterns.append({"signature": str(signature), "pattern": " ".join(pattern_list)})
                continue

            origin_log = sensitive_pattern[ORIGIN_LOG_INDEX][0]
            pattern_str = ""
            for pattern in sensitive_pattern[PATTERN_INDEX]:

                if hasattr(pattern, "name"):
                    value = pattern.value
                    name = f"#{pattern.name}#"
                else:
                    value = pattern
                    name = pattern
                idx = origin_log.find(value)
                if idx == -1:
                    break
                pattern_str += origin_log[0:idx]
                pattern_str += name
                origin_log = origin_log[idx + len(value) :]
            pattern_str += origin_log
            patterns.append({"signature": str(signature), "pattern": pattern_str})
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
