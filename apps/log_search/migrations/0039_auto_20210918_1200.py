# Generated by Django 2.2.6 on 2021-09-18 04:00

from django.db import migrations

from apps.log_search.constants import (
    ASYNC_EXPORT_EMAIL_ERR_TEMPLATE,
    ASYNC_EXPORT_EMAIL_ERR_TEMPLATE_PATH,
    ASYNC_EXPORT_EMAIL_ERR_TEMPLATE_PATH_EN,
)


def forwards_func(apps, schema_editor):
    email_template = apps.get_model("log_search", "EmailTemplate")
    email_template.objects.bulk_create(
        [
            email_template(
                name=ASYNC_EXPORT_EMAIL_ERR_TEMPLATE, path=ASYNC_EXPORT_EMAIL_ERR_TEMPLATE_PATH, language="zh-cn"
            ),
            email_template(
                name=ASYNC_EXPORT_EMAIL_ERR_TEMPLATE, path=ASYNC_EXPORT_EMAIL_ERR_TEMPLATE_PATH_EN, language="en"
            ),
        ]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0038_auto_20210724_1617"),
    ]

    operations = [migrations.RunPython(forwards_func)]
