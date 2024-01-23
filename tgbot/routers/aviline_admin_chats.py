from aiogram import Router, Bot
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from ..filters import AvilineSupportChatFilter
from ..models import Ticket
from ..crud import TicketRelatedQueries
from ..utils.template_engine import async_render_template
from ..keyboards import get_inline_keyboard_builder
from config.settings import AVILINE_TECH_CHAT_ID, AVILINE_MANAGER_CHAT_ID
from ..constants import CONFIRMATION_MESSAGE, NEGATIVE_MESSAGE
from ..logging_config import handlers_logger

router = Router()


@router.message(AvilineSupportChatFilter(chats={AVILINE_TECH_CHAT_ID, AVILINE_MANAGER_CHAT_ID}, check_is_reply=True))
async def reply_in_aviline_chat(message: Message, db_session: AsyncSession, bot: Bot) -> None:
    quoted_message = message.reply_to_message.message_id
    ticket: Ticket = await TicketRelatedQueries(db_session) \
        .get_ticket_by_reply_message_id(replied_message_id=quoted_message)

    if ticket is None:
        msg = f'Ticket not found! {message.reply_to_message.message_id} | {message.reply_to_message.text}'
        handlers_logger.error(msg=msg)

    else:
        values = {"question": ticket.question, "answer": message.text}
        text = await async_render_template('reply_client_question.html', values=values)
        client_answer_keyboard = get_inline_keyboard_builder(
            is_initial=True,
            iterable=[CONFIRMATION_MESSAGE, NEGATIVE_MESSAGE],
            row_col=(2, 1),
        )
        await bot.send_message(chat_id=ticket.customer, text=text, reply_markup=client_answer_keyboard.as_markup())

        await TicketRelatedQueries(db_session).close_ticket(ticket_id=ticket.id)
        await db_session.commit()
