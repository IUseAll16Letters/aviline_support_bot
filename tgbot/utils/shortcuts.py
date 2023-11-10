__all__ = ("refresh_message_data_from_callback_query", "recursive_scout_products")

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.crud import ProductRelatedQueries
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import PurchaseState
from tgbot.utils import edit_base_message, render_template
from tgbot.logging_config import database as database_logging


async def refresh_message_data_from_callback_query(callback_query: CallbackQuery, state: FSMContext, **kwargs) -> dict:
    data = await state.update_data(
        {
            "message_id": callback_query.message.message_id,
            "chat_id": callback_query.message.chat.id,
            **kwargs,
        }
    )
    return data


async def recursive_scout_products(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot):
    product = callback_query.data
    data = await refresh_message_data_from_callback_query(callback_query, state, product=callback_query.data)

    try:
        sub_products = await ProductRelatedQueries(db_session).get_sub_products(data["product"])
        if sub_products:
            text = render_template('sub_products_list.html', values=data)
            await edit_base_message(
                chat_id=data['chat_id'],
                message_id=data['message_id'],
                text=text,
                keyboard=get_inline_keyboard_builder(sub_products, row_col=(1, 1)),
                bot=bot,
            )
            await state.set_state(PurchaseState.select_sub_product)
        else:
            product_details = await ProductRelatedQueries(db_session).get_product_detail(product)
            data['title'], data['details'], data['attachment'] = product_details[0].title, product_details[
                0].description, product_details[0].attachment
            text = render_template('product_description.html', values=data)
            await edit_base_message(
                chat_id=data['chat_id'],
                message_id=data['message_id'],
                text=text,
                keyboard=get_inline_keyboard_builder(support_reachable=True),  # TODO get database check
                bot=bot,
            )
            await state.set_state(PurchaseState.product_description)
    except Exception as e:
        msg = f"purchase_select_options | state: select_product | could not fetch product details for " \
              f"{product} product | error: {e}"
        database_logging.error(msg=msg)
        await callback_query.answer('Возникла ошибка обращения к БД. Приносим извинения')
