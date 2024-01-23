__all__ = ("ThrottlingMiddleware", )

from typing import Callable, Any, Awaitable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, CallbackQuery
from aiogram.fsm.storage.redis import RedisStorage


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis_storage: RedisStorage):
        self.storage = redis_storage

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]):
        user = f'user_throttle_{event.from_user.id}'

        check_user = await self.storage.redis.get(name=user)

        if check_user:
            return

        await self.storage.redis.set(name=user, value=1, ex=1)
        return await handler(event, data)
