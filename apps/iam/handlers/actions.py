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

from typing import Union, List, Dict

from django.utils.translation import ugettext as _

from apps.iam.exceptions import ActionNotExistError
from apps.iam.handlers.resources import ResourceEnum

from iam import Action


class ActionMeta(Action):
    """
    动作定义
    """

    def __init__(
        self,
        id: str,
        name: str,
        name_en: str,
        type: str,
        version: int,
        related_resource_types: list = None,
        related_actions: list = None,
        description: str = "",
        description_en: str = "",
    ):
        super(ActionMeta, self).__init__(id)
        self.name = name
        self.name_en = name_en
        self.type = type
        self.version = version
        self.related_resource_types = related_resource_types or []
        self.related_actions = related_actions or []
        self.description = description
        self.description_en = description_en

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "type": self.type,
            "version": self.version,
            "related_resource_types": self.related_resource_types,
            "related_actions": self.related_actions,
            "description": self.description,
            "description_en": self.description_en,
        }

    def is_read_action(self):
        """
        是否为读权限
        """
        return self.type == "view"


class ActionEnum:

    VIEW_BUSINESS = ActionMeta(
        id="view_business_v2",
        name=_("业务访问"),
        name_en="View Business",
        type="view",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )

    SEARCH_LOG = ActionMeta(
        id="search_log_v2",
        name=_("日志检索"),
        name_en="Search Log",
        type="view",
        related_resource_types=[ResourceEnum.INDICES],
        related_actions=[VIEW_BUSINESS.id],
        version=1,
    )

    VIEW_COLLECTION = ActionMeta(
        id="view_collection_v2",
        name=_("采集查看"),
        name_en="View Collection",
        type="view",
        related_resource_types=[ResourceEnum.COLLECTION],
        related_actions=[],
        version=1,
    )

    CREATE_COLLECTION = ActionMeta(
        id="create_collection_v2",
        name=_("采集新建"),
        name_en="Create Collection",
        type="create",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )

    MANAGE_COLLECTION = ActionMeta(
        id="manage_collection_v2",
        name=_("采集管理"),
        name_en="Manage Collection",
        type="manage",
        related_resource_types=[ResourceEnum.COLLECTION],
        related_actions=[],
        version=1,
    )

    CREATE_ES_SOURCE = ActionMeta(
        id="create_es_source_v2",
        name=_("ES源配置新建"),
        name_en="Create ES Source",
        type="create",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )

    MANAGE_ES_SOURCE = ActionMeta(
        id="manage_es_source_v2",
        name=_("ES源配置管理"),
        name_en="Manage ES Source",
        type="manage",
        related_resource_types=[ResourceEnum.ES_SOURCE],
        related_actions=[],
        version=1,
    )

    CREATE_INDICES = ActionMeta(
        id="create_indices_v2",
        name=_("索引集配置新建"),
        name_en="Create Indices",
        type="create",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )

    MANAGE_INDICES = ActionMeta(
        id="manage_indices_v2",
        name=_("索引集配置管理"),
        name_en="Manage Indices",
        type="manage",
        related_resource_types=[ResourceEnum.INDICES],
        related_actions=[],
        version=1,
    )

    MANAGE_EXTRACT_CONFIG = ActionMeta(
        id="manage_extract_config_v2",
        name=_("提取配置管理"),
        name_en="Manage Extract Config",
        type="manage",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )

    VIEW_DASHBOARD = ActionMeta(
        id="view_dashboard_v2",
        name=_("仪表盘查看"),
        name_en="View Dashboard",
        type="view",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )

    MANAGE_DASHBOARD = ActionMeta(
        id="manage_dashboard_v2",
        name=_("仪表盘管理"),
        name_en="Manage Dashboard",
        type="manage",
        related_resource_types=[ResourceEnum.BUSINESS],
        related_actions=[],
        version=1,
    )


_all_actions = {action.id: action for action in ActionEnum.__dict__.values() if isinstance(action, ActionMeta)}


def get_action_by_id(action_id: Union[str, ActionMeta]) -> ActionMeta:
    """
    根据动作ID获取动作实例
    """
    if isinstance(action_id, ActionMeta):
        # 如果已经是实例，则直接返回
        return action_id

    if action_id not in _all_actions:
        raise ActionNotExistError(_("动作ID不存在：{action_id}").format(action_id=action_id))

    return _all_actions[action_id]


def fetch_related_actions(actions: List[Union[ActionMeta, str]]) -> Dict[str, ActionMeta]:
    """
    递归获取 action 动作依赖列表
    """
    actions = [get_action_by_id(action) for action in actions]

    def fetch_related_actions_recursive(_action: ActionMeta):
        _related_actions = {}
        for related_action_id in _action.related_actions:
            try:
                related_action = get_action_by_id(related_action_id)
            except ActionNotExistError:
                continue
            _related_actions[related_action_id] = related_action
            _related_actions.update(fetch_related_actions_recursive(related_action))
        return _related_actions

    related_actions = {}
    for action in actions:
        related_actions.update(fetch_related_actions_recursive(action))

    # 剔除根节点本身
    for action in actions:
        related_actions.pop(action.id, None)

    return related_actions


def generate_all_actions_json() -> List:
    """
    生成migrations的json配置
    """
    results = []
    for value in _all_actions.values():
        results.append({"operation": "upsert_action", "data": value.to_json()})
    return results
