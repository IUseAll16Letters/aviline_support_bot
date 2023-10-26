from typing import Tuple, Optional, Iterable

from aiogram.utils.keyboard import KeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_inline_keyboard_builder(
        iterable: Optional[Iterable] = None,
        is_initial: bool = False,
        row_col: Tuple[int, int] = (1, 1),
        support_reachable: bool = False,
):
    iterable = iterable if iterable else []
    builder = KeyboardBuilder(button_type=InlineKeyboardButton)
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            builder.button(text=key, callback_data=value)
    else:
        for item in iterable:
            builder.button(text=item, callback_data=item)

    builder.adjust(*row_col)

    if support_reachable:
        builder.row(InlineKeyboardButton(text="Остались вопросы? Задайте их нам",
                                         callback_data='contact_support'))
    if not is_initial:
        builder.row(InlineKeyboardButton(text="<< Назад", callback_data='back'))

    return builder
