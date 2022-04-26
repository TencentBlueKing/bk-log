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
from django.db import models
from .settings import APP_LABEL


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.IntegerField()
    login = models.CharField(unique=True, max_length=190)
    email = models.CharField(unique=True, max_length=190)
    name = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    salt = models.CharField(max_length=50, blank=True, null=True)
    rands = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    org_id = models.BigIntegerField()
    is_admin = models.IntegerField()
    email_verified = models.IntegerField(blank=True, null=True)
    theme = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    help_flags1 = models.BigIntegerField()
    last_seen_at = models.DateTimeField(blank=True, null=True)
    is_disabled = models.IntegerField()

    class Meta:
        managed = False
        app_label = APP_LABEL
        db_table = "user"


class Org(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.IntegerField()
    name = models.CharField(unique=True, max_length=190)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    billing_email = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        app_label = APP_LABEL
        db_table = "org"


class OrgUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    org_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    role = models.CharField(max_length=20)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        app_label = APP_LABEL
        db_table = "org_user"
        unique_together = (("org_id", "user_id"),)


class DataSource(models.Model):
    id = models.BigAutoField(primary_key=True)
    org_id = models.BigIntegerField()
    version = models.IntegerField()
    type = models.CharField(max_length=255)
    name = models.CharField(max_length=190)
    access = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    password = models.CharField(max_length=255, blank=True, null=True)
    user = models.CharField(max_length=255, blank=True, null=True)
    database = models.CharField(max_length=255, blank=True, null=True)
    basic_auth = models.BooleanField(default=False)
    basic_auth_user = models.CharField(max_length=255, blank=True, null=True)
    basic_auth_password = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    json_data = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    with_credentials = models.BooleanField(default=False)
    secure_json_data = models.TextField(blank=True, null=True)
    read_only = models.BooleanField(default=False)

    def __str__(self):
        return f"<{self.id}, {self.name}>"

    class Meta:
        managed = False
        app_label = APP_LABEL
        db_table = "data_source"
        unique_together = (("org_id", "name"),)


class Dashboard(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.IntegerField()
    slug = models.CharField(max_length=189)
    title = models.CharField(max_length=189)
    data = models.TextField()
    org_id = models.BigIntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    gnet_id = models.BigIntegerField(blank=True, null=True)
    plugin_id = models.CharField(max_length=189, blank=True, null=True)
    folder_id = models.BigIntegerField()
    is_folder = models.IntegerField()
    has_acl = models.IntegerField()
    uid = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        app_label = APP_LABEL
        db_table = "dashboard"
        unique_together = (
            ("org_id", "folder_id", "title"),
            ("org_id", "uid"),
        )
