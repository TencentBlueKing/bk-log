# -*- coding: utf-8 -*-

from django.db import migrations

from bkm_space.utils import bk_biz_id_to_space_uid


def forwards_func(apps, schema_editor):
    project_model_cls = apps.get_model("log_search", "ProjectInfo")
    project_biz_mapping = {}
    for project in project_model_cls.objects.all():
        project_biz_mapping[project.project_id] = project.bk_biz_id
    print("[convert project_id to space_uid] projects fetch count: {}".format(len(project_biz_mapping)))

    for model_name in ["AccessSourceConfig", "LogIndexSet", "ResourceChange", "FavoriteSearch"]:
        model_cls = apps.get_model("log_search", model_name)
        success = 0
        failed = 0
        skipped = 0
        for record in model_cls.objects.all():
            if record.space_uid or not record.project_id:
                # 已经有 space_uid 就直接忽略
                skipped += 1
            elif record.project_id not in project_biz_mapping:
                # 项目ID对应的业务不存在，则标记为失败
                failed += 1
            else:
                record.space_uid = bk_biz_id_to_space_uid(project_biz_mapping[record.project_id])
                record.save(update_fields=["space_uid"])
                success += 1
        print(
            "[convert project_id to space_uid] model({}), success({}), skipped({}), failed({})".format(
                model_name, success, skipped, failed
            )
        )


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0048_auto_20220807_1713"),
    ]

    operations = [migrations.RunPython(forwards_func)]
