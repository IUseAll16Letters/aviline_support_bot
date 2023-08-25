from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from constants import AVAILABLE_SERVICES, AVAILABLE_PRODUCTS
from keyboards import get_inline_keyboard_builder
from utils.template_engine import render_template
from states import PurchaseState, TechSupportState, ContactSupportState


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES)
    text = render_template('start.html')
    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(F.data == 'back')
async def move_back(callback_query: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    print(f'BACK from: {current_state = }')
    data = await state.get_data()
    print(data)
    # TODO enter_name состояние должно возвращать пользователя к вопросу, с которого он перешел

    keyboard = get_inline_keyboard_builder()
    # TODO clean mess
    if current_state is not None:
        reverse_template = {
            ContactSupportState.enter_message: ('client_enter_contact.html', ContactSupportState.enter_contact),
            ContactSupportState.enter_contact: ('client_enter_name.html', ContactSupportState.enter_name),
            ContactSupportState.enter_name: ('products_list.html', PurchaseState.select_product if data['branch'] == 'purchase' else TechSupportState.select_product),
            PurchaseState.product_description: ('products_list.html', PurchaseState.select_product),
            TechSupportState.product_problems: ('products_list.html', TechSupportState.select_product),
        }

    if current_state is not None and current_state in (reverse_template.keys()):
        pattern, state_to_set = reverse_template.get(current_state),
        print(pattern, state_to_set)
        await state.set_state(state_to_set)
        if pattern == 'products_list.html':
            keyboard = get_inline_keyboard_builder(AVAILABLE_PRODUCTS)
    else:
        print('ELSE')
        await state.clear()
        keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True)
        pattern = 'start.html'

    await callback_query.answer(text="Not yet implemented, but your data is clear")

    await callback_query.message.edit_text(
        text=render_template(pattern, values=data),
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query()
async def wasted_query(callback: CallbackQuery, state: FSMContext) -> None:
    print(f'\033[032mCallback wasted\nCallback.data: {callback.data}\nstate: {await state.get_state()}\033[0m')
