from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.constants import AVAILABLE_SERVICES, CONFIRMATION_MESSAGE
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.utils.template_engine import render_template
from tgbot.crud import ProductRelatedQueries, get_product_problems
from tgbot.navigation import Navigation, template_from_state
from tgbot.logging_config import navigation


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, db_session: AsyncSession, state: FSMContext) -> None:
    """/start command handler, clear state, no db_access"""
    await state.clear()
    keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True, row_col=(2, 1))
    text = render_template('start.html')
    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(F.data == 'back')
async def move_back(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    """
    Navigation reversing logic that hooks "back" callback_query based on states and state related template.
    Returns to base welcome message (/start) in case no state found.
    Node tree implementation using dfs with states as Node value and next/prev as parent/child Nodes
    """
    try:
        current_state = await state.get_state()
        data = await state.get_data()
        reverse_state = Navigation.find(current_state).reverse_state(par=data.get("branch"))  # get node, get node parent

        keyboard = get_inline_keyboard_builder()
        template = template_from_state[reverse_state]

        if template == 'products_list.html':
            keyboard = get_inline_keyboard_builder(await ProductRelatedQueries(db_session).get_all_products())

        elif template == 'product_problems.html':
            problems = await get_product_problems(db_session=db_session, product=data["product"])
            data['problems'], data['enumerate'] = problems, enumerate
            keyboard = get_inline_keyboard_builder(
                [str(i) for i in range(1, len(data['problems']) + 1)],
                support_reachable=True,
                row_col=(2, 2),
            )
        elif template == "product_description.html":
            keyboard = get_inline_keyboard_builder(
                support_reachable=True,
            )

        elif template == 'warranty_confirm_entry.html':
            keyboard = get_inline_keyboard_builder(
                iterable=[CONFIRMATION_MESSAGE, ],
                row_col=(1, 1),
            )

        if reverse_state is None:
            await state.clear()
            keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True, row_col=(2, 1))
        else:
            await state.set_state(reverse_state)

        await callback_query.message.edit_text(
            text=render_template(template, values=data),
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        msg = f"Backward_reversing. Could not reverse, state: {await state.get_state()}. Error: {e}"
        navigation.error(msg=msg)
        await callback_query.answer(f"Возникла ошибка реверса.\nПожалуйста, перезапустите бота через "
                                    f"/start или свяжитесь с техподдержкой")
