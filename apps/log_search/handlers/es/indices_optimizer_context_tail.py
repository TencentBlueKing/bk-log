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

import datetime
from typing import List, Any
from dateutil.rrule import rrule
from dateutil.rrule import DAILY
import arrow
from apps.log_esquery.type_constants import type_index_set_string, type_index_set_list
from apps.log_search.models import Scenario


class IndicesOptimizerContextTail(object):
    def __init__(
        self,
        index_set_string: type_index_set_string,
        scenario_id: str,
        dtEventTimeStamp: str = None,
        search_type_tag: str = None,
    ):
        self._index: str = ""
        if index_set_string:
            index_set_string = index_set_string.replace(" ", "")
            result_table_id_list: List[str] = index_set_string.split(",")
            result_table_id_list = [x for x in result_table_id_list if x]

            # 根据查询场景优化index
            if scenario_id in [Scenario.BKDATA, Scenario.LOG]:
                if search_type_tag == "context" and dtEventTimeStamp:
                    self._index = self.index_filter_context(dtEventTimeStamp, result_table_id_list)
                elif search_type_tag == "tail" and dtEventTimeStamp:
                    self._index = self.index_filter_tail(result_table_id_list)
            else:
                self._index = ",".join(result_table_id_list)

            if scenario_id in [Scenario.BKDATA, Scenario.LOG]:
                self._index = self._index.replace(".", "_")
            else:
                self._index = self._index

    @property
    def index(self):
        return self._index

    # 上下文查询索引集优化
    def index_filter_context(
        self,
        timestamp: str,
        result_table_id_list: type_index_set_list,
    ) -> str:
        final_index_list: list = []
        for x in result_table_id_list:
            a_index_list = self.index_time_filter_context(timestamp, x)
            final_index_list = final_index_list + a_index_list
        return ",".join(final_index_list)

    @staticmethod
    def index_time_filter_context(timestamp, index: str) -> type_index_set_list:
        filter_list: List[Any] = []
        now: datetime = arrow.utcnow().naive
        date_timestamp: datetime = arrow.get(int(timestamp) / 1000).naive
        if date_timestamp > now:
            date_end: datetime = now
        else:
            date_end: datetime = date_timestamp

        date_start: datetime = date_end - datetime.timedelta(hours=1)

        date_day_list: List[Any] = list(rrule(DAILY, interval=1, dtstart=date_start, until=date_end))
        date_day_list.append(date_end)

        for x in date_day_list:
            filter_list.append("{}_{}*".format(index, x.strftime("%Y%m%d")))

        return list(set(filter_list))

    # 实时日志索引集优化
    def index_filter_tail(self, result_table_id_list: type_index_set_list) -> str:
        final_index_list: list = []
        for x in result_table_id_list:
            a_index_list = self.index_time_filter_tail(x)
            final_index_list = final_index_list + a_index_list
        return ",".join(final_index_list)

    @staticmethod
    def index_time_filter_tail(index: str) -> type_index_set_list:
        filter_list: List[str] = []
        now: datetime = arrow.utcnow().naive
        now1hbefore: datetime = now - datetime.timedelta(hours=1)
        date_day_list: List[Any] = list(rrule(DAILY, interval=1, dtstart=now1hbefore, until=now))
        date_day_list.append(now)

        for x in date_day_list:
            filter_list.append("{}_{}*".format(index, x.strftime("%Y%m%d")))
        return list(set(filter_list))
