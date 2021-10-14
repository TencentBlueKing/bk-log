from django.db import migrations

from apps.log_search.constants import InnerTag, TagColor


def forwards_func(apps, schema_editor):
    tag_model = apps.get_model("log_search", "IndexSetTag")
    create_objs = [
        tag_model(
            name=InnerTag.TRACE.value,
            color=TagColor.GREEN.value,
        ),
        tag_model(
            name=InnerTag.RESTORING.value,
            color=TagColor.BLUE.value,
        ),
        tag_model(
            name=InnerTag.RESTORED.value,
            color=TagColor.BLUE.value,
        ),
        tag_model(
            name=InnerTag.NO_DATA.value,
            color=TagColor.RED.value,
        ),
        tag_model(
            name=InnerTag.HAVE_DELAY.value,
            color=TagColor.YELLOW.value,
        ),
        tag_model(
            name=InnerTag.BCS.value,
            color=TagColor.BLUE.value,
        ),
        tag_model(
            name=InnerTag.BKDATA.value,
            color=TagColor.BLUE.value,
        ),
    ]
    tag_model.objects.bulk_create(create_objs)


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0039_auto_20210918_1200"),
    ]

    operations = [migrations.RunPython(forwards_func)]
