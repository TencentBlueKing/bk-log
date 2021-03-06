# Generated by Django 2.2.6 on 2022-01-14 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_clustering", "0006_auto_20211126_2043"),
    ]

    operations = [
        migrations.CreateModel(
            name="NoticeGroup",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="创建时间")),
                ("created_by", models.CharField(default="", max_length=32, verbose_name="创建者")),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name="更新时间")),
                ("updated_by", models.CharField(blank=True, default="", max_length=32, verbose_name="修改者")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="删除时间")),
                ("deleted_by", models.CharField(blank=True, max_length=32, null=True, verbose_name="删除者")),
                ("index_set_id", models.IntegerField(db_index=True, verbose_name="索引集id")),
                ("notice_group_id", models.IntegerField(verbose_name="通知人组id")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SignatureStrategySettings",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="创建时间")),
                ("created_by", models.CharField(default="", max_length=32, verbose_name="创建者")),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name="更新时间")),
                ("updated_by", models.CharField(blank=True, default="", max_length=32, verbose_name="修改者")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="删除时间")),
                ("deleted_by", models.CharField(blank=True, max_length=32, null=True, verbose_name="删除者")),
                ("signature", models.CharField(db_index=True, max_length=256, verbose_name="数据指纹")),
                ("index_set_id", models.IntegerField(db_index=True, verbose_name="索引集id")),
                ("strategy_id", models.IntegerField(blank=True, null=True, verbose_name="监控策略id")),
                ("enabled", models.BooleanField(default=True, verbose_name="是否启用")),
                ("bk_biz_id", models.IntegerField(verbose_name="业务id")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
