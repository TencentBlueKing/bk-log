# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Any

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.tools.batch_request import request_multi_thread, batch_request
from bkm_ipchooser.handlers.base import BaseHandler
from bkm_ipchooser.handlers.topo_handler import TopoHandler

logger = logging.getLogger("bkm_ipchooser")


class DynamicGroupHandler:
    """动态分组处理器"""

    def __init__(self, scope_list: types.ScopeList) -> None:
        # 暂时不支持多业务同时查询
        self.bk_biz_id = [scope["bk_biz_id"] for scope in scope_list][0]
        self.meta = BaseHandler.get_meta_data(self.bk_biz_id)

    def list(self, dynamic_group_list: List[Dict] = None) -> List[types.DynamicGroup]:
        """获取动态分组列表"""
        dynamic_group_ids = [dynamic_group["id"] for dynamic_group in dynamic_group_list]
        params = {"bk_biz_id": self.bk_biz_id, "no_request": True}
        groups = batch_request(func=BkApi.search_dynamic_group, params=params)
        if not groups:
            return groups
        if dynamic_group_ids:
            groups = [group for group in groups if group["id"] in dynamic_group_ids]
        # 排序并添加是否最近更新标签
        BaseHandler.sort_by_name(groups)
        return self._format_dynamic_groups(groups)

    def _format_dynamic_groups(self, groups: List[Dict]) -> List[Dict]:
        """格式化获取动态分组列表的返回"""
        groups = [
            {
                "id": group["id"],
                "name": group["name"],
                "meta": self.meta,
                "last_time": group["last_time"],
                # TODO: 当需要支持动态分组为集群时, 去掉这个注释
                # "object_id": group["bk_obj_id"],
                # "object_name": constants.ObjectType.get_member_value__alias_map().get(group["bk_obj_id"]),
            }
            for group in groups
            # 仅返回主机动态分组
            # TODO: 当需要支持动态分组为集群时, 去掉这个过滤
            if group["bk_obj_id"] == constants.ObjectType.HOST.value
        ]
        return groups

    def execute(self, dynamic_group_id: str, start: int, page_size: int) -> Dict[str, Any]:
        """执行动态分组"""
        result = {"start": start, "page_size": page_size, "total": 0}

        execute_dynamic_group_result = BkApi.execute_dynamic_group(
            {
                "bk_biz_id": self.bk_biz_id,
                "id": dynamic_group_id,
                "fields": constants.CommonEnum.DEFAULT_HOST_FIELDS.value,
                "page": {"start": start, "limit": page_size},
            }
        )
        if not execute_dynamic_group_result or not execute_dynamic_group_result["info"]:
            return result
        # count预留给分页使用
        # TODO: 当动态分组为集群时, 暂不支持
        result["total"] = execute_dynamic_group_result["count"]
        host_list = execute_dynamic_group_result["info"]
        TopoHandler.fill_agent_status(host_list)
        host_list = BaseHandler.format_hosts(host_list, self.bk_biz_id)
        result["data"] = host_list
        return result

    def agent_statistics(self, dynamic_group_list: List[Dict] = None):
        dynamic_group_ids = [dynamic_group["id"] for dynamic_group in dynamic_group_list]
        params = {"bk_biz_id": self.bk_biz_id, "no_request": True}
        groups = batch_request(func=BkApi.search_dynamic_group, params=params)
        if not groups:
            return groups
        params_list = [
            {
                "dynamic_group": {
                    "id": group["id"],
                    "name": group["name"],
                    "meta": self.meta,
                },
            }
            for group in groups
            if group["id"] in dynamic_group_ids
        ]
        return request_multi_thread(
            func=self._get_dynamic_group_agent_statistic, params_list=params_list, get_data=lambda x: x
        )

    def _get_dynamic_group_agent_statistic(self, dynamic_group: dict):
        result = {"dynamic_group": dynamic_group}
        params = {
            "bk_biz_id": self.bk_biz_id,
            "id": dynamic_group["id"],
            "fields": constants.CommonEnum.SIMPLE_HOST_FIELDS.value,
            "no_request": True,
        }
        hosts = batch_request(func=BkApi.execute_dynamic_group, params=params)
        TopoHandler.fill_agent_status(hosts)
        agent_statistics = TopoHandler.count_agent_status(hosts)
        result.update(agent_statistics)
        return result
