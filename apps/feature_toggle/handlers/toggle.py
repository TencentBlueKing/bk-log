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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.feature_toggle.plugins.base import FeatureToggleBase, get_feature_toggle
from apps.utils.function import ignored
from apps.utils.log import logger


def feature_switch(featue):
    # 如果未设置特性开关，则直接隐藏
    if featue not in settings.FEATURE_TOGGLE:
        return False

    # 灰度功能：非测试环境或管理员直接隐藏
    toggle = settings.FEATURE_TOGGLE[featue]
    if toggle == "off":
        return False
    elif toggle == "debug":
        if settings.ENVIRONMENT not in ["dev", "stag"]:
            return False

    return True


class Toggle(object):
    def __init__(
        self, name="", status="", alias="", description="", is_viewed=True, feature_config=None, biz_id_white_list=None
    ):
        self.name = name
        self.status = status
        self.alias = alias
        self.description = description
        self.is_viewed = is_viewed
        self.feature_config = feature_config
        self.biz_id_white_list = biz_id_white_list


class FeatureToggleObject(object):
    """
    特性开关表
    同一个变量读取顺序为: settings-->db-->plugins
    """

    @classmethod
    def switch(cls, name, biz_id=None):
        """
        获取开关状态
        1. 当获取不到对应开关返回False
        2. 当开关状态返回为off返回False
        3. 当开关状态返回为debug且开关具有白名单配置时，如果传入的业务id处于白名单中则返回True，不传入业务id或者不在白名单中返回false
        4. 当开关状态返回为debug且环境不为预发布或者测试环境返回False
        5. 其他情况为True
        Args:
            name: [str] toggle name
            biz_id: [int] 业务id
        Returns:
            True or False
        """
        toggle = cls.toggle(name=name)
        if not toggle:
            return False

        if toggle.status == "off":
            return False

        if toggle.status == "debug" and toggle.biz_id_white_list:
            if biz_id and biz_id in toggle.biz_id_white_list:
                return True
            else:
                return False

        if toggle.status == "debug" and settings.ENVIRONMENT not in ["dev", "stag"]:
            return False

        return True

    @classmethod
    def toggle(cls, name):
        """
        获取单个name对应相关特性配置等
        Args:
            name: [Str] toggle name
        Returns:
            None or Toggle object
        """
        from apps.feature_toggle.models import FeatureToggle

        param = {}
        if settings.FEATURE_TOGGLE.get(name):
            param["name"] = name
            param["alias"] = ""
            param["status"] = settings.FEATURE_TOGGLE.get(name)
            param["description"] = ""
            param["is_viewed"] = True
            param["feature_config"] = None
            param["biz_id_white_list"] = None

        with ignored(Exception, log_exception=True):
            feature_toggle = FeatureToggle.objects.filter(name=name).first()
            if feature_toggle:
                param["name"] = feature_toggle.name
                param["alias"] = feature_toggle.alias
                param["status"] = feature_toggle.status
                param["description"] = feature_toggle.description
                param["is_viewed"] = feature_toggle.is_viewed
                param["feature_config"] = feature_toggle.feature_config
                param["biz_id_white_list"] = feature_toggle.biz_id_white_list

        if not param:
            return None

        param = cls._load_plugins(name=name, param=param)
        return cls._format_result(param)

    @classmethod
    def toggle_list(cls, **kwargs):
        """
        获取对应filter过滤后的特性开关配置列表
        Args:
            kwargs: 获取对应toggle list 过滤条件
        Returns:
            [Toggle()]
        """
        params = cls._get_params()
        result = list(params.values())
        return [cls._format_result(param) for param in cls._filter_params(result, kwargs)]

    @classmethod
    def _load_plugins(cls, name, param):
        """
        执行对应plugin并将对应返回值赋值给param
        Args:
            name: [Str] toggle name
            param: [Dict] 预存到cache toggle 参数
        Returns:
            param: [Dict] 返回处理后的param
        Raises:
            BaseException: 对应cls没有继承自FutureToggleBase
        """
        feature_toggle_cls = get_feature_toggle(name)
        if not issubclass(feature_toggle_cls, FeatureToggleBase):
            raise BaseException(
                _("{feature_toggle_cls} 没有继承自FutureToggleBase").format(feature_toggle_cls=feature_toggle_cls)
            )
        return feature_toggle_cls().set_status(param=param)

    @classmethod
    def _get_params(cls) -> dict:
        """
        获取全量params combine后的列表
        Returns:
            Dict
        """
        from apps.feature_toggle.models import FeatureToggle

        params = {}
        for name, status in settings.FEATURE_TOGGLE.items():
            params[name] = {
                "name": name,
                "alias": "",
                "status": status,
                "description": "",
                "is_viewed": True,
                "feature_config": None,
                "biz_id_white_list": None,
            }

        for feature_toggle in FeatureToggle.objects.all():
            params[feature_toggle.name] = {
                "name": feature_toggle.name,
                "alias": feature_toggle.alias,
                "status": feature_toggle.status,
                "description": feature_toggle.description,
                "is_viewed": feature_toggle.is_viewed,
                "feature_config": feature_toggle.feature_config,
                "biz_id_white_list": feature_toggle.biz_id_white_list,
            }

        for name, param in params.items():
            try:
                param = cls._load_plugins(name, param)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"load plugin error: {e}")
            else:
                params[name] = param

        return params

    @classmethod
    def _filter_params(cls, params, params_filter):
        """
        获取包含params_filter过滤后的params
        Args:
            params: [Dict] 待过滤参数列表
            params_filter: Dict 过滤参数
        Returns:
            result: [Dict] 过滤后的参数列表
        """
        if not params_filter:
            return params
        result = []
        for param in params:
            if params_filter.items() <= param.items():
                result.append(param)
        return result

    @classmethod
    def _format_result(cls, result):
        """
        将result dict 返回为Toggle object对象
        Returns:
            Toggle
        """

        return Toggle(
            name=result["name"],
            alias=result["alias"],
            status=result["status"],
            description=result["description"],
            is_viewed=result["is_viewed"],
            feature_config=result["feature_config"],
            biz_id_white_list=result["biz_id_white_list"],
        )
