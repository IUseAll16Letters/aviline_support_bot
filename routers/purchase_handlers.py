from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import get_inline_keyboard_builder
from states import PurchaseState, BaseState
from constants import AVAILABLE_PRODUCTS, PRODUCT_DESCRIPTION, AVAILABLE_SERVICES
from utils.template_engine import render_template


router = Router()


@router.callback_query(F.data == 'purchase')
async def purchase_selected(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(PurchaseState.select_product)
    data = await state.update_data({"branch": callback_query.data})
    text = render_template('products_list.html', data)
    await callback_query.message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder(AVAILABLE_PRODUCTS, row_col=(3, 2)).as_markup()
    )


@router.callback_query(F.data.in_(AVAILABLE_PRODUCTS), PurchaseState.select_product)
async def purchase_product_options(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(PurchaseState.product_description)
    data = await state.update_data({"product": callback_query.data})
    text = render_template('product_description.html', data)
    await callback_query.message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder(PRODUCT_DESCRIPTION, support_reachable=True).as_markup(),
    )


# @router.callback_query(PurchaseState.product_description)
# async def description_point(callback_query: CallbackQuery, state: FSMContext):
#     ...
