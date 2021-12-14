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
import arrow
from dateutil.parser import parse
from dateutil.rrule import rrule
from dateutil.rrule import DAILY
from dateutil import tz
from apps.log_esquery.type_constants import type_index_set_string, type_index_set_list
from apps.log_search.models import Scenario
from apps.utils.function import map_if


class QueryIndexOptimizer(object):
    def __init__(
        self,
        indices: type_index_set_string,
        scenario_id: str,
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        use_time_range: bool = True,
    ):
        self._index: str = ""
        if not indices:
            return

        indices = indices.replace(" ", "")
        result_table_id_list: List[str] = map_if(indices.split(","))
        # 根据查询场景优化index
        if scenario_id in [Scenario.BKDATA, Scenario.LOG]:
            # 日志采集使用0时区区分index入库,数据平台使用服务器所在时区
            time_zone = "GMT" if scenario_id == Scenario.LOG else tz.gettz()
            result_table_id_list = self.index_filter(result_table_id_list, start_time, end_time, time_zone)

        if not use_time_range:
            result_table_id_list = []

        self._index = ",".join(result_table_id_list)

        if not self._index:

            map_func_map = {
                Scenario.LOG: lambda x: f"{x}_*",
                Scenario.BKDATA: lambda x: f"{x}*",
                Scenario.ES: lambda x: f"{x}",
            }
            result_table_id_list: List[str] = map_if(indices.split(","), map_func_map.get(scenario_id))

            self._index = ",".join(result_table_id_list)
        if scenario_id in [Scenario.LOG]:
            self._index = self._index.replace(".", "_")

    @property
    def index(self):
        return self._index

    def index_filter(
        self, result_table_id_list: type_index_set_list, start_time: datetime, end_time: datetime, time_zone: str
    ) -> List[str]:
        # BkData索引集优化
        final_index_list: list = []
        for x in result_table_id_list:
            a_index_list: list = self.index_time_filter(x, start_time, end_time, time_zone)
            final_index_list = final_index_list + a_index_list
        return final_index_list

    def index_time_filter(
        self, index: str, date_start: datetime, date_end: datetime, time_zone: str
    ) -> type_index_set_list:
        date_start = date_start.to(time_zone).strftime("%Y%m%d000000")
        date_end = date_end.to(time_zone).strftime("%Y%m%d%H%M%S")
        now: datetime = arrow.now(time_zone).naive
        if parse(date_end) > now:
            date_end: str = now.strftime("%Y%m%d%H%M%S")

        start, end = parse(date_start), parse(date_end)
        date_day_list: List[Any] = list(rrule(DAILY, interval=1, dtstart=start, until=end))
        # date_day_list.append(end)

        date_month_list: List[Any] = list(rrule(DAILY, interval=14, dtstart=start, until=end))
        # date_month_list.append(end)

        filter_list: type_index_set_list = self._generate_filter_list(
            index, date_day_list, date_month_list, date_end, now
        )
        return list(set(filter_list))

    def _generate_filter_list(self, index, date_day_list, date_month_list, date_end, now):
        filter_list: type_index_set_list = []
        if len(date_day_list) == 1:
            if date_day_list[0].strftime("%d") != now.strftime("%d"):
                date_day_list.append(parse(date_end))
            for x in date_day_list:
                filter_list.append("{}_{}*".format(index, x.strftime("%Y%m%d")))
        elif len(date_day_list) > 1 and len(date_month_list) == 1:
            if len(date_day_list) > 14:
                for x in date_month_list:
                    filter_list.append("{}_{}*".format(index, x.strftime("%Y%m")))
            else:
                for x in date_day_list:
                    filter_list.append("{}_{}*".format(index, x.strftime("%Y%m%d")))
        elif len(date_day_list) > 1 and len(date_month_list) > 1:
            if len(date_month_list) <= 6:
                for x in date_month_list:
                    filter_list.append("{}_{}*".format(index, x.strftime("%Y%m")))
            else:
                for x in date_month_list[-6::1]:
                    filter_list.append("{}_{}*".format(index, x.strftime("%Y%m")))
        return filter_list
