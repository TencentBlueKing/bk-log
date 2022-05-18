from collections import defaultdict

from apps.log_search.constants import TimeEnum
from apps.utils import local
from apps.utils.core.cache.cache_base import CacheBase
from apps.utils.log import logger

setattr(local, "host_info_cache", {})


class CmdbHostCache(CacheBase):
    CACHE_KEY = f"{CacheBase.CACHE_KEY_PREFIX}.cmdb.host_info"
    CACHE_TIMEOUT = TimeEnum.ONE_DAY_SECOND.value

    @classmethod
    def get(cls, bk_biz_id, host_ip):
        host_id = f"{bk_biz_id}:{host_ip}"
        host = local.host_info_cache.get(host_id, None)
        if host is None:
            result = cls.cache.hget(cls.CACHE_KEY, host_id)
            if result:
                result = cls.deserialize(result)
                local.host_info_cache[host_id] = result
                return result
            local.host_info_cache[host_id] = {}
            host = {}
        return host

    @classmethod
    def get_biz_cache_key(cls):
        return "{}.biz".format(cls.CACHE_KEY)

    @classmethod
    def refresh_by_biz(cls, bk_biz_id):
        from apps.log_search.handlers.biz import BizHandler

        host_info = BizHandler(bk_biz_id).get_hosts()
        result = defaultdict(dict)
        for host in host_info:
            result[host["host"]["bk_host_innerip"]][str(host["host"]["bk_cloud_id"])] = host
        return result

    @classmethod
    def refresh(cls):
        from apps.log_search.handlers.biz import BizHandler

        businesses = BizHandler.list()
        if not businesses:
            logger.error("[log_search][tasks]get business error")
            return

        new_keys = []
        biz_cache_key = cls.get_biz_cache_key()
        biz_ids = []

        for biz in businesses:
            bk_biz_id = biz["bk_biz_id"]
            biz_ids.append(bk_biz_id)
            objs = {}
            try:
                objs = cls.refresh_by_biz(bk_biz_id)
            except Exception as e:
                logger.error(f"get bk_biz_id[{bk_biz_id}] host info failed {e}")

            pipeline = cls.cache.pipeline(transaction=False)
            for key, obj in objs.items():
                host_id = f"{bk_biz_id}:{key}"
                pipeline.hset(cls.CACHE_KEY, host_id, cls.serialize(obj))
                new_keys.append(host_id)

            pipeline.hset(biz_cache_key, str(bk_biz_id), cls.serialize(list(objs.keys())))
            pipeline.expire(cls.CACHE_KEY, cls.CACHE_TIMEOUT)
            pipeline.execute()

        old_biz_ids = {biz_id.decode() for biz_id in cls.cache.hkeys(biz_cache_key)}
        new_biz_ids = {str(biz_id) for biz_id in biz_ids}
        delete_biz_ids = old_biz_ids - new_biz_ids
        if delete_biz_ids:
            cls.cache.hdel(biz_cache_key, *delete_biz_ids)

        cls.cache.expire(biz_cache_key, cls.CACHE_TIMEOUT)
        # 清理业务下已被删除的对象数据
        old_keys = {key.decode() for key in cls.cache.hkeys(cls.CACHE_KEY)}
        deleted_keys = set(old_keys) - set(new_keys)
        if deleted_keys:
            cls.cache.hdel(cls.CACHE_KEY, *deleted_keys)
        cls.cache.expire(cls.CACHE_KEY, cls.CACHE_TIMEOUT)
        logger.info(
            "cache_key({}) refresh CMDB data finished, amount: updated: {}, removed: {}, "
            "removed_biz: {}".format(cls.CACHE_KEY, len(new_keys), len(deleted_keys), len(delete_biz_ids))
        )
