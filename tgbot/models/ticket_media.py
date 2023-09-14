__all__ = ("TicketMedia", )

from sqlalchemy import Integer, Column, String, BigInteger, Text, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base, TimeStampMixin
from .ticket import Ticket


class TicketMedia(Base, TimeStampMixin):
    __tablename__ = 'aviline_ticketmedia'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger(), nullable=False) #  TODO I MA NOT INT< I AM STR!
    media_type: Mapped[int] = mapped_column(Integer(), default=1, nullable=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("aviline_ticket.id"))

    ticket: Mapped["Ticket"] = relationship(back_populates="medias")

    def __repr__(self):
        return f"TicketMedia(id={self.id!r}, ticket_id={self.ticket_id!r})"
