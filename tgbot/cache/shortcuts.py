from typing import Any
from redis.asyncio.client import Redis

from tgbot.types import KeyLike
from config import settings


class RedisAdapter:
    """Redis cache adapter object"""
    def __init__(self):
        host = settings.CACHE[settings.DEBUG]['HOST']
        port = settings.CACHE[settings.DEBUG]['PORT']
        db = settings.CACHE[settings.DEBUG]['DBS']['cache']
        self.redis = Redis(host=host, port=port, db=db)

    async def set(self, key: KeyLike, value: Any):  # Typing should be set to Json_serializable
        await self.redis.set(key, value)

    def get(self, key: KeyLike):
        ...

    def exists(self, key: KeyLike):
        ...
