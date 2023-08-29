from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.states import TechSupportState
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.constants import AVAILABLE_PRODUCTS, KNOWN_PROBLEMS
from tgbot.utils.template_engine import render_template
from tgbot.utils.base import get_product_problems

router = Router()


@router.callback_query(F.data == 'support')
async def support_selected(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TechSupportState.select_product)
    data = await state.update_data({"branch": "support"})
    text = render_template('products_list.html', data)
    await callback_query.message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder(AVAILABLE_PRODUCTS, row_col=(1, 1)).as_markup()
    )


@router.callback_query(F.data.in_(AVAILABLE_PRODUCTS), TechSupportState.select_product)
async def support_product_options(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TechSupportState.product_problems)
    data = await state.update_data({"product": callback_query.data})

    # TODO make more predictable. i.e. wrap in pydantic model
    problems_list = get_product_problems(data['product'], KNOWN_PROBLEMS)
    data['problems'], data['enumerate'] = problems_list, enumerate
    keyboard = get_inline_keyboard_builder(
        [str(i) for i in range(1, len(data['problems']) + 1)],
        support_reachable=True,
    )

    await callback_query.message.edit_text(
        text=render_template('product_problems.html', values=data),
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data.regexp(r'\d+'), TechSupportState.product_problems)
async def problem_number(callback_query: CallbackQuery, state: FSMContext):
    storage = await state.get_data()
    await state.set_state(TechSupportState.problem_details)
    data = await state.get_data()
    prod = storage.get('product')
    # Get the problem from const. TODO pydaticify this
    selected_problem = KNOWN_PROBLEMS.get(prod)[int(callback_query.data) - 1]
    data['problem'], data['solution'] = selected_problem[0], selected_problem[1]

    await callback_query.message.edit_text(
        text=render_template('product_problem_solution.html', values=data),
        reply_markup=get_inline_keyboard_builder(support_reachable=True).as_markup(),
    )
