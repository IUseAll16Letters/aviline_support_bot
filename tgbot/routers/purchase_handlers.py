from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import PurchaseState
from tgbot.utils import render_template, edit_base_message
from tgbot.crud import get_all_products


router = Router()


@router.callback_query(F.data == 'purchase')
async def purchase_selected(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await state.set_state(PurchaseState.select_product)
    data = await state.update_data({"branch": callback_query.data})

    text = render_template('products_list.html', data)
    available_products = await get_all_products(db_session)
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder(available_products, row_col=(1, 1)),
    )


@router.callback_query(F.data != "back", PurchaseState.select_product)  # TODO Achtung, tyt kostil!
async def purchase_product_options(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await state.set_state(PurchaseState.product_description)
    product = callback_query.data

    # TODO select from database if product has subproducts -> set state to subproducts, else set product details
    #  also call must be DRY
    data = await state.update_data({"product": product})
    text = render_template('product_description.html', data)
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder(support_reachable=True),   # TODO get database check
    )
