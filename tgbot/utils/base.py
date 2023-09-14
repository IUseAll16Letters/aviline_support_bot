__all__ = ("edit_base_message", "get_client_message", "parse_message_media",
           "on_startup", "on_shutdown")

from typing import Optional, Union

from aiogram import Bot
from aiogram.types import Message, InputMediaVideo, InputMediaPhoto, InputMediaDocument
from aiogram.utils.keyboard import KeyboardBuilder


async def on_startup(bot: Bot) -> None:
    print('starting', bot)


async def on_shutdown(bot: Bot) -> None:
    print('Stopping', bot)


async def edit_base_message(message: Message, text: str, keyboard: KeyboardBuilder) -> None:
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


def get_client_message(message: Message) -> Optional[str]:
    """Get client message text based on message type (has or hasn't any media attached)"""
    user_message = message.text
    user_message = message.caption or user_message
    return user_message


def parse_message_media(message: Message) -> Union[InputMediaPhoto, InputMediaVideo, InputMediaDocument, None]:
    """Parse client photo or video from message if there are any attached"""
    media_object = None
    print(message.photo, message.video)
    if getattr(message, 'photo') is not None:
        media_object = message.photo[-1]
        media_object = InputMediaPhoto(media=media_object.file_id)
        print(media_object.type, f'{media_object.media = }')

    elif getattr(message, 'video') is not None:
        media_object = message.video
        media_object = InputMediaVideo(media=media_object.file_id)
        print(media_object.type, f'{media_object.media = }')

    elif getattr(message, 'document') is not None:
        ...
        # media_object = message.document
        # TODO parse mime type

    return media_object
