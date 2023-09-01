from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.states import TechSupportState
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.utils import edit_base_message, render_template
from tgbot.crud import get_product_problems, get_problem_solution, get_all_products

router = Router()


@router.callback_query(F.data == 'support')
async def support_selected(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await state.set_state(TechSupportState.select_product)
    data = await state.update_data({"branch": "support"})
    text = render_template('products_list.html', data)
    available_products = await get_all_products(db_session)

    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder(available_products, row_col=(1, 1)),
    )


@router.callback_query(F.data != 'back', TechSupportState.select_product)
async def get_product_problems_handler(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await state.set_state(TechSupportState.product_problems)
    data = await state.update_data({"product": callback_query.data})
    problems = await get_product_problems(db_session, callback_query.data)
    data['problems'], data['enumerate'] = problems, enumerate

    text = render_template('product_problems.html', values=data)
    keyboard = get_inline_keyboard_builder(
        [str(i) for i in range(1, len(data['problems']) + 1)],
        support_reachable=True,
    )
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=keyboard,
    )


@router.callback_query(F.data.regexp(r'\d+'), TechSupportState.product_problems)
async def get_problem_solution_by_number(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    await state.set_state(TechSupportState.problem_details)
    data = await state.get_data()
    solution = await get_problem_solution(db_session, data['product'], int(callback_query.data) - 1)
    data['problem'], data['solution'] = solution.title, solution.solution

    text = render_template('product_problem_solution.html', values=data)
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder(support_reachable=True),
    )
