__all__ = ("edit_base_message", "get_client_message", "parse_message_media",
           "webhook_on_startup", "polling_on_startup", "webhook_on_shutdown", "polling_on_shutdown",
           "add_caption_to_media", "get_media_type",
           "download_file_from_telegram_file_id", "get_allowed_media_id")

from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

from aiogram import Bot
from aiogram.types import Message, InputMediaVideo, InputMediaPhoto, InputMediaDocument, InputMediaAudio, CallbackQuery
from aiogram.utils.keyboard import KeyboardBuilder

from tgbot.constants import MIME_TYPES_ALLOWED, MEDIA_TYPES
from tgbot.types import Media, Optional_Media
from tgbot.logging_config import utils_logger

from config import settings


async def webhook_on_startup(bot: Bot) -> None:
    """Initing webhook, bot: inited bot instance with attached token"""
    webhook_is_set = await bot.set_webhook(
        url=f"{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH[1:]}",
        drop_pending_updates=True,
        secret_token=settings.WEBHOOK_SECRET,
    )
    utils_logger.debug(msg=f'Webhook was successfully set for {bot.id}: {webhook_is_set}. Starting in WEBHOOK mode')


async def polling_on_startup(bot: Bot) -> None:
    utils_logger.debug(msg=f'Starting Bot(id={bot.id}) in POLLING mode')


async def webhook_on_shutdown(bot: Bot) -> None:
    """Stopping webhook, bot: bot instance in webhook mode"""
    try:
        webhook_was_stopped = await bot.delete_webhook(drop_pending_updates=True)
        utils_logger.debug(msg=f'Webhook bot {bot.id} was successfully stopped: {webhook_was_stopped}')
    except Exception as e:
        utils_logger.warning(msg=f"Could not stop WEBHOOK for {bot.id}. {e}")


async def polling_on_shutdown(bot: Bot) -> None:
    try:
        utils_logger.debug(msg=f'Bot {bot.id} was successfully stopped at POLLING mode')
    except Exception as e:
        utils_logger.warning(msg=f"Could not stop WEBHOOK for {bot.id}. {e}")


async def edit_base_message(chat_id: int, message_id: int, text: str, keyboard: KeyboardBuilder, bot: Bot) -> None:
    if isinstance(keyboard, KeyboardBuilder):
        keyboard = keyboard.as_markup()

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard,
    )


def get_client_message(message: Message) -> Optional[str]:
    """Get client message text based on message type (has or hasn't any media attached)"""
    user_message = message.text
    user_message = message.caption or user_message
    return user_message


def parse_message_media(message: Message) -> Optional[str]:
    """Parse client photo or video from message if there are any attached"""
    media_object = None

    if message.photo is not None:
        media_object = f"img%%{message.photo[-1].file_id}"

    elif message.video is not None or message.video_note is not None:
        media_object = message.video if message.video else message.video_note
        media_object = f"video%%{media_object.file_id}"

    elif message.audio is not None or message.voice is not None:
        media_object = message.audio if message.audio else message.voice
        media_object = f"audio%%{media_object.file_id}"

    elif message.document is not None and message.document.mime_type in MIME_TYPES_ALLOWED:
        media_object = f"document%%{message.document.file_id}"

    return media_object


def get_media_type(media_prefix: str):
    media_type = MEDIA_TYPES.get(media_prefix)
    if media_type is None:
        raise TypeError(
            f"Type identification error for '{media_prefix}' {media_prefix.__class__}")  # TODO set correct error type
    return media_type


def add_caption_to_media(media_files: List[Media], caption: str):
    for media in media_files:
        if isinstance(InputMediaPhoto, InputMediaVideo):
            media.caption = caption
            break
    else:
        media_files[0].caption = caption


def get_allowed_media_id(message: Message):
    # TODO FIX THIS MESS
    file_id = None
    try:
        print(f'warranty: {message.document.mime_type = }')
    except Exception:
        ...
    if message.photo or (message.document is not None and message.document.mime_type.startswith('image')):
        if message.photo:
            file_id = message.photo[-1].file_id
        else:
            file_id = message.document.file_id

    return file_id


async def download_file_from_telegram_file_id(bot_instance: Bot, telegram_file_id: str, telegram_user_id: int) -> str:
    """downloads file and returns its location"""
    f = await bot_instance.get_file(telegram_file_id)
    dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    user_file_name = f"{telegram_user_id}_{dt}.jpg"
    full_file_name = str(Path(settings.WARRANTY_CARDS_LOCATION) / user_file_name)
    # print(f'warranty: {full_file_name = }')
    await bot_instance.download_file(f.file_path, destination=full_file_name)
    return full_file_name
