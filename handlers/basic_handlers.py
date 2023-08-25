from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from constants import AVAILABLE_SERVICES
from keyboards import get_inline_keyboard_builder
from templates import start


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_data({"history": []})
    await message.answer(
        start.START,
        reply_markup=get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True).as_markup(),
    )


@router.callback_query(F.data == 'back')
async def move_back(callback_query: CallbackQuery, state: FSMContext) -> None:
    print(f'BACK from: {await state.get_state() = }')
    await state.set_data({"history": []})
    await callback_query.answer(text="Not yet implemented, but your data is clear")
    await callback_query.message.edit_text(
        text=start.START,
        reply_markup=get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True).as_markup(),
    )


@router.callback_query()
async def wasted_query(callback: CallbackQuery, state: FSMContext) -> None:
    print(f'\033[032mCallback wasted\nCallback.data: {callback.data}\nstate: {await state.get_state()}\033[0m')
