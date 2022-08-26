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

from django.conf import settings

from apps.feature_toggle.handlers.toggle import FeatureToggleObject
from apps.feature_toggle.plugins.constants import USER_GUIDE_CONFIG
from apps.iam import Permission, ActionEnum
from apps.log_search.constants import UserMetaConfType
from apps.utils import APIModel
from apps.api import BKLoginApi, CmsiApi, TransferApi
from apps.log_search.models import ProjectInfo, UserMetaConf, Space
from apps.utils.local import get_request_username
from apps.log_search import exceptions
from apps.feature_toggle.handlers import toggle


class MetaHandler(APIModel):
    @classmethod
    def get_user_spaces(cls, username):
        spaces = Space.objects.all()
        spaces = Permission(username).filter_space_list_by_action(ActionEnum.VIEW_BUSINESS, spaces)
        allowed_space_mapping = {space.bk_biz_id for space in spaces}

        # 获取置顶空间列表
        # 返回格式： space_uid 的列表
        sticky_spaces = TransferApi.list_sticky_spaces({"username": username})

        result = []
        for space in spaces:
            result.append(
                {
                    "id": space.id,
                    "space_type_id": space.space_type_id,
                    "space_type_name": space.space_type_name,
                    "space_id": space.space_id,
                    "space_name": space.space_name,
                    "space_uid": space.space_uid,
                    "space_code": space.space_code,
                    "bk_biz_id": space.bk_biz_id,
                    "time_zone": space.properties.get("time_zone", "Asia/Shanghai"),
                    "is_sticky": space.space_uid in sticky_spaces,
                    "permission": {ActionEnum.VIEW_BUSINESS.id: space.bk_biz_id in allowed_space_mapping},
                }
            )
        return result

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
        allowed_business_mapping = {project.bk_biz_id for project in business_list}

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
    def get_menus(cls, space_uid, is_superuser):
        modules = copy.deepcopy(settings.MENUS)
        cls.get_present_menus(modules, is_superuser)
        return modules

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

        # 管理员可见采集链路管理页面和提取链路接入
        if (
            module["id"] == "manage_data_link"
            or module["id"] == "extract_link_manage"
            or module["id"] == "manage_data_link_conf"
        ):
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
    def get_biz_maintainer(cls, space_uid):
        """
        @summary:查询业务运维列表
        """
        # TODO: 确认改函数是否已被废弃
        return {"bk_biz_name": space_uid, "maintainer": []}

    @classmethod
    def get_present_menus(cls, child_modules, is_superuser):
        if not isinstance(child_modules, list):
            raise exceptions.SettingMenuException

        for child_module in child_modules[:]:
            if "feature" not in child_module:
                raise exceptions.SettingMenuException
            if not cls.check_menu_feature(child_module, is_superuser):
                child_modules.remove(child_module)
                continue
            if "scenes" in child_module and not toggle.feature_switch(child_module["scenes"]):
                child_modules.remove(child_module)
                continue
            child_module["project_manage"] = True
            if "children" in child_module:
                cls.get_present_menus(child_module["children"], is_superuser)

    @classmethod
    def check_menu_feature(cls, module, is_superuser):
        toggle = module["feature"]
        if toggle == "off":
            return False

        if toggle == "debug":
            if settings.ENVIRONMENT not in ["dev", "stag"] and not is_superuser:
                return False

        if module["id"] in ["manage_data_link", "extract_link_manage", "manage_data_link_conf"]:
            return True if is_superuser else False

        return True

    @classmethod
    def get_user_guide(cls, username):
        toggle = FeatureToggleObject.toggle(USER_GUIDE_CONFIG)
        if not toggle:
            return {}
        feature_config = toggle.feature_config
        user_meta_conf = UserMetaConf.objects.filter(username=username, type=UserMetaConfType.USER_GUIDE).first()
        if not user_meta_conf:
            meta_conf = {
                toggle_key: {**toggle_val, **{"current_step": 0}} for toggle_key, toggle_val in feature_config.items()
            }
        else:
            meta_conf = {
                toggle_key: {**toggle_val, **{"current_step": user_meta_conf.conf.get(toggle_key, 0)}}
                for toggle_key, toggle_val in feature_config.items()
            }
        return meta_conf

    @classmethod
    def update_user_guide(cls, username, user_guide_dict):
        user_meta_conf = UserMetaConf.objects.filter(username=username, type=UserMetaConfType.USER_GUIDE).first()
        if not user_meta_conf:
            user_meta_conf = UserMetaConf.objects.create(username=username, type=UserMetaConfType.USER_GUIDE, conf={})
        user_meta_conf.conf.update(user_guide_dict)
        user_meta_conf.save()
