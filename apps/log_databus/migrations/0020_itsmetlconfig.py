# Generated by Django 3.2.5 on 2022-04-12 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_databus", "0019_auto_20220411_2105"),
    ]

    operations = [
        migrations.CreateModel(
            name="ItsmEtlConfig",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="创建时间")),
                ("created_by", models.CharField(default="", max_length=32, verbose_name="创建者")),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name="更新时间")),
                ("updated_by", models.CharField(blank=True, default="", max_length=32, verbose_name="修改者")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="删除时间")),
                ("deleted_by", models.CharField(blank=True, max_length=32, null=True, verbose_name="删除者")),
                ("ticket_sn", models.CharField(max_length=255, verbose_name="itsm单据号")),
                ("request_param", models.JSONField(verbose_name="请求参数")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
