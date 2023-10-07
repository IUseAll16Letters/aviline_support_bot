from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import PurchaseState
from tgbot.utils import render_template, edit_base_message
from tgbot.crud import get_all_products, get_product_detail
from tgbot.logging_config.setup_logger import database as database_logging

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


@router.callback_query(PurchaseState.select_product)
async def purchase_product_options(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession) -> None:
    await state.set_state(PurchaseState.product_description)
    product = callback_query.data
    data = await state.update_data({"product": product})
    product_details = await get_product_detail(db_session, product)
    try:
        if product_details:
            data['title'], data['details'], data['attachment'] = product_details[0].title, product_details[0].description, product_details[0].attachment

        text = render_template('product_description.html', values=data)
        await edit_base_message(
            message=callback_query.message,
            text=text,
            keyboard=get_inline_keyboard_builder(support_reachable=True),   # TODO get database check
        )
    except Exception as e:
        msg = f"purchase_select_options | state: select_product | could not fetch product details for " \
              f"{product} product | error: {e}"
        database_logging.error(msg=msg)
        await callback_query.answer('Возникла ошибка обращения к БД. Приносим извинения')
