from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from pathlib import Path

from states import BaseState, TechSupportState, PurchaseState
from keyboards import get_inline_keyboard_builder
from constants import AVAILABLE_PRODUCTS, KNOWN_PROBLEMS
from utils.template_engine import render_template

router = Router()


@router.callback_query(F.data == 'support')
async def purchase_selected(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TechSupportState.select_product)
    data = await state.update_data({"branch": "support"})
    text = render_template('products_list.html', data)
    await callback_query.message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder(AVAILABLE_PRODUCTS).as_markup()
    )


@router.callback_query(F.data.in_(AVAILABLE_PRODUCTS), TechSupportState.select_product)
async def purchase_product_options(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TechSupportState.product_problems)
    await state.update_data({"product": callback_query.data})

    problems = KNOWN_PROBLEMS.get(callback_query.data, [])
    problems_list = '\n'.join(f'{idx}. {problem}' for idx, problem in enumerate(problems, 1))

    await callback_query.message.edit_text(
        text=f"Вы находитесь в ветке: {'support'}\n"
             f"Выбранный продукт: {callback_query.data.capitalize()}\n"
             f"{problems_list}",
        reply_markup=get_inline_keyboard_builder(
            list(str(i) for i in range(1, len(problems) + 1)),
            support_reachable=True,
            row_col=(2, 2)).as_markup(),
    )


@router.callback_query(F.data.regexp(r'\d+'), TechSupportState.product_problems)
async def problem_number(callback_query: CallbackQuery, state: FSMContext):
    storage = await state.get_data()

    prod = storage.get('product')
    selected_problem = KNOWN_PROBLEMS.get(prod)[int(callback_query.data) - 1]

    await callback_query.message.edit_text(
        text=f'{"support" if state in TechSupportState else "purchase"} -> {storage.get("product")} -> '
             f'{selected_problem}',
        reply_markup=get_inline_keyboard_builder(support_reachable=True).as_markup(),
    )
