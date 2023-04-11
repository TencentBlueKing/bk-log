# -*- coding: utf-8 -*-
from django.db import migrations

from apps.log_databus.constants import TargetNodeTypeEnum
from apps.log_search.models import Favorite


def forwards_func(apps, schema_editor):
    objs = list(Favorite.objects.all())
    for obj in objs:
        ip_chooser = {}
        params = obj.params
        host_scopes = params.get("host_scopes", {})
        target_nodes = host_scopes.get("target_nodes", [])

        if target_nodes:
            if not host_scopes.get("target_node_type"):
                continue
            if host_scopes["target_node_type"] == TargetNodeTypeEnum.INSTANCE.value:
                ip_chooser["host_list"] = [
                    {"ip": target_node["ip"], "cloud_area": {"id": target_node["bk_cloud_id"]}}
                    for target_node in target_nodes
                ]
            elif host_scopes["target_node_type"] == TargetNodeTypeEnum.DYNAMIC_GROUP.value:
                ip_chooser["dynamic_group_list"] = [{"id": target_node["id"]} for target_node in target_nodes]
            elif host_scopes["target_node_type"] == TargetNodeTypeEnum.SERVICE_TEMPLATE.value:
                ip_chooser["service_template_list"] = [{"id": target_node["id"]} for target_node in target_nodes]
            elif host_scopes["target_node_type"] == TargetNodeTypeEnum.SET_TEMPLATE.value:
                ip_chooser["set_template_list"] = [{"id": target_node["id"]} for target_node in target_nodes]
            else:
                ip_chooser["node_list"] = [
                    {
                        "object_id": target_node["object_id"],
                        "instance_id": target_node["instance_id"],
                    }
                    for target_node in target_nodes
                ]
        params["ip_chooser"] = ip_chooser
        obj.params = params
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0064_fix_abnormal_operator"),
    ]

    operations = [migrations.RunPython(forwards_func)]
