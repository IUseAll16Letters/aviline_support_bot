__all__ = ("edit_base_message", "get_client_message", "parse_message_media",
           "on_startup", "on_shutdown", "add_caption_to_media", "get_media_type")

from typing import Optional, Union, Tuple, List

from aiogram import Bot
from aiogram.types import Message, InputMediaVideo, InputMediaPhoto, InputMediaDocument, InputMediaAudio, \
    InputMediaAnimation
from aiogram.utils.keyboard import KeyboardBuilder

from tgbot.constants import MIME_TYPES_ALLOWED, MEDIA_TYPES
from tgbot.types import Media, Optional_Media


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


def parse_message_media(message: Message) -> Tuple[Optional[bool], Optional_Media]:
    """Parse client photo or video from message if there are any attached"""
    media_object = None
    media_is_document = None
    print(message)
    if message.photo is not None:
        media_object = message.photo[-1]
        media_object = InputMediaPhoto(media=media_object.file_id)
        media_is_document = 0
        print(media_object.type, f'{media_object.media = }')

    elif message.video is not None or message.video_note is not None:
        media_object = message.video if message.video else message.video_note
        media_object = InputMediaVideo(media=media_object.file_id)
        media_is_document = message.video is None
        print(media_object.type, f'{media_object.media = }')

    elif message.audio is not None or message.voice is not None:
        media_object = message.audio if message.audio else message.voice
        media_object = InputMediaAudio(media=media_object.file_id)
        media_is_document = 1
        print(media_object.type, f"{media_object.media = }")

    elif message.document is not None and message.document.mime_type in MIME_TYPES_ALLOWED:
        print(f"{message.document.mime_type = }")
        if message.animation is not None:
            return media_is_document, media_object

        media_object = message.document.file_id
        media_object = InputMediaDocument(media=media_object)
        print(media_object.type, f"{media_object.media = }")
        media_is_document = 1

    return media_is_document, media_object


def get_media_type(media_file: Media):
    media_type = MEDIA_TYPES.get(media_file.__class__)
    if media_type is None:
        raise TypeError(
            f"Type identification error for {media_file.media} {media_file.__class__}")  # TODO set correct error type
    return media_type


def add_caption_to_media(media_files: List[Media], caption: str):
    for media in media_files:
        if isinstance(InputMediaPhoto, InputMediaVideo):
            media.caption = caption
            break
    else:
        media_files[0].caption = caption

