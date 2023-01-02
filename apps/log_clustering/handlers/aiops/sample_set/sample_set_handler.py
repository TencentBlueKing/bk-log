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
from typing import List

import arrow

from apps.log_clustering.handlers.aiops.base import BaseAiopsHandler
from apps.log_clustering.handlers.data_access.data_access import DataAccessHandler
from apps.log_clustering.handlers.aiops.sample_set.constants import (
    TIMESTAMP_FIELD_TYPE,
    TS_FILED_ATTR_TYPE,
    FEATURE_ATTR_TYPE,
)
from apps.log_clustering.handlers.aiops.sample_set.data_cls import (
    CreateSampleSetCls,
    AddResultTableToSampleSetCls,
    FieldsCls,
    AutoCollectCls,
    AutoCollectCollectConfigCls,
    AutoCollectRemoveConfigCls,
    AutoCollectCollectConfigConfigCls,
    CommitApplyCls,
    SubmitStatusCls,
    DeleteSampleSetCls,
    CollectConfigsCls,
    SampleSetInfoCls,
)
from apps.log_clustering.constants import MAX_FAILED_REQUEST_RETRY

from apps.api import BkDataAIOPSApi
from apps.api.base import DataApiRetryClass, check_result_is_true


class SampleSetHandler(BaseAiopsHandler):
    def create(self, sample_set_name: str, description: str):
        """
        创建样本集
        @param sample_set_name str 样本集名称
        @param description str 样本集说明
        """
        create_sample_set_request = CreateSampleSetCls(
            project_id=self.conf.get("project_id"),
            sample_set_name=sample_set_name,
            description=description,
            processing_cluster_id=self.conf.get("processing_cluster_id"),
            storage_cluster_id=self.conf.get("storage_cluster_id"),
        )
        request_dict = self._set_username(create_sample_set_request)
        return BkDataAIOPSApi.create_sample_set(params=request_dict)

    def add_rt_to_sample_set(self, sample_set_id: int, result_table_id: str, field_filter: List[str] = None):
        """
        把rt添加到stag表
        @param sample_set_id int 样本集id
        @param result_table_id str 结果表id
        @param field_filter List[str] rt_name过滤
        """

        rt_fields = DataAccessHandler.get_fields(result_table_id=result_table_id)
        field_index = 0
        target_fields = []
        for field in rt_fields:
            if field_filter and field["field_name"] not in field_filter:
                continue
            target_fields.append(
                FieldsCls(
                    field_name=field["field_name"],
                    field_type=field["field_type"],
                    field_alias=field["field_alias"],
                    rt_field_name=field["field_name"],
                    attr_type=TS_FILED_ATTR_TYPE if field["field_type"] == TIMESTAMP_FIELD_TYPE else FEATURE_ATTR_TYPE,
                    field_index=field_index,
                    description=field["field_name"],
                )
            )
            field_index += 1
        add_rt_to_sample_set_request = AddResultTableToSampleSetCls(
            sample_set_id=sample_set_id,
            result_table_id=result_table_id,
            fields=target_fields,
            project_id=self.conf.get("project_id"),
        )
        request_dict = self._set_username(add_rt_to_sample_set_request)
        return BkDataAIOPSApi.add_rt_to_sample_set(
            request_dict,
            data_api_retry_cls=DataApiRetryClass.create_retry_obj(
                fail_check_functions=[check_result_is_true], stop_max_attempt_number=MAX_FAILED_REQUEST_RETRY
            ),
        )

    def collect_configs(self, sample_set_id: int):
        """
        创建或更新样本采集配置
        @param sample_set_id int 样本集id
        """
        collect_config_request = CollectConfigsCls(sample_set_id=sample_set_id, project_id=self.conf.get("project_id"))
        target_time = int(arrow.now().timestamp)
        collect_config_request.collect_config["config"]["end_time"] = target_time
        collect_config_request.collect_config["config"]["start_time"] = target_time
        request_dict = self._set_username(collect_config_request)
        return BkDataAIOPSApi.collect_configs(request_dict)

    def auto_collect(self, sample_set_id: int, result_table_id: str):
        """
        创建或更新自动修改样本集配置
        @param sample_set_id int 样本集id
        @param result_table_id str 结果表id
        """
        auto_collect_request = AutoCollectCls(
            result_table_id=result_table_id,
            sample_set_id=sample_set_id,
            project_id=self.conf.get("project_id"),
            collect_config=AutoCollectCollectConfigCls(
                config=AutoCollectCollectConfigConfigCls(
                    remove_config=[
                        AutoCollectRemoveConfigCls(type="truncate_before", unit="day", index=0),
                        AutoCollectRemoveConfigCls(type="sample_size_exceed", unit="row", index=1),
                    ]
                )
            ),
        )
        request_dict = self._set_username(auto_collect_request)
        return BkDataAIOPSApi.auto_collect(request_dict)

    def apply_sample_set(self, sample_set_id: int):
        """
        执行样本集提交
        @param sample_set_id int 样本集id
        """
        apply_sample_request = CommitApplyCls(sample_set_id=sample_set_id, project_id=self.conf.get("project_id"))
        request_dict = self._set_username(apply_sample_request)
        return BkDataAIOPSApi.apply_sample_set(request_dict)

    def submit_status(self, sample_set_id: int):
        """
        轮询样本集提交状态
        @param sample_set_id int 样本集id
        """
        submit_status_request = SubmitStatusCls(sample_set_id=sample_set_id, project_id=self.conf.get("project_id"))
        request_dict = self._set_username(submit_status_request)
        return BkDataAIOPSApi.submit_status(request_dict)

    def delete_sample_set(self, sample_set_id: int):
        """
        删除样本集
        """
        delete_sample_set_request = DeleteSampleSetCls(
            sample_set_id=sample_set_id, project_id=self.conf.get("project_id"),
        )
        request_dict = self._set_username(delete_sample_set_request)
        return BkDataAIOPSApi.delete_sample_set(request_dict)

    def sample_set_info(self, sample_set_id: int):
        """
        删除样本集
        """
        sample_set_info_request = SampleSetInfoCls(sample_set_id=sample_set_id, project_id=self.conf.get("project_id"))
        request_dict = self._set_username(sample_set_info_request)
        return BkDataAIOPSApi.sample_set_info(request_dict)
