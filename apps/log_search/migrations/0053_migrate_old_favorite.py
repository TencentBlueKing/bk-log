# -*- coding: utf-8 -*-

from django.db import migrations

from apps.log_search.constants import FavoriteVisibleType
from apps.log_search.handlers.search.favorite_handlers import FavoriteHandler


def forwards_func(apps, schema_editor):
    old_favorite_model = apps.get_model("log_search", "FavoriteSearch")
    search_history_model = apps.get_model("log_search", "UserIndexSetSearchHistory")
    index_set_model = apps.get_model("log_search", "LogIndexSet")

    old_favorite_cnt = old_favorite_model.objects.all().count()
    delete_cnt = 0
    success_migrate_cnt = 0
    failed_migrate_cnt = 0

    for old_favorite_obj in old_favorite_model.objects.all():
        try:
            name = old_favorite_obj.description
            search_history_id = old_favorite_obj.search_history_id
            space_uid = old_favorite_obj.space_uid

            search_history = search_history_model.objects.get(pk=search_history_id)
            index_set_id = search_history.index_set_id
            if not index_set_model.objects.filter(index_set_id=index_set_id).exists():
                print(f"Old favorite [{name}]'s index_set: [{index_set_id}] is not exist, do not migrate it.")
                delete_cnt += 1
                continue
            params = search_history.params
            favorite_obj = FavoriteHandler(space_uid=space_uid).create_or_update(
                name=name,
                host_scopes=params.get("host_scopes"),
                addition=params.get("addition"),
                keyword=params.get("keyword"),
                visible_type=str(FavoriteVisibleType.PUBLIC.value),
                search_fields=[],
                display_fields=[],
                index_set_id=index_set_id,
            )
            if favorite_obj["name"] == name:
                success_migrate_cnt += 1
        except Exception as e:
            print(f"Migrate old favorite failed, err: {e}")
            failed_migrate_cnt += 1

    print(f"All({old_favorite_cnt}),Success({success_migrate_cnt}),Failed({failed_migrate_cnt}),Delete({delete_cnt})")


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0052_auto_20221017_0232"),
    ]

    operations = [migrations.RunPython(forwards_func)]
