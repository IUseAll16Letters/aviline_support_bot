from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..states import TechSupportState
from ..keyboards import get_inline_keyboard_builder
from ..utils import edit_base_message, async_render_template
from ..crud import get_product_problems, get_problem_solution, ProductRelatedQueries
from ..logging_config import database
from ..utils.shortcuts import refresh_message_data_from_callback_query

router = Router()


@router.callback_query(F.data == 'support')
async def select_product(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot) -> None:
    data = await refresh_message_data_from_callback_query(callback_query, state, branch="support")
    text = await async_render_template('products_list.html', data)
    available_products = await ProductRelatedQueries(db_session).get_all_products()
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(available_products, row_col=(1, 1)),
        bot=bot,
    )
    await state.set_state(TechSupportState.select_product)


@router.callback_query(F.data != 'back', TechSupportState.select_product)
async def product_problems(
        callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot,
) -> None:
    data = await refresh_message_data_from_callback_query(callback_query, state, product=callback_query.data)

    problems = await get_product_problems(db_session, callback_query.data)
    data['problems'], data['enumerate'] = problems, enumerate
    text = await async_render_template('product_problems.html', values=data)
    keyboard = get_inline_keyboard_builder(
        [str(i) for i in range(1, len(data['problems']) + 1)],
        support_reachable=True,
        row_col=(2, 2),
    )
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=keyboard,
        bot=bot,
    )
    await state.set_state(TechSupportState.product_problems)


@router.callback_query(F.data.regexp(r'\d+'), TechSupportState.product_problems)
async def problem_solution(
        callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot,
) -> None:
    data = await refresh_message_data_from_callback_query(callback_query, state)

    try:
        solution = await get_problem_solution(db_session, data['product'], int(callback_query.data) - 1)
        data['problem'] = solution.title
        data['solutions'] = solution.solution.split("\n")
        data['attachments'] = solution.attachment

    except KeyError as e:
        msg = f'Key not found in Storage items. {e}'
        database.error(msg=msg)
        await callback_query.answer("Ошибка исполнения запроса к стороннему сервису. Пожалуйста подождите")
        return

    except IndexError as e:
        msg = f'Product{callback_query.data} has been removed or deactivated during session. ERR: {e}'
        database.error(msg=msg)
        await callback_query.answer("Продукт, который вы выбрали, был удален.\nПриносим извинения.")
        return

    text = await async_render_template('product_problem_solution.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(support_reachable=True),
        bot=bot,
    )
    await state.set_state(TechSupportState.problem_details)
