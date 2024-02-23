__all__ = ("RedisConnectionPoolMiddleware", )

from typing import Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from redis.asyncio import BlockingConnectionPool, Redis


class RedisConnectionPoolMiddleware(BaseMiddleware):
    def __init__(self, pool: BlockingConnectionPool):
        self.__pool: BlockingConnectionPool = pool

    async def __aenter__(self):
        self._pool: Redis = await Redis(connection_pool=self.__pool)
        return self._pool

    # Do I really need this? The redis fromm doesn't seem to be required to close
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pool.aclose()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        async with self as cache:
            data['cache'] = cache
            return await handler(event, data)
