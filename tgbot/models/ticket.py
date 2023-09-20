__all__ = ("Ticket", )

from typing import List

from sqlalchemy import BigInteger, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimeStampMixin


class Ticket(Base, TimeStampMixin):
    __tablename__ = 'aviline_ticket'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer: Mapped[int] = mapped_column(BigInteger(), index=True, nullable=False)
    question: Mapped[str] = mapped_column(Text(), nullable=False)

    is_solved: Mapped[bool] = mapped_column(Boolean(), default=False)

    messages: Mapped[List["TicketMessage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan",
    )
    medias: Mapped[List["TicketMedia"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'Ticket(id={self.id!r}, name={self.question!r}, solved={self.is_solved!r})'