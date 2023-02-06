"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
from django.db.transaction import atomic
from django.forms import model_to_dict
from django.utils.translation import ugettext_lazy as _

from apps.api import TransferApi
from apps.log_databus.constants import ArchiveInstanceType, RESTORE_INDEX_SET_PREFIX
from apps.log_databus.exceptions import (
    ArchiveNotFound,
    RestoreNotFound,
    RestoreExpired,
    CollectorConfigNotExistException,
    CollectorActiveException,
)
from apps.log_databus.models import ArchiveConfig, RestoreConfig, CollectorConfig
from apps.log_search.constants import DEFAULT_TIME_FIELD, TimeFieldTypeEnum, TimeFieldUnitEnum, InnerTag
from apps.log_search.handlers.index_set import IndexSetHandler
from apps.log_search.models import Scenario
from apps.utils.db import array_group, array_hash
from apps.utils.function import ignored
from apps.utils.time_handler import format_user_time_zone, format_user_time_zone_humanize
from apps.utils.local import get_local_param
from bkm_space.utils import bk_biz_id_to_space_uid


class ArchiveHandler:
    def __init__(self, archive_config_id=None):
        self.archive = None
        if archive_config_id is not None:
            try:
                self.archive: ArchiveConfig = ArchiveConfig.objects.get(archive_config_id=archive_config_id)
            except ArchiveConfig.DoesNotExist:
                raise ArchiveNotFound

    @classmethod
    def to_user_time_format(cls, time):
        return format_user_time_zone(time, get_local_param("time_zone"))

    @classmethod
    def list(cls, archives):
        """
        list
        @param archives:
        @return:
        """
        archive_group = array_group(archives, "archive_config_id", True)
        archive_config_ids = list(archive_group.keys())
        archive_objs = ArchiveConfig.objects.filter(archive_config_id__in=archive_config_ids)
        table_ids = [archive.table_id for archive in archive_objs]
        archive_detail = array_group(TransferApi.list_result_table_snapshot({"table_ids": table_ids}), "table_id", True)
        for archive in archive_objs:
            archive_group[archive.archive_config_id]["instance_name"] = archive.instance_name
            archive_group[archive.archive_config_id]["_collector_config_id"] = archive.collector_config_id
            for field in ["doc_count", "store_size", "index_count"]:
                archive_group[archive.archive_config_id][field] = archive_detail[archive.table_id][field]
        return archives

    def retrieve(self, page, pagesize):
        """
        retrieve
        @param page:
        @param pagesize:
        @return:
        """
        snapshot_info, *_ = TransferApi.list_result_table_snapshot_indices({"table_ids": [self.archive.table_id]})
        archive = model_to_dict(self.archive)
        indices = []
        for snapshot in snapshot_info:
            for indice in snapshot.get("indices", []):
                indices.append(
                    {
                        **indice,
                        "start_time": self.to_user_time_format(indice.get("start_time")),
                        "end_time": self.to_user_time_format(indice.get("end_time")),
                        "expired_time": format_user_time_zone_humanize(
                            snapshot.get("expired_time"), get_local_param("time_zone")
                        ),
                        "state": snapshot.get("state"),
                    }
                )
        archive["indices"] = indices[page * pagesize : (page + 1) * pagesize]
        return archive

    @atomic
    def create_or_update(self, params):
        """
        create_or_update
        @param params:
        @return:
        """
        if self.archive:
            self.archive.snapshot_days = params.get("snapshot_days")
            self.archive.save()
            meta_update_params = {"table_id": self.archive.table_id, "snapshot_days": self.archive.snapshot_days}
            TransferApi.modify_result_table_snapshot(meta_update_params)
            return
        # 只有采集项类型需要确认结果表状态
        if params["instance_type"] == ArchiveInstanceType.COLLECTOR_CONFIG.value:
            try:
                collector: CollectorConfig = CollectorConfig.objects.get(collector_config_id=params["instance_id"])
            except CollectorConfig.DoesNotExist:
                raise CollectorConfigNotExistException
            if not collector.is_active:
                raise CollectorActiveException
        create_obj = ArchiveConfig.objects.create(**params)
        meta_create_params = {
            "table_id": create_obj.table_id,
            "target_snapshot_repository_name": create_obj.target_snapshot_repository_name,
            "snapshot_days": create_obj.snapshot_days,
        }
        TransferApi.create_result_table_snapshot(meta_create_params)

    @atomic
    def delete(self):
        self.archive.delete()
        TransferApi.delete_result_table_snapshot({"table_id": self.archive.table_id})

    @atomic
    def restore(self, bk_biz_id, index_set_name, start_time, end_time, expired_time, notice_user):
        """
        restore
        @param bk_biz_id:
        @param index_set_name:
        @param start_time:
        @param end_time:
        @param expired_time:
        @param notice_user:
        @return:
        """
        index_set = self._create_index_set(index_set_name)
        create_restore_config = RestoreConfig.objects.create(
            **{
                "bk_biz_id": bk_biz_id,
                "archive_config_id": self.archive.archive_config_id,
                "start_time": start_time,
                "end_time": end_time,
                "expired_time": expired_time,
                "index_set_name": index_set_name,
                "notice_user": ",".join(notice_user),
            }
        )

        meta_params = {
            "table_id": self.archive.table_id,
            "start_time": start_time,
            "end_time": end_time,
            "expired_time": expired_time,
        }
        meta_restore_result = TransferApi.restore_result_table_snapshot(meta_params)

        create_restore_config.index_set_id = index_set.index_set_id
        create_restore_config.meta_restore_id = meta_restore_result["restore_id"]
        create_restore_config.total_store_size = meta_restore_result["total_store_size"]
        create_restore_config.total_doc_count = meta_restore_result["total_doc_count"]
        create_restore_config.save()

    def _create_index_set(self, index_set_name):
        index_set_name = _("[回溯]") + index_set_name
        indexes = [
            {
                "bk_biz_id": self.archive.bk_biz_id,
                "result_table_id": f"{RESTORE_INDEX_SET_PREFIX}*{self.archive.table_id.replace('.', '_')}_*",
                "result_table_name": self.archive.instance_name,
                "time_field": DEFAULT_TIME_FIELD,
            }
        ]

        cluster_infos = TransferApi.get_result_table_storage(
            {"result_table_list": self.archive.table_id, "storage_type": "elasticsearch"}
        )
        cluster_info = cluster_infos.get(self.archive.table_id)
        storage_cluster_id = cluster_info["cluster_config"]["cluster_id"]
        index_set = IndexSetHandler.create(
            index_set_name=index_set_name,
            space_uid=bk_biz_id_to_space_uid(self.archive.bk_biz_id),
            storage_cluster_id=storage_cluster_id,
            scenario_id=Scenario.ES,
            view_roles=[],
            indexes=indexes,
            category_id=self.archive.instance.category_id,
            collector_config_id=self.archive.collector_config_id,
            time_field=DEFAULT_TIME_FIELD,
            time_field_type=TimeFieldTypeEnum.DATE.value,
            time_field_unit=TimeFieldUnitEnum.MILLISECOND.value,
        )
        index_set.set_tag(index_set.index_set_id, InnerTag.RESTORING.value)
        return index_set

    @classmethod
    def list_archive(cls, bk_biz_id):
        """
        list_archive
        @param bk_biz_id:
        @return:
        """
        return [
            {
                "archive_config_id": archive.archive_config_id,
                "instance_name": archive.instance_name,
                "instance_id": archive.instance_id,
            }
            for archive in ArchiveConfig.objects.filter(bk_biz_id=bk_biz_id)
        ]

    @classmethod
    def list_restore(cls, restore_list):
        """
        list_restore
        @param restore_list:
        @return:
        """
        ret = []
        instances = restore_list.serializer.instance
        for instance in instances:
            # archive config maybe delete so not show restore
            with ignored(ArchiveConfig.DoesNotExist):
                ret.append(
                    {
                        "restore_config_id": instance.restore_config_id,
                        "index_set_name": instance.index_set_name,
                        "index_set_id": instance.index_set_id,
                        "start_time": cls.to_user_time_format(instance.start_time),
                        "end_time": cls.to_user_time_format(instance.end_time),
                        "expired_time": cls.to_user_time_format(instance.expired_time),
                        "total_store_size": instance.total_store_size,
                        "instance_id": instance.archive.instance_id,
                        "instance_name": instance.archive.instance_name,
                        "instance_type": instance.archive.instance_type,
                        "_collector_config_id": instance.archive.collector_config_id,
                        "archive_config_id": instance.archive.archive_config_id,
                        "notice_user": instance.notice_user.split(","),
                        "is_expired": instance.is_expired(),
                    }
                )
        return ret

    @classmethod
    @atomic
    def update_restore(cls, restore_config_id, expired_time):
        """
        update_restore
        @param restore_config_id:
        @param expired_time:
        @return:
        """
        try:
            restore: RestoreConfig = RestoreConfig.objects.get(restore_config_id=restore_config_id)
        except RestoreConfig.DoesNotExist:
            raise RestoreNotFound
        if restore.is_expired():
            raise RestoreExpired

        restore.expired_time = expired_time
        restore.save()
        TransferApi.modify_restore_result_table_snapshot(
            {"restore_id": restore.meta_restore_id, "expired_time": expired_time}
        )

    @classmethod
    @atomic
    def delete_restore(cls, restore_config_id):
        """
        delete_restore
        @param restore_config_id:
        @return:
        """
        try:
            restore: RestoreConfig = RestoreConfig.objects.get(restore_config_id=restore_config_id)
        except RestoreConfig.DoesNotExist:
            raise RestoreNotFound
        restore.delete()
        index_set_handler = IndexSetHandler(restore.index_set_id)
        index_set_handler.stop()
        TransferApi.delete_restore_result_table_snapshot({"restore_id": restore.meta_restore_id})

    def archive_state(self):
        return TransferApi.get_result_table_snapshot_state({"table_ids": [self.archive.table_id]})

    @staticmethod
    def batch_get_restore_state(restore_config_ids: list):
        """
        batch_get_restore_state
        @param restore_config_ids:
        @return:
        """
        restores = RestoreConfig.objects.filter(restore_config_id__in=restore_config_ids).values(
            "meta_restore_id", "restore_config_id"
        )
        meta_restore_ids = [restore["meta_restore_id"] for restore in restores]
        restore_hash = array_hash(restores, "meta_restore_id", "restore_config_id")
        meta_restore_states = TransferApi.get_restore_result_table_snapshot_state({"restore_ids": meta_restore_ids})
        for meta_restore_state in meta_restore_states:
            meta_restore_state["restore_config_id"] = restore_hash[meta_restore_state["restore_id"]]
        return meta_restore_states
