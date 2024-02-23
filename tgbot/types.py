__all__ = ("Optional_Media", "Media", "KeyLike")

from typing import Union, TypeVar

from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio


Optional_Media = Union[InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio, None]
Media = Union[InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio]
KeyLike = TypeVar("KeyLike", str, int)
