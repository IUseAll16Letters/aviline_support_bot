from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.constants import AVAILABLE_SERVICES, AVAILABLE_PRODUCTS, KNOWN_PROBLEMS
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.utils.template_engine import render_template
from tgbot.utils.base import get_product_problems
from tgbot.states import PurchaseState, TechSupportState, ContactSupportState


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True)
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
            ContactSupportState.entry_confirmation: ('client_enter_message.html', ContactSupportState.enter_message),
            ContactSupportState.enter_message: ('client_enter_contact.html', ContactSupportState.enter_contact),
            ContactSupportState.enter_contact: ('client_enter_name.html', ContactSupportState.enter_name),
            ContactSupportState.enter_name: ('products_list.html', PurchaseState.select_product if data['branch'] == 'purchase' else TechSupportState.select_product),
            PurchaseState.product_description: ('products_list.html', PurchaseState.select_product),
            TechSupportState.product_problems: ('products_list.html', TechSupportState.select_product),
            TechSupportState.problem_details: ('product_problems.html', TechSupportState.product_problems),
        }

    if current_state is not None and current_state in (reverse_template.keys()):
        pattern, state_to_set = reverse_template[current_state]
        print(pattern, state_to_set)
        await state.set_state(state_to_set)
        if pattern == 'products_list.html':
            keyboard = get_inline_keyboard_builder(AVAILABLE_PRODUCTS)
        if pattern == 'product_problems.html':
            problems_list = get_product_problems(data['product'], KNOWN_PROBLEMS)
            data['problems'], data['enumerate'] = problems_list, enumerate
            keyboard = get_inline_keyboard_builder(
                [str(i) for i in range(1, len(data['problems']) + 1)],
                support_reachable=True,
            )
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
    print(f'\033[032mCallback wasted\nCallback.data: {callback.data}\nstate: {await state.get_state()}\033\n'
          f'data: {await state.get_data()}[0m')


# @router.message()
# async def get_chat_id(message: Message, tgbot: Bot):
#
#     print(f"{message.message_thread_id = }")
#     res = await tgbot.delete_message(chat_id=AVILINE_CHAT_ID, message_id=message.message_thread_id)
#     print(f'{res = }')
#     res = await tgbot.delete_message(chat_id=AVILINE_CHAT_ID, message_id=message.message_id)
#     print(f'{res = }')

    # for attr in dir(message):
    #     try:
    #         print(attr)
    #         print(getattr(message, attr))
    #         print()
    #     except Exception as e:
    #         ...
