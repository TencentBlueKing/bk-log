# -*- coding: utf-8 -*-
import os
import json
import codecs

from django.db import migrations
from django.conf import settings

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "initial.json"

    dependencies = [("iam_migration", "0007_bk_log_search_202106281034")]

    operations = [migrations.RunPython(forward_func)]
