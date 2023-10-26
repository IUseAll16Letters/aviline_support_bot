__all__ = ("TicketRelatedQueries", )

from typing import Union, List, Optional
from datetime import datetime

from aiogram.types import InputMediaPhoto, InputMediaVideo, Message, InputMediaDocument, InputMediaAudio
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Ticket, TicketMedia, TicketMessage
from tgbot.utils import get_media_type
from tgbot.types import Media


class TicketRelatedQueries:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_ticket(self, question: str, user_telegram_id: int, created_at: Optional[datetime] = None):
        """Create ticket after client confirmed. 1st in chain"""
        stmt = insert(Ticket)\
            .values(
            question=question,
            customer=user_telegram_id,
            created_at=created_at or datetime.now())\
            .returning(Ticket.id)

        res = await self.db_session.execute(stmt)
        return res.first()

    async def create_user_media_attached(self, media: List[Media], ticket_id: int) -> None:
        """Attach media to ticket if it exists"""
        medias = [
            {
                "telegram_id": media_file.media,
                "media_type": get_media_type(media_file),
                "ticket_id": ticket_id,
            } for media_file in media
        ]
        stmt = insert(TicketMedia).values(medias).returning(TicketMedia.id)
        res = await self.db_session.execute(stmt)
        return res

    async def create_ticket_message(self, messages: List[Message], ticket_id: int) -> None:
        """Attach text to ticket if it exists"""
        messages = [
            {
                "message_id": message.message_id,
                "ticket_id": ticket_id,
            } for message in messages
        ]

        stmt = insert(TicketMessage).values(messages).returning(TicketMessage.id)
        res = await self.db_session.execute(stmt)
        return res

    async def get_customer_id_from_message(self, message_id: int):
        """When REPLY in any of AVILINE chat - get client to reply based on message id"""
        stmt = select(Ticket.customer, Ticket.id, Ticket.question)\
            .join_from(Ticket, TicketMessage)\
            .where(TicketMessage.message_id == message_id)
        res = await self.db_session.execute(stmt)
        return res.first()

    async def close_ticket(self, ticket_id: int):
        """Closing ticket after it was replied from chat"""
        stmt = update(Ticket).where(Ticket.id == ticket_id).values(is_solved=True)
        res = await self.db_session.execute(stmt)
        return res
