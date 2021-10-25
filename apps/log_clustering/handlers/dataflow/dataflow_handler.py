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
from apps.api import BkDataDataFlowApi
from apps.log_clustering.handlers.aiops.base import BaseAiopsHandler
from apps.log_clustering.handlers.dataflow.data_cls import ExportFlowCls, StopFlowCls, StartFlowCls


class DataFlowHandler(BaseAiopsHandler):
    def export(self, flow_id: int):
        """
        导出flow
        @param flow_id flow id
        """
        export_request = ExportFlowCls(flow_id=flow_id)
        request_dict = self._set_username(export_request)
        return BkDataDataFlowApi.export_flow(request_dict)

    def stop(self, flow_id: int):
        """
        停止flow
        @param flow_id flow id
        """
        stop_request = StopFlowCls(flow_id=flow_id)
        request_dict = self._set_username(stop_request)
        return BkDataDataFlowApi.stop_flow(request_dict)

    def start(self, flow_id: int, consuming_mode: str, cluster_group: str):
        """
        启动flow
        @param flow_id flow id
        @param cluster_group 计算集群组
        @param consuming_mode 数据处理模式
        """
        start_request = StartFlowCls(flow_id=flow_id, consuming_mode=consuming_mode, cluster_group=cluster_group)
        request_dict = self._set_username(start_request)
        return BkDataDataFlowApi.start_flow(request_dict)

    def create_pre_treat_flow(self):
        """
        创建pre-treat flow
        """
        pass
