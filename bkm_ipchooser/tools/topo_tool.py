# -*- coding: utf-8 -*-
import logging
import typing
from collections import defaultdict
from copy import deepcopy

from django.core.cache import cache

from bkm_ipchooser import constants, types
from bkm_ipchooser.query import resource

logger = logging.getLogger("bkm_ipchooser")


class TopoTool:
    CACHE_5MIN = 5 * 60

    @staticmethod
    def find_topo_node_paths(bk_biz_id: int, node_list: typing.List[types.TreeNode]):
        def _find_topo_node_paths(
            _cur_node: types.TreeNode, _cur_path: typing.List[types.TreeNode], _hit_inst_ids: typing.Set
        ):
            if _cur_node["bk_inst_id"] in inst_id__node_map:
                inst_id__node_map[_cur_node["bk_inst_id"]]["bk_path"] = deepcopy(_cur_path)
                _hit_inst_ids.add(_cur_node["bk_inst_id"])
                # 全部命中后提前返回
                if len(_hit_inst_ids) == len(inst_id__node_map.keys()):
                    return

            for _child_node in _cur_node.get("child") or []:
                _cur_path.append(_child_node)
                _find_topo_node_paths(_child_node, _cur_path, _hit_inst_ids)
                # 以 del 代替 [:-1]，防止后者产生 list 对象导致路径重复压栈
                del _cur_path[-1]

        topo_tree: types.TreeNode = resource.ResourceQueryHelper.get_topo_tree(bk_biz_id)
        inst_id__node_map: typing.Dict[int, types.TreeNode] = {bk_node["bk_inst_id"]: bk_node for bk_node in node_list}
        _find_topo_node_paths(topo_tree, [topo_tree], set())
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
    def get_topo_tree_with_count(
        cls, bk_biz_id: int, return_all: bool = True, topo_tree: types.TreeNode = None
    ) -> types.TreeNode:
        topo_tree: types.TreeNode = topo_tree or resource.ResourceQueryHelper.get_topo_tree(
            bk_biz_id, return_all=return_all
        )

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
