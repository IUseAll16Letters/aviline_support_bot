__all__ = ("create_ticket", "create_user_media_attached")

from datetime import datetime
from typing import Union

from aiogram.types import InputMediaPhoto, InputMediaVideo
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Ticket, TicketMedia


async def create_ticket(db_session: AsyncSession, question: str, user_telegram_id: int, created_at: datetime):
    stmt = insert(Ticket)\
        .values(question=question, customer=user_telegram_id, created_at=created_at)\
        .returning(Ticket.id)

    res = await db_session.execute(stmt)
    return res.first()


async def create_user_media_attached(
        db_session: AsyncSession, media: list[Union[InputMediaPhoto, InputMediaVideo]], ticket_id: int
) -> None:
    stmt = insert(TicketMedia).values(
        [{"telegram_id": i, "media_type": 1, "ticket_id": ticket_id} for i in media]
    ).returning(TicketMedia.id)
    await db_session.execute(stmt)
