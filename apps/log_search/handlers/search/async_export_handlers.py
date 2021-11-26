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
import copy
import json

from rest_framework.reverse import reverse
from django.utils.http import urlencode

from apps.utils.local import get_request, get_request_language_code
from apps.log_search.constants import (
    MAX_ASYNC_COUNT,
    ASYNC_COUNT_SIZE,
)
from apps.log_search.exceptions import MissAsyncExportException
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler
from apps.log_search.models import AsyncTask, ProjectInfo
from apps.log_search.tasks.async_export import async_export


class AsyncExportHandlers(object):
    def __init__(self, index_set_id: int, search_dict: dict):
        self.index_set_id = index_set_id
        self.search_dict = search_dict
        self.search_handler = SearchHandler(index_set_id=self.index_set_id, search_dict=copy.deepcopy(self.search_dict))

    def async_export(self):
        # 判断fields是否支持
        fields = self._pre_check_fields()
        # 判断result是否符合要求
        result = self.search_handler.pre_get_result(sorted_fields=fields["async_export_fields"], size=ASYNC_COUNT_SIZE)
        # 判断是否超过支持异步的最大次数
        if result["hits"]["total"] > MAX_ASYNC_COUNT:
            self.search_handler.size = MAX_ASYNC_COUNT

        async_task = AsyncTask.objects.create(
            **{
                "request_param": self.search_dict,
                "sorted_param": fields["async_export_fields"],
                "scenario_id": self.search_handler.scenario_id,
                "index_set_id": self.index_set_id,
            }
        )

        url = self._get_url()
        search_url = self._get_search_url()

        async_export.delay(
            search_handler=self.search_handler,
            sorted_fields=fields["async_export_fields"],
            async_task_id=async_task.id,
            url_path=url,
            search_url_path=search_url,
            language=get_request_language_code(),
        )
        return async_task.id

    def _pre_check_fields(self):
        fields = self.search_handler.fields()
        for config in fields["config"]:
            if config["name"] == "async_export":
                if not config["is_active"]:
                    raise MissAsyncExportException(config["extra"]["usable_reason"])
                return {"async_export_fields": config["extra"]["fields"]}

    def _get_url(self):
        url = reverse("tasks-download-file", request=get_request())
        return url

    def _get_search_url(self):
        request = get_request()
        project_id = ProjectInfo.objects.get(bk_biz_id=self.search_dict["bk_biz_id"]).project_id
        search_dict = copy.deepcopy(self.search_dict)
        search_dict["projectId"] = project_id
        if "host_scopes" in search_dict:
            search_dict["host_scopes"] = json.dumps(search_dict["host_scopes"])

        if "addition" in search_dict:
            search_dict["addition"] = json.dumps(search_dict["addition"])

        if "bk_biz_id" in search_dict:
            search_dict["bizId"] = search_dict["bk_biz_id"]

        url_params = urlencode(search_dict)
        # 这里是为了拼接前端检索请求
        search_url = f"{request.scheme}://{request.get_host()}/#/retrieve/{self.index_set_id}?{url_params}"
        return search_url
