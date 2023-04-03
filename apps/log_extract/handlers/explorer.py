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
import copy
import re
import time
from itertools import product

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from apps.api import CCApi
from apps.utils.log import logger
from apps.utils.db import array_chunk
from apps.iam import ActionEnum, Permission
from apps.log_search.handlers.biz import BizHandler
from apps.log_extract import exceptions
from apps.log_extract import constants
from apps.log_extract.fileserver import FileServer
from apps.log_extract.handlers.thread import ThreadPool
from apps.log_extract.models import Strategies
from apps.utils.local import get_request_username
from apps.exceptions import ApiResultError
from apps.log_extract.constants import JOB_API_PERMISSION_CODE, BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE
from bkm_ipchooser.handlers import topo_handler
from bkm_ipchooser.query import resource
from bkm_ipchooser.tools import topo_tool


class ExplorerHandler(object):
    def __init__(self):
        self.request_user = get_request_username()

    def list_files(self, bk_biz_id, ip, request_dir, is_search_child, time_range, start_time, end_time):
        """
        :param bk_biz_id: 业务ID
        :param ip: 业务机器ip
        :param request_dir: 文件路径
        :param is_search_child: 是否搜索子目录
        :param time_range: 时间跨度
        :return: 列出业务机器下指定path目录中，用户可访问的目录或文件
        """
        strategies = self.get_strategies(bk_biz_id, ip)
        allowed_dir_file_list = strategies["allowed_dir_file_list"]
        operator = strategies["operator"]
        # 检查用户所请求的目录是否授权，并返回目录下可访问的文件类型
        search_params = self.get_search_params(allowed_dir_file_list, request_dir)
        bk_os_type = strategies["bk_os_type"]

        file_types = []
        for file_type in search_params["file_type"]:
            file_types.append("(" + file_type + ")" + ("$" if file_type[-1] != "*" else ""))
        search_context_kwargs = {
            "file_path": search_params["file_path"],
            "file_type": "|".join(file_types),
            "is_search_child": "1" if is_search_child else "0",
            "time_range": time_range if time_range else "0",
            "start_time": start_time,
            "end_time": end_time,
        }
        script_content = FileServer.get_script_info(
            action="list_file", args=search_context_kwargs, bk_os_type=bk_os_type
        )
        try:
            task_result = FileServer.execute_script(
                content=script_content["content"],
                script_params=script_content["script_params"],
                ip=ip,
                bk_biz_id=bk_biz_id,
                operator=operator,
                account=self.get_account(bk_os_type),
                task_name="[BKLOG] File Search By {}".format(self.request_user),
            )
        except ApiResultError as e:
            if e.code == JOB_API_PERMISSION_CODE:
                raise ApiResultError(
                    _(
                        "{strategy_name} 策略中的执行人 {operator} 没有JOB的操作权限,无法执行下载操作".format(
                            strategy_name=allowed_dir_file_list[0]["strategy_name"], operator=operator
                        )
                    ),
                    code=e.code,
                    errors=e.errors,
                )
            raise

        query_result = self.get_finished_result(task_result["job_instance_id"], operator, bk_biz_id)
        success_step = self.get_success_step(query_result)
        host_list = [
            {"ip": ip["ip"], "bk_cloud_id": ip["bk_cloud_id"], "bk_host_id": ip.get("bk_host_id", 0)}
            for ip in success_step.get("step_ip_result_list", [])
        ]
        host_logs = self.get_all_host_logs(
            host_list, task_result["job_instance_id"], success_step["step_instance_id"], bk_biz_id
        )
        res = self.job_log_to_file_list(host_logs, allowed_dir_file_list)
        res = sorted(res, key=lambda k: k["mtime"], reverse=True)
        return res

    @staticmethod
    def get_finished_result(task_instance_id, operator, bk_biz_id):
        query_result = FileServer.query_task_result(task_instance_id, operator, bk_biz_id)
        start_time = time.time()
        try:
            while not FileServer.is_finished_for_single_ip(query_result):
                query_result = FileServer.query_task_result(task_instance_id, operator, bk_biz_id)
                time.sleep(1)
                if time.time() - start_time > constants.FILE_SEARCH_TIMEOUT:
                    raise exceptions.ExplorerFilesTimeout
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("[explorer] FileSearchService failed: {}".format(str(e)))
            raise exceptions.PipelineApiFailed(exceptions.PipelineApiFailed.MESSAGE.format(message=str(e)))
        return query_result

    @staticmethod
    def get_success_step(query_result):
        step_result = FileServer.get_step_instance(query_result)
        ip_status = step_result["status"]
        if ip_status == constants.JOB_SUCCESS_STATUS:
            return step_result
        raise exceptions.ExplorerException(_("文件预览异常({})".format(",".join(ip_status))))

    @staticmethod
    def get_all_host_logs(ip_list, job_instance_id, step_instance_id, bk_biz_id):
        ip_list_group = array_chunk(ip_list, BATCH_GET_JOB_INSTANCE_IP_LOG_IP_LIST_SIZE)
        ip_logs = []
        for ip_list in ip_list_group:
            ip_list_log = FileServer.get_host_list_log(ip_list, job_instance_id, step_instance_id, bk_biz_id)
            ip_logs.extend(ip_list_log.get("script_task_logs", []))
        return ip_logs

    def job_log_to_file_list(self, ip_logs, allowed_dir_file_list):
        res = []
        exists_record = set()
        for ip_log in ip_logs:
            file_meta_data_list = ip_log["log_content"]
            file_meta_data_list = file_meta_data_list.split("\n")
            output_pattern = re.compile(r"(dirname|fname)")
            for file_meta_data in file_meta_data_list:
                if not output_pattern.match(file_meta_data):
                    continue
                try:
                    file_meta_data = file_meta_data.split(" ")
                    file_type_and_name, *__ = file_meta_data
                    if file_type_and_name in exists_record:
                        continue
                    file_type, file_name = self._get_file_type_and_name(file_type_and_name)
                    file_size = file_meta_data[1].split(":") if len(file_meta_data) > 1 else "0"
                    # 过滤不符合策略规范的服务器文件
                    if not self.filter_server_access_file(allowed_dir_file_list, file_name, file_type):
                        continue
                    res.append(
                        {
                            "ip": ip_log["ip"],
                            "bk_cloud_id": ip_log["bk_cloud_id"],
                            "bk_host_id": ip_log["host_id"],
                            "type": "dir" if file_type == "dirname" else "file",
                            "path": file_name,
                            "size": format_size(int(file_size[-1])) if file_type != "dirname" else "0",
                            "mtime": self._get_file_mtime(file_meta_data),
                        }
                    )
                    exists_record.add(file_type_and_name)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error("[list_files] parse output error, output=> {}, e=>{}".format(file_meta_data, e))
        return res

    @staticmethod
    def _get_file_type_and_name(file_meta_data):
        if file_meta_data.startswith("dirname"):
            return "dirname", file_meta_data.lstrip("dirname:")
        return "fname", file_meta_data.lstrip("fname:")

    @staticmethod
    def _get_file_mtime(file_meta_data):
        if len(file_meta_data) > 1:
            file_mtime = file_meta_data[2].split(":")
            return f"{file_mtime[-1]} {file_meta_data[-1]}"
        return "-"

    def get_strategies(self, bk_biz_id, ip_list):
        """
        :param bk_biz_id: 业务ID
        :param ip_list: 业务机器IP列表
        :return: 返回用户在对应业务下所选择的多个服务器中可访问目录及目录下文件类型的交集
        """
        # step 1: 获取ip所属模块列表
        request_topo_list = self.get_module_by_ip(bk_biz_id, ip_list)

        # 用户选择的业务机器数量需要和返回的topo列表数量一致，这代表用户选择的每个服务器都由对应的TOPO
        request_topo_list_len = len(request_topo_list)
        ip_list_len = len(ip_list)
        if request_topo_list_len != ip_list_len:
            raise exceptions.ExplorerMatchTopoFailed(
                exceptions.ExplorerMatchTopoFailed.MESSAGE.format(
                    mismatch_number=abs(ip_list_len - request_topo_list_len)
                )
            )

        # step 2: 多个IP对应的服务器操作系统必须一致
        host_os_type = self.get_bk_os_type(request_topo_list[0]["host"])
        for host_info in request_topo_list:
            if self.get_bk_os_type(host_info["host"]) != host_os_type:
                raise exceptions.ExplorerOsTypeMismatch

        # step 3: 获取ip可以访问的策略信息
        strategies = self.get_user_strategies(bk_biz_id, self.request_user)
        allowed_strategies = []
        for request_topo_list_sub in request_topo_list:
            allowed_strategies.append(self.get_allowed_dir_file_list(strategies, request_topo_list_sub["topo"]))

        # allowed_strategies = self.polish_file_type(allowed_strategies)
        # step 4: 获取用户所有IP都可以访问的目录及扩展名
        result = []
        for ip_allowed_strategies in allowed_strategies:
            result = self.get_intersection_strategies(result, ip_allowed_strategies)

        return {"allowed_dir_file_list": result, "bk_os_type": host_os_type, "operator": result[0]["operator"]}

    def list_accessible_topo(self, bk_biz_id):
        """
        过滤topo
        @param bk_biz_id: 业务ID
        @return: 返回过滤后的topo，过滤后的topo结构与原先一致
        """
        # 获取biz_id和username
        request_user = get_request_username()
        # 获取全部的topo树
        total_topo, *_ = self.search_biz_inst_topo(bk_biz_id)
        format_bizs_set = self.format_topo(total_topo)
        # 获取策略
        auth_info = self.get_auth_info(request_user, bk_biz_id)
        user_topo_list = []
        # 过滤
        self.get_user_topo(copy.deepcopy(total_topo), user_topo_list, auth_info)
        # 合并过滤后的topo
        combined_topo = self.combin_filter_topo(user_topo_list, format_bizs_set)
        return combined_topo

    @classmethod
    def check_node(cls, node, auth_info):
        if node["bk_obj_id"] == "biz" and node["bk_inst_id"] in auth_info["auth_topo"]["bizs"]:
            return True
        if node["bk_obj_id"] == "set" and node["bk_inst_id"] in auth_info["auth_topo"]["sets"]:
            return True
        if node["bk_obj_id"] == "module" and (
            node["bk_inst_name"] in auth_info["auth_modules"] or node["bk_inst_id"] in auth_info["auth_topo"]["modules"]
        ):
            return True
        return False

    @classmethod
    def filter_nodes(cls, nodes, auth_info):
        filtered_nodes = []
        for node in nodes:
            if cls.check_node(node, auth_info):
                filtered_nodes.append(node)
            else:
                node["child"] = cls.filter_nodes(node["child"], auth_info)
                if node["child"]:
                    filtered_nodes.append(node)
        return filtered_nodes

    def ipchooser_trees(self, scope_list):
        """
        新版IP选择器：查询拓扑树
        """
        if not scope_list:
            return []

        bk_biz_id = scope_list[0]["bk_biz_id"]
        request_user = get_request_username()
        origin_tree = resource.ResourceQueryHelper.get_topo_tree(bk_biz_id, return_all=True)

        # 获取策略
        auth_info = self.get_auth_info(request_user, bk_biz_id)

        # 过滤用户有权限的节点
        filtered_nodes = self.filter_nodes([origin_tree], auth_info)

        # 对拓扑树进行格式化
        formatted_tree = topo_handler.TopoHandler.format_tree(
            topo_tool.TopoTool.get_topo_tree_with_count(bk_biz_id, return_all=True, topo_tree=filtered_nodes[0])
        )
        return [formatted_tree]

    @classmethod
    def dig_out_modules(cls, tree):
        """
        挖掘出节点下面的所有模块列表
        """
        if tree["object_id"] == "module":
            return [{"instance_id": tree["instance_id"], "object_id": tree["object_id"]}]
        modules = []
        for node in tree["child"]:
            modules.extend(cls.dig_out_modules(node))
        return modules

    @classmethod
    def filter_modules(cls, trees, query_nodes):
        """
        过滤出node_list中用户有权限的模块列表
        :param trees: 用户有权限的整个拓扑结构
        :param query_nodes: 用户想要查询主机的节点列表
        :return: 用户有权限查询主机的模块列表
        """
        modules = []
        for tree in trees:
            matched = False
            for query_node in query_nodes:
                if query_node["object_id"] == tree["object_id"] and query_node["instance_id"] == tree["instance_id"]:
                    matched = True
                    break
            if matched:
                # 节点匹配的话，直接挖掘出节点下面全部的模块列表
                modules.extend(cls.dig_out_modules(tree))
            else:
                # 不匹配的话，继续递归查找
                modules.extend(cls.filter_modules(tree["child"], query_nodes))
        return modules

    def ipchooser_query_hosts(self, data):
        """
        新版IP选择器：查询主机
        """
        trees = self.ipchooser_trees(data["scope_list"])
        node_list = self.filter_modules(trees, data["node_list"])
        return topo_handler.TopoHandler.query_hosts(
            scope_list=data["scope_list"],
            readable_node_list=node_list,
            conditions=data["conditions"],
            start=data["start"],
            page_size=data["page_size"],
        )

    def ipchooser_query_host_id_infos(self, data):
        """
        新版IP选择器：查询主机ID
        """
        trees = self.ipchooser_trees(data["scope_list"])
        node_list = self.filter_modules(trees, data["node_list"])
        return topo_handler.TopoHandler.query_host_id_infos(
            scope_list=data["scope_list"],
            readable_node_list=node_list,
            conditions=data["conditions"],
            start=data["start"],
            page_size=data["page_size"],
        )

    @staticmethod
    def add_dot(file_type):
        if file_type == "*":
            # 如果只带一个星号，代表匹配全部，包括无后缀
            return "[^/]*"
        file_type = file_type.replace("*", "[^/]*")
        return f".{file_type}"

    def get_bk_os_type(self, host_info):
        bk_os_type = host_info.get("bk_os_type")
        bk_os_name = host_info.get("bk_os_name") or ""
        if not bk_os_type and self.is_windows_os(bk_os_name.lower()):
            return constants.WINDOWS
        return bk_os_type or constants.LINUX

    @staticmethod
    def is_windows_os(bk_os_name):
        if any(key in bk_os_name for key in constants.WINDOWS_OS_NAME_LIST):
            return True
        return False

    @classmethod
    def remove_child(cls, dic):
        """
        移除child节点
        @param dic: topo树
        @return: 去掉child的topo
        """
        dic["child"] = []
        # 删除多余的children键
        dic.pop("children")
        return dic

    @classmethod
    def search_biz_inst_topo(cls, bk_biz_id):
        """
        通过get_instance_topo获取主机的topo信息
        @param bk_biz_id:
        @return:
        """
        params = {"bk_biz_id": bk_biz_id, "instance_type": "host", "remove_empty_nodes": True}
        try:
            host_info = BizHandler(bk_biz_id).get_instance_topo(params, is_inner=True)
        except Exception as e:  # pylint: disable=broad-except
            raise exceptions.ExplorerPullTopoError(
                exceptions.ExplorerPullTopoError.MESSAGE.format(error=e, params=params)
            )
        if not host_info:
            raise exceptions.ExplorerPullTopoNotExist(exceptions.ExplorerPullTopoNotExist.MESSAGE.format(params=params))
        return host_info

    @classmethod
    def format_topo(cls, total_topo):
        """
        格式化topo树
        @param total_topo:全部topo树
        @return: (格式化的业务，格式化的sets）
        """
        topo_bizs_dict = {}
        topo_bizs = cls.remove_child(copy.deepcopy(total_topo))
        topo_bizs_dict.update({topo_bizs["bk_inst_id"]: topo_bizs})
        total_sets_dict = {}
        total_sets_list = list(map(cls.remove_child, copy.deepcopy(total_topo["children"])))
        for item in total_sets_list:
            total_sets_dict.update({item["bk_inst_id"]: item})
        return topo_bizs_dict, total_sets_dict

    @classmethod
    def get_auth_info(cls, username, bk_biz_id):
        """
        从策略表中取出策略信息
        @param username: 当前用户名
        @param bk_biz_id: 业务ID
        @return: user_auth，根据topo和module选择的策略dict
        """
        user_auth = {"auth_topo": {"bizs": [], "sets": [], "modules": []}, "auth_modules": []}
        kwargs = {"user_list__contains": f",{username},", "bk_biz_id": bk_biz_id}
        auth_modules = []
        auth_topo = []
        strategies = Strategies.objects.filter(**kwargs).values("select_type", "modules")
        if not strategies:
            has_biz_manage = Permission().is_allowed(ActionEnum.MANAGE_EXTRACT_CONFIG)
            # 业务运维
            if has_biz_manage:
                raise exceptions.StrategiesNoExistsForOperator
            # 普通用户
            raise exceptions.StrategiesNoExistsForGeneral
        # 遍历判断select_type
        for strategy in strategies:
            if strategy["select_type"] == "module":
                auth_modules.append({"modules": strategy["modules"]})
            else:
                auth_topo.append({"modules": strategy["modules"]})
        # 转换策略的格式
        if auth_modules:
            user_auth["auth_modules"].extend(
                [modules["bk_inst_name"] for auth in auth_modules for modules in auth["modules"]]
            )
        if auth_topo:
            for auth in auth_topo:
                for modules in auth["modules"]:
                    if modules["bk_obj_id"] == "biz":
                        user_auth["auth_topo"]["bizs"].append(modules["bk_inst_id"])
                    elif modules["bk_obj_id"] == "set":
                        user_auth["auth_topo"]["sets"].append(modules["bk_inst_id"])
                    elif modules["bk_obj_id"] == "module":
                        user_auth["auth_topo"]["modules"].append(modules["bk_inst_id"])
        return user_auth

    @classmethod
    def check_auth(cls, topo, auth_topo):
        """
        检索用户是否有这个TOPO的访问权限
        @param topo: 当前topo节点
        @param username: 当前用户
        @return: Bool
        """
        if topo["bk_obj_id"] == "biz" and topo["bk_inst_id"] in auth_topo["auth_topo"]["bizs"]:
            return True
        if topo["bk_obj_id"] == "set" and topo["bk_inst_id"] in auth_topo["auth_topo"]["sets"]:
            return True
        if topo["bk_obj_id"] == "module" and (
            topo["bk_inst_name"] in auth_topo["auth_modules"] or topo["bk_inst_id"] in auth_topo["auth_topo"]["modules"]
        ):
            return True
        return False

    @classmethod
    def get_user_topo(cls, topo, user_topo, auth_info, parents=None):
        """
        递归判断topo是否有权限
        @param topo: 待检查的topo
        @param user_topo: 检查后的topo
        @param username: 当前用户
        @param parents: 记录topo的所有路径
        @return: 过滤后的topo
        """
        if not parents:
            parents = []
        parents.append(topo["bk_inst_id"])
        if cls.check_auth(topo, auth_info):
            # pop当前层的节点
            parents.pop()
            topo["parents"] = parents.copy()
            user_topo.append(topo)
            return
        if len(topo["children"]) and topo["bk_obj_id"] != "module":  # pylint:disable=len-as-condition
            for child in topo["children"]:
                cls.get_user_topo(child, user_topo, auth_info, parents=parents)
        # 递归结束后把自己节点pop出去
        parents.pop()
        return

    @classmethod
    def combin_filter_topo(cls, filter_topo, format_topo):
        """
        还原过滤后的topo为树形结构
        @param filter_topo: 过滤后的topo
        @param format_topo: 格式化的bizs和sets
        @return: 带child的树形的topo
        """
        if not filter_topo:
            raise exceptions.ExplorerFilterTopoNotExist
        user_topo_list = []
        user_topo = []
        # 遍历过滤后的topo列表
        for topo in filter_topo:
            user_tree_list = []
            if len(topo["parents"]) == 0:
                topo.pop("parents")
                topo["children"] = cls.combin_set_tree(topo["children"])
                user_topo.append(topo)
                return user_topo

            bk_biz_id = topo["parents"][0]
            # topo['parents'] = topo['parents'][::-1]
            # last_inst = []
            # 正向遍历获取每层节点
            for inst, parent_index in zip(copy.deepcopy(format_topo), topo["parents"]):
                user_tree_list.append(inst[parent_index])
            topo.pop("parents")
            user_tree_list.append(topo)
            # 反向遍历拼接tree
            for index in range(len(user_tree_list) - 1, 0, -1):
                if "children" not in user_tree_list[index - 1]:
                    user_tree_list[index - 1].setdefault("children", [])
                user_tree_list[index - 1]["children"].append(user_tree_list[index])
            user_topo_list.append(copy.deepcopy(user_tree_list[1]))
        # 合并set层级的模块
        set_tree = cls.combin_set_tree(user_topo_list)
        # 拼接biz层级
        biz_topo = copy.deepcopy(format_topo[0][bk_biz_id])
        if "children" not in biz_topo:
            biz_topo.setdefault("children", [])
        biz_topo["children"].extend(set_tree)
        user_topo.append(biz_topo)
        return user_topo

    @classmethod
    def combin_set_tree(cls, user_set_trees_list):
        """
        合并set级别的topo
        @param base_set_tree: 初始的sets
        @param user_set_trees_list: 其他的多个sets列表
        @return:
        """
        if not user_set_trees_list:
            return user_set_trees_list
        res = [user_set_trees_list[0]]
        sets_bk_inst_ids = list(map(lambda sets: sets["bk_inst_id"], res))
        for set_child in user_set_trees_list:
            # 添加不同set
            if set_child["bk_inst_id"] not in sets_bk_inst_ids:
                res.append(set_child)
                sets_bk_inst_ids.append(set_child["bk_inst_id"])
                continue
        for set_child, sets in product(user_set_trees_list, res):
            if sets["bk_inst_id"] == set_child["bk_inst_id"]:
                child_bk_inst_ids = list(map(lambda child: child["bk_inst_id"], sets["children"]))
                for set_child_child in set_child["children"]:
                    if set_child_child["bk_inst_id"] not in child_bk_inst_ids:
                        sets["children"].append(set_child_child)
                        child_bk_inst_ids.append(set_child_child["bk_inst_id"])
        return res

    @classmethod
    def _get_topo_filter_rule(cls, ip_list):
        condition = {
            "condition": "OR",
            "rules": [],
        }

        for ip in ip_list:
            if ip.get("bk_host_id"):
                rules = [
                    {"field": "bk_host_id", "operator": "equal", "value": ip["bk_host_id"]},
                ]
            else:
                rules = [
                    {"field": "bk_host_innerip", "operator": "equal", "value": ip["ip"]},
                    {"field": "bk_cloud_id", "operator": "equal", "value": ip["bk_cloud_id"]},
                ]
            condition["rules"].append({"condition": "AND", "rules": rules})

        return condition

    @classmethod
    def get_module_by_ip(cls, bk_biz_id, ip_list):
        search_topo_of_host = {
            "bk_biz_id": bk_biz_id,
            "fields": ["bk_host_id", "bk_os_type", "bk_os_name", "bk_cloud_id", "bk_host_innerip"],
            "host_property_filter": cls._get_topo_filter_rule(ip_list),
        }
        # host_info 是一个列表，host_info[i-1](host_info[1]) 代表所查询第i台(第2台)主机的信息，包括topo信息和主机详情信息
        host_info = batch_request(func=CCApi.list_biz_hosts_topo, params=search_topo_of_host)
        if not host_info:
            raise exceptions.ExplorerStrategiesFailed
        return host_info

    @classmethod
    def get_allowed_dir_file_list(cls, strategies, request_topo_list) -> list:
        """
        获取用户访问IP所属TOPO可以访问的策略信息
        :param strategies: 运维人员为这个用户在这个业务下配置的策略
        :param request_topo_list: 用户请求业务机器IP对应的topo信息, 即这台机器属于哪些大区下的哪些模块
        :return: 策略表中该用户可访问的所有目录及目录下的文件后缀
        """
        allowed_strategies = []

        for strategy in strategies:
            is_match_strategy = False
            for request_topo in request_topo_list:
                """
                strategy.select_type == module -> 运维人员按选择模板的方式授权 -> allowed_module["bk_inst_id"] == 0
                strategy.select_type == topo -> 运维人员按选择topo的方式授权 -> allowed_module["bk_inst_id"] != 0
                """
                for allowed_module in strategy["modules"]:
                    # 按模板授权 -> 由模板实例化出来的模块可以属于多个大区，但不能跨越多个业务
                    if strategy["select_type"] == constants.SelectType.MODULES.value:
                        for request_module in request_topo["module"]:
                            # 比较模块名称是否一致
                            if allowed_module["bk_inst_name"] == request_module["bk_module_name"]:
                                is_match_strategy = True
                                break
                    # 按topo授权 -> 授权的最终位置可以是 [业务, 大区, 模块]
                    else:
                        for request_module in request_topo["module"]:
                            # 按业务授权
                            if allowed_module["bk_obj_id"] == "biz":
                                is_match_strategy = True
                            # 按大区授权
                            elif allowed_module["bk_obj_id"] == "set":
                                if allowed_module["bk_inst_id"] == request_topo["bk_set_id"]:
                                    is_match_strategy = True
                            # 模块授权
                            elif allowed_module["bk_obj_id"] == "module":
                                if allowed_module["bk_inst_id"] == request_module["bk_module_id"]:
                                    is_match_strategy = True

                            # 如果已有策略匹配，则直接跳出
                            if is_match_strategy:
                                break
                    if is_match_strategy:
                        break

                if is_match_strategy:
                    break

            if is_match_strategy:
                allowed_strategies.append(strategy)

        if not allowed_strategies:
            raise exceptions.ExplorerModuleNotAllowed(
                exceptions.ExplorerModuleNotAllowed.MESSAGE.format(request_module=request_topo_list)
            )
        return cls.get_unique_strategy(allowed_strategies, model=True)

    @classmethod
    def get_unique_strategy(cls, strategies, model=False):
        """
        @param strategies为对应的策略集合
        @param model如果为False则为原始默认，调用为True则为修改的调用 需要使用到allowed_strategy["strategy_name"] 字段
        """
        if not strategies:
            return []

        # 合并不同策略的目录/扩展名
        operator = ""
        strategy_name = ""
        allowed_dir_file_list = {}
        for allowed_strategy in strategies:
            operator = allowed_strategy["operator"]
            if model:
                strategy_name = allowed_strategy["strategy_name"]
            for dir_path in allowed_strategy["visible_dir"]:
                if not dir_path:
                    continue
                if dir_path not in allowed_dir_file_list:
                    allowed_dir_file_list[dir_path] = set(allowed_strategy["file_type"])
                else:
                    allowed_dir_file_list[dir_path].update(allowed_strategy["file_type"])

        return [
            {"file_path": path, "file_type": file_type, "operator": operator, "strategy_name": strategy_name}
            for path, file_type in allowed_dir_file_list.items()
        ]

    @classmethod
    def get_intersection_strategies(cls, strategies_source, strategies_target) -> list:
        """
        获取IP访问策略的交集
          - 同个IP内的文件目录及后缀取并集，不同IP之间文件目录及后缀取交集
          - data/ 与 /data/logs/ 的交集是 /data/logs/
        """
        if not strategies_source or not strategies_target:
            return strategies_source if not strategies_target else strategies_target

        result = []
        for strategy in strategies_source:
            for strategy_target in strategies_target:
                visible_dir = ""
                if strategy["file_path"] == strategy_target["file_path"]:
                    visible_dir = strategy["file_path"]
                elif strategy["file_path"].startswith(strategy_target["file_path"]):
                    visible_dir = strategy_target["file_path"]
                elif strategy_target["file_path"].startswith(strategy["file_path"]):
                    visible_dir = strategy["file_path"]
                if visible_dir:
                    file_type = strategy["file_type"].intersection(strategy_target["file_type"])
                    if not file_type:
                        continue
                    result.append(
                        {"visible_dir": [visible_dir], "file_type": file_type, "operator": strategy["operator"]}
                    )

        if not result:
            raise exceptions.ExplorerStrategiesFailed()
        return cls.get_unique_strategy(result)

    def get_search_params(self, allowed_dir_file_list, request_dir):
        """
        :param allowed_dir_file_list: 策略表中配置的该用户可访问的目录及目录下的文件类型
        :param request_dir: 用户请求访问的目录
        :return: 用户可访问的目录及目录下的文件类型
        """
        search_params = {"file_type": set()}
        for allowed_dir_file in allowed_dir_file_list:
            if request_dir.startswith(allowed_dir_file["file_path"]):
                search_params["file_path"] = request_dir
                for file_type in allowed_dir_file["file_type"]:
                    if file_type.startswith("."):
                        # 如果是以 . 开头，则增加对其的转义
                        file_type = f"\\{file_type}"
                    search_params["file_type"].add(file_type)

        if not search_params["file_type"]:
            search_params.clear()
        if not search_params:
            logger.error("用户{}访问目录{}失败".format(self.request_user, request_dir))
            raise exceptions.ExplorerDirFailed(exceptions.ExplorerDirFailed.MESSAGE.format(request_dir=request_dir))

        return search_params

    @staticmethod
    def filter_server_access_file(allowed_dir_file_list, request_file, request_file_type="fname"):
        if request_file_type == "fname":
            # 匹配可访问的文件
            for allowed_dir_file in allowed_dir_file_list:
                file_types = []
                for file_type in allowed_dir_file["file_type"]:
                    if file_type.startswith("."):
                        # 如果是以 . 开头，则增加对其的转义
                        file_types.append(rf"(\{file_type})" + ("$" if file_type[-1] != "*" else ""))
                    else:
                        file_types.append(file_type + ("$" if file_type[-1] != "*" else ""))
                # pattern样例：'^/data/[a-zA-Z0-9._/-]+(.gz|.log|.txt)$'
                if request_file.startswith(allowed_dir_file["file_path"]):
                    file_name = request_file.replace(allowed_dir_file["file_path"], "")
                    file_pattern = re.compile(
                        r"^[{}]+({})".format(settings.EXTRACT_FILE_PATTERN_CHARACTERS, "|".join(file_types))
                    )
                    if file_pattern.match(file_name):
                        return True
        else:
            # 匹配可访问的目录
            for allowed_dir_file in allowed_dir_file_list:
                # pattern样例：'^/data/'
                dir_pattern = re.compile(r"^{}".format(allowed_dir_file["file_path"]))
                if dir_pattern.match(request_file):
                    return True
        return False

    def get_user_strategies(self, bk_biz_id, request_user):
        """
        获取用户可查看的策略列表
        """
        strategies = (
            Strategies.objects.filter(bk_biz_id=bk_biz_id, user_list__contains=f",{request_user},")
            .exclude(operator="")
            .values("strategy_id", "select_type", "modules", "visible_dir", "file_type", "operator", "strategy_name")
            .all()
        )
        if not strategies:
            raise exceptions.ExplorerStrategiesFailed
        # file_type前加 '.', "*" 替换为 "[^/]*"
        for strategy in strategies:
            strategy["file_type"] = set(map(self.add_dot, strategy["file_type"]))
        return list(strategies)

    @staticmethod
    def get_account(bk_os_type):
        if bk_os_type != constants.WINDOWS:
            return constants.ACCOUNT["linux"]
        return constants.ACCOUNT["windows"]


