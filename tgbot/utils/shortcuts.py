__all__ = ("refresh_message_data_from_callback_query", )

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


async def refresh_message_data_from_callback_query(callback_query: CallbackQuery, state: FSMContext, **kwargs) -> dict:
    data = await state.update_data(
        {
            "message_id": callback_query.message.message_id,
            "chat_id": callback_query.message.chat.id,
            **kwargs,
        },
    )
    return data
