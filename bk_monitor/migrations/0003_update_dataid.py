from django.db import migrations


def forwards_func(apps, schema_editor):
    monitor_report_config = apps.get_model("bk_monitor", "MonitorReportConfig")
    monitor_report_config.objects.filter(data_name="metric").update(data_id=1100013)


class Migration(migrations.Migration):
    dependencies = [
        ("bk_monitor", "0001_initial"),
    ]
    operations = [migrations.RunPython(forwards_func)]
