__all__ = ("AvilineSupportChatFilter", )

from typing import Iterable

from aiogram.filters import BaseFilter
from aiogram.types import Message


class AvilineSupportChatFilter(BaseFilter):
    def __init__(self, chats: Iterable, check_is_reply: bool = False) -> None:
        self._chats = set(chats)
        self._reply = check_is_reply

    async def __call__(self, message: Message) -> bool:
        reply = message.reply_to_message is not None if self._reply else True
        return reply and message.chat.id in self._chats
