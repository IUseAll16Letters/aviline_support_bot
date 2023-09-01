from typing import List, Tuple

from aiogram.utils.keyboard import KeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_inline_keyboard_builder(
        iterable: List[str] | None = None,
        is_initial: bool = False,
        row_col: Tuple[int, int] = (2, 1),
        support_reachable: bool = False,
):
    iterable = iterable if iterable else []
    builder = KeyboardBuilder(button_type=InlineKeyboardButton)
    for item in iterable:
        builder.button(text=item, callback_data=item)

    builder.adjust(*row_col)

    if support_reachable:
        builder.row(InlineKeyboardButton(text="Остались вопросы? Задайте их нам напрямую:",
                                         callback_data='contact_support'))
    if not is_initial:
        builder.row(InlineKeyboardButton(text="<< Назад", callback_data='back'))

    return builder


if __name__ == '__main__':
    from constants import AVAILABLE_PRODUCTS, AVAILABLE_SERVICES
    print(get_inline_keyboard_builder(AVAILABLE_SERVICES).as_markup())
    print(get_inline_keyboard_builder(AVAILABLE_PRODUCTS).as_markup())
    print(get_inline_keyboard_builder(None).as_markup())
