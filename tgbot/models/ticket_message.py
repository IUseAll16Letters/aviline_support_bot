__all__ = ("TicketMessage", )

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimeStampMixin


class TicketMessage(Base, TimeStampMixin):
    __tablename__ = "aviline_ticketmessage"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger())
    ticket_id: Mapped[int] = mapped_column(ForeignKey("aviline_ticket.id"))

    ticket: Mapped["Ticket"] = relationship(back_populates='messages')

    def __repr__(self):
        return f"TicketMessage(id={self.id!r}, ticket_id={self.ticket_id!r})"
