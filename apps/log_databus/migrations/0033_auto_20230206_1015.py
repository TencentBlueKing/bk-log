# Generated by Django 3.2.15 on 2023-02-06 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_databus", "0032_auto_20221209_1058"),
    ]

    operations = [
        migrations.RenameField(
            model_name="archiveconfig",
            old_name="collector_config_id",
            new_name="instance_id",
        ),
        migrations.AddField(
            model_name="archiveconfig",
            name="instance_type",
            field=models.CharField(
                choices=[("collector_config", "采集项"), ("collector_plugin", "采集插件")],
                default="collector_config",
                max_length=64,
                verbose_name="实例类型",
            ),
        ),
    ]
