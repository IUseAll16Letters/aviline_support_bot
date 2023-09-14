__all__ = ("ProductProblem", )


from sqlalchemy import Integer, Column, String, Boolean, BigInteger, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base, TimeStampMixin
from . import Product


class ProductProblem(Base, TimeStampMixin):
    """
    Class that implements Problem of Product model
    Attributes:
        id: Problem unique identifier
        title: Problem statement
        solution: Problem solution

        product_id: Relation to Product by FK

    Inherited Attributes:
        Inherits from Base, TimestampMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin classes, which provide additional functionality.

    """
    __tablename__ = 'aviline_productproblem'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    solution: Mapped[str] = mapped_column(Text(), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("aviline_product.id"))

    product: Mapped["Product"] = relationship(back_populates="problems")

    def __repr__(self):
        return F"Prod_Problem(id={self.id!r}, title={self.title[:10]})"
