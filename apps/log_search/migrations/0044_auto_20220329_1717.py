# Generated by Django 3.2.5 on 2022-03-29 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0043_auto_20220126_1152"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asynctask",
            name="request_param",
            field=models.JSONField(verbose_name="检索请求参数"),
        ),
        migrations.AlterField(
            model_name="asynctask",
            name="sorted_param",
            field=models.JSONField(blank=True, null=True, verbose_name="异步导出排序字段"),
        ),
        migrations.AlterField(
            model_name="usermetaconf",
            name="conf",
            field=models.JSONField(default=dict, verbose_name="用户meta配置"),
        ),
    ]
