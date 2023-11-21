from typing import Tuple, Union
from redis.asyncio.client import Redis
from datetime import timedelta

from tgbot.types import KeyLike
from tgbot.logging_config import redis_logger
from config import settings


class RedisAdapter:
    """Redis cache adapter object"""
    host = settings.CACHE[settings.DEBUG]['HOST']
    port = settings.CACHE[settings.DEBUG]['PORT']
    db = settings.CACHE[settings.DEBUG]['DBS']['cache']
    redis = Redis(host=host, port=port, db=db)
    lock_ttl = settings.CACHE_SUPPORT_TTL
    image_ttl = settings.CACHE_IMAGE_TTL
    lock_prefix = "support_lock_"
    image_prefix = 'warranty_image_'

    @classmethod
    async def set_lock(cls, user_id: KeyLike):  # Typing should be set to Json_serializable
        return await cls.redis.set(f"{cls.lock_prefix}{user_id}", 1, ex=timedelta(seconds=cls.lock_ttl))

    @classmethod
    async def check_lock_ttl(cls, user_id: KeyLike) -> Union[int, Tuple[int, int]]:
        """return ttl in minutes"""
        ttl = await cls.redis.ttl(f"{cls.lock_prefix}{user_id}")
        if ttl == -2:
            return -2, -2
        elif ttl == -1:
            msg = f"Got endless lock for {cls.lock_prefix}{user_id} key. Expected <{cls.lock_ttl}"
            redis_logger.error(msg=msg)
            return -1, -1
        else:
            return ttl // 60, ttl % 60

    @classmethod
    async def save_client_warranty_image(cls, user_id: KeyLike, file) -> bool:
        return await cls.redis.set(f"{cls.image_prefix}{user_id}", file, ex=timedelta(seconds=cls.image_ttl))

    @classmethod
    async def check_client_warranty_image_exists(cls, user_id: KeyLike) -> int:
        return await cls.redis.ttl(f"{cls.image_prefix}{user_id}")

    @classmethod
    async def get_client_warranty_image(cls, user_id: KeyLike):
        return await cls.redis.get(f"{cls.image_prefix}{user_id}")

    @classmethod
    async def clear_client_warranty_image(cls, user_id: KeyLike):
        return await cls.redis.delete(f"{cls.image_prefix}{user_id}")
