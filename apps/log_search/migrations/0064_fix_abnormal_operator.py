# -*- coding: utf-8 -*-
from django.db import migrations

from apps.log_search.models import Favorite, UserIndexSetSearchHistory


def forwards_func(apps, schema_editor):
    history_objs = UserIndexSetSearchHistory.objects.filter(params__contains="operator").all()
    for history_obj in history_objs:
        params = history_obj.params
        addition = params.get("addition", [])
        if not addition:
            continue
        for _add in addition:
            operator = _add.get("operator", "")
            if operator == "is":
                _add["operator"] = "="
            elif operator == "is not":
                _add["operator"] = "!="
        params["addition"] = addition
        history_obj.params = params
        history_obj.save()

    favorite_objs = Favorite.objects.filter(params__contains="operator").all()
    for favorite_obj in favorite_objs:
        params = favorite_obj.params
        addition = params.get("addition", [])
        if not addition:
            continue
        for _add in addition:
            operator = _add.get("operator", "")
            if operator == "is":
                _add["operator"] = "="
            elif operator == "is not":
                _add["operator"] = "!="
        params["addition"] = addition
        favorite_obj.params = params
        favorite_obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0063_alter_space_space_uid"),
    ]

    operations = [migrations.RunPython(forwards_func)]
