import abc
import json
from abc import ABC

from django.core.serializers.json import DjangoJSONEncoder
from django_redis import get_redis_connection

import settings
from apps.log_search.constants import TimeEnum


def prefix_cache_key():
    return f"{settings.APP_CODE}:"


class CacheBase(ABC):
    CACHE_KEY_PREFIX = prefix_cache_key()
    CACHE_TIMEOUT = TimeEnum.ONE_MINUTE_SECOND.value
    cache = get_redis_connection()

    @abc.abstractclassmethod
    def refresh(cls):
        raise NotImplementedError

    @classmethod
    def serialize(cls, obj):
        return json.dumps(obj, cls=DjangoJSONEncoder)

    @classmethod
    def deserialize(cls, str):
        return json.loads(str)
