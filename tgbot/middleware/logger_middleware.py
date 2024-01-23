from tgbot.logging_config import middleware_debug
from typing import Callable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggerMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler: Callable, event: TelegramObject, data: Dict[str, Any]) -> Any:
        middleware_debug.debug(msg=f'{handler.__wrapped__} handler called')
        return await handler(event, data)
