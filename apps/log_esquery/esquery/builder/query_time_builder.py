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

import datetime
from typing import Dict, Any, Tuple, Union
from apps.log_search.constants import TimeFieldTypeEnum, TimeFieldUnitEnum
from apps.log_search.exceptions import SearchUnKnowTimeFieldType


class QueryTimeBuilder(object):

    TIME_FIELD_UNIT_RATE_MAP = {
        TimeFieldUnitEnum.SECOND.value: 1,
        TimeFieldUnitEnum.MILLISECOND.value: 1000,
        TimeFieldUnitEnum.MICROSECOND.value: 1000000,
    }

    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"

    def __init__(
        self,
        time_field: str = "",
        start_time: datetime = "",
        end_time: datetime = "",
        time_field_type: str = TimeFieldTypeEnum.DATE.value,
        time_field_unit: str = TimeFieldUnitEnum.SECOND.value,
        include_start_time: bool = True,
        include_end_time: bool = True,
    ):
        self.time_field: str = time_field
        self.start_time: Union[int, datetime]
        self.end_time: Union[int, datetime]
        self.time_field_type = time_field_type
        self.time_field_unit = time_field_unit

        self._time_range_dict: Dict = {}

        self.start_time, self.end_time = self.time_serilizer(start_time, end_time)

        self.start_time_filter = self._start_time_filter(include_start_time)
        self.end_time_filter = self._end_time_filter(include_end_time)

    @property
    def time_range_dict(self):
        # 返回构建dsl的时间字典
        if self.time_field_type in ["date"]:
            self._time_range_dict.update(
                {
                    self.time_field: {
                        self.start_time_filter: self.start_time,
                        self.end_time_filter: self.end_time,
                        "format": "epoch_second",
                    }
                }
            )
            return self._time_range_dict
        if self.time_field_type in ["long"]:
            time_field_unit_rate = self.TIME_FIELD_UNIT_RATE_MAP.get(self.time_field_unit)
            if time_field_unit_rate is not None:
                self._time_range_dict.update(
                    {
                        self.time_field: {
                            self.start_time_filter: self.start_time * time_field_unit_rate,
                            self.end_time_filter: self.end_time * time_field_unit_rate,
                        }
                    }
                )
            return self._time_range_dict

        raise SearchUnKnowTimeFieldType()

    def time_serilizer(self, start_time: Any, end_time: Any) -> Tuple[Union[Any, int], Union[Any, int]]:
        # 序列化接口能够识别的时间格式
        return start_time.timestamp, end_time.timestamp

    def _start_time_filter(self, include_start_time):
        if include_start_time:
            return self.GTE
        return self.GT

    def _end_time_filter(self, include_end_time):
        if include_end_time:
            return self.LTE
        return self.LT
