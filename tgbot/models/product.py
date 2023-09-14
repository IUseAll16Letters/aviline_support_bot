__all__ = ("Product", )

from typing import List

from sqlalchemy import Integer, Column, String, Boolean, BigInteger, Text, DateTime, func
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base, TimeStampMixin


class Product(Base, TimeStampMixin):
    """
    Class that implements Product model
    Attributes:
        id: Product unique identifier
        name: Product name, as varchar255
        description: Product description as text

    Inherited Attributes:
        Inherits from Base, TimestampMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin classes, which provide additional functionality.

    """
    __tablename__ = 'aviline_product'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)

    problems: Mapped[List["ProductProblem"]] = relationship(
        back_populates="product", cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'Product(id={self.id!r}, name={self.name!r})'
