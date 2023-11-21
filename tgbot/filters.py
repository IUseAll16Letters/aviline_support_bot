__all__ = ("AvilineSupportChatFilter", )


from aiogram.filters import Filter
from aiogram.types import Message


class AvilineSupportChatFilter(Filter):
    def __init__(self, chats: set, check_is_reply: bool = False) -> None:
        self._chats = chats
        self._reply = check_is_reply

    async def __call__(self, message: Message) -> bool:
        reply = message.reply_to_message is not None if self._reply else True
        return reply and message.chat.id in self._chats
