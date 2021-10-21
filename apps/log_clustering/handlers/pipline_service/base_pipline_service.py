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
from retrying import retry
from abc import ABC, abstractmethod

from pipeline.builder import Data
from pipeline.core.pipeline import Pipeline
from pipeline.service import task_service


class BasePipeLineService(ABC):
    @abstractmethod
    def build_data_context(self, params, *args, **kwargs) -> Data:
        """
        生成pipeline上下文
        @param params 原始数据对象
        """
        pass

    @abstractmethod
    def build_pipeline(self, data_context: Data, *args, **kwargs):
        """
        生成pipeline
        @param data_context pipeline context
        """
        pass

    @retry(retry_on_result=lambda val: val and not val.result)
    def start_pipeline(self, pipeline: Pipeline):
        """
        执行pipeline
        @param pipeline 生成的pipeline对象
        """
        return task_service.run_pipeline(pipeline=pipeline)
