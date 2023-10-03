__all__ = ("Visitor", )

from sqlalchemy import String, Text, ForeignKey, URL, Integer, BigInteger
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base, TimeStampMixin


class Visitor(Base, TimeStampMixin):
    __tablename__ = 'aviline_visitor'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger(), index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    firstname: Mapped[str] = mapped_column(String(255), nullable=True)
    lastname: Mapped[str] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return F"Bot_Visitor(id={self.id!r}, title={self.username})"
