__all__ = ("Product", )

from typing import List

from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    problems: Mapped[List["ProductProblem"]] = relationship(
        back_populates="product", cascade="all, delete-orphan",
    )
    details: Mapped[List["ProductDetail"]] = relationship(
        back_populates="product", cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'Product(id={self.id!r}, name={self.name!r})'
