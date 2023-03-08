# -*- coding: utf-8 -*-

from django.db import migrations
from django.utils.crypto import get_random_string

from apps.log_search.constants import FavoriteVisibleType, FavoriteGroupType


def get_or_create_ungrouped_group(apps, space_uid):
    """
    由于动态获取模型的方式，无法调用实例方法, 所以手动实现一次
    """
    favorite_group_model = apps.get_model("log_search", "FavoriteGroup")
    obj, __ = favorite_group_model.objects.get_or_create(
        group_type=FavoriteGroupType.UNGROUPED.value,
        space_uid=space_uid,
        defaults={"name": FavoriteGroupType.get_choice_label(str(FavoriteGroupType.UNGROUPED.value))},
    )
    return obj


def forwards_func(apps, schema_editor):
    old_favorite_model = apps.get_model("log_search", "FavoriteSearch")
    new_favorite_model = apps.get_model("log_search", "Favorite")
    search_history_model = apps.get_model("log_search", "UserIndexSetSearchHistory")
    old_favorite_qs = old_favorite_model.objects.filter(is_deleted=False)
    old_favorite_cnt = old_favorite_qs.count()
    success_migrate_cnt = 0
    failed_migrate_cnt = 0

    for old_favorite_obj in old_favorite_qs.all():
        try:
            name = old_favorite_obj.description
            search_history_id = old_favorite_obj.search_history_id
            space_uid = old_favorite_obj.space_uid
            search_history = search_history_model.objects.get(pk=search_history_id)
            index_set_id = search_history.index_set_id
            params = search_history.params

            if new_favorite_model.objects.filter(name=name, space_uid=space_uid).exists():
                random_suffix = get_random_string(length=10)
                if len(name) + len(str(index_set_id)) + len(random_suffix) > new_favorite_model.name.field.max_length:
                    name = name[
                        : new_favorite_model.name.field.max_length - len(str(index_set_id)) - len(random_suffix)
                    ]
                name = f"{index_set_id}_{name}_{random_suffix}"
            # 检索字段置为空
            params["search_fields"] = []
            group_id = get_or_create_ungrouped_group(apps=apps, space_uid=space_uid).id
            favorite_obj = new_favorite_model.objects.create(
                space_uid=space_uid,
                index_set_id=index_set_id,
                name=name,
                group_id=group_id,
                params=params,
                visible_type=str(FavoriteVisibleType.PUBLIC.value),
                is_enable_display_fields=False,
                display_fields=[],
            )
            favorite_obj.created_by = old_favorite_obj.created_by
            favorite_obj.updated_by = old_favorite_obj.updated_by
            favorite_obj.save()
            if favorite_obj.name == name:
                success_migrate_cnt += 1

        except Exception as e:
            print(f"Migrate old favorite failed, err: {e}")
            failed_migrate_cnt += 1

    print(f"All({old_favorite_cnt}),Success({success_migrate_cnt}),Failed({failed_migrate_cnt})")


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0058_alter_favorite_name"),
    ]

    operations = [migrations.RunPython(forwards_func)]
