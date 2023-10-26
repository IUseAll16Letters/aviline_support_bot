from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import PurchaseState
from tgbot.utils import render_template, edit_base_message
from tgbot.crud import ProductRelatedQueries
from tgbot.utils.shortcuts import recursive_scout_products

router = Router()


@router.callback_query(F.data == 'purchase')
async def purchase_selected(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await state.set_state(PurchaseState.select_product)
    data = await state.update_data({"branch": callback_query.data})

    text = render_template('products_list.html', data)
    available_products = await ProductRelatedQueries(db_session).get_all_products()
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder(available_products, row_col=(1, 1)),
    )


# *start* TODO Fix this piece
@router.callback_query(PurchaseState.select_product)
async def purchase_product_options(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await recursive_scout_products(callback_query, state, db_session)


@router.callback_query(PurchaseState.select_sub_product)
async def select_subproduct_options(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await recursive_scout_products(callback_query, state, db_session)
# *end* TODO fix this piece
