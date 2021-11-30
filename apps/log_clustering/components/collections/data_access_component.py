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
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline.builder import ServiceActivity, Var

from apps.api import BkDataAuthApi
from apps.log_clustering.handlers.clustering_config import ClusteringConfigHandler
from apps.log_clustering.handlers.data_access.data_access import DataAccessHandler
from apps.log_clustering.models import ClusteringConfig
from apps.utils.pipline import BaseService


class ChangeDataStreamService(BaseService):
    name = _("切换数据流")

    def inputs_format(self):
        return [
            Service.InputItem(name="collector config id", key="collector_config_id", type="int", required=True),
            Service.InputItem(name="topic name", key="topic_name", type="str", required=True),
        ]

    def _execute(self, data, parent_data):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        topic_name = data.get_one_of_inputs("topic_name")
        ClusteringConfigHandler(collector_config_id=collector_config_id).change_data_stream(topic=topic_name)
        return True


class ChangeDataStreamComponent(Component):
    name = "ChangeDataStream"
    code = "change_data_stream"
    bound_service = ChangeDataStreamService


class ChangeDataStream(object):
    def __init__(self, collector_config_id: int):
        self.change_data_stream = ServiceActivity(
            component_code="change_data_stream", name=f"change_data_stream:{collector_config_id}"
        )
        self.change_data_stream.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )
        self.change_data_stream.component.inputs.topic_name = Var(type=Var.SPLICE, value="${topic_name}")


class CreateBkdataAccessService(BaseService):
    name = _("创建清洗接入")

    def inputs_format(self):
        return [
            Service.InputItem(name="collector config id", key="collector_config_id", type="int", required=True),
        ]

    def _execute(self, data, parent_data):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        DataAccessHandler().create_bkdata_access(collector_config_id=collector_config_id)
        return True


class CreateBkdataAccessComponent(Component):
    name = "CreateBkdataAccess"
    code = "create_bkdata_access"
    bound_service = CreateBkdataAccessService


class CreateBkdataAccess(object):
    def __init__(self, collector_config_id: int):
        self.create_bkdata_access = ServiceActivity(
            component_code="create_bkdata_access", name=f"create_bkdata_access:{collector_config_id}"
        )
        self.create_bkdata_access.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )


class SyncBkdataEtlService(BaseService):
    name = _("同步清洗配置到数据平台")

    def inputs_format(self):
        return [
            Service.InputItem(name="collector config id", key="collector_config_id", type="int", required=True),
        ]

    def _execute(self, data, parent_data):
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        DataAccessHandler().sync_bkdata_etl(collector_config_id=collector_config_id)
        return True


class SyncBkdataEtlComponent(Component):
    name = "SyncBkdataEtl"
    code = "sync_bkdata_etl"
    bound_service = SyncBkdataEtlService


class SyncBkdataEtl(object):
    def __init__(self, collector_config_id: int):
        self.sync_bkdata_etl = ServiceActivity(
            component_code="sync_bkdata_etl", name=f"sync_bkdata_etl:{collector_config_id}"
        )
        self.sync_bkdata_etl.component.inputs.collector_config_id = Var(type=Var.SPLICE, value="${collector_config_id}")


class AddProjectDataService(BaseService):
    name = _("项目添加rt权限")

    def inputs_format(self):
        return [
            Service.InputItem(name="collector config id", key="collector_config_id", type="int", required=True),
        ]

    def _execute(self, data, parent_data):
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        collector_config_id = data.get_one_of_inputs("collector_config_id")
        project_id = data.get_one_of_inputs("project_id")
        clustering_config = ClusteringConfig.objects.filter(collector_config_id=collector_config_id).first()
        BkDataAuthApi.add_project_data(
            params={
                "bk_biz_id": bk_biz_id,
                "object_id": clustering_config.bkdata_etl_result_table_id,
                "project_id": project_id,
            }
        )
        return True


class AddProjectDataComponent(Component):
    name = "AddProjectData"
    code = "add_project_data"
    bound_service = AddProjectDataService


class AddProjectData(object):
    def __init__(self, collector_config_id: int):
        self.add_project_data = ServiceActivity(
            component_code="add_project_data", name=f"add_project_data:{collector_config_id}"
        )
        self.add_project_data.component.inputs.bk_biz_id = Var(type=Var.SPLICE, value="${bk_biz_id}")
        self.add_project_data.component.inputs.collector_config_id = Var(
            type=Var.SPLICE, value="${collector_config_id}"
        )
        self.add_project_data.component.inputs.project_id = Var(type=Var.SPLICE, value="${project_id}")
