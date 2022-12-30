# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.task import periodic_task

from apps.api import TransferApi
from apps.log_search.models import SpaceType, Space
from apps.utils.lock import share_lock
from apps.utils.log import logger
from bkm_space.utils import space_uid_to_bk_biz_id


@periodic_task(run_every=crontab(minute="*/5"))
@share_lock()
def sync():
    """
    同步空间配置
    """
    sync_space_types()
    sync_spaces()


def sync_space_types():
    """
    同步空间类型信息
    """
    space_types = TransferApi.list_space_types()
    all_space_types = []

    for space_type in space_types:
        type_id = space_type.pop("type_id")
        type_name = space_type.pop("type_name")

        type_obj = SpaceType(type_id=type_id, type_name=type_name, properties=space_type, is_deleted=False)
        type_obj.save()

        all_space_types.append(type_obj)

    # 删除不存在的空间类型
    deleted_rows = SpaceType.objects.exclude(type_id__in=[t.type_id for t in all_space_types]).update(is_deleted=True)
    logger.info("[sync_space_types] sync ({}), delete ({})".format(len(all_space_types), deleted_rows))


def sync_spaces():
    """
    同步空间信息
    """
    # 获取类型ID到类型名称的映射
    type_names = {t["type_id"]: t["type_name"] for t in TransferApi.list_space_types()}

    spaces = TransferApi.list_spaces({"is_detail": True, "page": 0})["list"]

    all_spaces = []

    for space in spaces:
        space_pk = space.pop("id")
        space_type_id = space.pop("space_type_id")
        space_type_name = type_names.get(space_type_id, space_type_id)
        space_id = space.pop("space_id")
        space_name = space.pop("space_name")
        space_code = space.pop("space_code") or space_id
        space_uid = space.pop("space_uid")
        bk_biz_id = space_uid_to_bk_biz_id(space_uid=space_uid, id=space_pk)

        space_obj = Space(
            id=space_pk,
            space_uid=space_uid,
            bk_biz_id=bk_biz_id,
            space_type_id=space_type_id,
            space_type_name=space_type_name,
            space_id=space_id,
            space_name=space_name,
            space_code=space_code,
            properties=space,
            is_deleted=False,
        )

        space_obj.save()
        all_spaces.append(space_obj)

    # 删除不存在的空间
    deleted_rows = Space.objects.exclude(id__in=[t.id for t in all_spaces]).update(is_deleted=True)
    logger.info("[sync_spaces] sync ({}), delete ({})".format(len(all_spaces), deleted_rows))
