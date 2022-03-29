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
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core import exceptions
from django.db import models

from apps.utils.base_crypt import BaseCrypt
from apps.utils.local import get_request_username


class JsonField(models.TextField):
    """
    Json字段，入库json.dumps， 出库json.load
    """

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return {}
        try:
            return json.loads(value)
        except (TypeError, KeyError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )

    def to_python(self, value):
        if value is None:
            return value
        try:
            return json.dumps(value, cls=DjangoJSONEncoder)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            return json.dumps(value, cls=DjangoJSONEncoder)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )


class MixinMultiStrSplitByCommaField(models.Field):
    """
    多个字段，使用逗号隔开，入库list->str， 出库 str->list
    头尾都加逗号","，为了方便使用ORM的contains进行过滤且避免子集字符串的越权问题
    """

    def read_from_db(self, value, expression, connection, context):
        if not value:
            return []
        try:
            value = value.split(",")
        except (TypeError, KeyError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )
        result = []
        for _v in value[1:-1]:
            try:
                result.append(self.sub_type(_v))
            except ValueError:
                continue

        return result

    def write_to_db(self, value):
        if not value:
            return ""

        if isinstance(value, str):
            if value[0] == "[" and value[-1] == "]":
                value = value[1:-1]
            value = value.split(",")

        value = [str(_value) for _value in value]
        try:
            value = ",%s," % ",".join(value)
        except (TypeError, KeyError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )
        return value


class MultiStrSplitByCommaField(models.CharField, MixinMultiStrSplitByCommaField):
    def __init__(self, *args, **kwargs):
        sub_type = kwargs.get("sub_type")
        if sub_type is None:
            self.sub_type = str
        else:
            self.sub_type = sub_type
        kwargs.pop("sub_type", "")
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        return super().read_from_db(value, expression, connection, context)

    def get_prep_value(self, value):
        return super().write_to_db(value)


class MultiStrSplitByCommaFieldText(models.TextField, MixinMultiStrSplitByCommaField):
    def __init__(self, *args, **kwargs):
        sub_type = kwargs.get("sub_type")
        if sub_type is None:
            self.sub_type = str
        else:
            self.sub_type = sub_type
        kwargs.pop("sub_type", "")
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        return super().read_from_db(value, expression, connection, context)

    def get_prep_value(self, value):
        return super().write_to_db(value)


def model_to_dict(instance, fields=None, exclude=None):
    """Return django model Dict, Override django model_to_dict: <foreignkey use column as key>"""
    opts = instance._meta
    data = {}
    from itertools import chain

    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if f.get_internal_type() == "ForeignKey":
            f.name = f.column
        # if f.choices:
        #     data[f'{f.name}_display'] = getattr(instance, f'get_{f.name}_display')()
        data[f.name] = f.value_from_object(instance)
    return data


class OperateRecordQuerySet(models.query.QuerySet):
    """
    批量更新时写入更新时间和更新者
    """

    def update(self, **kwargs):
        kwargs.update({"updated_at": timezone.now(), "updated_by": get_request_username()})
        super().update(**kwargs)


class OperateRecordModelManager(models.Manager):
    def get_queryset(self):
        return OperateRecordQuerySet(self.model, using=self._db)

    def create(self, *args, **kwargs):
        kwargs.update({"created_at": timezone.now(), "created_by": get_request_username()})
        return super().create(*args, **kwargs)

    def bulk_create(self, *args, **kwargs):
        return super().bulk_create(*args, **kwargs)


class OperateRecordModel(models.Model):
    """
    需要记录操作的model父类
    自动记录创建时间/修改时间与操作者
    """

    objects = OperateRecordModelManager()

    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    created_by = models.CharField(_("创建者"), max_length=32, default="")
    updated_at = models.DateTimeField(_("更新时间"), blank=True, null=True, auto_now=True, db_index=True)
    updated_by = models.CharField(_("修改者"), max_length=32, blank=True, default="")

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.created_at = timezone.now()
            self.created_by = get_request_username()

        self.updated_at = timezone.now()
        self.updated_by = get_request_username()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.query.QuerySet):
    def delete(self):
        self.update(is_deleted=True, deleted_by=get_request_username(), deleted_at=timezone.now())


class SoftDeleteModelManager(OperateRecordModelManager):
    """
    默认的查询和过滤方法, 不显示被标记为删除的记录
    """

    def exclude(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        return super(SoftDeleteModelManager, self).filter(is_deleted=False).exclude(*args, **kwargs)

    def all(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        return super(SoftDeleteModelManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        if not kwargs.get("is_deleted"):
            kwargs["is_deleted"] = False
        return super(SoftDeleteModelManager, self).filter(*args, **kwargs)

    def get(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        if not kwargs.get("is_deleted"):
            kwargs["is_deleted"] = False
        return super(SoftDeleteModelManager, self).get(*args, **kwargs)

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(OperateRecordModel):
    """
    需要记录删除操作的model父类
    自动记录删除时间与删除者
    对于此类的表提供软删除
    """

    objects = SoftDeleteModelManager()

    is_deleted = models.BooleanField(_("是否删除"), default=False)
    deleted_at = models.DateTimeField(_("删除时间"), blank=True, null=True)
    deleted_by = models.CharField(_("删除者"), max_length=32, blank=True, null=True)

    def delete(self, *args, **kwargs):
        """
        删除方法，不会删除数据
        而是通过标记删除字段 is_deleted 来软删除
        """
        self.is_deleted = True
        self.deleted_by = get_request_username()
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True


class EncryptionField(models.TextField):
    """
    加密字段 入库加密 出库解密
    """

    def read_from_db(self, value, expression, connection, context):
        if not value:
            return ""
        return BaseCrypt().decrypt(value)

    def write_to_db(self, value):
        if value is None:
            return ""
        return BaseCrypt().encrypt(value.strip().encode())
