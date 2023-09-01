__all__ = ("edit_base_message", "get_client_message", "get_client_media",
           "on_startup", "on_shutdown")

from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.keyboard import KeyboardBuilder


async def on_startup(bot: Bot):
    print('starting', bot)


async def on_shutdown(bot: Bot):
    print('Stopping', bot)


async def edit_base_message(message: Message, text: str, keyboard: KeyboardBuilder):
    """
    :param message: Aiogram Message, base message to update text + inline keyboard
    :param text: jinja2 rendered template as str (or any str)
    :param keyboard: KeyboardBuilder/InlineKeyboard class - as reply_markup
    """
    if isinstance(keyboard, KeyboardBuilder):
        keyboard = keyboard.as_markup()

    await message.edit_text(
        text=text,
        reply_markup=keyboard
    )


def get_client_message(message: Message):
    """Get client message text based on message type (has or hasn't any media attached)"""
    user_message = ""
    user_message = message.text or user_message
    user_message = message.caption or user_message
    return user_message


def get_client_media(message: Message):
    """Get client media attached if there are any"""
    try:
        media_sources = ['']
        media = message.photo[0].file_id
        print(f"{media = }")
        return media
    # What is this for ?
    except Exception:
        return None
