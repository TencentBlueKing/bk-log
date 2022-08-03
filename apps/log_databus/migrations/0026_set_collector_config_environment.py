# -*- coding: utf-8 -*-

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    collector_config = apps.get_model("log_databus", "CollectorConfig")
    collector_configs = collector_config.objects.filter(environment__isnull=True)
    for collector in collector_configs:
        if collector.collector_scenario_id == "wineventlog":
            collector.environment = "windows"
        else:
            collector.environment = "linux"
        collector.save()


class Migration(migrations.Migration):

    dependencies = [
        ("log_databus", "0025_auto_20220621_1042"),
    ]

    operations = [migrations.RunPython(forwards_func)]
