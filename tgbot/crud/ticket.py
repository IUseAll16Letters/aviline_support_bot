__all__ = ("create_ticket", "create_user_media_attached", "create_ticket_message", "get_customer_id_from_message",
           "close_ticket")

from typing import Union, List
from datetime import datetime

from aiogram.types import InputMediaPhoto, InputMediaVideo, Message, InputMediaDocument, InputMediaAudio
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Ticket, TicketMedia, TicketMessage
from tgbot.utils import get_media_type


async def create_ticket(
        db_session: AsyncSession,
        question: str,
        user_telegram_id: int,
        created_at: datetime = datetime.now(),
):
    stmt = insert(Ticket)\
        .values(question=question, customer=user_telegram_id, created_at=created_at)\
        .returning(Ticket.id)

    res = await db_session.execute(stmt)
    return res.first()


async def create_user_media_attached(
        db_session: AsyncSession,
        media: List[Union[InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument]],
        ticket_id: int,
) -> None:
    medias = [
        {
            "telegram_id": media_file.media,
            "media_type": get_media_type(media_file),
            "ticket_id": ticket_id,
        } for media_file in media
    ]
    stmt = insert(TicketMedia).values(medias).returning(TicketMedia.id)
    res = await db_session.execute(stmt)
    return res


async def create_ticket_message(
        db_session: AsyncSession, messages: List[Message], ticket_id: int
) -> None:
    messages = [
        {
            "message_id": message.message_id,
            "ticket_id": ticket_id,
        } for message in messages
    ]
    stmt = insert(TicketMessage).values(messages).returning(TicketMessage.id)
    res = await db_session.execute(stmt)
    return res


async def get_customer_id_from_message(db_session: AsyncSession, message_id: int):
    stmt = select(Ticket.customer, Ticket.id, Ticket.question)\
        .join_from(Ticket, TicketMessage)\
        .where(TicketMessage.message_id == message_id)
    res = await db_session.execute(stmt)
    return res.first()


async def close_ticket(db_session: AsyncSession, ticket_id: int):
    stmt = update(Ticket).where(Ticket.id == ticket_id).values(is_solved=True)
    res = await db_session.execute(stmt)
    return res
