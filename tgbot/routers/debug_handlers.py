from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from ..logging_config import waster_queries

router = Router()


@router.callback_query()
async def wasted_query(callback: CallbackQuery, state: FSMContext) -> None:
    """Trash handler when no other work (for debug and log purpose)
    should raise error in future"""
    logger_message = f"wasted callback_query with data: {callback.data} | " \
                     f"at state: {await state.get_state()} | " \
                     f"from_user: {callback.from_user.id} | " \
                     f"template: {callback.message.text[:20]}..."
    waster_queries.info(msg=logger_message)
    await state.clear()
    await callback.answer("Ошибка отсутствия состояния\nПожалуйста нажмите назад или презапустите бота через /start "
                          "или из меню внизу")


@router.message()
async def wasted_message(message: Message, state: FSMContext) -> None:
    logger_message = f"wasted message text: {message.text}, " \
                     f"at state: {await state.get_state()}, " \
                     f"from_user: {message.from_user.id} in chat {message.chat.id}"
    waster_queries.debug(msg=logger_message)