def batch_request(func, params, get_data=lambda x: x["info"], get_count=lambda x: x["data"]["count"], limit=500):
    """
    并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :return: 请求结果
    """

    first_param = copy.deepcopy(params)
    first_param["page"] = {"start": 0, "limit": 1}
    # 请求第一次获取总数
    result = func(params=first_param, raw=True)

    if not result["result"]:
        logger.error("[batch_request] {api} count request error, result: {result}".format(api=func.path, result=result))
        return []

    count = get_count(result)
    data = []
    start = 0

    # 根据请求总数并发请求
    pool = ThreadPool()
    params_and_future_list = []
    while start < count:
        request_params = {"page": {"limit": limit, "start": start}}
        request_params.update(params)
        params_and_future_list.append(
            {"params": request_params, "future": pool.apply_async(func, kwds={"params": request_params})}
        )

        start += limit

    pool.close()
    pool.join()

    # 取值
    for params_and_future in params_and_future_list:
        result = params_and_future["future"].get()

        if not result:
            logger.error(
                "[batch_request] {api} request error, params: {params}, result: {result}".format(
                    api=func.__name__, params=params_and_future["params"], result=result
                )
            )
            return []

        data.extend(get_data(result))

    return data


def format_size(file_size):
    if file_size >= constants.GB_SIZE:
        _format = "%.1fGB" % (file_size / constants.GB_SIZE)
    elif file_size >= constants.MB_SIZE:
        _format = "%.1fMB" % (file_size / constants.MB_SIZE)
    else:
        _format = "%.1fKB" % (file_size / constants.KB_SIZE)
    return _format
