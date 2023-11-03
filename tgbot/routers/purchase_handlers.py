from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import PurchaseState
from tgbot.utils import render_template, edit_base_message
from tgbot.crud import ProductRelatedQueries
from tgbot.utils.shortcuts import recursive_scout_products, refresh_message_data_from_callback_query

router = Router()


@router.callback_query(F.data == 'purchase')
async def purchase_selected(
        callback_query: CallbackQuery,
        state: FSMContext,
        db_session: AsyncSession,
        bot: Bot
) -> None:
    data = await refresh_message_data_from_callback_query(callback_query, state, branch=callback_query.data)
    available_products = await ProductRelatedQueries(db_session).get_all_products()
    text = render_template('products_list.html', data)

    await state.set_state(PurchaseState.select_product)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(available_products, row_col=(1, 1)),
        bot=bot,
    )


# *start* TODO Fix this piece
@router.callback_query(PurchaseState.select_product)
async def product(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot) -> None:
    await recursive_scout_products(callback_query, state, db_session, bot)


@router.callback_query(PurchaseState.select_sub_product)
async def subproduct(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot) -> None:
    await recursive_scout_products(callback_query, state, db_session, bot)
# *end* TODO fix this piece
