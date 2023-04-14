# -*- coding: utf-8 -*-
import logging
import typing

from bkm_ipchooser import constants, exceptions, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.tools.batch_request import batch_request

logger = logging.getLogger("app")


class ResourceQueryHelper:
    @staticmethod
    def fetch_biz_list(bk_biz_ids: typing.Optional[typing.List[int]] = None) -> typing.List[typing.Dict]:
        """
        查询业务列表
        :param bk_biz_ids: 业务 ID 列表
        :return: 列表 ，包含 业务ID、名字、业务运维
        """
        search_business_params = {
            # "no_request": True,
            "fields": ["bk_biz_id", "bk_biz_name", "bk_biz_maintainer"],
        }
        biz_infos: typing.List[typing.Dict] = BkApi.search_business(search_business_params)["info"]
        if not bk_biz_ids:
            return biz_infos

        # 转为 set，避免 n^2 查找
        bk_biz_ids: typing.Set[int] = set(bk_biz_ids)
        return [biz_info for biz_info in biz_infos if biz_info["bk_biz_id"] in bk_biz_ids]

    @staticmethod
    def get_topo_tree(bk_biz_id: int, return_all=False) -> types.TreeNode:
        internal_set_info: typing.Dict = BkApi.get_biz_internal_module({"bk_biz_id": bk_biz_id, "no_request": True})
        internal_topo: typing.Dict = {
            "bk_obj_name": constants.ObjectType.get_member_value__alias_map().get(constants.ObjectType.SET.value, ""),
            "bk_obj_id": constants.ObjectType.SET.value,
            "bk_inst_id": internal_set_info["bk_set_id"],
            "bk_inst_name": internal_set_info["bk_set_name"],
            "child": [],
        }

        for internal_module in internal_set_info.get("module") or []:
            internal_topo["child"].append(
                {
                    "bk_obj_name": constants.ObjectType.get_member_value__alias_map().get(
                        constants.ObjectType.MODULE.value, ""
                    ),
                    "bk_obj_id": constants.ObjectType.MODULE.value,
                    "bk_inst_id": internal_module["bk_module_id"],
                    "bk_inst_name": internal_module["bk_module_name"],
                    "child": [],
                }
            )

        if return_all:
            try:
                topo_tree: types.TreeNode = BkApi.search_biz_inst_topo({"bk_biz_id": bk_biz_id, "no_request": True})[0]
            except IndexError:
                logger.error(f"topo not exists, bk_biz_id -> {bk_biz_id}")
                raise exceptions.TopoNotExistsError(f"业务【bk_biz_id: {bk_biz_id}】拓扑不存在")

            # 补充空闲机拓扑
            topo_tree["child"] = [internal_topo] + topo_tree.get("child") or []
            return topo_tree

        return internal_topo

    @staticmethod
    def fetch_host_topo_relations(bk_biz_id: int) -> typing.List[typing.Dict]:
        host_topo_relations: typing.List[typing.Dict] = batch_request(
            func=BkApi.find_host_topo_relation,
            params={"bk_biz_id": bk_biz_id, "no_request": True},
            get_data=lambda x: x["data"],
        )
        return host_topo_relations

    @staticmethod
    def fetch_biz_hosts(
        bk_biz_id: int,
        fields: typing.List[str] = None,
        filter_obj_id: typing.Optional[str] = None,
        filter_inst_ids: typing.Optional[typing.List[int]] = None,
        host_property_filter: typing.Optional[typing.Dict] = None,
    ) -> typing.List[types.HostInfo]:

        CC_HOST_FIELDS = [
            "bk_host_id",
            "bk_agent_id",
            "bk_cloud_id",
            "bk_addressing",
            "bk_host_innerip",
            "bk_host_outerip",
            "bk_host_innerip_v6",
            "bk_host_outerip_v6",
            "bk_host_name",
            "bk_os_type",
            "bk_os_name",
            "bk_os_bit",
            "bk_os_version",
            "bk_cpu_module",
            "operator",
            "bk_bak_operator",
            "bk_isp_name",
            "bk_biz_id",
            "bk_province_name",
            "bk_state",
            "bk_state_name",
            "bk_supplier_account",
        ]

        query_params: typing.Dict[str, typing.Union[int, typing.Dict, typing.List[int]]] = {
            "bk_biz_id": bk_biz_id,
            "fields": fields or CC_HOST_FIELDS,
            "no_request": True,
        }
        if filter_inst_ids:
            query_params[f"bk_{filter_obj_id}_ids"] = filter_inst_ids
        if host_property_filter:
            query_params["host_property_filter"] = host_property_filter
        return batch_request(func=BkApi.list_biz_hosts, params=query_params)
