from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message


async def on_startup(bot: Bot):
    print('starting', bot)


async def on_shutdown(bot: Bot):
    print('Stopping', bot)


def get_client_message(message: Message):
    user_message = ""
    user_message = message.text or user_message
    user_message = message.caption or user_message
    return user_message


def get_client_media(message: Message):
    media_sources = ['']
    media = message.photo[0].file_id
    print(f"{media = }")

    return media
