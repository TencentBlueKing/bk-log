# Generated by Django 2.2.6 on 2021-12-09 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_databus", "0016_archiveconfig_restoreconfig"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="archiveconfig",
            options={"ordering": ("-archive_config_id",), "verbose_name": "归档配置表", "verbose_name_plural": "归档配置表"},
        ),
        migrations.AlterModelOptions(
            name="restoreconfig",
            options={"ordering": ("-restore_config_id",), "verbose_name": "回溯配置表", "verbose_name_plural": "回溯配置表"},
        ),
        migrations.AddField(
            model_name="collectorconfig",
            name="custom_type",
            field=models.CharField(
                choices=[("log", "容器日志上报"), ("otlp_log", "otlp日志上报"), ("otlp_trace", "otlpTrace上报")],
                default="log",
                max_length=30,
                verbose_name="自定义类型",
            ),
        ),
        migrations.AlterField(
            model_name="collectorconfig",
            name="target_node_type",
            field=models.CharField(
                choices=[
                    ("TOPO", "TOPO"),
                    ("INSTANCE", "主机实例"),
                    ("SERVICE_TEMPLATE", "服务模板"),
                    ("SET_TEMPLATE", "集群模板"),
                ],
                default="INSTANCE",
                max_length=32,
                verbose_name="节点类型",
            ),
        ),
        migrations.AlterField(
            model_name="collectorconfig",
            name="target_object_type",
            field=models.CharField(
                choices=[("HOST", "主机"), ("SERVICE", "服务实例")], default="HOST", max_length=32, verbose_name="对象类型"
            ),
        ),
    ]
