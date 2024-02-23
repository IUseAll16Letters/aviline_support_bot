__all__ = ("edit_base_message", "get_client_message", "parse_message_media",
           "webhook_on_startup", "polling_on_startup", "webhook_on_shutdown", "polling_on_shutdown",
           "add_caption_to_media", "get_media_type",
           "download_file_from_telegram_file_id", "get_allowed_media_id")

from typing import Optional, List, Union, Tuple

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InputMediaVideo, InputMediaPhoto
from aiogram.utils.keyboard import KeyboardBuilder

from ..constants import MIME_TYPES_ALLOWED, MEDIA_TYPES
from ..types import Media
from ..logging_config import utils_logger
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
    msg = f'Starting Bot(id={bot.id}) in POLLING mode...'
    print(msg)
    utils_logger.debug(msg=msg)


async def webhook_on_shutdown(bot: Bot) -> None:
    """Stopping webhook, bot: bot instance in webhook mode"""
    try:
        webhook_was_stopped = await bot.delete_webhook(drop_pending_updates=True)
        utils_logger.debug(msg=f'Webhook bot {bot.id} was successfully stopped: {webhook_was_stopped}')
    except Exception as e:
        utils_logger.warning(msg=f"Could not stop WEBHOOK for {bot.id}. {e}")
    print(bot.id, 'is stopped...')


async def polling_on_shutdown(bot: Bot) -> None:
    try:
        utils_logger.debug(msg=f'Bot {bot.id} was successfully stopped at POLLING mode')
    except Exception as e:
        utils_logger.warning(msg=f"Could not stop WEBHOOK for {bot.id}. {e}")


async def edit_base_message(chat_id: int, message_id: int, text: str, keyboard: KeyboardBuilder, bot: Bot) -> None:
    if isinstance(keyboard, KeyboardBuilder):
        keyboard = keyboard.as_markup()
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
        )
    except TelegramBadRequest as e:
        msg = f'Bad request for {chat_id}. Message was not modified. Err = {e}'
        utils_logger.error(msg=msg)
    except Exception as e:
        msg = f'Unknown exception during {edit_base_message.__name__}. Err = {e}'
        utils_logger.critical(msg=msg)


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


def get_allowed_media_id(message: Message) -> Union[Tuple[str, str], Tuple[int, int]]:
    file_id = -2
    extension = -2

    if message.photo is not None:
        if message.photo[-1].file_size > settings.MAX_WARRANTY_IMAGE_SIZE_BYTES:
            return -1, -1
        file_id = message.photo[-1].file_id
        extension = 'jpg'
    elif message.document is not None and message.document.mime_type.startswith('image'):
        if message.document.file_size > settings.MAX_WARRANTY_IMAGE_SIZE_BYTES:
            return -1, -1
        file_id = message.document.file_id
        extension = message.document.mime_type.replace('image/', '')

    return file_id, extension


async def download_file_from_telegram_file_id(bot_instance: Bot, telegram_file_id: str) -> bytes:
    """downloads file and returns it as bytes if filesize is < than settings.MAX_WARRANTY_IMAGE_SIZE_BYTES"""
    f_id = await bot_instance.get_file(telegram_file_id)
    file = await bot_instance.download_file(f_id.file_path)
    file_as_bytes = file.read()
    return file_as_bytes
