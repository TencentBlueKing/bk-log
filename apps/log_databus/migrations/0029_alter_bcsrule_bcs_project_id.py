# Generated by Django 3.2.5 on 2022-07-19 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_databus", "0028_merge_0024_auto_20220510_1434_0027_auto_20220706_0012"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bcsrule",
            name="bcs_project_id",
            field=models.CharField(default="", max_length=64, verbose_name="项目ID"),
        ),
    ]
