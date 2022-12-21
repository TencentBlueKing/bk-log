# -*- coding: utf-8 -*-
import logging
import typing
from collections import defaultdict

from django.core.cache import cache

from bkm_ipchooser.api import BkApi
from bkm_ipchooser import constants, types
from bkm_ipchooser.query import resource

logger = logging.getLogger("bkm_ipchooser")


class TopoTool:
    CACHE_5MIN = 5 * 60

    @staticmethod
    def find_topo_node_paths(bk_biz_id: int, node_list: typing.List[types.TreeNode]):
        """
        填写节点路径, 需要格式化之后的节点列表
        """

        def _build_node_key(object_id, instance_id) -> str:
            return f"{object_id}-{instance_id}"

        params = {
            "bk_biz_id": bk_biz_id,
            "bk_nodes": [
                {
                    "bk_obj_id": node["object_id"],
                    "bk_inst_id": node["instance_id"],
                }
                for node in node_list
            ],
        }
        topo_node_paths = BkApi.find_topo_node_paths(params)
        if not topo_node_paths:
            return
        node_path_map = {}
        for topo_node_path in topo_node_paths:
            node_key = _build_node_key(topo_node_path["bk_obj_id"], topo_node_path["bk_inst_id"])
            node_path = [TopoTool.format_topo_node(bk_path) for bk_path in topo_node_path["bk_paths"][0]]
            node_path.append(TopoTool.format_topo_node(topo_node_path))
            node_path_map[node_key] = node_path

        for node in node_list:
            node_key = _build_node_key(node["object_id"], node["instance_id"])
            node["node_path"] = node_path_map[node_key]
        return node_list

    @classmethod
    def fill_host_count_to_tree(
        cls, nodes: typing.List[types.TreeNode], host_ids_gby_module_id: typing.Dict[int, typing.List[int]]
    ) -> typing.Set[int]:
        total_host_ids: typing.Set[int] = set()
        for node in nodes:
            bk_host_ids: typing.Set[int] = set()
            if node.get("bk_obj_id") == constants.ObjectType.MODULE.value:
                bk_host_ids = bk_host_ids | set(host_ids_gby_module_id.get(node["bk_inst_id"], set()))
            else:
                bk_host_ids = cls.fill_host_count_to_tree(node.get("child", []), host_ids_gby_module_id)
            node["count"] = len(bk_host_ids)
            total_host_ids = bk_host_ids | total_host_ids
        return total_host_ids

    @classmethod
    def get_topo_tree_with_count(cls, bk_biz_id: int, return_all: bool = True) -> types.TreeNode:
        topo_tree: types.TreeNode = resource.ResourceQueryHelper.get_topo_tree(bk_biz_id, return_all=return_all)

        # 这个接口较慢，缓存5min
        cache_key = f"host_topo_relations:{bk_biz_id}"
        host_topo_relations: typing.List[typing.Dict] = cache.get(cache_key)
        if not host_topo_relations:
            host_topo_relations = resource.ResourceQueryHelper.fetch_host_topo_relations(bk_biz_id)
            cache.set(cache_key, host_topo_relations, cls.CACHE_5MIN)

        host_ids_gby_module_id: typing.Dict[int, typing.List[int]] = defaultdict(list)
        for host_topo_relation in host_topo_relations:
            bk_host_id: int = host_topo_relation["bk_host_id"]
            # 暂不统计非缓存数据，遇到不一致的情况需要触发缓存更新
            host_ids_gby_module_id[host_topo_relation["bk_module_id"]].append(bk_host_id)
        cls.fill_host_count_to_tree([topo_tree], host_ids_gby_module_id)

        return topo_tree

    @classmethod
    def format_topo_node(cls, node: typing.Dict) -> typing.Dict:
        """
        格式化节点
        """
        return {
            "object_id": node["bk_obj_id"],
            "object_name": constants.ObjectType.get_member_value__alias_map().get(node["bk_obj_id"], ""),
            "instance_id": node["bk_inst_id"],
            "instance_name": node["bk_inst_name"],
        }
