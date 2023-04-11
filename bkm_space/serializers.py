# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkm_space.utils import parse_space_uid


class SpaceUIDField(serializers.CharField):
    def run_validation(self, *args, **kwargs):
        value = super(SpaceUIDField, self).run_validation(*args, **kwargs)
        try:
            parse_space_uid(value)
        except ValueError:
            raise ValidationError(_('"{space_uid}" 不是合法的空间唯一标识符').format(space_uid=value))
        return value
