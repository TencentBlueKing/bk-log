# -*- coding: utf-8 -*
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
import arrow

from django.conf import settings

from apps.bk_log_admin.constants import (
    BK_DATA_CUSTOM_REPORT_USER_INDEX_SET_HISTORY,
    OPERATION_PIE_CHOICE_MAP,
    MINUTE_GROUP_BY,
)
from apps.bk_log_admin.exceptions import InitDataSourceErrorException
from apps.log_search.models import UserIndexSetSearchHistory
from apps.utils.drf import DataPageNumberPagination
from apps.models import model_to_dict
from apps.utils.lucene import generate_query_string
from apps.utils.local import get_local_param
from bk_monitor.exceptions import GetTsDataException
from bk_monitor.handler.monitor import BKMonitor
from config.domains import MONITOR_APIGATEWAY_ROOT


class IndexSetHandler(object):
    def __init__(self):
        self._client = BKMonitor(
            app_id=settings.APP_CODE,
            app_token=settings.SECRET_KEY,
            monitor_host=MONITOR_APIGATEWAY_ROOT,
            report_host=f"{settings.BKMONITOR_CUSTOM_PROXY_IP}/",
            bk_username="admin",
            bk_biz_id=settings.BLUEKING_BK_BIZ_ID,
        )

    def get_date_histogram(self, index_set_id, user_search_history_operation_time):
        """
        @param index_set_id {Int} the id of log_index_set
        @param user_search_history_operation_time {dict} the search dict
        @param user_search_history_operation_time.start_time {Str} the search begin
        @param user_search_history_operation_time.end_time the search end
        """
        start_time, end_time = self._get_start_end_time(
            user_search_history_operation_time=user_search_history_operation_time
        )
        try:
            daily_data = self._client.custom_metric().query(
                data_name=BK_DATA_CUSTOM_REPORT_USER_INDEX_SET_HISTORY,
                fields=["count(search_history_duration) as _count"],
                where_conditions=[f"index_set_id = '{index_set_id}'", f"time >= {start_time}", f"time < {end_time}"],
                group_by_conditions=[MINUTE_GROUP_BY],
            )
        except GetTsDataException:
            raise InitDataSourceErrorException()

        daily_label_list = []
        daily_data_list = []
        for data in daily_data["list"]:
            daily_label_list.append(arrow.get(data["time"] / 1000).format())
            daily_data_list.append(data["_count"])

        return {"labels": daily_label_list, "values": daily_data_list}

    def get_user_terms(self, index_set_id, user_search_history_operation_time):
        """
        @param index_set_id {Int} the id of log_index_set
        @param user_search_history_operation_time {dict} the search dict
        @param user_search_history_operation_time.start_time {Str} the search begin
        @param user_search_history_operation_time.end_time the search end
        """
        start_time, end_time = self._get_start_end_time(
            user_search_history_operation_time=user_search_history_operation_time
        )
        try:
            created_by_data = self._client.custom_metric().query(
                data_name=BK_DATA_CUSTOM_REPORT_USER_INDEX_SET_HISTORY,
                fields=["count(search_history_duration) as _count"],
                where_conditions=[f"index_set_id = '{index_set_id}'", f"time >= {start_time}", f"time < {end_time}"],
                group_by_conditions=["created_by"],
            )
        except GetTsDataException:
            raise InitDataSourceErrorException()

        created_by_label_list = []
        created_by_data_list = []
        for data in created_by_data["list"]:
            created_by_label_list.append(data["created_by"])
            created_by_data_list.append(data["_count"])

        return {"labels": created_by_label_list, "values": created_by_data_list}

    def get_duration_terms(self, index_set_id, user_search_history_operation_time):
        """
        @param index_set_id {Int} the id of log_index_set
        @param user_search_history_operation_time {dict} the search dict
        @param user_search_history_operation_time.start_time {Str} the search begin
        @param user_search_history_operation_time.end_time the search end
        """
        start_time, end_time = self._get_start_end_time(
            user_search_history_operation_time=user_search_history_operation_time
        )

        pie_label_list = []
        pie_data_list = []
        try:
            for pie_choice in OPERATION_PIE_CHOICE_MAP:
                pie_label_list.append(pie_choice["label"])
                where_conditions = [f"index_set_id = '{index_set_id}'", f"time >= {start_time}", f"time < {end_time}"]
                if "min" in pie_choice:
                    where_conditions.append(f"search_history_duration >= {pie_choice['min']}")
                if "max" in pie_choice:
                    where_conditions.append(f"search_history_duration < {pie_choice['max']}")
                pie_data = self._client.custom_metric().query(
                    data_name=BK_DATA_CUSTOM_REPORT_USER_INDEX_SET_HISTORY,
                    fields=["count(search_history_duration) as _count"],
                    where_conditions=where_conditions,
                )
                if pie_data["list"]:
                    pie_data_list.append(pie_data["list"][0]["_count"])
                    continue
                pie_data_list.append(0)
        except GetTsDataException:
            raise InitDataSourceErrorException()

        return {"labels": pie_label_list, "values": pie_data_list}

    def list_user_set_history(self, start_time, end_time, request, view, index_set_id):
        time_zone = get_local_param("time_zone")
        user_index_set_history = UserIndexSetSearchHistory.objects.filter(
            index_set_id=index_set_id,
            is_deleted=False,
            search_type="default",
            created_at__range=[
                start_time.replace(tzinfo=time_zone).datetime,
                end_time.replace(tzinfo=time_zone).datetime,
            ],
        ).order_by("-created_at", "created_by")
        pg = DataPageNumberPagination()
        page_user_index_set_history = pg.paginate_queryset(queryset=user_index_set_history, request=request, view=view)
        res = pg.get_paginated_response(
            [
                IndexSetHandler.build_query_string(
                    model_to_dict(
                        history, fields=["id", "index_set_id", "duration", "created_by", "created_at", "params"]
                    )
                )
                for history in page_user_index_set_history
            ]
        )
        return res

    @staticmethod
    def build_query_string(history):
        history["query_string"] = generate_query_string(history["params"])
        return history

    @staticmethod
    def _get_start_end_time(user_search_history_operation_time):
        time_zone = get_local_param("time_zone")
        start_time = int(
            arrow.get(user_search_history_operation_time["start_time"]).replace(tzinfo=time_zone).float_timestamp * 1000
        )
        end_time = int(
            arrow.get(user_search_history_operation_time["end_time"]).replace(tzinfo=time_zone).float_timestamp * 1000
        )
        return start_time, end_time
