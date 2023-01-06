# -*- coding: utf-8 -*-
import typing

from pypinyin import lazy_pinyin

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.query import resource
from bkm_ipchooser.tools.topo_tool import TopoTool


class BaseHandler:
    @staticmethod
    def get_meta_data(bk_biz_id: int) -> types.MetaData:
        return {"scope_type": constants.ScopeType.BIZ.value, "scope_id": str(bk_biz_id), "bk_biz_id": bk_biz_id}

    @classmethod
    def format_hosts(cls, hosts: typing.List[types.HostInfo], bk_biz_id: int) -> typing.List[types.FormatHostInfo]:
        """
        格式化主机信息
        :param hosts: 尚未进行格式化处理的主机信息
        :return: 格式化后的主机列表
        """
        biz_id__info_map: typing.Dict[int, typing.Dict] = {
            biz_info["bk_biz_id"]: biz_info for biz_info in resource.ResourceQueryHelper.fetch_biz_list()
        }

        # TODO: 暂不支持 >1000
        resp = BkApi.search_cloud_area({"page": {"start": 0, "limit": 1000}})

        if resp.get("info"):
            cloud_id__info_map: typing.Dict[int, typing.Dict] = {
                cloud_info["bk_cloud_id"]: cloud_info["bk_cloud_name"] for cloud_info in resp["info"]
            }
        else:
            # 默认存在直连区域
            cloud_id__info_map = {
                constants.DEFAULT_CLOUD: {
                    "bk_cloud_id": constants.DEFAULT_CLOUD,
                    "bk_cloud_name": constants.DEFAULT_CLOUD_NAME,
                }
            }

        formatted_hosts: typing.List[types.HostInfo] = []
        for host in hosts:
            bk_cloud_id = host["bk_cloud_id"]
            formatted_hosts.append(
                {
                    "meta": BaseHandler.get_meta_data(bk_biz_id),
                    "host_id": host["bk_host_id"],
                    "ip": host["bk_host_innerip"],
                    "ipv6": host.get("bk_host_innerip_v6", ""),
                    "cloud_id": host["bk_cloud_id"],
                    "cloud_vendor": host.get("bk_cloud_vendor", ""),
                    "agent_id": host.get("bk_agent_id", ""),
                    "host_name": host["bk_host_name"],
                    "os_name": host["bk_os_name"],
                    "os_type": host["bk_os_type"],
                    "alive": host.get("status"),
                    "cloud_area": {"id": bk_cloud_id, "name": cloud_id__info_map.get(bk_cloud_id, bk_cloud_id)},
                    "biz": {
                        "id": bk_biz_id,
                        "name": biz_id__info_map.get(bk_biz_id, {}).get("bk_biz_name", bk_biz_id),
                    },
                    # 暂不需要的字段，留作扩展
                    "bk_mem": host["bk_mem"],
                    "bk_disk": host["bk_disk"],
                    "bk_cpu": host["bk_cpu"],
                    # "bk_cpu_architecture": host["bk_cpu_architecture"],
                    # "bk_cpu_module": host["bk_cpu_module"],
                }
            )

        return formatted_hosts

    @classmethod
    def format_host_id_infos(
        cls, hosts: typing.List[types.HostInfo], bk_biz_id: int
    ) -> typing.List[types.FormatHostInfo]:
        """
        格式化主机信息
        :param hosts: 尚未进行格式化处理的主机信息
        :return: 格式化后的主机列表
        """

        formatted_hosts: typing.List[types.HostInfo] = []
        for host in hosts:
            formatted_hosts.append(
                {
                    "meta": BaseHandler.get_meta_data(bk_biz_id),
                    "host_id": host["bk_host_id"],
                    "ip": host["bk_host_innerip"],
                    "ipv6": host.get("bk_host_innerip_v6"),
                    "cloud_id": host["bk_cloud_id"],
                }
            )

        return formatted_hosts

    @classmethod
    def sort_by_name(cls, datas: typing.List[typing.Dict]):
        # 按照名称排序
        # 用在 动态拓扑, 服务模板, 集群模板
        datas.sort(key=lambda g: lazy_pinyin(g["name"]))

    @classmethod
    def fill_node_path(cls, bk_biz_id: int, node_list: typing.List[typing.Dict[str, typing.Any]]):
        """
        填充前端需要的节点路径格式
        """
        result = []
        if not node_list:
            return result

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
            return result

        node_path_map = {}
        for topo_node_path in topo_node_paths:
            node_key = _build_node_key(topo_node_path["bk_obj_id"], topo_node_path["bk_inst_id"])
            node_path = [TopoTool.format_topo_node(bk_path) for bk_path in topo_node_path["bk_paths"][0]]
            node_path.append(TopoTool.format_topo_node(topo_node_path))
            node_path_map[node_key] = node_path

        for node in node_list:
            node_key = _build_node_key(node["object_id"], node["instance_id"])
            node["node_path"] = node_path_map[node_key]

        return result
