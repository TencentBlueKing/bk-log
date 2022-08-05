# -*- coding: utf-8 -*-
from rest_framework import serializers

from bkm_space.utils import inject_space_field


def patched_validate(self, attr):
    """
    改写 DRF serializer 基类，增加空间相关参数
    """
    return inject_space_field(attr)


def patch():
    serializers.Serializer.validate = patched_validate
