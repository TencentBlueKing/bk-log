# -*- coding: utf-8 -*-
import time
import logging
from typing import List, Dict

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.tools.batch_request import request_multi_thread
from bkm_ipchooser.handlers.base import BaseHandler
from bkm_ipchooser.handlers.topo_handler import TopoHandler

logger = logging.getLogger("bkm_ipchooser")


class DynamicGroupHandler:
    """动态分组处理器"""

    def __init__(self, scope_list: types.ScopeList) -> None:
        # 暂时不支持多业务同时查询
        self.bk_biz_id = [scope["bk_biz_id"] for scope in scope_list][0]
        self.meta = BaseHandler.get_meta_data(self.bk_biz_id)

    def list(self) -> List[types.DynamicGroup]:
        """获取动态分组列表"""
        now_time = time.time()
        groups = BkApi.search_dynamic_group({"bk_biz_id": self.bk_biz_id})
        if not groups:
            return groups
        # 先根据是否为最近更新分组，再按照名称排序
        latest_groups = []
        other_groups = []
        for group in groups:
            _group = {
                "id": group["id"],
                "name": group["name"],
                "is_latest": False,
                "meta": self.meta,
            }
            last_time = group["last_time"]
            last_time_unix = time.mktime(time.strptime(last_time, "%Y-%m-%dT%H:%M:%S.%fZ"))
            if last_time_unix >= now_time - constants.TimeEnum.DAY.value:
                _group["is_latest"] = True
                latest_groups.append(_group)
            else:
                other_groups.append(_group)
        # 按照名称排序
        latest_groups.sort(key=lambda g: g["name"])
        other_groups.sort(key=lambda g: g["name"])

        groups = latest_groups + other_groups

        multi_get_dynamic_group_host_count_result = request_multi_thread(
            func=self._get_dynamic_group_host_count,
            params_list=[{"group_id": group["id"]} for group in groups],
            get_data=lambda x: x,
        )
        host_count_by_group_id = {
            _result["id"]: _result["count"] for _result in multi_get_dynamic_group_host_count_result
        }
        for group in groups:
            group["count"] = host_count_by_group_id.get(group["id"], 0)

        return groups

    def _get_dynamic_group_host_count(self, group_id: str) -> Dict:
        """获取动态分组主机数量"""
        result = {
            "id": group_id,
            "count": 0,
        }
        execute_dynamic_group_result = BkApi.execute_dynamic_group(
            {
                "bk_biz_id": self.bk_biz_id,
                "id": group_id,
                "fields": ["bk_host_id"],
                "page": {"start": 0, "limit": 1},
                "no_request": True,
            }
        )
        if not execute_dynamic_group_result:
            return result
        result["count"] = execute_dynamic_group_result["count"]
        return result

    def execute(self, dynamic_group_id: str, start: int, page_size: int) -> List[Dict]:
        """执行动态分组"""
        result = {"start": start, "page_size": page_size, "count": 0, "child": []}

        execute_dynamic_group_result = BkApi.execute_dynamic_group(
            {
                "bk_biz_id": self.bk_biz_id,
                "id": dynamic_group_id,
                "fields": constants.CommonEnum.EXECUTE_DYNAMIC_GROUP_FIELDS.value,
                "page": {"start": start, "limit": page_size},
            }
        )
        if not execute_dynamic_group_result or not execute_dynamic_group_result["info"]:
            return result
        # count预留给分页使用
        # TODO: 当动态分组为集群时, 暂不支持
        result["count"] = execute_dynamic_group_result["count"]
        host_list = execute_dynamic_group_result["info"]
        TopoHandler.fill_agent_status(host_list)
        result["child"] = host_list
        return result
