from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.constants import AVAILABLE_SERVICES
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.utils.template_engine import render_template
from tgbot.states import PurchaseState, TechSupportState, ContactSupportState
from tgbot.crud import get_all_products, get_product_problems
from tgbot.navigation import Navigation, template_from_state


router = Router()
D = dict()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """/start command handler, no state, no db_access"""
    # await state.clear()
    keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True)
    text = render_template('start.html')
    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(F.data == 'back')
async def move_back(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    """
    Navigation reversing logic that hooks "back" callback_query based on states and templates related to current state.
    Returns to base welcome message (/start) in case no state set.
    Node tree implementation using dfs with states as Node value and next/prev as parent/child Nodes
    """
    current_state = await state.get_state()
    data = await state.get_data()
    reverse_state = Navigation.find(current_state).reverse_state(data.get("branch"))  # get node, get node parent

    keyboard = get_inline_keyboard_builder()
    template = template_from_state[reverse_state]

    if template == 'products_list.html':
        keyboard = get_inline_keyboard_builder(await get_all_products(db_session))

    elif template == 'product_problems.html':
        problems = await get_product_problems(db_session=db_session, product=data["product"])
        data['problems'], data['enumerate'] = problems, enumerate
        keyboard = get_inline_keyboard_builder(
            [str(i) for i in range(1, len(data['problems']) + 1)],
            support_reachable=True)

    if reverse_state is None:
        await state.clear()
        keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True)
    else:
        await state.set_state(reverse_state)

    await callback_query.message.edit_text(
        text=render_template(template, values=data),
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query()
async def wasted_query(callback: CallbackQuery, state: FSMContext) -> None:
    """Trash handler when no other work (for debug and log purpose)
    shoudl raise error in future"""
    print(f'\033[032mCallback wasted\nCallback.data: {callback.data}\nstate: {await state.get_state()}\033\n'
          f'data: {await state.get_data()}[0m')


@router.message()
async def wasted_message(message: Message, state: FSMContext, db_session: AsyncSession) -> None:
    print(message.reply_to_message, message.chat.id)
    if message.reply_to_message:
        print(message.reply_to_message.message_id)

    print('\033[35;4m***\033[0m', message)
    from tgbot.utils import parse_message_media
    if any((message.photo, message.video,
            message.audio, message.document,
            message.video_note, message.voice)):
        print('caught media')
        media_is_document, new_media_object = parse_message_media(message)
        print(f'{media_is_document = }')
        print(new_media_object)
    else:
        print(message)
