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
import json
import base64

from django.utils.translation import ugettext_lazy as _

from apps.api.base import DataAPI
from apps.api.modules.utils import add_esb_info_before_request
from config.domains import MONITOR_APIGATEWAY_ROOT


def get_cluster_info_after(response_result):
    """
    get_cluster_info_after
    @param response_result:
    @return:
    """
    for cluster_obj in response_result["data"]:
        if not cluster_obj.get("cluster_config"):
            continue
        parse_cluster_info(cluster_obj)
    return response_result


def create_cluster_info_before(params):
    """
    create_cluster_info_before
    @param params:
    @return:
    """
    params = add_esb_info_before_request(params)
    params["custom_option"] = json.dumps(params["custom_option"])
    return params


def register_bcs_cluster_info_before_request(params):
    """
    register_bcs_cluster_info_before_request
    @param params:
    @return:
    """
    params = add_esb_info_before_request(params)
    params["creator"] = params["bk_username"]
    return params


def get_result_table_storage_after(response_result):
    """
    get_result_table_storage_after
    @param response_result:
    @return:
    """
    for cluster_obj in response_result["data"].values():
        if not cluster_obj.get("cluster_config"):
            continue
        parse_cluster_info(cluster_obj)
    return response_result


def parse_cluster_info(cluster_obj):
    """
    parse_cluster_info
    @param cluster_obj:
    @return:
    """
    custom_option = cluster_obj["cluster_config"].get("custom_option", {})
    try:
        cluster_obj["cluster_config"]["custom_option"] = (
            json.loads(custom_option) if custom_option else {"bk_biz_id": ""}
        )

        cluster_obj["auth_info"] = json.loads(base64.b64decode(cluster_obj["auth_info"]))

        # bk_biz_id str to int
        biz_id = str(cluster_obj["cluster_config"]["custom_option"]["bk_biz_id"])
        if biz_id.isdigit():
            cluster_obj["cluster_config"]["custom_option"]["bk_biz_id"] = int(biz_id)
    except ValueError:
        cluster_obj["cluster_config"]["custom_option"] = {}
        cluster_obj["auth_info"] = {}
    return cluster_obj


def modify_result_table_before(params):
    """
    modify_result_table_before
    @param params:
    @return:
    """
    params = add_esb_info_before_request(params)
    params.update({"external_storage": {"elasticsearch": params["default_storage_config"]}})
    del params["default_storage_config"]
    return params


