__all__ = ("Optional_Media", "Media")

from typing import Union
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio


Optional_Media = Union[InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio, None]
Media = Union[InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio]
