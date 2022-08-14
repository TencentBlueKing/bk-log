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

import abc
from typing import List

from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy

from apps.api import TransferApi
from apps.iam.exceptions import ResourceNotExistError
from bkm_space.define import SpaceTypeEnum
from bkm_space.utils import space_uid_to_bk_biz_id
from iam import Resource


class ResourceMeta(metaclass=abc.ABCMeta):
    """
    资源定义
    """

    system_id: str = ""
    id: str = ""
    name: str = ""
    selection_mode: str = ""
    related_instance_selections: List = ""

    @classmethod
    def to_json(cls):
        return {
            "system_id": cls.system_id,
            "id": cls.id,
            "selection_mode": cls.selection_mode,
            "related_instance_selections": cls.related_instance_selections,
        }

    @classmethod
    def get_biz_attribute(cls, bk_biz_id):
        attribute = {}
        from apps.log_search.models import Space

        space = Space.objects.filter(bk_biz_id=bk_biz_id).first()
        if space:
            attribute.update({"id": str(space.space_id), "name": space.space_name})
            instance_type = None
            if space.space_type_id == SpaceTypeEnum.BKCC.value:
                instance_type = Business.id
            elif space.space_type_id == SpaceTypeEnum.BCS.value:
                instance_type = BcsProject.id
            elif space.space_type_id == SpaceTypeEnum.BKDEVOPS.value:
                instance_type = DevopsProject.id
            if instance_type:
                # 补充路径信息
                attribute.update({"_bk_iam_path_": "/{},{}/".format(instance_type, space.space_id)})
        return attribute

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        """
        创建简单资源实例
        :param instance_id: 实例ID
        :param attribute: 属性kv对
        """
        attribute = attribute or {}
        if "bk_biz_id" in attribute:
            attribute.update(cls.get_biz_attribute(attribute["bk_biz_id"]))
        return Resource(cls.system_id, cls.id, str(instance_id), attribute)

    @classmethod
    def create_instance(cls, instance_id: str, attribute=None) -> Resource:
        """
        创建资源实例（带实例名称）可由子类重载
        :param instance_id: 实例ID
        :param attribute: 属性kv对
        """
        return cls.create_simple_instance(instance_id, attribute)


class Business(ResourceMeta):
    """
    CMDB业务
    """

    system_id = "bk_cmdb"
    id = "biz"
    name = _lazy("业务")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "business"}]

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        """
        创建简单资源实例
        :param instance_id: 实例ID
        :param attribute: 属性kv对
        """
        from apps.log_search.models import Space

        space = Space.objects.filter(bk_biz_id=instance_id).first()
        if not space:
            resource_cls = Business
        elif space.space_type_id == SpaceTypeEnum.BKCC.value:
            resource_cls = Business
        elif space.space_type_id == SpaceTypeEnum.BCS.value:
            resource_cls = BcsProject
        elif space.space_type_id == SpaceTypeEnum.BKDEVOPS.value:
            resource_cls = DevopsProject
        else:
            resource_cls = Business

        return Resource(
            system=resource_cls.system_id,
            type=resource_cls.id,
            id=str(instance_id),
            attribute={"id": str(instance_id), "name": space.space_name if space else str(instance_id)},
        )


class BcsProject(Business):
    """
    BCS 项目
    """

    system_id = "bk_bcs_app"
    id = "project"
    name = _lazy("BCS项目")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "project_list"}]


class DevopsProject(Business):
    """
    蓝盾项目
    """

    system_id = "bk_ci"
    id = "project"
    name = _lazy("蓝盾项目")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "project_instance"}]


class Collection(ResourceMeta):

    system_id = settings.BK_IAM_SYSTEM_ID
    id = "collection"
    name = _lazy("采集项")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "collection_list"}]

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        from apps.log_databus.models import CollectorConfig

        resource = super().create_simple_instance(instance_id, attribute)
        if resource.attribute:
            return resource

        try:
            config = CollectorConfig.objects.get(pk=instance_id)
        except CollectorConfig.DoesNotExist:
            return resource
        resource.attribute = {
            "id": str(instance_id),
            "name": config.collector_config_name,
            "bk_biz_id": config.bk_biz_id,
            "_bk_iam_path_": cls.get_biz_attribute(config.bk_biz_id).get("_bk_iam_path_", ""),
        }
        return resource


class EsSource(ResourceMeta):

    system_id = settings.BK_IAM_SYSTEM_ID
    id = "es_source"
    name = _lazy("ES源")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "es_source_list"}]

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        resource = super().create_simple_instance(instance_id, attribute)
        if resource.attribute:
            return resource

        try:
            result = TransferApi.get_cluster_info({"cluster_id": instance_id})
            if not result:
                return resource
            cluster_info = result[0]
            name = cluster_info["cluster_config"]["cluster_name"]
            bk_biz_id = cluster_info["cluster_config"]["custom_option"].get("bk_biz_id", 0)
        except Exception:  # pylint: disable=broad-except
            return resource
        resource.attribute = {
            "id": str(instance_id),
            "name": name,
            "bk_biz_id": bk_biz_id,
            "_bk_iam_path_": cls.get_biz_attribute(bk_biz_id).get("_bk_iam_path_", ""),
        }
        return resource


class Indices(ResourceMeta):

    system_id = settings.BK_IAM_SYSTEM_ID
    id = "indices"
    name = _lazy("索引集")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "indices_list"}]

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        from apps.log_search.models import LogIndexSet

        resource = super().create_simple_instance(instance_id, attribute)
        if resource.attribute:
            return resource

        try:
            index_set = LogIndexSet.objects.get(pk=instance_id)
        except LogIndexSet.DoesNotExist:
            return resource
        bk_biz_id = space_uid_to_bk_biz_id(index_set.space_uid)
        resource.attribute = {
            "id": str(instance_id),
            "name": index_set.index_set_name,
            "bk_biz_id": bk_biz_id,
            "_bk_iam_path_": cls.get_biz_attribute(bk_biz_id).get("_bk_iam_path_", ""),
        }
        return resource


class ResourceEnum:
    """
    资源类型枚举
    """

    BUSINESS = Business
    BCS_PROJECT = BcsProject
    DEVOPS_PROJECT = DevopsProject
    COLLECTION = Collection
    ES_SOURCE = EsSource
    INDICES = Indices


_all_resources = {resource.id: resource for resource in ResourceEnum.__dict__.values() if hasattr(resource, "id")}


def get_resource_by_id(resource_id: str) -> ResourceMeta:
    """
    根据资源ID获取资源
    """
    if resource_id not in _all_resources:
        raise ResourceNotExistError(_("资源ID不存在：{resource_id}").format(resource_id=resource_id))

    return _all_resources[resource_id]
