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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.iam import Permission, ActionEnum
from apps.utils import APIModel
from apps.exceptions import BizNotExistError
from apps.api import BKLoginApi, CmsiApi
from apps.log_search.models import ProjectInfo
from apps.utils.cache import cache_one_hour
from apps.utils.local import get_request_username


class MetaHandler(APIModel):
    @classmethod
    def get_projects(cls, project_ids=None):
        if not project_ids:
            projects = ProjectInfo.objects.all()
        else:
            projects = ProjectInfo.objects.filter(project_id__in=project_ids).all()
        for project in projects:
            project.project_name = f"[{project.bk_biz_id}] {project.project_name}"
        return projects

    @classmethod
    def get_user_projects(cls, username):
        result = []
        business_list = MetaHandler.get_projects()
        projects = Permission(username).filter_business_list_by_action(ActionEnum.VIEW_BUSINESS, business_list)
        allowed_business_mapping = {project.bk_biz_id for project in projects}

        for project in business_list:
            result.append(
                {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "bk_biz_id": project.bk_biz_id,
                    "time_zone": project.time_zone,
                    "project_manage": project.bk_biz_id in allowed_business_mapping,
                    "permission": {ActionEnum.VIEW_BUSINESS.id: project.bk_biz_id in allowed_business_mapping},
                }
            )
        return result

    @classmethod
    def get_msg_type(cls):
        """
        获取通知列表
        """
        return CmsiApi.get_msg_type()

    @classmethod
    def get_project_info(cls, bk_biz_id):
        return cls._cache_project_info(bk_biz_id=bk_biz_id)

    @staticmethod
    @cache_one_hour("meta_biz_to_project_{bk_biz_id}")
    def _cache_project_info(*, bk_biz_id):
        try:
            project = ProjectInfo.objects.filter(bk_biz_id=bk_biz_id).first()
            if not project:
                raise ProjectInfo.DoesNotExist
            project_info = {
                "bk_biz_id": bk_biz_id,
                "project_id": project.pk,
                "project_name": project.project_name,
            }
            return project_info
        except ProjectInfo.DoesNotExist:
            raise BizNotExistError(BizNotExistError.MESSAGE.format(bk_biz_id=bk_biz_id))

    @classmethod
    def get_menus(cls, project_id, is_superuser):
        is_project_manage = True
        project = ProjectInfo.objects.get(project_id=project_id)
        modules = [
            {"id": "search", "name": _("检索"), "router": "retrieve", "project_manage": is_project_manage},
            {"id": "trace", "name": _("调用链"), "router": "trace", "project_manage": is_project_manage},
            {"id": "extract", "name": _("日志提取"), "router": "extract", "project_manage": is_project_manage},
            {"id": "monitor", "name": _("监控策略"), "router": "monitor", "project_manage": is_project_manage},
            {
                "id": "dashboard",
                "name": _("仪表盘"),
                "router": "dashboard",
                "children": [
                    {"id": "create_dashboard", "name": _("新建仪表盘"), "project_manage": is_project_manage},
                    {"id": "create_folder", "name": _("新建目录"), "project_manage": is_project_manage},
                    {"id": "import_dashboard", "name": _("导入仪表盘"), "project_manage": is_project_manage},
                ],
            },
            {
                "id": "manage",
                "name": _("管理"),
                "router": "manage",
                "children": [
                    {"id": "manage_access", "name": _("数据接入"), "project_manage": is_project_manage},
                    {"id": "manage_index_set", "name": _("索引集管理"), "project_manage": is_project_manage},
                    {"id": "manage_extract", "name": _("日志提取配置"), "project_manage": is_project_manage},
                    {"id": "manage_user_group", "name": _("用户组管理"), "project_manage": is_project_manage},
                    {"id": "manage_migrate", "name": _("V3迁移"), "project_manage": is_project_manage},
                    {"id": "manage_data_link", "name": _("数据链路管理"), "project_manage": is_project_manage},
                ],
            },
        ]

        data = []
        for module in modules:
            module = cls.get_menu(module, is_superuser, project)
            if not module:
                continue

            if module.get("children") and isinstance(module["children"], list):
                children = []
                for sub_module in module["children"]:
                    sub_module = cls.get_menu(sub_module, is_superuser, project)
                    if not sub_module:
                        continue
                    children.append(sub_module)
                if children:
                    module["children"] = children
            data.append(module)
        return data

    @classmethod
    def get_menu(cls, module, is_superuser, project):
        # 如果未设置特性开关，则直接隐藏
        if module["id"] not in settings.FEATURE_TOGGLE:
            return False

        # 灰度功能：非测试环境或管理员直接隐藏
        toggle = settings.FEATURE_TOGGLE[module["id"]]
        if toggle == "off":
            return False

        if toggle == "debug":
            if (
                settings.ENVIRONMENT not in ["dev", "stag"]
                and not is_superuser
                and module["id"] not in project.feature_toggle
            ):
                return False

        # 管理员可见链路管理页面
        if module["id"] == "manage_data_link":
            return module if is_superuser else False

        return module

    @classmethod
    def get_user(cls):
        username = get_request_username()
        data = BKLoginApi.get_user()
        return {
            "username": username,
            "language": data.get("language", "zh-cn"),
            "time_zone": data.get("time_zone", "Asia/Shanghai"),
            "chname": data.get("chname", username),
            "operator": username,
        }

    @classmethod
    def get_biz_maintainer(cls, bk_biz_id, project_id):
        """
        @summary:查询业务运维列表
        """
        if bk_biz_id:
            project = ProjectInfo.objects.filter(bk_biz_id=bk_biz_id, is_deleted=False).first()
        elif project_id:
            project = ProjectInfo.objects.filter(project_id=project_id, is_deleted=False).first()
        else:
            return {}

        if not project:
            return {}
        project_name = project.project_name
        maintainer = []
        data = {"bk_biz_name": project_name, "maintainer": list(maintainer)}
        return data
