from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from jinja2 import TemplateSyntaxError
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import PurchaseState
from tgbot.utils import async_render_template, edit_base_message
from tgbot.crud import ProductRelatedQueries
from tgbot.utils.shortcuts import refresh_message_data_from_callback_query
from tgbot.logging_config import database as database_logging

router = Router()


@router.callback_query(F.data == 'purchase')
async def purchase_selected(
        callback_query: CallbackQuery,
        state: FSMContext,
        db_session: AsyncSession,
        bot: Bot,
) -> None:
    data = await refresh_message_data_from_callback_query(callback_query, state, branch=callback_query.data)
    available_products = await ProductRelatedQueries(db_session).get_all_products()
    text = await async_render_template('products_list.html', data)

    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(available_products, row_col=(1, 1)),
        bot=bot,
    )
    await state.set_state(PurchaseState.select_product)


@router.callback_query(StateFilter(PurchaseState.select_product, PurchaseState.select_sub_product))
async def product_subproduct_selected(
        callback_query: CallbackQuery,
        state: FSMContext,
        db_session: AsyncSession,
        bot: Bot,
) -> None:
    product = callback_query.data

    try:
        sub_products = await ProductRelatedQueries(db_session).get_sub_products(product)
        data = await refresh_message_data_from_callback_query(callback_query, state, product=product)
        if sub_products:
            text = await async_render_template('sub_products_list.html', values=data)
            await edit_base_message(
                chat_id=data['chat_id'],
                message_id=data['message_id'],
                text=text,
                keyboard=get_inline_keyboard_builder(sub_products, row_col=(1, 1)),
                bot=bot,
            )
            await state.set_state(PurchaseState.select_sub_product)
        else:
            data = await state.get_data()
            product_details = await ProductRelatedQueries(db_session).get_product_detail(product)
            data['description'] = product_details.description
            data['attachment'] = product_details.attachment
            text = await async_render_template('product_description.html', values=data)
            await edit_base_message(
                chat_id=data['chat_id'],
                message_id=data['message_id'],
                text=text,
                keyboard=get_inline_keyboard_builder(support_reachable=True),  # TODO get database check
                bot=bot,
            )
            await state.set_state(PurchaseState.product_description)
    except TemplateSyntaxError as e:
        msg = f"Jinja template error | error: {e.__class__} | {e}"
        database_logging.error(msg=msg)
        await callback_query.answer(
            text="Возникла ошибка отрисовки ответа. "
                 "Пожалуйста вернитесь к предыдущему пункту меню",
        )

    except Exception as e:
        msg = f"purchase_select_options | state: select_product | could not fetch product details for " \
              f"{product} product | error: {e.__class__} | {e}"
        database_logging.error(msg=msg)
        await callback_query.answer(
            text='Возникла ошибка обращения к БД. '
                 'Пожалуйста если ошибка повторится - пожалуйста перезапустите бота через /start',
        )
