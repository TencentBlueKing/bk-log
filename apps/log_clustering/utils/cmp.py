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

from django.utils.translation import ugettext_lazy as _


def cmp(src_json_obj, target_json_obj, ignore_keys=None):
    if not ignore_keys:
        ignore_keys = []
    if isinstance(src_json_obj, list):
        if not isinstance(target_json_obj, list):
            print(
                _("list类型不匹配: {src_json_obj} - {target_json_obj}").format(
                    src_json_obj=src_json_obj, target_json_obj=target_json_obj
                )
            )
            return
        if len(src_json_obj) != len(target_json_obj):
            print(
                _("数组长度不匹配: {src_json_obj} - {target_json_obj}").format(
                    src_json_obj=src_json_obj, target_json_obj=target_json_obj
                )
            )
            return
        for index, __ in enumerate(src_json_obj):
            cmp(src_json_obj[index], target_json_obj[index], ignore_keys=ignore_keys)

    if isinstance(src_json_obj, dict):
        if not isinstance(target_json_obj, dict):
            print(_("dict类型不匹配: "), src_json_obj)
            return
        for key, val in target_json_obj.items():
            if key in ignore_keys:
                continue
            if key not in src_json_obj.keys():
                print(_("源dict为:{dict} 未包含对应{key}: ").format(dict=src_json_obj, key=key))
                continue
            if isinstance(src_json_obj[key], (dict, list)):
                cmp(src_json_obj[key], target_json_obj[key], ignore_keys=ignore_keys)
                continue
            if src_json_obj[key] != val:
                print(_("源dict为:{dict} key的对应值不匹配: {key}-{val}").format(dict=src_json_obj, key=key, val=val))
                continue
