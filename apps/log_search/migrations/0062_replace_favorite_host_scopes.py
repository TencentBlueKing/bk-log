# -*- coding: utf-8 -*-
from django.db import migrations

from apps.log_databus.constants import TargetNodeTypeEnum
from apps.log_search.models import Favorite
from apps.utils.ipchooser import BkApi
from bkm_space.utils import space_uid_to_bk_biz_id


def forwards_func(apps, schema_editor):
    objs = list(Favorite.objects.filter(is_deleted=False).all())
    for obj in objs:
        ip_chooser = {}
        params = obj.params
        host_scopes = params.get("host_scopes", {})
        target_nodes = host_scopes.get("target_nodes", [])

        if target_nodes:
            if host_scopes["target_node_type"] == TargetNodeTypeEnum.INSTANCE.value:
                # 因为没有实例ID，所以只能通过IP去查询
                _params = {
                    "bk_biz_id": space_uid_to_bk_biz_id(obj.space_uid),
                    "fields": ["bk_host_id"],
                    "host_property_filter": {
                        "condition": "OR",
                        "rules": [],
                    },
                }
                for target_node in target_nodes:
                    _params["host_property_filter"]["rules"].append(
                        {
                            "condition": "AND",
                            "rules": [
                                {
                                    "field": "bk_cloud_id",
                                    "operator": "equal",
                                    "value": target_node["bk_cloud_id"],
                                },
                                {
                                    "field": "bk_host_innerip",
                                    "operator": "equal",
                                    "value": target_node["ip"],
                                },
                            ],
                        }
                    )
                hosts = BkApi.bulk_list_biz_hosts(_params)
                if not hosts:
                    continue
                ip_chooser["host_list"] = [{"host_id": host["bk_host_id"]} for host in hosts]
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
        ("log_search", "0061_migrate_old_userindexconfig"),
    ]

    operations = [migrations.RunPython(forwards_func)]