class _TransferApi(object):
    MODULE = _("Transfer元数据")

    def __init__(self):
        self.create_data_id = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_create_data_id/",
            module=self.MODULE,
            description=_("创建数据源"),
            before_request=add_esb_info_before_request,
        )
        self.modify_data_id = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_data_id/",
            module=self.MODULE,
            description=_("修改数据源"),
            before_request=add_esb_info_before_request,
        )
        self.modify_datasource_result_table = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_datasource_result_table/",
            module=self.MODULE,
            description=_("修改数据源与结果表的关系"),
            before_request=add_esb_info_before_request,
        )
        self.create_result_table = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_create_result_table/",
            module=self.MODULE,
            description=_("创建结果表"),
            before_request=add_esb_info_before_request,
        )
        self.delete_cluster_info = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_delete_cluster_info/",
            module=self.MODULE,
            description=_("删除存储集群"),
            before_request=add_esb_info_before_request,
        )
        self.modify_result_table = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_result_table/",
            module=self.MODULE,
            description=_("修改结果表"),
            before_request=modify_result_table_before,
        )
        self.switch_result_table = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_result_table/",
            module=self.MODULE,
            description=_("结果表起停"),
            before_request=add_esb_info_before_request,
        )
        self.get_label = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_label/",
            module=self.MODULE,
            description=_("获取数据源标签"),
            before_request=add_esb_info_before_request,
        )
        self.get_data_id = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_data_id/",
            module=self.MODULE,
            description=_("查询一个数据源的ID"),
            before_request=add_esb_info_before_request,
        )
        self.get_result_table = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_result_table/",
            module=self.MODULE,
            description=_("查询一个结果表的信息"),
            before_request=add_esb_info_before_request,
        )
        self.get_result_table_storage = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_result_table_storage/",
            module=self.MODULE,
            description=_("查询一个结果表的存储信息"),
            before_request=add_esb_info_before_request,
            after_request=get_result_table_storage_after,
        )
        self.get_cluster_info = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_cluster_info/",
            module=self.MODULE,
            description=_("查询存储集群列表"),
            before_request=add_esb_info_before_request,
            after_request=get_cluster_info_after,
        )
        self.create_cluster_info = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_create_cluster_info/",
            module=self.MODULE,
            description=_("创建存储集群"),
            before_request=create_cluster_info_before,
        )
        self.modify_cluster_info = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_cluster_info/",
            module=self.MODULE,
            description=_("修改存储集群"),
            before_request=create_cluster_info_before,
        )
        self.list_result_table = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_result_table/",
            module=self.MODULE,
            description=_("创建存储集群"),
            before_request=add_esb_info_before_request,
        )
        self.list_transfer_cluster = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_transfer_cluster/",
            module=self.MODULE,
            description=_("获取所有transfer集群信息"),
            before_request=add_esb_info_before_request,
        )

        self.create_es_snapshot_repository = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_create_es_snapshot_repository/",
            module=self.MODULE,
            description=_("创建ES快照仓库"),
            before_request=add_esb_info_before_request,
        )
        self.modify_es_snapshot_repository = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_es_snapshot_repository/",
            module=self.MODULE,
            description=_("修改ES快照仓库"),
            before_request=add_esb_info_before_request,
        )
        self.delete_es_snapshot_repository = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_delete_es_snapshot_repository/",
            module=self.MODULE,
            description=_("删除ES快照仓库"),
            before_request=add_esb_info_before_request,
        )
        self.verify_es_snapshot_repository = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_verify_es_snapshot_repository/",
            module=self.MODULE,
            description=_("验证ES快照仓库"),
            before_request=add_esb_info_before_request,
        )
        self.es_snapshot_repository = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_es_snapshot_repository/",
            module=self.MODULE,
            description=_("查看指定ES快照仓库"),
            before_request=add_esb_info_before_request,
        )
        self.list_es_snapshot_repository = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_es_snapshot_repository/",
            module=self.MODULE,
            description=_("所有快照仓库列表"),
            before_request=add_esb_info_before_request,
        )
        self.create_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_create_result_table_snapshot/",
            module=self.MODULE,
            description=_("创建结果表快照配置"),
            before_request=add_esb_info_before_request,
        )
        self.modify_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_result_table_snapshot/",
            module=self.MODULE,
            description=_("修改结果表快照配置"),
            before_request=add_esb_info_before_request,
        )
        self.delete_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_delete_result_table_snapshot/",
            module=self.MODULE,
            description=_("删除结果表快照配置"),
            before_request=add_esb_info_before_request,
        )
        self.list_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_result_table_snapshot/",
            module=self.MODULE,
            description=_("结果表快照配置列表"),
            before_request=add_esb_info_before_request,
        )
        self.list_result_table_snapshot_indices = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_result_table_snapshot_indices/",
            module=self.MODULE,
            description=_("结果表快照配置列表含物理索引"),
            before_request=add_esb_info_before_request,
        )
        self.get_result_table_snapshot_state = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_result_table_snapshot_state/",
            module=self.MODULE,
            description=_("获取结果表快照状态"),
            before_request=add_esb_info_before_request,
        )
        self.restore_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_restore_result_table_snapshot/",
            module=self.MODULE,
            description=_("快照回溯"),
            before_request=add_esb_info_before_request,
        )
        self.modify_restore_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_restore_result_table_snapshot/",
            module=self.MODULE,
            description=_("修改快照回溯"),
            before_request=add_esb_info_before_request,
        )
        self.delete_restore_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_delete_restore_result_table_snapshot/",
            module=self.MODULE,
            description=_("删除快照回溯"),
            before_request=add_esb_info_before_request,
        )
        self.list_restore_result_table_snapshot = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_restore_result_table_snapshot/",
            module=self.MODULE,
            description=_("快照回溯列表"),
            before_request=add_esb_info_before_request,
        )
        self.get_restore_result_table_snapshot_state = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_restore_result_table_snapshot_state/",
            module=self.MODULE,
            description=_("快照回溯状态"),
            before_request=add_esb_info_before_request,
        )

        # bcs operate
        self.register_bcs_cluster = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "register_bcs_cluster/",
            module=self.MODULE,
            description=_("注册bcs集群"),
            before_request=register_bcs_cluster_info_before_request,
        )
        self.list_bcs_cluster_info = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "list_bcs_cluster_info/",
            module=self.MODULE,
            description=_("list bcs集群"),
            before_request=add_esb_info_before_request,
        )
        self.apply_yaml_to_bcs_cluster = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "apply_yaml_to_bcs_cluster/",
            module=self.MODULE,
            description=_("apply yaml to bcs"),
            before_request=add_esb_info_before_request,
        )

        # space
        self.list_space_types = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_space_types/",
            module=self.MODULE,
            description=_("查询空间类型列表"),
            before_request=add_esb_info_before_request,
        )
        self.list_spaces = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_spaces/",
            module=self.MODULE,
            description=_("查询空间实例列表"),
            before_request=add_esb_info_before_request,
        )
        self.get_space_detail = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_space_detail/",
            module=self.MODULE,
            description=_("查看具体空间实例详情"),
            before_request=add_esb_info_before_request,
        )
        self.list_sticky_spaces = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_list_sticky_spaces/",
            module=self.MODULE,
            description=_("查询置顶空间实例列表"),
            before_request=add_esb_info_before_request,
        )
        self.create_log_group = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_create_log_group/",
            module=self.MODULE,
            description=_("创建自定义日志组"),
            before_request=add_esb_info_before_request,
        )
        self.modify_log_group = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_modify_log_group/",
            module=self.MODULE,
            description=_("修改自定义日志组"),
            before_request=add_esb_info_before_request,
        )
        self.get_log_group = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_log_group/",
            module=self.MODULE,
            description=_("获取自定义日志组"),
            before_request=add_esb_info_before_request,
        )


Transfer = _TransferApi()
