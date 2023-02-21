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
import re
import socket
from hashlib import md5
from typing import Union

from dataclasses import dataclass, asdict, fields
from django.core.cache import cache

from apps.log_databus.constants import (
    CHECK_COLLECTOR_CACHE_KEY_PREFIX,
    CHECK_COLLECTOR_ITEM_CACHE_TIMEOUT,
    CheckStatusEnum,
    InfoTypeEnum,
    INFO_TYPE_PREFIX_MAPPING,
)


@dataclass
class CheckResult:
    status: str
    infos: list

    to_dict = asdict

    @classmethod
    def from_dict(cls, data: dict):
        init_fields = {f.name for f in fields(cls) if f.init}
        filtered_data = {k: data.pop(k, None) for k in init_fields}
        instance = cls(**filtered_data)
        return instance


class CheckCollectorRecord:
    @staticmethod
    def generate_check_record_id(collector_config_id: int, hosts: str = None) -> str:
        """
        生成检查结果的缓存key
        :param collector_config_id: 采集项ID
        :param hosts: host字符串 example "{bk_cloud_id}:{ip},{bk_cloud_id}:{ip},{bk_cloud_id}:{ip}"
        :return: 检查结果的缓存key
        """
        generate_key_list = [str(collector_config_id)]

        if hosts:
            hosts_mapping = {}
            sorted_hosts = []
            hosts = hosts.split(",")
            for host in hosts:
                bk_cloud_id, ip = host.split(":")
                hosts_mapping.setdefault(bk_cloud_id, []).append(ip)

            for bk_cloud_id in sorted(list(hosts_mapping.keys())):
                sorted_ips = sorted(hosts_mapping[bk_cloud_id], key=socket.inet_aton)
                sorted_hosts.extend([f"{bk_cloud_id}:{ip}" for ip in sorted_ips])

            generate_key_list.extend(sorted_hosts)

        raw_record_id = "_".join(generate_key_list)
        new_md5 = md5()
        new_md5.update(raw_record_id.encode(encoding="utf-8"))
        return f"{CHECK_COLLECTOR_CACHE_KEY_PREFIX}_{new_md5.hexdigest()}"

    @classmethod
    def get_check_result(cls, check_record_id: str) -> Union[CheckResult, None]:
        cache_result = cache.get(check_record_id, None)

        result = None

        if cache_result:
            result = CheckResult.from_dict(cache_result)

        return result

    def __init__(self, check_record_id: str):
        self.check_record_id = check_record_id
        self.check_record = self.get_check_result(self.check_record_id)
        self.have_error = False

    def is_exist(self) -> bool:
        return self.check_record is not None

    def new_record(self):
        record = CheckResult(status=CheckStatusEnum.WAIT.value, infos=[])
        self.check_record = record
        self.save_check_record()
        self.have_error = False

    def save_check_record(self):
        if not self.is_exist():
            return

        cache.set(self.check_record_id, self.check_record.to_dict(), CHECK_COLLECTOR_ITEM_CACHE_TIMEOUT)

    def get_check_status(self) -> Union[str, None]:
        if not self.is_exist():
            return None
        return self.check_record.status

    def get_infos(self) -> str:
        if not self.is_exist():
            return ""
        last_info_prefix = ""
        result_infos = []
        for info in self.check_record.infos:
            match_list = re.findall(r"\[(.*?)]", info)
            info_type, info_prefix = match_list[0], match_list[1]
            if info_prefix != last_info_prefix:
                result_infos.append(f'\n{"-" * 5}{info_prefix}{"-" * 5}\n')
                last_info_prefix = info_prefix

            info = f"[{INFO_TYPE_PREFIX_MAPPING[info_type]}] {info}"

            result_infos.append(info)

        return "\n".join(result_infos)

    def append_info(self, info: str):
        if not self.is_exist():
            return

        self.check_record.infos.append(info)
        self.save_check_record()

    def append_base_info(self, info_type: str, info: str, prefix: str):
        info = f"[{info_type}][{prefix}]{info}"
        self.append_info(info)

    def append_normal_info(self, info: str, prefix: str):
        self.append_base_info(InfoTypeEnum.INFO.value, info, prefix)

    def append_warning_info(self, info: str, prefix: str):
        self.append_base_info(InfoTypeEnum.WARNING.value, info, prefix)

    def append_error_info(self, info: str, prefix: str):
        self.have_error = True
        self.append_base_info(InfoTypeEnum.ERROR.value, info, prefix)

    def change_status(self, status: str):
        self.check_record.status = status
        self.save_check_record()

    @property
    def finished(self) -> bool:
        if self.is_exist():
            return self.check_record.status == CheckStatusEnum.FINISH.value
        return False
