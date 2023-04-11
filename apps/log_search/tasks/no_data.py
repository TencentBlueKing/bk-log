import time

from celery.schedules import crontab
from celery.task import periodic_task

from django.core.cache import cache

from apps.log_search.constants import (
    InnerTag,
    TimeEnum,
    INDEX_SET_NO_DATA_CHECK_PREFIX,
    INDEX_SET_NO_DATA_CHECK_INTERVAL,
)
from apps.log_search.handlers.search.search_handlers_esquery import SearchHandler
from apps.log_search.models import LogIndexSet
from apps.utils.lock import share_lock
from apps.utils.log import logger
from apps.utils.thread import MultiExecuteFunc


@periodic_task(run_every=crontab(minute="*/15"))
@share_lock()
def no_data_check():
    logger.info("[no_data_check] start check index set no data")
    multi_execute_func = MultiExecuteFunc()
    index_set_id_list = LogIndexSet.objects.filter(is_active=True).values_list("index_set_id", flat=True)
    for index_set_id in index_set_id_list:
        multi_execute_func.append(index_set_id, index_set_no_data_check, index_set_id, use_request=False)
        cache.set(
            # 这里设置缓存时长为索引集无数据检查时间间隔+1的原因是作为时间冗余
            INDEX_SET_NO_DATA_CHECK_PREFIX + str(index_set_id),
            time.time(),
            TimeEnum.ONE_MINUTE_SECOND.value * INDEX_SET_NO_DATA_CHECK_INTERVAL + 1,
        )
    multi_execute_func.run()
    logger.info("[no_data_check]  end check index set no data")


def index_set_no_data_check(index_set_id):
    result = SearchHandler(index_set_id=index_set_id, search_dict={"time_range": "1d", "size": 1}).search(
        search_type=None
    )
    if result["total"] == 0:
        LogIndexSet.set_tag(index_set_id, InnerTag.NO_DATA.value)
        logger.warning(f"[no data check] index_set_id => [{index_set_id}] no have data")
        return
    LogIndexSet.delete_tag_by_name(index_set_id, InnerTag.NO_DATA.value)
