# -*- coding: utf-8 -*-
from django.db import migrations


def forwards_func(apps, schema_editor):
    favorite_model = apps.get_model("log_search", "Favorite")
    user_index_set_search_history_model = apps.get_model("log_search", "UserIndexSetSearchHistory")

    history_objs = user_index_set_search_history_model.objects.filter(params__contains="operator").all().iterator()
    need_update_history_objs = []
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
        if params["addition"] == addition:
            continue
        params["addition"] = addition
        history_obj.params = params
        if len(need_update_history_objs) < 10:
            need_update_history_objs.append(history_obj)
        else:
            user_index_set_search_history_model.objects.bulk_update(need_update_history_objs, ["params"], batch_size=10)
            need_update_history_objs = []
    if need_update_history_objs:
        user_index_set_search_history_model.objects.bulk_update(need_update_history_objs, ["params"], batch_size=10)

    favorite_objs = favorite_model.objects.filter(params__contains="operator").all()
    need_update_favorite_objs = []
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
        if params["addition"] == addition:
            continue
        params["addition"] = addition
        favorite_obj.params = params
        need_update_favorite_objs.append(favorite_obj)
    if need_update_favorite_objs:
        favorite_model.objects.bulk_update(need_update_favorite_objs, ["params"], batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0063_alter_space_space_uid"),
    ]

    operations = [migrations.RunPython(forwards_func)]
