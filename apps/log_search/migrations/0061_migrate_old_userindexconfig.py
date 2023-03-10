# -*- coding: utf-8 -*-
from django.db import migrations


def forwards_func(apps, schema_editor):
    user_index_set_config_model = apps.get_model("log_search", "UserIndexSetConfig")
    index_set_fields_config_model = apps.get_model("log_search", "IndexSetFieldsConfig")
    user_index_set_fields_config_model = apps.get_model("log_search", "UserIndexSetFieldsConfig")

    total = 0
    success = 0
    failed = 0

    old_config_objs = list(user_index_set_config_model.objects.filter(is_deleted=False).all())
    for old_config_obj in old_config_objs:
        scope = old_config_obj.scope
        # 由于目前trace弃用该配置, 所以只同步scope为default的配置
        if scope != "default":
            continue
        total += 1
        index_set_id = old_config_obj.index_set_id
        username = old_config_obj.created_by
        display_fields = old_config_obj.display_fields
        sort_list = old_config_obj.sort_list
        config_name = f"{username}的配置"
        try:
            # 先创建配置
            new_config_obj = index_set_fields_config_model.objects.create(
                name=config_name,
                index_set_id=index_set_id,
                display_fields=display_fields,
                sort_list=sort_list,
            )
            # 再将用户该索引集的配置关联到新创建的配置
            user_config_obj = user_index_set_fields_config_model.objects.create(
                index_set_id=index_set_id,
                username=username,
                config_id=new_config_obj.id,
            )
            success += 1
        except Exception as e:
            print(f"Migrate old config failed, err: {e}")
            failed += 1

    print(f"Total: {total}, Success: {success}, Failed: {failed}")


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0060_indexsetfieldsconfig_userindexsetfieldsconfig"),
    ]

    operations = [migrations.RunPython(forwards_func)]
