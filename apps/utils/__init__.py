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
import hashlib
import re
import unicodedata
from enum import Enum
from html.parser import HTMLParser

from django.conf import settings


class APIModel(object):
    KEYS = []

    @classmethod
    def init_by_data(cls, data):
        kvs = {_key: data[_key] for _key in cls.KEYS}
        o = cls(**kvs)
        o._data = data
        return o

    def __init__(self, *args, **kwargs):
        self._data = None

    def _get_data(self):
        """
        获取基本数据方法，用于给子类重载
        """
        return None

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data()

        return self._data


def build_auth_args(request):
    """
    组装认证信息
    """
    # auth_args 用于ESB身份校验
    auth_args = {}
    if request is None:
        return auth_args

    for k, v in list(settings.OAUTH_COOKIES_PARAMS.items()):
        if v in request.COOKIES:
            auth_args.update({k: request.COOKIES[v]})

    return auth_args


def html_decode(key):
    """
    @summary:符号转义
    """
    h = HTMLParser()
    cleaned_text = unicodedata.normalize("NFKD", h.unescape(key).strip())
    return cleaned_text


def get_display_from_choices(key, choices):
    """
    choices中获取display
    @apiParam {List} flow_ids
    @apiParamExample {*args} 参数样例:
        "key": "project",
        "choices": (
            ("user", _(u"用户")),
            ("app", _(u"APP")),
            ("project", _(u"项目")),
    @apiSuccessExample {String}
        项目
    """
    for choice in choices:
        if key == choice[0]:
            return choice[1]


class ChoicesEnum(Enum):
    """
    常量枚举choices
    """

    @classmethod
    def get_choices(cls) -> tuple:
        """
        获取所有_choices_labels的tuple元组
        :return: tuple(tuple(key, value))
        """
        return cls._choices_labels.value

    @classmethod
    def get_choice_label(cls, key: str) -> dict:
        """
        获取_choices_labels的某个key值的value
        :param key: 获取choices的key值的value
        :return: str 字典value值
        """
        return dict(cls.get_choices()).get(key, key)

    @classmethod
    def get_dict_choices(cls) -> dict:
        """
        获取dict格式的choices字段
        :return: dict{key, value}
        """
        return dict(cls.get_choices())

    @classmethod
    def get_keys(cls) -> tuple:
        """
        获取所有_choices_keys的tuple元组(关联key值)
        :return: tuple(tuple(key, value))
        """
        return cls._choices_keys.value

    @classmethod
    def get_choice_key(cls, key: str) -> dict:
        """
        获取_choices_keys的某个key值的value
        :param key: 获取choices的key值的value
        :return: str 字典value值
        """
        return dict(cls.get_keys()).get(key, key)

    @classmethod
    def get_choices_list_dict(cls) -> list:
        """
        获取_choices_keys的某个key值的value
        :return: list[dict{id, name}]
        """
        return [{"id": key, "name": value} for key, value in cls.get_dict_choices().items()]


def is_match_variate(data):
    return re.compile("[a-zA-Z_]{1}[a-zA-Z0-9_]*").match(data)


def md5_sum(src_str: str):
    """
    计算md5_sum值
    @param src_str {str} 源字符串
    """
    md5 = hashlib.md5()
    md5.update(src_str.encode("utf-8"))
    md5_key = md5.hexdigest()
    return md5_key
