import logging
from typing import List, Dict

from django.conf import settings
from bkm_ipchooser.constants import AgentStatusType, GSEV2AgentStatusType
from bkm_ipchooser.api import BkApi

logger = logging.getLogger("bkm_ipchooser")


class GseAdapter:
    """GSE适配器"""

    @classmethod
    def fill_agent_status(cls, cc_hosts: List[Dict]) -> None:
        """
        填充主机agent状态
        params:
            cc_hosts: CC list_biz_hosts接口获取到的主机列表
        """
        raise NotImplementedError


class GseAdapterV1(GseAdapter):
    """GSE适配器V1, bk_cloud_id:ip为唯一标识版本"""

    @classmethod
    def fill_agent_status(cls, cc_hosts: List[Dict]) -> None:
        """填充主机agent状态"""
        if not cc_hosts:
            return

        index = 0
        hosts, host_map = [], {}
        for cc_host in cc_hosts:
            ip, bk_cloud_id = cc_host["bk_host_innerip"], cc_host["bk_cloud_id"]
            hosts.append({"ip": ip, "bk_cloud_id": bk_cloud_id})

            host_map[f"{bk_cloud_id}:{ip}"] = index
            index += 1

        try:
            # 添加no_request参数, 多线程调用时，保证用户信息不漏传
            status_map = BkApi.get_agent_status({"hosts": hosts, "no_request": True})

            for ip_cloud, detail in status_map.items():
                cc_hosts[host_map[ip_cloud]]["status"] = detail["bk_agent_alive"]
        except KeyError as e:
            logger.exception("fill_agent_status exception: %s", e)


class GseAdapterV2(GseAdapter):
    """GSE适配器V2, bk_agent_id为唯一标识版本"""

    @classmethod
    def fill_agent_status(cls, cc_hosts: List[Dict]) -> None:
        """填充主机agent状态"""
        if not cc_hosts:
            return

        index = 0
        agent_id_list, host_map = [], {}
        for cc_host in cc_hosts:
            bk_agent_id = cc_host["bk_agent_id"]
            agent_id_list.append(bk_agent_id)
            host_map[bk_agent_id] = index
            index += 1

        try:
            # 添加no_request参数, 多线程调用时，保证用户信息不漏传
            agents = BkApi.get_agent_status_v2({"agent_id_list": agent_id_list, "no_request": True})
            for agent in agents:
                bk_agent_id = agent["bk_agent_id"]
                cc_hosts[host_map[bk_agent_id]]["status"] = (
                    AgentStatusType.ALIVE.value
                    if agent["status_code"] == GSEV2AgentStatusType.RUNNING.value
                    else AgentStatusType.NO_ALIVE.value
                )

        except KeyError as e:
            logger.exception("fill_agent_status exception: %s", e)


class GseTool:
    """GSE Tool"""

    @classmethod
    def get_adapter(cls) -> GseAdapter:
        """获取GSE适配器"""
        if settings.ENABLE_DHCP:
            return GseAdapterV2()
        return GseAdapterV1()
