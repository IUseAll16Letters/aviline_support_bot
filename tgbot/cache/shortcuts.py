from datetime import timedelta
from typing import Tuple, Union

from redis.asyncio import Redis

from ..types import KeyLike
from ..logging_config import redis_logger
from config import settings


class RedisFacade:
    """Redis memory storage facade object"""
    lock_ttl = settings.CACHE_SUPPORT_TTL
    image_ttl = settings.CACHE_IMAGE_TTL
    lock_prefix = "support_lock_"
    image_prefix = 'warranty_image_'

    def __init__(self, redis: Redis):
        self._pool = redis

    async def set_lock(self, user_id: KeyLike):  # Typing should be set to Json_serializable
        return await self._pool.set(f"{self.lock_prefix}{user_id}", 1, ex=timedelta(seconds=self.lock_ttl))

    async def check_lock_ttl(self, user_id: KeyLike) -> Union[int, Tuple[int, int]]:
        """return ttl in minutes"""
        ttl = await self._pool.ttl(f"{self.lock_prefix}{user_id}")
        if ttl == -2:
            return -2, -2
        elif ttl == -1:
            msg = f"Got endless lock for {self.lock_prefix}{user_id} key. Expected <{self.lock_ttl}"
            redis_logger.error(msg=msg)
            return -1, -1
        else:
            return ttl // 60, ttl % 60

    async def save_client_warranty_image(self, user_id: KeyLike, file) -> bool:
        return await self._pool.set(f"{self.image_prefix}{user_id}", file, ex=timedelta(seconds=self.image_ttl))

    async def check_client_warranty_image_exists(self, user_id: KeyLike) -> int:
        return await self._pool.ttl(f"{self.image_prefix}{user_id}")

    async def get_client_warranty_image(self, user_id: KeyLike):
        return await self._pool.get(f"{self.image_prefix}{user_id}")

    async def clear_client_warranty_image(self, user_id: KeyLike):
        return await self._pool.delete(f"{self.image_prefix}{user_id}")
