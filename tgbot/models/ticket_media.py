__all__ = ("TicketMedia", )

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base, TimeStampMixin


class TicketMedia(Base, TimeStampMixin):
    __tablename__ = 'aviline_ticketmedia'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[str] = mapped_column(String(150), nullable=False)
    media_type: Mapped[int] = mapped_column(Integer(), default=1, nullable=False)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("aviline_ticket.id"))

    ticket: Mapped["Ticket"] = relationship(back_populates="medias")

    def __repr__(self):
        return f"TicketMedia(id={self.id!r}, telegram_id={self.telegram_id!r})"
