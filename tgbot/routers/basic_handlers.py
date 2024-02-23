from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import AVAILABLE_SERVICES, VERIFY_ENTRY, CONFIRM_POLICY
from ..keyboards import get_inline_keyboard_builder
from ..utils.template_engine import async_render_template
from ..crud import ProductRelatedQueries, get_product_problems
from ..navigation import get_navigation, template_from_state
from ..logging_config import navigation as navigation_logger


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    """/start command handler, clear state, no db_access"""
    await state.clear()
    keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True, row_col=(2, 1))
    text = await async_render_template('start.html')
    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup(),
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.reply("Раздел находится в разработке. Приносим извинения. Пожалуйста, воспользуйтесь командой /start"
                        "для получения информации о боте.")


@router.callback_query(F.data == 'back')
async def move_back(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    """
    Navigation reversing logic that hooks "back" callback_query based on states and state related template.
    Returns to base welcome message (/start) in case no state found.
    Node tree implementation using dfs with states as Node value and next/prev as parent/child Nodes
    """
    try:
        navigation = get_navigation()
        current_state = await state.get_state()
        data = await state.get_data()
        reverse_state = navigation.find(current_state).reverse_state(par=data.get("branch"))  # find node, then parent

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
            product_details = await ProductRelatedQueries(db_session=db_session)\
                .get_product_detail(product_name=data["product"])
            data['description'] = product_details.description
            data['attachment'] = product_details.attachment
            keyboard = get_inline_keyboard_builder(
                support_reachable=True,
            )

        elif template == 'warranty_confirm_entry.html':
            keyboard = get_inline_keyboard_builder(
                iterable=[VERIFY_ENTRY],
                row_col=(1, 1),
            )
        elif template == 'privacy_policy.html':
            keyboard = get_inline_keyboard_builder(iterable=[CONFIRM_POLICY])

        if reverse_state is None:
            await state.clear()
            keyboard = get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True, row_col=(2, 1))
        else:
            await state.set_state(reverse_state)

        await callback_query.message.edit_text(
            text=(await async_render_template(template, values=data)),
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        msg = f"Backward_reversing. Could not reverse, state: {await state.get_state()}. " \
              f"Error: {e.__class__.__name__}. {e}"
        navigation_logger.error(msg=msg)
        await callback_query.answer("Возникла ошибка возврата.\nПожалуйста, перезапустите бота через "
                                    "/start или свяжитесь с техподдержкой по телефону на сайте.")
        await callback_query.message.edit_text(
            text=(await async_render_template('start.html')),
            reply_markup=get_inline_keyboard_builder(AVAILABLE_SERVICES, is_initial=True, row_col=(2, 1)).as_markup(),
        )
        await state.clear()
